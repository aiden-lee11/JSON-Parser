import pytest
from lexer import Lexer
from parser import Parser

@pytest.fixture
def lexer():
    return Lexer

@pytest.fixture
def parser():
    return Parser



def test_simple_object(lexer, parser):
    json_input = '{"key": "value"}'
    tokens = lexer(source=json_input).tokenize()
    result = parser(tokens=tokens).parse_json()

    assert {'key': 'value'} == result

def test_server_json(lexer, parser):
    tokens = lexer(path='./examples/server.json').tokenize()
    result = parser(tokens=tokens).parse_json()

    expected = {
        "id": "0001",
        "type": "donut",
        "name": "Cake",
        "ppu": 0.55,
        "batters":
        {
            "batter":
            [
                { "id": "1001", "type": "Regular" },
                { "id": "1002", "type": "Chocolate" },
                { "id": "1003", "type": "Blueberry" },
                { "id": "1004", "type": "Devil's Food" }
            ]
        },
        "topping":
        [
            { "id": "5001", "type": "None" },
            { "id": "5002", "type": "Glazed" },
            { "id": "5005", "type": "Sugar" },
            { "id": "5007", "type": "Powdered Sugar" },
            { "id": "5006", "type": "Chocolate with Sprinkles" },
            { "id": "5003", "type": "Chocolate" },
            { "id": "5004", "type": "Maple" }
        ]
    }
    assert expected == result


def test_empty_object(lexer, parser):
    json_input = '{}'
    tokens = lexer(source=json_input).tokenize()
    result = parser(tokens=tokens).parse_json()

    assert {} == result


def test_simple_array(lexer, parser):
    json_input = '[1, 2, 3, 4]'
    tokens = lexer(source=json_input).tokenize()
    result = parser(tokens=tokens).parse_json()

    assert [1, 2, 3, 4] == result


def test_nested_objects(lexer, parser):
    json_input = '{"outer": {"inner": {"key": "value"}}}'
    tokens = lexer(source=json_input).tokenize()
    result = parser(tokens=tokens).parse_json()

    assert {"outer": {"inner": {"key": "value"}}} == result


def test_nested_arrays(lexer, parser):
    json_input = '[1, [2, [3, [4]]]]'
    tokens = lexer(source=json_input).tokenize()
    result = parser(tokens=tokens).parse_json()

    assert [1, [2, [3, [4]]]] == result


def test_mixed_structure(lexer, parser):
    json_input = '{"array": [1, {"key": "value"}], "empty": {}, "number": 42}'
    tokens = lexer(source=json_input).tokenize()
    result = parser(tokens=tokens).parse_json()

    assert {
        "array": [1, {"key": "value"}],
        "empty": {},
        "number": 42
    } == result


def test_empty_array(lexer, parser):
    json_input = '[]'
    tokens = lexer(source=json_input).tokenize()
    result = parser(tokens=tokens).parse_json()

    assert [] == result


def test_true_false_null(lexer, parser):
    json_input = '{"true_key": true, "false_key": false, "null_key": null}'
    tokens = lexer(source=json_input).tokenize()
    result = parser(tokens=tokens).parse_json()

    assert {
        "true_key": True,
        "false_key": False,
        "null_key": None
    } == result


def test_string_with_special_characters(lexer, parser):
    json_input = '{"key": "value with \\n newlines and \\t tabs"}'
    tokens = lexer(source=json_input).tokenize()
    result = parser(tokens=tokens).parse_json()

    assert {
        "key": "value with \n newlines and \t tabs"
    } == result

def test_invalid_json(lexer, parser):
    json_input = '{"key": "value",}'
    tokens = lexer(source=json_input).tokenize()

    with pytest.raises(Exception):
        parser(tokens=tokens).parse_json()

def test_large_json(lexer, parser):
    json_input = '{"numbers": ' + str(list(range(10000))) + '}'
    tokens = lexer(source=json_input).tokenize()
    result = parser(tokens=tokens).parse_json()

    assert {"numbers": list(range(10000))} == result
