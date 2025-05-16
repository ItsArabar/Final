import pytest
from app.utils import validate_number_input


def test_validate_number_input():
    assert validate_number_input("5") == 5
    assert validate_number_input("3.14") == 3.14

    with pytest.raises(ValueError):
        validate_number_input("abc")
