# app/utils/metrics.py

from google.cloud import monitoring_v3
from typing import Dict, Any
import time

class MetricsClient:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{project_id}"
        
    def create_time_series(self, series: Dict[str, Any]):
        """CREATE A NEW TIME SERIES"""
        try:
            self.client.create_time_series(
                request={
                    "name": self.project_name,
                    "time_series": [series]
                }
            )
        except Exception as e:
            print(f"error creating time series: {str(e)}")

class ProcessingMetrics:
    def __init__(self, project_id: str):
        self.metrics_client = MetricsClient(project_id)
        self.start_time = None
        
    def start_processing(self):
        """START TIMING DOCUMENT PROCESSING"""
        self.start_time = time.time()
        
    def end_processing(self, document_id: str, success: bool):
        """RECORD PROCESSING COMPLETION METRICS"""
        if not self.start_time:
            return
            
        duration = time.time() - self.start_time
        self._record_metrics(document_id, duration, success)
        
    def _record_metrics(self, document_id: str, duration: float, success: bool):
        """RECORD PROCESSING METRICS"""
        metrics = {
            "processing_duration": duration,
            "processing_success": 1 if success else 0,
            "document_id": document_id
        }
        self.metrics_client.create_time_series(metrics)