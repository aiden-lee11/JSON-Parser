from os import path
import pytest
from lexer import Lexer, TokenType

@pytest.fixture
def lexer():
    return Lexer

def test_simple_object(lexer):
    json_input = '{"key": "value"}'
    tokens = lexer(source=json_input).tokenize()
    expected = [
        {"tokenType": TokenType.LBRACE, "value": "{", "line": 1, "column": 0},
        {"tokenType": TokenType.STR, "value": "key", "line": 1, "column": 1},
        {"tokenType": TokenType.COLON, "value": ":", "line": 1, "column": 6},
        {"tokenType": TokenType.STR, "value": "value", "line": 1, "column": 8},
        {"tokenType": TokenType.RBRACE, "value": "}", "line": 1, "column": 15},
    ]
    assert [{"tokenType": token.tokenType, "value": token.value, "line": token.line, "column": token.column} for token in tokens] == expected

def test_nested_object(lexer):
    json_input = '''
    {
        "nested": {
            "innerKey": [1, 2, 3, 4]
        }
    }
    '''
    tokens = lexer(source=json_input).tokenize()
    expected_token_types = [
        TokenType.LBRACE,
        TokenType.STR,
        TokenType.COLON,
        TokenType.LBRACE,
        TokenType.STR,
        TokenType.COLON,
        TokenType.LBRACKET,
        TokenType.NUM,
        TokenType.COMMA,
        TokenType.NUM,
        TokenType.COMMA,
        TokenType.NUM,
        TokenType.COMMA,
        TokenType.NUM,
        TokenType.RBRACKET,
        TokenType.RBRACE,
        TokenType.RBRACE,
    ]
    assert [token.tokenType for token in tokens] == expected_token_types

def test_escaped_strings(lexer):
    json_input = '''{
      "simple": "This is a string",
      "escaped_quote": "She said, \\"Hello!\\"",
      "newline": "Line 1\\nLine 2",
      "tab": "Column1\\tColumn2",
      "backslash": "This is a backslash: \\\\",
      "unicode": "Emoji: \\uD83D\\uDE80",
      "mixed": "This \\"string\\" has \\t multiple\\nescapes \\\\ and unicode \\u2603"
    }'''
    tokens = lexer(source=json_input).tokenize()
    assert tokens[0].tokenType == TokenType.LBRACE
    assert tokens[-1].tokenType == TokenType.RBRACE

def test_numbers(lexer):
    json_input = '''{
      "integer": 42,
      "negative_integer": -42,
      "zero": 0,
      "float": 3.14159,
      "negative_float": -2.71828,
      "exponent_positive": 1.23e4,
      "exponent_negative": 5.67E-8,
      "large_integer": 1234567890,
      "small_negative_float": -0.0000123,
      "leading_zero": 0.1234
    }'''
    tokens = lexer(source=json_input).tokenize()
    number_tokens = [token for token in tokens if token.tokenType == TokenType.NUM]
    assert len(number_tokens) == 10

def test_complex_nested(lexer):
    json_input = '''
    {
        "string_key": "Hello, World!",
        "integer_key": 123,
        "float_key": 45.67,
        "boolean_key": true,
        "null_key": null,
        "array_key": [1, 2, 3, 4, 5],
        "nested_object_key": {
            "nested_string": "Nested Hello",
            "nested_array": ["a", "b", "c"],
            "nested_object": {
                "deep_key": 789
            }
        },
        "complex_array": [
            {"item_key": 1},
            {"item_key": 2},
            {"item_key": 3}
        ]
    }
    '''
    tokens = lexer(source=json_input).tokenize()
    assert any(token.tokenType == TokenType.BOOL for token in tokens)
    assert any(token.tokenType == TokenType.NULL for token in tokens)

def test_server_response_file(lexer):
    tokens = lexer(path='./examples/server.json').tokenize()
    assert any(token.tokenType == TokenType.STR and token.value == "batters" for token in tokens)
