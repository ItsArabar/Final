from app.monitoring import track_operation

def add(a: float, b: float) -> float:
    track_operation('add')
    return a + b


def subtract(a: float, b: float) -> float:
    track_operation('subtract')
    return a - b


def multiply(a: float, b: float) -> float:
    track_operation('multiply')
    return a * b


def divide(a: float, b: float) -> float:
    track_operation('divide')
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def power(base: float, exponent: float) -> float:
    track_operation('power')
    return base**exponent


def sqrt(number: float) -> float:
    track_operation('sqrt')
    if number < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return number**0.5
