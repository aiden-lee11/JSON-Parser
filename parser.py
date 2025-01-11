"""
<json> ::= <primitive> | <container>

<primitive> ::= <number> | <string> | <boolean>
; Where:
; <number> is a valid real number expressed in one of a number of given formats
; <string> is a string of valid characters enclosed in quotes
; <boolean> is one of the literal strings 'true', 'false', or 'null' (unquoted)

<container> ::= <object> | <array>
<array> ::= '[' [ <json> *(', ' <json>) ] ']' ; A sequence of JSON values separated by commas
<object> ::= '{' [ <member> *(', ' <member>) ] '}' ; A sequence of 'members'
<member> ::= <string> ': ' <json> ; A pair consisting of a name, and a JSON value

"""

from typing import Dict, List, Any, Union 
from lexer import Lexer, Token, TokenType

class Parser:
    def __init__(self, tokens : List[Token]) -> None:
        self.tokens = tokens
        # index into the token array
        self.current = 0
        self.res = {}

    def parse_json(self) -> Any:
        """<json> ::= <primitive> | <container>"""
        token = self.peek()
        if self.is_primitive_token(token):
            return self.parse_primitive()
        else:
            return self.parse_container()
    
    def parse_primitive(self) -> Union[int, float, str, bool, None]:
        """<primitive> ::= <number> | <string> | <boolean> | <null>"""
        token = self.advance()

        match token.tokenType:
            case TokenType.NUM:
                if '.' in token.value or 'e' in token.value.lower():
                    return float(token.value)
                else:
                    return int(token.value)
            case TokenType.STR:
                return token.value
            case TokenType.BOOL:
                return token.value == "true"
            case TokenType.NULL:
                return None
            case _:
                raise Exception(f"Expected primitive token, got {token} mismatching type")

    def parse_container(self) -> Union[Dict, List]:
        """<container> ::= <object> | <array>"""
        token = self.peek()

        if token.tokenType == TokenType.LBRACKET:
            return self.parse_array()
        elif token.tokenType == TokenType.LBRACE:
            return self.parse_object()
        else:
            raise Exception(f"Expected container token, got {token}")

    def parse_array(self) -> List:
        """<array> ::= '[' [ <json> *(', ' <json>) ] ']' ; A sequence of JSON values separated by commas"""
        token = self.advance()

        if token.tokenType != TokenType.LBRACKET:
            raise Exception(f"Expected start of array token, got {token}")

        res = []

        if self.peek().tokenType == TokenType.RBRACKET:
            return res

        res.append(self.parse_json())

        while self.peek().tokenType == TokenType.COMMA:
            # consume the comma
            self.advance()
            # non optional json element
            res.append(self.parse_json())

        if self.peek().tokenType != TokenType.RBRACKET:
            raise Exception(f"Expected closing bracket to array, got {token}")

        # fell through so consume the ]
        self.advance()
        
        return res
    
    def parse_object(self) -> Dict:
        """<object> ::= '{' [ <member> *(', ' <member>) ] '}' ; A sequence of 'members'"""
        token = self.advance()

        if token.tokenType != TokenType.LBRACE:
            raise Exception(f"Expected start of object token, got {token}")

        res = {}

        if self.peek().tokenType == TokenType.RBRACE:
            self.advance()
            return res
        
        key, val = self.parse_member()
        res[key] = val

        while self.peek().tokenType == TokenType.COMMA:
            # consume the comma
            self.advance()
            # non optional json element
            key, val = self.parse_member()
            res[key] = val


        if self.peek().tokenType != TokenType.RBRACE:
            raise Exception(f"Expected closing brace to object, got {token}")

        # fell through so consume the }
        self.advance()
        
        return res

    def parse_member(self) -> tuple[str, Any]:
        """<member> ::= <string> ': ' <json> ; A pair consisting of a name, and a JSON value"""
        token = self.advance()

        if token.tokenType != TokenType.STR:
            raise Exception(f"Expected string as key token for member, got {token}")

        key = token.value

        token = self.advance()

        if token.tokenType != TokenType.COLON:
            raise Exception(f"Expected colon separator for member, got {token}")

        value = self.parse_json()

        return (key, value)

    def is_primitive_token(self, token: Token) -> bool:
        return token.tokenType in [TokenType.STR, TokenType.NUM, TokenType.BOOL, TokenType.NULL]

    def is_container_token(self, token: Token) -> bool:
        return token.tokenType in [TokenType.LBRACE, TokenType.LBRACKET]


    # looks at curr char DOES NOT REMOVE
    def peek(self) -> Token:
        if self.is_at_end():
            raise Exception("Unexpected end of input")
        return self.tokens[self.current]
    
    # consume and return token, might need a bounds check ? 
    def advance(self) -> Token:
        if self.is_at_end():
            raise Exception("Unexpected end of input")
        token = self.tokens[self.current]
        self.current += 1
        return token

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)

if __name__ == "__main__":
    json_input = '{"array": [1, {"key": "value"}], "empty": {}, "number": 42}'
    lexer = Lexer(source=json_input)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    print(parser.parse_json())
