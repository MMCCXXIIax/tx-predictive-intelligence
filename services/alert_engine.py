
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional

class TXAlertEngine:
    """
    The 'Overprotective Trading Dad' - Advanced alert system that won't let you miss anything
    """
    
    def __init__(self):

    def get_pattern_explanation(self, symbol, pattern):
        # Detailed explanation of the pattern
        explanations = {
            "Shooting Star": (
                f"A Shooting Star pattern indicates a potential reversal after an uptrend in {symbol}. "
                "Characterized by a small body and a long upper shadow, it suggests potential bearishness."
            ),
            # Other patterns could be added here
        }
        return explanations.get(pattern, "No detailed explanation available.")

        self.alert_history = []
        self.user_preferences = {}
        self.device_tokens = {}
        
    def create_alert(self, symbol: str, pattern: str, confidence: float, price: float, 
                    risk_level: str = "MEDIUM", suggested_amounts: List[float] = None):
        """
        Creates a TX alert with personality and multiple action options
        """
        if suggested_amounts is None:
            suggested_amounts = [100, 250, 500, 1000]
            
        # TX personality responses based on risk level
        personality_messages = {
            "HIGH": [
                f"🚨 WAKE UP! {symbol} is about to do something CRAZY!",
                f"GET THE F*** UP! {symbol} just printed a {pattern}!",
                f"This is NOT a drill - {symbol} is moving NOW!"
            ],
            "MEDIUM": [
                f"👀 {symbol} caught my attention with a {pattern}",
                f"Interesting... {symbol} is showing some behavior",
                f"Hey bestie, {symbol} might be worth a look"
            ],
            "LOW": [
                f"📊 FYI: {symbol} has a weak {pattern} signal",
                f"Not urgent, but {symbol} is showing some patterns",
                f"Casual observation: {symbol} detected {pattern}"
            ]
        }
        
        detailed_explanation = self.get_pattern_explanation(symbol, pattern)
        
        alert = {
            "id": f"tx_{int(time.time())}_{symbol}",
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "pattern": pattern,
            "confidence": confidence,
            "explanation": detailed_explanation,
            "price": price,
            "risk_level": risk_level,
            "message": personality_messages[risk_level][0],  # Use first message
            "suggested_amounts": suggested_amounts,
            "actions": ["IGNORE", "SIMULATE", "EXECUTE", "SNOOZE"],
            "status": "PENDING",
            "expires_at": datetime.now().timestamp() + 300  # 5 minutes
        }
        
        self.alert_history.append(alert)
        return alert
    
    def send_multi_device_alert(self, alert: Dict):
        """
        Sends alerts to all connected devices
        """
        # This would integrate with push notification services
        # For now, we'll simulate with console output
        print(f"""
🔔 MULTI-DEVICE ALERT 🔔
{alert['message']}
Pattern: {alert['pattern']} ({alert['confidence']:.0%})
Price: ${alert['price']:,.2f}
Suggested amounts: {', '.join(f'${amt}' for amt in alert['suggested_amounts'])}
Actions: {' | '.join(alert['actions'])}
""")
        
    def process_user_response(self, alert_id: str, action: str, amount: Optional[float] = None):
        """
        Processes user response to alerts
        """
        for alert in self.alert_history:
            if alert['id'] == alert_id:
                alert['status'] = action.upper()
                alert['response_time'] = datetime.now().isoformat()
                if amount:
                    alert['chosen_amount'] = amount
                break
                
        return {"status": "processed", "action": action}
    
    def get_active_alerts(self):
        """
        Returns currently active alerts
        """
        current_time = time.time()
        return [alert for alert in self.alert_history 
                if alert['status'] == 'PENDING' and alert['expires_at'] > current_time]
