import re
from enum import Enum
from typing import List, Tuple


class PlayerColor(Enum):
    WHITE = 1
    BLACK = 2


class MovetextTokenizer:
    """A class for tokenizing chess game movetext in PGN format."""

    # Constants
    COMMENT_START = '{'
    COMMENT_END = '}'
    VARIATION_START = '('
    VARIATION_END = ')'

    @classmethod
    def tokenize(cls, movetext: str) -> List[str]:
        """
        Tokenize the movetext into moves, move numbers, and comments.

        Args:
            movetext (str): The movetext to tokenize.

        Returns:
            A list of tokens.
        """
        tokens = cls._split_tokens(movetext)
        return cls._process_tokens(tokens)

    @classmethod
    def _split_tokens(cls, movetext: str) -> List[str]:
        """Split the movetext into raw tokens."""
        tokens = []
        current_token = ""
        state = {"in_comment": False, "in_variation": 0, "append_token": False}

        for char in movetext:
            if state["in_comment"]:
                current_token += char
                if char == cls.COMMENT_END:
                    state["in_comment"] = False
                    state["append_token"] = True
            elif state["in_variation"] > 0:
                current_token += char
                if char == cls.VARIATION_START:
                    state["in_variation"] += 1
                elif char == cls.VARIATION_END:
                    state["in_variation"] -= 1
                    if state["in_variation"] == 0:
                        state["append_token"] = True
            else:
                if char == cls.COMMENT_START:
                    if current_token:
                        state["append_token"] = True
                    current_token = char
                    state["in_comment"] = True
                elif char == cls.VARIATION_START:
                    if current_token:
                        state["append_token"] = True
                    current_token = char
                    state["in_variation"] = 1
                elif char.isspace():
                    if current_token:
                        state["append_token"] = True
                else:
                    current_token += char

            if state["append_token"]:
                tokens.append(current_token.strip())
                current_token = ""
                state["append_token"] = False

        if current_token:
            tokens.append(current_token.strip())

        return tokens

    @classmethod
    def _process_tokens(cls, tokens: List[str]) -> List[str]:
        """Process the raw tokens, combining move numbers and dots."""
        processed_tokens = []
        i = 0
        while i < len(tokens):
            if cls._is_move_number(tokens[i]):
                if i + 1 < len(tokens) and tokens[i + 1] == '.':
                    processed_tokens.append(tokens[i] + '.')
                    i += 2
                    if i < len(tokens) and tokens[i] == '.':
                        processed_tokens[-1] += '.'
                        i += 1
                else:
                    processed_tokens.append(tokens[i])
                    i += 1
            else:
                processed_tokens.append(tokens[i])
                i += 1

        return [token for token in processed_tokens if token.strip()]

    @staticmethod
    def _is_move_number(token: str) -> bool:
        """Check if a token is a move number."""
        return bool(re.match(r'^\d+$', token))
