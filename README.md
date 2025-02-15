# philo-agents


# 🎯 Getting Started

## 1. Clone the Repository

Start by cloning the repository and navigating to the project directory:
```
git clone https://github.com/neural-maze/philoagents.git
cd philoagents 
```

## 2. Installation


To install the dependencies and activate the virtual environment, run the following commands:

```bash
uv venv .venv
. ./.venv/bin/activate # or source ./.venv/bin/activate
uv pip install -e .
```

## 3. Environment Configuration

Before running any command, you have to set up your environment:
1. Create your environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and configure the required credentials following the inline comments and the recommendations from the [Cloud Services](#-prerequisites) section.