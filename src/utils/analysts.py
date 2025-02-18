"""Constants and utilities related to analysts configuration."""

from typing import Dict, Any

# Define analyst configuration - single source of truth
ANALYST_CONFIG = {
    "ben_graham": {
        "display_name": "Ben Graham",
        "key": "ben_graham",
        "order": 0,
    },
    "bill_ackman": {
        "display_name": "Bill Ackman",
        "key": "bill_ackman",
        "order": 1,
    },
    "warren_buffett": {
        "display_name": "Warren Buffett",
        "key": "warren_buffett",
        "order": 2,
    },
    "technical_analyst": {
        "display_name": "Technical Analyst",
        "key": "technicals",
        "order": 3,
    },
    "fundamentals_analyst": {
        "display_name": "Fundamentals Analyst",
        "key": "fundamentals",
        "order": 4,
    },
    "sentiment_analyst": {
        "display_name": "Sentiment Analyst",
        "key": "sentiment",
        "order": 5,
    },
    "valuation_analyst": {
        "display_name": "Valuation Analyst",
        "key": "valuation",
        "order": 6,
    },
}

# Derive ANALYST_ORDER from ANALYST_CONFIG for backwards compatibility
ANALYST_ORDER = sorted(
    ANALYST_CONFIG.keys(),
    key=lambda x: ANALYST_CONFIG[x]["order"]
)

def get_analyst_nodes(secured_agents: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get analyst nodes for the workflow.
    
    Args:
        secured_agents: Optional dictionary of secured agent instances.
                      If not provided, uses unsecured agents (for backward compatibility).
    
    Returns:
        Dictionary mapping analyst names to their agent instances.
    """
    if secured_agents is None:
        # Backward compatibility - import and use unsecured agents
        from agents.ben_graham import ben_graham_agent
        from agents.bill_ackman import bill_ackman_agent
        from agents.warren_buffett import warren_buffett_agent
        from agents.technicals import technical_analyst_agent
        from agents.fundamentals import fundamentals_agent
        from agents.sentiment import sentiment_agent
        from agents.valuation import valuation_agent
        
        return {
            "ben_graham": ben_graham_agent,
            "bill_ackman": bill_ackman_agent,
            "warren_buffett": warren_buffett_agent,
            "technical_analyst": technical_analyst_agent,
            "fundamentals_analyst": fundamentals_agent,
            "sentiment_analyst": sentiment_agent,
            "valuation_analyst": valuation_agent,
        }
    
    # Map secured agents to their workflow nodes
    return {
        "ben_graham": secured_agents["ben_graham"],
        "bill_ackman": secured_agents["bill_ackman"],
        "warren_buffett": secured_agents["warren_buffett"],
        "technical_analyst": secured_agents["technicals"],
        "fundamentals_analyst": secured_agents["fundamentals"],
        "sentiment_analyst": secured_agents["sentiment"],
        "valuation_analyst": secured_agents["valuation"],
    }
