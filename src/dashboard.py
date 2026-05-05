"""Dashboard for monitoring automation metrics and status."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class Dashboard:
    """Dashboard for monitoring automation metrics."""
    
    def __init__(self):
        """Initialize dashboard."""
        self.metrics = defaultdict(int)
        self.events = []
        self.lead_status_counts = defaultdict(int)
        self.campaign_stats = {}
    
    def record_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Record an event.
        
        Args:
            event_type: Type of event
            details: Event details
        """
        event = {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'details': details,
        }
        self.events.append(event)
        
        # Keep only last 1000 events
        if len(self.events) > 1000:
            self.events = self.events[-1000:]
        
        logger.debug(f"Recorded event: {event_type}")
    
    def increment_metric(self, metric_name: str, value: int = 1) -> None:
        """Increment a metric.
        
        Args:
            metric_name: Name of metric
            value: Value to increment by
        """
        self.metrics[metric_name] += value
        logger.debug(f"Incremented metric {metric_name} by {value}")
    
    def update_lead_status(self, status: str) -> None:
        """Update lead status count.
        
        Args:
            status: Lead status
        """
        self.lead_status_counts[status] += 1
    
    def update_campaign_stats(self, campaign_id: str, stats: Dict[str, Any]) -> None:
        """Update campaign statistics.
        
        Args:
            campaign_id: Campaign ID
            stats: Campaign statistics
        """
        self.campaign_stats[campaign_id] = stats
    
    def get_summary(self) -> Dict[str, Any]:
        """Get dashboard summary.
        
        Returns:
            Summary of dashboard metrics
        """
        return {
            'metrics': dict(self.metrics),
            'lead_status_counts': dict(self.lead_status_counts),
            'campaign_stats': self.campaign_stats,
            'total_events': len(self.events),
            'last_updated': datetime.now().isoformat(),
        }
    
    def get_lead_status_breakdown(self) -> Dict[str, Any]:
        """Get lead status breakdown.
        
        Returns:
            Lead status breakdown with percentages
        """
        total_leads = sum(self.lead_status_counts.values())
        
        breakdown = {}
        for status, count in self.lead_status_counts.items():
            percentage = (count / total_leads * 100) if total_leads > 0 else 0
            breakdown[status] = {
                'count': count,
                'percentage': round(percentage, 2),
            }
        
        return {
            'total_leads': total_leads,
            'breakdown': breakdown,
        }
    
    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent events.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        return self.events[-limit:]
    
    def get_events_by_type(self, event_type: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get events by type.
        
        Args:
            event_type: Type of events to get
            limit: Maximum number of events to return
            
        Returns:
            List of events of specified type
        """
        filtered_events = [e for e in self.events if e['type'] == event_type]
        return filtered_events[-limit:]
    
    def get_metrics_over_time(self, metric_name: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics over time.
        
        Args:
            metric_name: Name of metric
            hours: Number of hours to look back
            
        Returns:
            List of metric values over time
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        metric_events = []
        for event in self.events:
            if event['type'] == 'metric_update' and event['details'].get('metric') == metric_name:
                event_time = datetime.fromisoformat(event['timestamp'])
                if event_time >= cutoff_time:
                    metric_events.append({
                        'timestamp': event['timestamp'],
                        'value': event['details'].get('value', 0),
                    })
        
        return metric_events
    
    def get_campaign_performance(self) -> Dict[str, Any]:
        """Get campaign performance metrics.
        
        Returns:
            Campaign performance summary
        """
        performance = {}
        
        for campaign_id, stats in self.campaign_stats.items():
            performance[campaign_id] = {
                'total_leads': stats.get('total_leads', 0),
                'active_leads': stats.get('active_leads', 0),
                'connected_leads': stats.get('connected_leads', 0),
                'replied_leads': stats.get('replied_leads', 0),
                'interested_leads': stats.get('interested_leads', 0),
                'response_rate': stats.get('response_rate', 0.0),
            }
        
        return performance
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary.
        
        Returns:
            Error summary with counts and details
        """
        error_events = [e for e in self.events if e['type'] == 'error']
        
        error_counts = defaultdict(int)
        error_details = []
        
        for event in error_events:
            error_type = event['details'].get('error_type', 'unknown')
            error_counts[error_type] += 1
            error_details.append(event)
        
        return {
            'total_errors': len(error_events),
            'error_counts': dict(error_counts),
            'recent_errors': error_details[-10:],
        }
    
    def get_activity_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get activity summary.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Activity summary
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_events = [
            e for e in self.events 
            if datetime.fromisoformat(e['timestamp']) >= cutoff_time
        ]
        
        activity_counts = defaultdict(int)
        for event in recent_events:
            activity_counts[event['type']] += 1
        
        return {
            'total_events': len(recent_events),
            'activity_counts': dict(activity_counts),
            'time_period_hours': hours,
        }
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.metrics = defaultdict(int)
        self.lead_status_counts = defaultdict(int)
        self.events = []
        self.campaign_stats = {}
        logger.info("Reset all dashboard metrics")
    
    def export_report(self) -> str:
        """Export dashboard report as JSON string.
        
        Returns:
            JSON string of dashboard report
        """
        import json
        
        report = {
            'summary': self.get_summary(),
            'lead_status_breakdown': self.get_lead_status_breakdown(),
            'campaign_performance': self.get_campaign_performance(),
            'error_summary': self.get_error_summary(),
            'activity_summary': self.get_activity_summary(),
            'recent_events': self.get_recent_events(100),
            'exported_at': datetime.now().isoformat(),
        }
        
        return json.dumps(report, indent=2)
