import unittest
from lexer import Lexer, TokenType

class TestLexer(unittest.TestCase):
    def setUp(self):
        self.Lexer = Lexer

    def test_simple_object(self):
        json_input = '{"key": "value"}'
        lexer = self.Lexer(json_input)
        tokens = lexer.tokenize()
        expected = [
            {"tokenType": TokenType.LBRACE, "value": "{", "line": 1, "column": 0},
            {"tokenType": TokenType.STR, "value": "key", "line": 1, "column": 1},
            {"tokenType": TokenType.COLON, "value": ":", "line": 1, "column": 6},
            {"tokenType": TokenType.STR, "value": "value", "line": 1, "column": 8},
            {"tokenType": TokenType.RBRACE, "value": "}", "line": 1, "column": 15},
        ]
        self.assertEqual(
            [{"tokenType": token.tokenType, "value": token.value, "line": token.line, "column": token.column} for token in tokens],
            expected,
        )

    def test_nested_object(self):
        json_input = '''
        {
            "nested": {
                "innerKey": [1, 2, 3, 4]
            }
        }
        '''
        lexer = self.Lexer(json_input)
        tokens = lexer.tokenize()
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
        self.assertEqual([token.tokenType for token in tokens], expected_token_types)

    def test_escaped_strings(self):
        json_input = '''{
          "simple": "This is a string",
          "escaped_quote": "She said, \\"Hello!\\"",
          "newline": "Line 1\\nLine 2",
          "tab": "Column1\\tColumn2",
          "backslash": "This is a backslash: \\\\",
          "unicode": "Emoji: \\uD83D\\uDE80",
          "mixed": "This \\"string\\" has \\t multiple\\nescapes \\\\ and unicode \\u2603"
        }'''
        lexer = self.Lexer(json_input)
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].tokenType, TokenType.LBRACE)
        self.assertEqual(tokens[-1].tokenType, TokenType.RBRACE)

    def test_numbers(self):
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
        lexer = self.Lexer(json_input)
        tokens = lexer.tokenize()
        number_tokens = [token for token in tokens if token.tokenType == TokenType.NUM]
        self.assertEqual(len(number_tokens), 10)

    def test_complex_nested(self):
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
        lexer = self.Lexer(json_input)
        tokens = lexer.tokenize()
        self.assertTrue(any(token.tokenType == TokenType.BOOL for token in tokens))
        self.assertTrue(any(token.tokenType == TokenType.NULL for token in tokens))

if __name__ == "__main__":
    unittest.main()
