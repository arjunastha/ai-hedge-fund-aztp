# AI Hedge Fund AZTP Implementation Plan

## Overview
This plan outlines the implementation of secure agent connections using AZTP (Astha Zero Trust Protocol) for the AI Hedge Fund project. Following the blog_py example pattern, we'll wrap existing agents with secure connections without modifying their internal implementation.

## Current Structure Analysis
The project currently has the following agents:
1. Investment Strategy Agents:
   - Warren Buffett Agent
   - Ben Graham Agent
   - Bill Ackman Agent
2. Analysis Agents:
   - Fundamentals Agent
   - Technical Analysis Agent
   - Sentiment Analysis Agent
   - Valuation Agent
3. Management Agents:
   - Portfolio Management Agent
   - Risk Management Agent

## Implementation Steps

### 1. Environment Setup
- Update `.env` file to include:
  ```
  AZTP_API_KEY=<your-api-key>
  ```

### 2. Agent Verification Function
Add to main.py:
```python
async def verify_agent(client: Aztp, agent: Any, agent_type: str):
    """Verify agent identity."""
    is_valid = await agent.verify()
    identity = await client.get_identity(agent)
    print(f"\n{agent_type} Identity:", identity)
    return is_valid
```

### 3. Main Workflow Updates
Update main.py to wrap existing agents with secure connections:

```python
from aztp_client import Aztp
import asyncio
import os
from typing import Dict, Any

async def secure_wrap_agents(client: Aztp) -> Dict[str, Any]:
    """Wrap existing agents with secure connections."""
    # Import existing agents (no modifications needed)
    from agents.warren_buffett import warren_buffett_agent
    from agents.ben_graham import ben_graham_agent
    from agents.bill_ackman import bill_ackman_agent
    from agents.fundamentals import fundamentals_agent
    from agents.technicals import technical_analyst_agent
    from agents.sentiment import sentiment_agent
    from agents.valuation import valuation_agent
    from agents.portfolio_manager import portfolio_management_agent
    from agents.risk_manager import risk_management_agent

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
    
    # Wrap each agent with secure_connect
    secured_agents = {}
    for name, agent in agents.items():
        secured_agents[name] = await client.secure_connect(
            agent,
            name=f"{name}analyst"
        )
    
    # Verify all agents
    verification_tasks = [
        verify_agent(client, agent, name.title())
        for name, agent in secured_agents.items()
    ]
    agents_valid = await asyncio.gather(*verification_tasks)
    
    if not all(agents_valid):
        raise ValueError("Agent verification failed")
        
    return secured_agents

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
    # Initialize AZTP client
    api_key = os.getenv("AZTP_API_KEY")
    if not api_key:
        raise ValueError("AZTP_API_KEY is required")
    
    client = Aztp(api_key=api_key)
    
    # Wrap existing agents with secure connections
    secured_agents = await secure_wrap_agents(client)
    
    # Use secured agents in the workflow
    # The rest of the implementation remains unchanged, just use secured_agents instead of original agents
```

### 4. Graph Workflow Updates
Update the graph workflow to use secured agents:

1. No changes needed to state.py or agent implementations
2. Only update the agent nodes in the workflow to use secured versions
3. All security is handled by the AZTP wrapper

Example:
```python
def get_analyst_nodes(secured_agents):
    """Get analyst nodes using secured agents."""
    return {
        "warren": secured_agents["warren_buffett"],
        "graham": secured_agents["ben_graham"],
        "ackman": secured_agents["bill_ackman"],
        # ... etc
    }
```

### 5. Security Considerations
1. Each agent gets a unique SPIFFE identity based on their role:
   - `warrenanalyst`
   - `grahamanalyst`
   - `ackmananalyst`
   - `fundamentalsanalyst`
   - `technicalanalyst`
   - `sentimentanalyst`
   - `valuationanalyst`
   - `portfoliomanager`
   - `riskmanager`

2. Security features:
   - All agent verification is handled by AZTP
   - Inter-agent communications are automatically secured
   - No modifications to original agent code required
   - Clean separation of security concerns

## Next Steps
1. Implement secure wrapping in main.py
2. Update graph workflow to use secured agents
3. Add logging for security operations
4. Test secured agent interactions
5. Document security features

## Testing Plan
1. Verify each wrapped agent's identity
2. Test secure communication between agents
3. Validate workflow with secured agents
4. Test error handling for verification failures
5. Performance testing with security overhead
6. Integration testing with AZTP infrastructure

## Key Benefits of This Approach
1. Non-invasive - original agent code remains unchanged
2. Clean separation of concerns - security handled by AZTP wrapper
3. Easy to maintain - security can be updated without touching agent logic
4. Consistent with blog_py example pattern 