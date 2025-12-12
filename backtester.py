import pandas as pd
from typing import List, Dict, Any

class Backtester:
    
    def __init__(self, df: pd.DataFrame, signals: pd.DataFrame, initial_capital: float = 100.0):
        self.df = df
        self.signals = signals
        self.trades: List[Dict[str, Any]] = []
        self.in_position = False
        self.initial_capital = initial_capital
        self.equity_curve = [initial_capital]  
        self.max_drawdown = 0.0     
        self.running_peak = initial_capital 
        
    def run_simulation(self):
       
        current_trade = {}
        
        for i in range(len(self.df)):
            date = self.df.iloc[i]['date']
            close = self.df.iloc[i]['close']
            
            self.equity_curve.append(self.equity_curve[-1])

            entry_signal = self.signals.iloc[i]['entry'] if 'entry' in self.signals.columns and i < len(self.signals) else False
            exit_signal = self.signals.iloc[i]['exit'] if 'exit' in self.signals.columns and i < len(self.signals) else False

            
            if self.in_position and "entry_price" in current_trade:
                entry_price = current_trade["entry_price"]
                
                unrealized_return_pct = (close - entry_price) / entry_price
                
                last_realized_equity_base = self.equity_curve[current_trade.get("base_equity_index", -2)]
                
                current_unrealized_equity = last_realized_equity_base * (1 + unrealized_return_pct)
                
                self.running_peak = max(self.running_peak, current_unrealized_equity)
                
                current_drawdown_pct = (self.running_peak - current_unrealized_equity) / self.running_peak
                
                self.max_drawdown = max(self.max_drawdown, current_drawdown_pct)

            # EXIT LOGIC
            
            if self.in_position and exit_signal:
                
                pnl = close - current_trade["entry_price"]
                percent_return = (pnl / current_trade["entry_price"]) * 100
                
                current_trade.update({
                    "exit_date": date, "exit_price": close,
                    "pnl": pnl, "return_pct": percent_return
                })
                self.trades.append(current_trade)
                self.trades.append({"log": f"Exit: {date} at {close}"})
                
                last_realized_equity = self.equity_curve[current_trade.get("base_equity_index", -2)]
                new_equity = last_realized_equity * (1 + percent_return / 100)
                self.equity_curve[-1] = new_equity 
                
                self.running_peak = new_equity
                
                self.in_position = False
                current_trade = {} # Reset trade

           
            # ENTRY LOGIC
            
            elif not self.in_position and entry_signal:
                self.in_position = True
                entry_price = close 
                
                current_trade = {
                    "entry_date": date,
                    "entry_price": entry_price,
                    "base_equity_index": len(self.equity_curve) - 2 
                }
                self.trades.append({"log": f"Enter: {date} at {entry_price}"})

        if self.in_position and current_trade:
            i = len(self.df) - 1 
            last_date = self.df.iloc[i]['date']
            last_close = self.df.iloc[i]['close']
            
            pnl = last_close - current_trade["entry_price"]
            percent_return = (pnl / current_trade["entry_price"]) * 100
            
            current_trade.update({
                "exit_date": last_date, "exit_price": last_close,
                "pnl": pnl, "return_pct": percent_return
            })
            self.trades.append(current_trade)
            
            last_realized_equity = self.equity_curve[current_trade.get("base_equity_index", -2)]
            new_equity = last_realized_equity * (1 + percent_return / 100)
            self.equity_curve[-1] = new_equity
            
            self.in_position = False
            
            self.trades.append({"log": f"Trade closed at end of data: {last_date} at {last_close}"})


    def generate_report(self) -> Dict[str, Any]:
        """
        Calculates and formats the backtest results.
        """
        
        trade_log = [t for t in self.trades if "pnl" in t]
        trade_logs_text = [t.get("log") for t in self.trades if t.get("log")]
        
        final_equity = self.equity_curve[-1]
        total_return = (final_equity / self.initial_capital - 1) * 100
        
        max_dd = self.max_drawdown * 100  

        num_trades = len(trade_log)

        return {
            "Total Return": f"{total_return:.1f}%",
            "Max Drawdown": f"{max_dd:.1f}%",
            "Trades": num_trades,
            "Entry/Exit Log": trade_logs_text
        }