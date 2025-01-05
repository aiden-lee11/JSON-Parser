""" 
In JSON, values must be one of the following data types:

    a string
    a number
    an object
    an array
    a boolean
    null

JSON Syntax Rules

Data is in name/value pairs
Data is separated by commas
Curly braces hold objects
Square brackets hold arrays

"""


"""
Goal to output array of tokens given a string


Tokens will be a tuple with the following (TokenType, val)
ex: 
(TOKEN_LBRACE, "{")
(TOKEN_STRING, "example")
(TOKEN_BOOL, "true")
(TOKEN_NUM, "11")
"""

from enum import Enum, auto
from typing import Optional, Any, List, Tuple
from dataclasses import dataclass


JSON_QUOTE = '"'

class TokenType(Enum):
    STR = auto()
    NUM = auto()
    BOOL = auto()
    NULL = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    COLON = auto()

@dataclass
class Token:
    tokenType: TokenType
    value: str
    line: int
    column: int




# Possibly clear all \n etc whitespace beforehand
class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 0

    def tokenize(self) -> List[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.lex_token()
        return self.tokens
        
    def lex_token(self):
        char = self.advance()

        match char:
            case '{': self.add_token(TokenType.LBRACE)
            case '}': self.add_token(TokenType.RBRACE)
            case '[': self.add_token(TokenType.LBRACKET)
            case ']': self.add_token(TokenType.RBRACKET)
            case ',': self.add_token(TokenType.COMMA)
            case ':': self.add_token(TokenType.COLON)
            case '"': self.lex_string()

        if self.is_digit(char) or char == '-': self.lex_number()



    def lex_string(self):
        res = ""

        while not self.is_at_end() and self.peek() != '"':
            # reset col and increment line
            if self.peek() == '\n':
                self.line += 1
                self.column = 0

            if self.peek() == '\\':
                self.advance()

                escapes = {
                    'n': '\n',
                    't': '\t',
                    'r': '\r',
                    'f': '\f',
                    'b': '\b',
                    '\\': '\\',
                    '"': '"',
                    '/': '/'
                }

                if self.peek() in escapes:
                    res += escapes[self.advance()]
                elif self.peek() == 'u':
                    self.advance()

                    # need to now have 4 hex digits for proper unicode
                    hex = ""

                    for _ in range(4):
                        if not self.is_hex_digit(self.peek()):
                            raise Exception(f"Expected unicode hex digit, received {self.peek()} at line {self.line} and col {self.column}")
                        hex += self.advance()
                    res += hex
                else:
                    raise Exception(f"Expected escape sequence, received {self.peek()} at line {self.line} and col {self.column}")
            else:
                # normal string char
                res += self.advance()

        if self.is_at_end():
            raise Exception("Expected string terminator received end of stream")

        # fall through which means valid and that the cur char is terminator 
        self.advance()

        self.add_token(TokenType.STR, res)

    def lex_number(self):
        if self.peek() == "-" and not self.is_digit(self.peek2()):
            raise Exception(f"Expected digit following negative got {self.peek2()} following at line {self.line} and col {self.column}")

        while self.is_digit(self.peek()):
            self.advance()

        if self.peek() == '.' and not self.is_digit(self.peek2()):
            raise Exception(f"Expected digit following dot got {self.peek2()} following at line {self.line} and col {self.column}")


        if self.peek() == '.' and self.is_digit(self.peek2()):
            self.advance()

            while self.is_digit(self.peek()):
                self.advance()

        if self.peek() in ['e', 'E']:
            self.advance()
            if self.peek() in ['+', '-'] or self.is_digit(self.peek()):
                self.advance()
                while self.is_digit(self.peek()):
                    self.advance()

        self.add_token(TokenType.NUM)



    # looks at curr char DOES NOT REMOVE
    def peek(self) -> str:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    # look at curr + 1 char DOES NOT REMOVE
    def peek2(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        
        return self.source[self.current + 1]

    def previous(self) -> str:
        return self.source[self.current - 1]

    # consume and return token
    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        return char

    def add_token(self, tokenType: TokenType, value: str | None = None) -> None:
        text = self.source[self.start: self.current]
        self.tokens.append(Token(tokenType, value or text, self.line, self.column))

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    @staticmethod
    def is_digit(c: str) -> bool:
        return '0' <= c <= '9'

    @staticmethod
    def is_hex_digit(c: str) -> bool:
        return ('0' <= c <= '9') or ('a' <= c <= 'f') or ('A' <= c <= 'F')


if __name__ == "__main__":
    # Working
    # json_input = '''{
    #   "simple": "This is a string",
    #   "escaped_quote": "She said, \\\"Hello!\\\"",
    #   "newline": "Line 1\\nLine 2",
    #   "tab": "Column1\\tColumn2",
    #   "backslash": "This is a backslash: \\\\",
    #   "unicode": "Emoji: \\uD83D\\uDE80",
    #   "mixed": "This \\\"string\\\" has \\t multiple\\nescapes \\\\ and unicode \\u2603"
    # }'''


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

    lexer = Lexer(json_input)
    tokens = lexer.tokenize()
    for token in tokens:
        print(token)
        print()
