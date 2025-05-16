from prometheus_client import start_http_server, Counter

CALCULATOR_OPERATIONS = Counter(
    "calculator_operations_total",
    "Total number of calculator operations",
    ["operation"],
)


def track_operation(operation: str):
    CALCULATOR_OPERATIONS.labels(operation=operation).inc()


def start_monitoring(port: int = 8000):
    start_http_server(port)
