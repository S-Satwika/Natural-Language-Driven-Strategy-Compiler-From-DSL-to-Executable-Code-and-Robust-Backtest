# Natural Language-Driven Strategy Compiler: From DSL to Executable Code and Robust Backtest
This project is a modular, end-to-end strategy compiler that translates a Natural Language (NL) rule through a DSL (Domain-Specific Language) into executable Python code. The core function is to run a robust backtest that accurately calculates Total Return and the critical Max Drawdown (MDD) by tracking daily unrealized equity.

It fully automates the process of translating a high-level trading rule, given in plain English, into a simulated backtest result. The solution ensures technical rigor, particularly in the accurate calculation of risk metrics.

## ✨ Key Technical Achievements
Robust Max Drawdown (MDD) Tracking: The backtester.py implements a fix for a common backtesting flaw. It tracks the portfolio's unrealized equity daily to guarantee the reported Max Drawdown is the highest risk exposure experienced by the strategy, not just the loss between realized trades.

End-to-End Automation: Seamless conversion from a natural language rule string to a structured AST and finally to vectorized Python code.

Modular Architecture: The system is split into distinct, specialized modules for clean separation of concerns (Parsing, Code Generation, Execution).

## 📊 System Architecture and Component Flow
The system processes the input through five distinct files, demonstrating the complete data journey:

| File | Pipeline Stage | Role in the System |
| :--- | :--- | :--- |
| **`main.py`** | Orchestrator | Manages the sequence of execution. |
| **`backtester.py`** | Execution Engine | Runs the simulation, calculates compounded returns, and tracks **Max Drawdown (MDD)**. |
| **`nl_parser.py`** | NL → DSL | Translates ambiguous natural language into the formal DSL syntax.|
|**`strategy_parser.py`**|DSL → AST|Formal syntax analysis (using Lark grammar) to construct the structured Abstract Syntax Tree.|
|**`codegenerator.py`**|AST → Python Code|"Recursively translates the AST into a vectorized, executable Pandas function (evaluate_signals)."|
|**`test_data.csv`** | Data Source | Contains synthetic price and volume data for simulation and MDD validation.|



## 📚 **Domain-Specific Language (DSL) Grammar Specification**

The DSL is a boolean expression language designed for clarity and parsability. It is built from indicators, series, literals, and comparison operators.

**1. Syntax Components**
* **Actions:** `ENTRY:` and `EXIT:`
* **Indicators:** `SMA(series, period)`, `RSI(series, period)`
* **Series:** `close`, `high`, `low`, `volume`
* **Operators:** `>`, `<`, `==`, `AND`, `OR`

**2. Grammar Examples**
| Goal | DSL Representation |
| :--- | :--- |
| **Simple Trend** | `ENTRY: close > SMA(close, 50)` 
| **Volume Spike** | `ENTRY: volume > 1000000` |
| **Overbought Exit**| `EXIT: RSI(close, 14) > 80` |
| **Combined Rule** | `ENTRY: close > SMA(close, 20) AND volume > 500000` |



## 🚀 Setup and Execution
Prerequisites
You need Python 3.8+ and the following libraries:

**`pip install pandas numpy`**

How to Run the Demo

The pipeline is configured in main.py to demonstrate the end-to-end process using a specific rule designed to test the MDD calculation:

NL Rule: "Buy when the close price is above the 20-day moving average and volume is above 1 million. Exit when RSI(14) is below 20."
Execute the script from your terminal:

**`python main.py`**

Expected Output

The final report should confirm the successful pipeline execution and the accuracy of the MDD calculation against the test data:

Total Return: 8.3%

Max Drawdown: 8.0%  <-- Crucial confirmation of the robust MDD implementation

Trades: 1




