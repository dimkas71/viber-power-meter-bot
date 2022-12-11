import pytest

from utils import parse

def test_well_formed_data():
    message = "201302018759:1888"
    counter, value = parse(message)
    assert counter == "201302018759"
    assert value == 1888


@pytest.mark.parametrize(
    "message, expected_counter, expected_value",
    [
        ("09073747:3637", "09073747", 3637),
        ("0603490402540575:7445", "0603490402540575", 7445),
        ("14107938 /кава Нікорич:123", "14107938 /кава Нікорич", 123),
        ("17004441 кава 1сходи 1 тс:4040", "17004441 кава 1сходи 1 тс", 4040)
    ]
)
def test_well_formed_bulk_data(message, expected_counter, expected_value):
    counter, value = parse(message)
    assert counter == expected_counter
    assert value == expected_value


def test_bad_formed_value():
    with pytest.raises(ValueError):
        parse("12355345:56d5")


def test_empty_counter_should_raise_ValueError():
    with pytest.raises(ValueError) as e:
        parse(":4444")

def test_empty_value_should_raise_ValueError():
    with pytest.raises(ValueError) as e:
        parse("3234234:")

