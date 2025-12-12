import json
import re

def nl_to_structured_json(nl_input: str) -> dict:
    """
    Converts simple NL rules into a structured intermediate representation.
    This implementation uses regex and string replacement for simplification.
    """
    nl_input = nl_input.lower().replace('$', '') 

    entry_match = re.search(r'(?:buy|enter|trigger entry|when)\s+(.+)', nl_input)
    exit_split = re.split(r'exit when', nl_input)
    
    structured = {"entry": [], "exit": []}

    #Entry Rule
    entry_rule_str = ""
    if entry_match:
        if len(exit_split) > 1:
            entry_rule_str = entry_match.group(1).strip().split('exit when')[0].strip()
        else:
            entry_rule_str = entry_match.group(1).strip()
            
        
        #  Translate Indicators and constants
        
        entry_rule_str = re.sub(r'(\d+)-day moving average', r'SMA(close, \1)', entry_rule_str)
        
        entry_rule_str = entry_rule_str.replace('5 million', '5000000')
        entry_rule_str = entry_rule_str.replace('1 million', '1000000')
        
        entry_rule_str = entry_rule_str.replace('close price is above', 'close >')
        entry_rule_str = entry_rule_str.replace('price is above', 'close >') 
        entry_rule_str = entry_rule_str.replace('volume is above', 'volume >')
        
        entry_rule_str = entry_rule_str.replace('high price is below', 'high <')
        entry_rule_str = entry_rule_str.replace('is greater than', '>')
        entry_rule_str = entry_rule_str.replace('greater than', '>')
        
        entry_rule_str = entry_rule_str.replace('price crosses above yesterday\'s high', 'close CROSSES_ABOVE high[-1]')
        
        entry_rule_str = entry_rule_str.replace('and', ' AND ').replace('or', ' OR ')
        
        # Remove noise words that break the parser
        noise_words = ['when the', 'the', 'is', 'a', '.', 'price'] 
        for word in noise_words:
            entry_rule_str = entry_rule_str.replace(word, ' ')

        entry_rule_str = re.sub(r'\s+', ' ', entry_rule_str).strip()
        
        if entry_rule_str:
            structured["entry"] = [entry_rule_str]

    # 3. Process Exit Rule )
    if len(exit_split) > 1:
        exit_rule_str = exit_split[-1].strip()
                
        # Translate Indicators and Comparisons
        rsi_match = re.search(r'rsi\((\d+)\) is below (\d+)', exit_rule_str)
        if rsi_match:
            structured["exit"] = [f'RSI(close, {rsi_match.group(1)}) < {rsi_match.group(2)}']
        
        elif 'rsi' in exit_rule_str and 'below' in exit_rule_str:
             pass 


    # 4. Construct the Final DSL Text
    final_entry_rule = " ".join(structured["entry"]).strip()
    final_exit_rule = " ".join(structured["exit"]).strip()
    
    dsl_text = ""
    if final_entry_rule:
        dsl_text += "ENTRY: " + final_entry_rule
        
    # Harmless placeholder
    if not final_exit_rule:
        final_exit_rule = "0 > 1" 
        
    if dsl_text:
        dsl_text += "\n"
    dsl_text += "EXIT: " + final_exit_rule

    return {"dsl": dsl_text.strip()}    
        
    
nl_test_input = "Buy when the close price is above the 20-day moving average and volume is above 1 million. Exit when RSI(14) is below 20."
dsl_output = nl_to_structured_json(nl_test_input)['dsl']

