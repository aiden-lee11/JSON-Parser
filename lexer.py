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


JSON_QUOTE = '"'

class Token(Enum):
    STR = auto()
    NUM = auto()
    BOOL = auto()
    NULL = auto()


# Possibly clear all \n etc whitespace beforehand
class Lexer:
    def __init__(self, token_string) -> None:
        self.tokens = []
        self.token_string = token_string


    def lex(self): 
        while len(self.token_string):
            # go through and check what type it is 
            

            string = self.lex_string()
            if string is not None:
                token = (Token.STR, string)
                self.tokens.append(token)

            num = self.lex_num()
            if num is not None:
                token = (Token.NUM, num)
                self.tokens.append(token)

            boolean = self.lex_bool()
            if boolean is not None:
                token = (Token.BOOL, num)
                self.tokens.append(token)



    def lex_string(self) -> None | str:
        res = ''

        if not self.tokens[0] == JSON_QUOTE:
            return None

        # Fell through so remove the quote from the string and parse until you find another quote
        self.token_string = self.token_string[1:]

        for char in self.token_string:
            if char == JSON_QUOTE:
                self.token_string = self.token_string[len(res) + 1:]
                return res
            else:
                res += char

        raise Exception("Expected end of string quote")

    # def lex_bool(self) -> None | 
