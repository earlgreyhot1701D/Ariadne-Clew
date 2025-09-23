import pytest
from lambda_classifier import validate_input_length


def test_validate_input_within_limit():
    # Small string should pass without error
    text = "hello world" * 100
    try:
        validate_input_length(text)
    except ValueError:
        pytest.fail("validate_input_length() raised ValueError unexpectedly!")


def test_validate_input_exceeds_limit():
    # Oversized string should raise ValueError
    text = "a" * 120_000  # exceeds 100k chars
    with pytest.raises(ValueError) as excinfo:
        validate_input_length(text)
    assert "Input too long" in str(excinfo.value)
    assert "100,000" in str(excinfo.value)  # limit mentioned in error
