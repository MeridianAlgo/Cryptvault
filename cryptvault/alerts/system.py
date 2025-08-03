"""Advanced alert system for price movements, patterns, and portfolio changes."""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import threading
import time

from ..data.models import PricePoint
from ..patterns.types import DetectedPattern


@dataclass
class AlertCondition:
    """Alert condition definition."""
    id: str
    name: str
    symbol: str
    condition_type: str  # 'price', 'pattern', 'volume', 'technical'
    threshold: float
    comparison: str  # 'above', 'below', 'crosses_above', 'crosses_below'
    active: bool = True
    created_at: datetime = None
    triggered_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Alert:
    """Alert notification."""
    id: str
    condition_id: str
    symbol: str
    message: str
    severity: str  # 'info', 'warning', 'critical'
    triggered_at: datetime
    data: Dict[str, Any]


class AlertSystem:
    """Advanced cryptocurrency alert system."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conditions: Dict[str, AlertCondition] = {}
        self.alerts: List[Alert] = []
        self.callbacks: List[Callable[[Alert], None]] = []
        self.price_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.running = False
        self.monitor_thread = None
        
        # Email configuration (optional)
        self.email_config = {
            'smtp_server': None,
            'smtp_port': 587,
            'username': None,
            'password': None,
            'from_email': None
        }
    
    def add_price_alert(self, symbol: str, threshold: float, 
                       comparison: str = 'above', name: str = None) -> str:
        """Add price-based alert."""
        alert_id = f"price_{symbol}_{threshold}_{comparison}_{int(time.time())}"
        
        condition = AlertCondition(
            id=alert_id,
            name=name or f"{symbol} price {comparison} ${threshold:,.2f}",
            symbol=symbol.upper(),
            condition_type='price',
            threshold=threshold,
            comparison=comparison
        )
        
        self.conditions[alert_id] = condition
        self.logger.info(f"Added price alert: {condition.name}")
        return alert_id
    
    def add_pattern_alert(self, symbol: str, pattern_type: str, 
                         min_confidence: float = 0.8, name: str = None) -> str:
        """Add pattern-based alert."""
        alert_id = f"pattern_{symbol}_{pattern_type}_{int(time.time())}"
        
        condition = AlertCondition(
            id=alert_id,
            name=name or f"{symbol} {pattern_type} pattern detected",
            symbol=symbol.upper(),
            condition_type='pattern',
            threshold=min_confidence,
            comparison='above'
        )
        
        self.conditions[alert_id] = condition
        self.logger.info(f"Added pattern alert: {condition.name}")
        return alert_id
    
    def add_volume_alert(self, symbol: str, volume_multiplier: float = 2.0,
                        name: str = None) -> str:
        """Add volume spike alert."""
        alert_id = f"volume_{symbol}_{volume_multiplier}_{int(time.time())}"
        
        condition = AlertCondition(
            id=alert_id,
            name=name or f"{symbol} volume spike ({volume_multiplier}x average)",
            symbol=symbol.upper(),
            condition_type='volume',
            threshold=volume_multiplier,
            comparison='above'
        )
        
        self.conditions[alert_id] = condition
        self.logger.info(f"Added volume alert: {condition.name}")
        return alert_id
    
    def add_technical_alert(self, symbol: str, indicator: str, 
                           threshold: float, comparison: str = 'above',
                           name: str = None) -> str:
        """Add technical indicator alert."""
        alert_id = f"technical_{symbol}_{indicator}_{int(time.time())}"
        
        condition = AlertCondition(
            id=alert_id,
            name=name or f"{symbol} {indicator} {comparison} {threshold}",
            symbol=symbol.upper(),
            condition_type='technical',
            threshold=threshold,
            comparison=comparison
        )
        
        self.conditions[alert_id] = condition
        self.logger.info(f"Added technical alert: {condition.name}")
        return alert_id
    
    def remove_alert(self, alert_id: str) -> bool:
        """Remove alert condition."""
        if alert_id in self.conditions:
            del self.conditions[alert_id]
            self.logger.info(f"Removed alert: {alert_id}")
            return True
        return False
    
    def add_callback(self, callback: Callable[[Alert], None]):
        """Add alert callback function."""
        self.callbacks.append(callback)
    
    def configure_email(self, smtp_server: str, smtp_port: int, 
                       username: str, password: str, from_email: str):
        """Configure email notifications."""
        self.email_config.update({
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'username': username,
            'password': password,
            'from_email': from_email
        })
        self.logger.info("Email notifications configured")
    
    def start_monitoring(self):
        """Start alert monitoring."""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        self.logger.info("Alert monitoring started")
    
    def stop_monitoring(self):
        """Stop alert monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Alert monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        from ..data.package_fetcher import PackageDataFetcher
        from ..analyzer import PatternAnalyzer
        
        fetcher = PackageDataFetcher()
        analyzer = PatternAnalyzer()
        
        while self.running:
            try:
                # Get unique symbols to monitor
                symbols = set(condition.symbol for condition in self.conditions.values() 
                            if condition.active)
                
                for symbol in symbols:
                    self._check_symbol_alerts(symbol, fetcher, analyzer)
                
                # Sleep between checks
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Alert monitoring error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _check_symbol_alerts(self, symbol: str, fetcher, analyzer):
        """Check alerts for a specific symbol."""
        try:
            # Get current price
            current_price = fetcher.get_current_price(symbol)
            if not current_price:
                return
            
            # Update price history
            now = datetime.now()
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            
            self.price_history[symbol].append((now, current_price))
            
            # Keep only last 24 hours of price history
            cutoff = now - timedelta(hours=24)
            self.price_history[symbol] = [
                (ts, price) for ts, price in self.price_history[symbol] 
                if ts > cutoff
            ]
            
            # Check price alerts
            for condition in self.conditions.values():
                if (condition.symbol == symbol and condition.active and 
                    condition.condition_type == 'price'):
                    self._check_price_condition(condition, current_price)
            
            # Check pattern alerts (less frequently)
            if len(self.price_history[symbol]) > 50:  # Need enough data
                try:
                    data = fetcher.fetch_historical_data(symbol, 7, '1h')
                    if data:
                        analysis = analyzer.analyze_dataframe(data)
                        if analysis.get('success') and analysis.get('patterns'):
                            for condition in self.conditions.values():
                                if (condition.symbol == symbol and condition.active and 
                                    condition.condition_type == 'pattern'):
                                    self._check_pattern_condition(condition, analysis['patterns'])
                except Exception as e:
                    self.logger.warning(f"Pattern check failed for {symbol}: {e}")
        
        except Exception as e:
            self.logger.error(f"Symbol alert check failed for {symbol}: {e}")
    
    def _check_price_condition(self, condition: AlertCondition, current_price: float):
        """Check price-based condition."""
        triggered = False
        
        if condition.comparison == 'above' and current_price > condition.threshold:
            triggered = True
        elif condition.comparison == 'below' and current_price < condition.threshold:
            triggered = True
        elif condition.comparison in ['crosses_above', 'crosses_below']:
            # Need price history for crossover detection
            if len(self.price_history[condition.symbol]) >= 2:
                prev_price = self.price_history[condition.symbol][-2][1]
                
                if (condition.comparison == 'crosses_above' and 
                    prev_price <= condition.threshold < current_price):
                    triggered = True
                elif (condition.comparison == 'crosses_below' and 
                      prev_price >= condition.threshold > current_price):
                    triggered = True
        
        if triggered:
            self._trigger_alert(condition, {
                'current_price': current_price,
                'threshold': condition.threshold,
                'comparison': condition.comparison
            })
    
    def _check_pattern_condition(self, condition: AlertCondition, patterns: List[Dict]):
        """Check pattern-based condition."""
        for pattern in patterns:
            if pattern.get('confidence_raw', 0) >= condition.threshold:
                self._trigger_alert(condition, {
                    'pattern_type': pattern.get('type'),
                    'confidence': pattern.get('confidence'),
                    'pattern_data': pattern
                })
                break
    
    def _trigger_alert(self, condition: AlertCondition, data: Dict[str, Any]):
        """Trigger an alert."""
        # Avoid duplicate alerts (cooldown period)
        if (condition.triggered_at and 
            datetime.now() - condition.triggered_at < timedelta(minutes=15)):
            return
        
        alert_id = f"alert_{condition.id}_{int(time.time())}"
        
        # Create alert message
        if condition.condition_type == 'price':
            message = (f"{condition.symbol} price ${data['current_price']:,.2f} "
                      f"{condition.comparison} ${condition.threshold:,.2f}")
            severity = 'warning' if abs(data['current_price'] - condition.threshold) / condition.threshold < 0.05 else 'critical'
        
        elif condition.condition_type == 'pattern':
            message = (f"{condition.symbol} pattern detected: {data['pattern_type']} "
                      f"({data['confidence']})")
            severity = 'info'
        
        else:
            message = f"{condition.symbol} alert: {condition.name}"
            severity = 'info'
        
        alert = Alert(
            id=alert_id,
            condition_id=condition.id,
            symbol=condition.symbol,
            message=message,
            severity=severity,
            triggered_at=datetime.now(),
            data=data
        )
        
        # Update condition
        condition.triggered_at = datetime.now()
        
        # Store alert
        self.alerts.append(alert)
        
        # Keep only last 1000 alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
        
        # Notify callbacks
        for callback in self.callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback error: {e}")
        
        # Send email if configured
        self._send_email_alert(alert)
        
        self.logger.info(f"Alert triggered: {message}")
    
    def _send_email_alert(self, alert: Alert):
        """Send email notification."""
        if not all(self.email_config.values()):
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = self.email_config['from_email']  # Send to self for now
            msg['Subject'] = f"CryptVault Alert: {alert.symbol} - {alert.severity.upper()}"
            
            body = f"""
CryptVault Alert Notification

Symbol: {alert.symbol}
Message: {alert.message}
Severity: {alert.severity.upper()}
Time: {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}

Alert Data:
{json.dumps(alert.data, indent=2)}

---
CryptVault Alert System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email alert sent for {alert.symbol}")
        
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    def get_active_alerts(self, hours: int = 24) -> List[Alert]:
        """Get recent alerts."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert.triggered_at > cutoff]
    
    def get_alert_conditions(self) -> List[AlertCondition]:
        """Get all alert conditions."""
        return list(self.conditions.values())
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert system statistics."""
        active_conditions = sum(1 for c in self.conditions.values() if c.active)
        recent_alerts = len(self.get_active_alerts(24))
        
        return {
            'total_conditions': len(self.conditions),
            'active_conditions': active_conditions,
            'recent_alerts_24h': recent_alerts,
            'monitoring_active': self.running,
            'symbols_monitored': len(set(c.symbol for c in self.conditions.values() if c.active))
        }