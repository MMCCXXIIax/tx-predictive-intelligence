
class TXStrategyBuilder:
    """
    No-code strategy builder - "Like Tinder but for trading strategies"
    """
    
    def __init__(self):
        self.strategies = {}
        self.active_strategies = []
        
    def create_strategy(self, name: str, conditions: Dict, actions: Dict):
        """
        Creates a new trading strategy
        Example: "If RSI < 30 AND Bullish Engulfing appears, alert me"
        """
        strategy = {
            "id": f"strategy_{int(time.time())}",
            "name": name,
            "conditions": conditions,
            "actions": actions,
            "created_at": datetime.now().isoformat(),
            "active": True,
            "success_rate": 0.0,
            "total_signals": 0
        }
        
        self.strategies[strategy["id"]] = strategy
        return strategy
    
    def evaluate_strategy(self, strategy_id: str, market_data: Dict):
        """
        Evaluates if strategy conditions are met
        """
        if strategy_id not in self.strategies:
            return False
            
        strategy = self.strategies[strategy_id]
        conditions = strategy["conditions"]
        
        # Example condition checking
        conditions_met = True
        
        # Check pattern conditions
        if "pattern" in conditions:
            required_pattern = conditions["pattern"]
            detected_patterns = market_data.get("patterns", [])
            pattern_found = any(p["name"] == required_pattern for p in detected_patterns)
            conditions_met &= pattern_found
            
        # Check RSI conditions
        if "rsi" in conditions:
            rsi_condition = conditions["rsi"]
            current_rsi = market_data.get("rsi", 50)
            if rsi_condition["operator"] == "<":
                conditions_met &= current_rsi < rsi_condition["value"]
            elif rsi_condition["operator"] == ">":
                conditions_met &= current_rsi > rsi_condition["value"]
                
        return conditions_met
    
    def get_strategy_templates(self):
        """
        Pre-built strategy templates for users
        """
        return [
            {
                "name": "Oversold Reversal Hunter",
                "description": "Catches bullish reversals in oversold conditions",
                "conditions": {
                    "rsi": {"operator": "<", "value": 30},
                    "pattern": "Bullish Engulfing"
                },
                "actions": {"alert": True, "simulate": True}
            },
            {
                "name": "Bearish Breakdown Detector", 
                "description": "Spots bearish patterns at resistance",
                "conditions": {
                    "pattern": "Evening Star",
                    "volume": {"operator": ">", "value": "average"}
                },
                "actions": {"alert": True, "risk_warning": True}
            }
        ]
