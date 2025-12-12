from lark import Lark, Transformer, v_args
import re 
# DSL Grammar Definition 
# This is the language specification for Lark
dsl_grammar = r"""
    start: strategy

    strategy: entry_rule exit_rule
    
    entry_rule: "ENTRY:" expression
    exit_rule: "EXIT:" expression

    expression: atom
              | expression OP_AND expression -> and_operation
              | expression OP_OR expression -> or_operation
              | "(" expression ")"

    atom: comparison

    comparison: value_expr (OP_COMPARE | OP_CROSS) value_expr 
    
    value_expr: INDICATOR
              | SERIES
              | NUMBER
              
    // --- Terminals (Tokens) ---
    
    // Boolean Operators
    OP_AND: "AND"
    OP_OR: "OR"
    
    // Comparison Operators
    OP_COMPARE: ">=" | "<=" | "==" | "!=" | ">" | "<"
    OP_CROSS: "CROSSES_ABOVE" | "CROSSES_BELOW"
    
    // Data Series & Lookback (e.g., close, volume, high[-1])
    SERIES: /(close|open|high|low|volume)(\[-[0-9]+\])?/
    
    // Indicators (e.g., SMA(close, 20), RSI(close, 14))
    INDICATOR: /(SMA|RSI)\(([a-z]+)\s*,\s*([0-9]+)\)/ 
    
    %import common.NUMBER
    %import common.WS
    %ignore WS
"""

# AST Transformer 
@v_args(inline=True)
class StrategyTransformer(Transformer):
   
    def strategy(self, entry, exit_):
        # AST structure 
        return {"entry": entry, "exit": exit_}

    def entry_rule(self, *args):
        return args[-1] 
        
    def exit_rule(self, *args):
        return args[-1]

    def and_operation(self, left, op_token, right):
        return {"type": "binary_op", "op": "AND", "left": left, "right": right}
        
    def or_operation(self, left, op_token, right):
        return {"type": "binary_op", "op": "OR", "left": left, "right": right}
        
    def comparison(self, left, op, right):
        return {"type": "comparison", "op": str(op), "left": left, "right": right}
    
    def value_expr(self, val):
        return val

    def SERIES(self, token):
        name = str(token)
        lookback = 0
        if '[' in name:
            name, lookback_str = name.split('[')
            lookback = int(lookback_str.rstrip(']'))
        return {"type": "series", "name": name, "lookback": lookback}

    def INDICATOR(self, token):
        match = re.match(r'(?P<name>SMA|RSI)\((?P<series>[a-z]+)\s*,\s*(?P<period>[0-9]+)\)', str(token))
        return {
            "type": "indicator",
            "name": match.group("name"),
            "series": match.group("series"),
            "period": int(match.group("period"))
        }

    def NUMBER(self, token):
        return {"type": "literal", "value": float(str(token))}
    
    def atom(self, *args): return args[0]
    def expression(self, *args): return args[0]
    
#Main Parser Function 
def parse_dsl_to_ast(dsl_text: str) -> dict:
    parser = Lark(dsl_grammar, start='strategy', parser='lalr')
    try:
        tree = parser.parse(dsl_text)
        ast = StrategyTransformer().transform(tree)
        return ast
    except Exception as e:
        print(f"Error parsing DSL: {e}")
    
        raise ValueError(f"Invalid DSL Syntax: {e.__class__.__name__}: {e}")

