from enum import Enum, auto
from typing import List, Optional, overload, TypeAlias
from pathlib import Path
from dataclasses import dataclass

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
    
    def __str__(self) -> str:
        return f"\n Type: {self.tokenType}\n Value: {self.value}\n Line: {self.line}\n Column {self.column}\n"


SourceType: TypeAlias = str
PathType: TypeAlias = str | Path 

class Lexer:
    @overload
    def __init__(self, *, source: SourceType) -> None: ...
    
    @overload 
    def __init__(self, *, path: PathType) -> None: ...
    
    def __init__(
        self, 
        *, 
        source: Optional[SourceType] = None, 
        path: Optional[PathType] = None
    ) -> None:
        if source is not None and path is not None:
            raise ValueError("Cannot specify both source and path")
        if source is None and path is None:
            raise ValueError("Must specify either source or path")
            
        self.source: str = source if source is not None else open(str(path)).read()

        self.tokens: List[Token] = []
        self.current = 0
        self.line = 1
        self.column = 0

    def tokenize(self) -> List[Token]:
        while not self.is_at_end():
            self.lex_whitespace()
            self.lex_token()
            self.lex_whitespace()
        return self.tokens
        
    def lex_token(self):
        char = self.peek()

        match char:
            case '{': self.lex_object()
            case '[': self.lex_array()
            case ',': self.add_token(TokenType.COMMA, ',')
            case ':': self.add_token(TokenType.COLON, ':')
            case '"': self.lex_string()

        if self.is_digit(char) or char == '-': self.lex_number()
  

    def lex_string(self):
        res = ""

        # skip the first "
        start_col = self.column
        self.advance()

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
        self.add_token(TokenType.STR, res, start_col)
        self.advance()

    def lex_number(self):
        res = ''
        start_col = self.column

        if self.peek() == "-" and not self.is_digit(self.peek2()):
            raise Exception(f"Expected digit following negative got {self.peek2()} following at line {self.line} and col {self.column}")

        if self.peek() == "-":
            res += self.advance()

        while self.is_digit(self.peek()):
            res += self.advance()

        if self.peek() == '.' and not self.is_digit(self.peek2()):
            raise Exception(f"Expected digit following dot got {self.peek2()} following at line {self.line} and col {self.column}")


        if self.peek() == '.' and self.is_digit(self.peek2()):
            res += self.advance()

            while self.is_digit(self.peek()):
                res += self.advance()

        if self.peek() in ['e', 'E']:
            res += self.advance()
            if self.peek() in ['+', '-'] or self.is_digit(self.peek()):
                res += self.advance()
                while self.is_digit(self.peek()):
                    res += self.advance()

        self.add_token(TokenType.NUM, res, start_col)

    def lex_whitespace(self):
        white_space = ['\n', '\r', '\t', " "]

        while not self.is_at_end() and self.peek() in white_space:
            if self.peek() == "\n":
                self.line += 1
            self.advance()

    def lex_value(self):
        self.lex_whitespace()

        char = self.peek()

        match char:
            case '"':
                self.lex_string()
            case '{':
                self.lex_object()
            case '[':
                self.lex_array() 
            case _:
                if self.is_digit(char) or char == '-':
                    self.lex_number()
                elif char.isalpha():
                    self.lex_keyword()
                else:
                    raise Exception(f"Unexpected character in value: {char} at line {self.line} and col {self.column}")

        self.lex_whitespace()

    def lex_object(self):
        self.add_token(TokenType.LBRACE, '{')
        self.advance()

        self.lex_whitespace()

        while not self.is_at_end() and self.peek() != '}':
            if self.peek() != '"':
                raise Exception(f"Expected string start within object got {self.peek()} at line {self.line} and col {self.column}")

            self.lex_string()
            self.lex_whitespace()

            if self.peek() != ':':
                raise Exception(f"Expected colon within object got {self.peek()} at line {self.line} and col {self.column}")


            self.add_token(TokenType.COLON, ':')
            self.advance()
            self.lex_whitespace()
            
            self.lex_value()

            if self.peek() == ',':
                self.add_token(TokenType.COMMA, ',')
                self.advance()
                self.lex_whitespace()

        if self.is_at_end():
            raise Exception("Expected object terminator received end of stream")

        # valid array so handle '}'
        self.add_token(TokenType.RBRACE, '}')
        self.advance()

    def lex_array(self):
        # advance past the '['
        self.add_token(TokenType.LBRACKET, '[')
        self.advance()


        # clear whitespace
        self.lex_whitespace()

        while not self.is_at_end() and self.peek() != ']':
            self.lex_value()

            if self.peek() == ',':
                self.add_token(TokenType.COMMA, ',')
                self.advance()
                self.lex_whitespace()


        if self.is_at_end():
            raise Exception("Expected array terminator received end of stream")

        # valid array so handle ']'
        self.add_token(TokenType.RBRACKET, ']')
        self.advance()


    def lex_keyword(self):
        keywords = {
            'true': TokenType.BOOL,
            'false': TokenType.BOOL,
            'null': TokenType.NULL
        }

        start_ind = self.current

        # advance as far as possible if alphanumeric
        while not self.is_at_end() and self.peek().isalpha():
            self.advance()

        text = self.source[start_ind: self.current]

        if text not in keywords:
            raise Exception(f"Unexpected alpha sequence {text}, expected sequence to be a keyword at line {self.line} and col {self.column}")

        self.add_token(keywords[text], text)


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
    
    # consume and return token
    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        return char

    def add_token(self, tokenType: TokenType, value: str, start_col=None) -> None:
        col = start_col if start_col is not None else self.column
        self.tokens.append(Token(tokenType, value, self.line, col))

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    @staticmethod
    def is_digit(c: str) -> bool:
        return '0' <= c <= '9'

    @staticmethod
    def is_hex_digit(c: str) -> bool:
        return ('0' <= c <= '9') or ('a' <= c <= 'f') or ('A' <= c <= 'F')


if __name__ == "__main__":
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

    lexer = Lexer(source=json_input)
    tokens = lexer.tokenize()

    for i, token in enumerate(tokens):
        print(f'Token {i}: {token}')
