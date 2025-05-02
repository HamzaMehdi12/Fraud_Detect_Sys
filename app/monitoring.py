from prometheus_client import start_http_server, Counter, Gauge

PREDICTION_COUNTER = Counter(
    'fraud_predictions_total', 
    'Total fraud predictions',
    ['model_version', 'result']
)

PREDICTION_CONFIDENCE = Gauge(
    'fraud_prediction_confidence',
    'Prediction confidence score',
    ['model_version']
)

LATENCY_HISTOGRAM = Histogram(
    'fraud_prediction_latency_seconds',
    'Prediction request latency'
)