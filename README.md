# AI Hedge Fund with AZTP Security

This is a proof of concept for an AI-powered hedge fund with secure agent identity verification using AZTP (Agentic Zero Trust Protocol) from astha.ai. The goal of this project is to explore the use of AI to make trading decisions while ensuring secure and verified agent interactions. This project is for **educational** purposes only and is not intended for real trading or investment.

This system employs several secure agents working together:

1. Ben Graham Agent - The godfather of value investing, only buys hidden gems with a margin of safety
2. Bill Ackman Agent - An activist investors, takes bold positions and pushes for change
3. Warren Buffett Agent - The oracle of Omaha, seeks wonderful companies at a fair price
4. Valuation Agent - Calculates the intrinsic value of a stock and generates trading signals
5. Sentiment Agent - Analyzes market sentiment and generates trading signals
6. Fundamentals Agent - Analyzes fundamental data and generates trading signals
7. Technicals Agent - Analyzes technical indicators and generates trading signals
8. Risk Manager - Calculates risk metrics and sets position limits
9. Portfolio Manager - Makes final trading decisions and generates orders

Each agent is secured and verified using AZTP, ensuring:
- Unique AZTP identities for each agent based on the SPIFFE ID standard (www.spiffe.io)
- Secure inter-agent communication
- Identity verification before execution
- Zero-trust security model

<img width="1117" alt="Screenshot 2025-02-09 at 11 26 14 AM" src="https://github.com/user-attachments/assets/16509cc2-4b64-4c67-8de6-00d224893d58" />

**Note**: the system simulates trading decisions, it does not actually trade.

[![Twitter Follow](https://img.shields.io/twitter/follow/virattt?style=social)](https://twitter.com/virattt)

## Disclaimer

This project is for **educational and research purposes only**.

- Not intended for real trading or investment
- No warranties or guarantees provided
- Past performance does not indicate future results
- Creator assumes no liability for financial losses
- Consult a financial advisor for investment decisions

By using this software, you agree to use it solely for learning purposes.

## Prerequisites

- Python 3.8 or higher
- Poetry for dependency management
- OpenAI API key (or other supported LLM providers)
- AZTP API key (https://astha.ai)
- Local AZTP service running (or configured endpoint)
- Financial Datasets API key (optional, for extended stock data)

## Table of Contents
- [Setup](#setup)
- [Usage](#usage)
  - [Running the Hedge Fund](#running-the-hedge-fund)
  - [Running the Backtester](#running-the-backtester)
- [Project Structure](#project-structure)
- [AZTP Security Features](#aztp-security-features)
- [Contributing](#contributing)
- [Feature Requests](#feature-requests)
- [License](#license)

## Setup

Clone the repository:
```bash
git clone https://github.com/virattt/ai-hedge-fund.git
cd ai-hedge-fund
```

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Set up your environment variables:
```bash
# Create .env file for your API keys
cp .env.example .env
```

4. Set your API keys:
```bash
# AZTP API key for secure agent communication
AZTP_API_KEY=your-aztp-api-key

# For running LLMs hosted by openai (gpt-4, gpt-4-turbo, etc.)
OPENAI_API_KEY=your-openai-api-key

# For running LLMs hosted by groq (deepseek, llama3, etc.)
GROQ_API_KEY=your-groq-api-key

# For running LLMs hosted by Anthropic (claude-3, etc.)
ANTHROPIC_API_KEY=your-anthropic-api-key

# For getting financial data to power the hedge fund
FINANCIAL_DATASETS_API_KEY=your-financial-datasets-api-key
```

**Important**: You must set `OPENAI_API_KEY`, `GROQ_API_KEY`, or `ANTHROPIC_API_KEY` for the hedge fund to work.  If you want to use LLMs from all providers, you will need to set all API keys.

Financial data for AAPL, GOOGL, MSFT, NVDA, and TSLA is free and does not require an API key.

For any other ticker, you will need to set the `FINANCIAL_DATASETS_API_KEY` in the .env file.

## Usage

### Running the Hedge Fund
```bash
poetry run python src/main.py --ticker AAPL,MSFT,NVDA
```

The system will:
1. Initialize secure connections for all agents
2. Verify agent identities using AZTP
3. Create a secure workflow between agents
4. Execute the trading strategy with verified agents

**Example Output:**
<img width="992" alt="Screenshot 2025-01-06 at 5 50 17 PM" src="https://github.com/user-attachments/assets/e8ca04bf-9989-4a7d-a8b4-34e04666663b" />

Additional options:
```bash
# Show agent reasoning
poetry run python src/main.py --ticker AAPL,MSFT,NVDA --show-reasoning

# Specify date range
poetry run python src/main.py --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01 
```

### Running the Backtester

```bash
poetry run python src/backtester.py --ticker AAPL,MSFT,NVDA
```

**Example Output:**
<img width="941" alt="Screenshot 2025-01-06 at 5 47 52 PM" src="https://github.com/user-attachments/assets/00e794ea-8628-44e6-9a84-8f8a31ad3b47" />

Optional date range:
```bash
poetry run python src/backtester.py --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01
```

## Project Structure 
```
ai-hedge-fund-aztp/
├── src/
│   ├── agents/                   # Secure agent definitions
│   │   ├── bill_ackman.py        # Bill Ackman agent
│   │   ├── fundamentals.py       # Fundamental analysis agent
│   │   ├── portfolio_manager.py  # Portfolio management agent
│   │   ├── risk_manager.py       # Risk management agent
│   │   ├── sentiment.py          # Sentiment analysis agent
│   │   ├── technicals.py         # Technical analysis agent
│   │   ├── valuation.py          # Valuation analysis agent
│   │   ├── warren_buffett.py     # Warren Buffett agent
│   ├── tools/                    # Agent tools
│   │   ├── api.py                # API tools
│   ├── utils/                    # Utility functions
│   │   ├── analysts.py           # Analyst configuration
│   │   ├── display.py            # Display utilities
│   ├── backtester.py             # Backtesting tools
│   ├── main.py                   # Main entry point with AZTP integration
├── pyproject.toml                # Project dependencies
├── .env.example                  # Example environment variables
├── ...
```

## AZTP Security Features

This implementation uses AZTP to provide:

1. **Agent Identity**
   - Each agent has a unique SPIFFE ID
   - Identities are verified before execution
   - Format: `aztp://aztp.network/workload/production/node/{agent-name}-analyst`


2. **Agent Verification**
   - Agents are verified before joining the workflow
   - Identity status is checked and logged
   - Failed verifications prevent execution

3. **Clean Separation**
   - Security concerns are handled by AZTP
   - Agent logic remains unchanged
   - Easy to maintain and update

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

**Important**: Please keep your pull requests small and focused. This will make it easier to review and merge.

## Feature Requests

If you have a feature request, please open an [issue](https://github.com/virattt/ai-hedge-fund/issues) and make sure it is tagged with `enhancement`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
