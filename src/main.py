import sys
import asyncio
import os
import json
from typing import Dict, Any

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph
from colorama import Fore, Back, Style, init
import questionary
from aztp_client import Aztp
from agents.ben_graham import ben_graham_agent
from agents.bill_ackman import bill_ackman_agent
from agents.fundamentals import fundamentals_agent
from agents.portfolio_manager import portfolio_management_agent
from agents.technicals import technical_analyst_agent
from agents.risk_manager import risk_management_agent
from agents.sentiment import sentiment_agent
from agents.warren_buffett import warren_buffett_agent
from graph.state import AgentState
from agents.valuation import valuation_agent
from utils.display import print_trading_output
from utils.analysts import ANALYST_ORDER, get_analyst_nodes
from utils.progress import progress
from llm.models import LLM_ORDER, get_model_info

import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tabulate import tabulate
from utils.visualize import save_graph_as_png

# Load environment variables from .env file
load_dotenv()

init(autoreset=True)

async def secure_wrap_agents(client: Aztp) -> Dict[str, Any]:
    """Wrap existing agents with secure connections."""
    # Map of agent names to their instances
    agents = {
        "warren_buffett": warren_buffett_agent,
        "ben_graham": ben_graham_agent,
        "bill_ackman": bill_ackman_agent,
        "fundamentals": fundamentals_agent,
        "technicals": technical_analyst_agent,
        "sentiment": sentiment_agent,
        "valuation": valuation_agent,
        "portfolio": portfolio_management_agent,
        "risk": risk_management_agent
    }
    
    # Map of agent keys to their AZTP-compliant names
    aztp_names = {
        "warren_buffett": "warren-buffett",
        "ben_graham": "ben-graham",
        "bill_ackman": "bill-ackman",
        "fundamentals": "fundamentals",
        "technicals": "technicals",
        "sentiment": "sentiment",
        "valuation": "valuation",
        "portfolio": "portfolio",
        "risk": "risk"
    }
    
    print("\nInitializing secure agent connections...")
    
    # Secure each agent with AZTP
    secured_agents = {}
    for name, agent in agents.items():
        print(f"Securing {name} agent...")
        secured_conn = await client.secure_connect(
            agent,
            name=f"{aztp_names[name]}-analyst"
        )
        
        # Make the secured agent callable while maintaining sync interface
        def make_callable(secure_conn):
            def wrapped_agent(state: AgentState):
                return secure_conn._agent(state)  # Use the original agent function
            return wrapped_agent
            
        secured_agents[name] = make_callable(secured_conn)
    
    # Verify all agents
    print("\nVerifying agent identities...")
    verification_tasks = [
        client.verify_identity(agent.__closure__[0].cell_contents)  # Get the underlying SecureConnection
        for name, agent in secured_agents.items()
    ]
    agents_valid = await asyncio.gather(*verification_tasks)
    
    if not all(agents_valid):
        raise ValueError("Agent verification failed")
    
    # Print identities for debugging
    for name, agent in secured_agents.items():
        identity = await client.get_identity(agent.__closure__[0].cell_contents)  # Get the underlying SecureConnection
        print(f"\n{name.title()} Identity:", identity)
    
    print("\nAll agents verified successfully!")
    return secured_agents

def parse_hedge_fund_response(response):
    import json

    try:
        return json.loads(response)
    except:
        print(f"Error parsing response: {response}")
        return None

def create_workflow(selected_analysts: list[str], secured_agents: Dict[str, Any]) -> StateGraph:
    """Create a workflow with selected analysts using secured agents."""
    # Get analyst nodes using secured agents
    analyst_nodes = get_analyst_nodes(secured_agents)
    
    # Create workflow with selected analysts
    workflow = StateGraph(AgentState)
    
    # Add START node
    def start_node(state: AgentState):
        """Initialize the workflow."""
        return state
    
    workflow.add_node("START", start_node)
    
    # Add analyst nodes
    for analyst in selected_analysts:
        if analyst in analyst_nodes:
            workflow.add_node(analyst, analyst_nodes[analyst])
            # Connect START to first analyst
            if analyst == selected_analysts[0]:
                workflow.add_edge("START", analyst)
    
    # Add edges between analysts in sequence
    for i in range(len(selected_analysts) - 1):
        workflow.add_edge(selected_analysts[i], selected_analysts[i + 1])
    
    # Add edge from last analyst to END
    if selected_analysts:
        workflow.add_edge(selected_analysts[-1], END)
    
    # Set entry point
    workflow.set_entry_point("START")
    
    return workflow

##### Run the Hedge Fund #####
async def run_hedge_fund(
    tickers: list[str],
    start_date: str,
    end_date: str,
    portfolio: dict,
    show_reasoning: bool = False,
    selected_analysts: list[str] = [],
    model_name: str = "gpt-4",
    model_provider: str = "OpenAI",
):
    """Run the hedge fund with secured agents."""
    try:
        # Initialize AZTP client
        api_key = os.getenv("AZTP_API_KEY")
        if not api_key:
            raise ValueError("AZTP_API_KEY is required")
        
        client = Aztp(api_key=api_key)
        
        # Wrap existing agents with secure connections
        secured_agents = await secure_wrap_agents(client)
        
        # Start progress tracking
        progress.start()
        
        try:
            # Create a new workflow if analysts are customized
            if selected_analysts:
                workflow = create_workflow(selected_analysts, secured_agents)
                agent = workflow.compile()
            else:
                # Use all analysts in default order
                workflow = create_workflow(ANALYST_ORDER, secured_agents)
                agent = workflow.compile()
            
            final_state = agent.invoke(
                {
                    "messages": [
                        HumanMessage(
                            content="Make trading decisions based on the provided data.",
                        )
                    ],
                    "data": {
                        "tickers": tickers,
                        "portfolio": portfolio,
                        "start_date": start_date,
                        "end_date": end_date,
                        "analyst_signals": {},
                    },
                    "metadata": {
                        "show_reasoning": show_reasoning,
                        "model_name": model_name,
                        "model_provider": model_provider,
                    },
                },
            )
            
            return {
                "decisions": parse_hedge_fund_response(final_state["messages"][-1].content),
                "analyst_signals": final_state["data"]["analyst_signals"],
            }
        finally:
            # Stop progress tracking
            progress.stop()
    except Exception as e:
        print(f"Error running hedge fund: {e}")
        if hasattr(client, 'config'):
            print("\nCurrent configuration:")
            print(f"Base URL: {client.config.base_url}")
            print(f"Environment: {client.config.environment}")
        return None

def main():
    parser = argparse.ArgumentParser(description="AI Hedge Fund")
    parser.add_argument(
        "--tickers",
        type=str,
        help="Comma-separated list of stock tickers (e.g., AAPL,MSFT,NVDA)",
        required=True,
    )
    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date (YYYY-MM-DD). Defaults to 3 months before end date",
        required=False,
    )
    parser.add_argument(
        "--end-date",
        type=str,
        help="End date (YYYY-MM-DD). Defaults to today",
        required=False,
    )
    parser.add_argument(
        "--portfolio",
        type=str,
        help="Portfolio allocation (JSON)",
        default="{}",
    )
    parser.add_argument(
        "--show-reasoning",
        action="store_true",
        help="Show agent reasoning",
    )
    parser.add_argument(
        "--analysts",
        type=str,
        nargs="+",
        help="List of analysts to use",
        choices=ANALYST_ORDER,
        default=[],
    )
    
    args = parser.parse_args()
    
    # Parse tickers from comma-separated string
    tickers = [ticker.strip() for ticker in args.tickers.split(",")]
    
    # Set the start and end dates
    end_date = args.end_date or datetime.now().strftime("%Y-%m-%d")
    if not args.start_date:
        # Calculate 3 months before end_date
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        start_date = (end_date_obj - relativedelta(months=3)).strftime("%Y-%m-%d")
    else:
        start_date = args.start_date
    
    # Parse portfolio JSON
    try:
        portfolio = json.loads(args.portfolio)
    except json.JSONDecodeError:
        print("Error: Invalid portfolio JSON")
        sys.exit(1)
    
    # Get model choice
    model_choices = [
        "gpt-4 (OpenAI)",
        "gpt-3.5-turbo (OpenAI)",
        "claude-3-opus-20240229 (Anthropic)",
        "claude-3-sonnet-20240229 (Anthropic)",
        "mixtral-8x7b-32768 (Groq)",
    ]
    model_choice = questionary.select(
        "Select LLM model:",
        choices=model_choices,
        default=model_choices[0],
    ).ask()
    
    # Extract model name and provider
    model_name = model_choice.split(" (")[0]
    model_provider = model_choice.split("(")[1].rstrip(")")
    
    # Run the hedge fund
    result = asyncio.run(run_hedge_fund(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        portfolio=portfolio,
        show_reasoning=args.show_reasoning,
        selected_analysts=args.analysts,
        model_name=model_name,
        model_provider=model_provider,
    ))
    
    if result:
        print_trading_output(result)
    else:
        print("\nHedge fund execution failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
