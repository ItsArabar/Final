import pytest
from app.calculator import add, subtract, multiply, divide, power, sqrt


class TestCalculator:
    def test_add(self):
        assert add(2, 3) == 5
        assert add(-1, 1) == 0
        assert add(0, 0) == 0

    def test_subtract(self):
        assert subtract(5, 3) == 2
        assert subtract(3, 5) == -2

    def test_multiply(self):
        assert multiply(3, 4) == 12
        assert multiply(0, 5) == 0

    def test_divide(self):
        assert divide(6, 3) == 2
        assert divide(5, 2) == 2.5

        with pytest.raises(ValueError):
            divide(5, 0)

    def test_power(self):
        assert power(2, 3) == 8
        assert power(5, 0) == 1

    def test_sqrt(self):
        assert sqrt(9) == 3
        assert sqrt(0) == 0

        with pytest.raises(ValueError):
            sqrt(-1)
