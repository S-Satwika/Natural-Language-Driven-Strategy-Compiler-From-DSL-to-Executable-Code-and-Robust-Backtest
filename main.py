import pandas as pd
import json
import re

from nl_parser import nl_to_structured_json
from strategy_parser import parse_dsl_to_ast
from code_generator import CodeGenerator
from backtester import Backtester


def load_data(file_path: str) -> pd.DataFrame:

    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    return df

def run_pipeline(nl_input: str, data_path: str = 'data.csv'):
    """
    Executes the full NL -> DSL -> AST -> Code -> Backtest pipeline.
    """
    print(f"## 1. Natural Language Input\n")
    print(f"NL: \"{nl_input}\"\n")
    
    # 1. NL -> DSL 
    structured_output = nl_to_structured_json(nl_input)
    dsl_text = structured_output.get("dsl", "")
    
    print("-" * 50)
    print(f"## 2. Generated DSL\n")
    print(dsl_text)
    
    # 2. Parse DSL into AST 
    try:
        ast = parse_dsl_to_ast(dsl_text)
    except ValueError as e:
        print(f"\n--- ERROR ---\n{e}")
        return
        
    print("-" * 50)
    print(f"## 3. Parsed AST\n")
    print(json.dumps(ast, indent=2))
    
    # 3. AST -> Python Code and Pre-Calculation 
    df = load_data(data_path)
    code_gen = CodeGenerator(df.copy()) #copy 
    
    df_with_indicators = code_gen.df
    
    python_code = code_gen.generate_strategy_function(ast)
    
    print("-" * 50)
    print(f"## 4. Generated Python Code\n")
    print(python_code)

    # code to get signals
    exec_scope = {'pd': pd, 'df': df_with_indicators}
    exec(python_code, exec_scope)
    signals = exec_scope['evaluate_signals'](df_with_indicators)
    
    # 4. Run Backtest Simulator
    backtester = Backtester(df_with_indicators.reset_index(), signals.reset_index())
    backtester.run_simulation()
    report = backtester.generate_report()
    
    print("-" * 50)
    print(f"## 5. Backtest Result Report\n")
    print(f"Total Return: {report['Total Return']}")
    print(f"Max Drawdown: {report['Max Drawdown']}")
    print(f"Trades: {report['Trades']}")
    print("\nEntry/Exit Log:")
    for log_entry in report['Entry/Exit Log']:
        print(f"- {log_entry}")

# Run the Demo 
if __name__ == "__main__":
    nl_rule = "Buy when the close price is above the 20-day moving average and volume is above 1 million. Exit when RSI(14) is below 20."
    run_pipeline(nl_rule, data_path='mdd_dataset.csv')