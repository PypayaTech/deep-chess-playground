import re
from enum import Enum
from typing import List, Tuple
from dataclasses import dataclass
from src.pgn_parsing.movetext_tokenizer import MovetextTokenizer


class PlayerColor(Enum):
    """Enum representing the color of a chess player."""
    WHITE = 1
    BLACK = 2


@dataclass
class ParseResult:
    """Class to store the result of parsing movetext."""
    moves: List[str]
    comments: List[Tuple[int, PlayerColor, str]]


class MovetextParser:
    """A class for parsing chess game movetext in PGN format."""

    # Compiled regular expressions for better performance
    MOVE_NUMBER_REGEX = re.compile(r'^\d+\.\.?\.?$')
    MOVE_REGEX = re.compile(r'^([PNBRQK]?[a-h]?[1-8]?x?[a-h][1-8](=[NBRQ])?[+#]?|O-O(-O)?[+#]?)([!?]{1,2})?$')
    ANNOTATION_REGEX = re.compile(r'^([!?]{1,2}|\$\d+)$')
    RESULT_REGEX = re.compile(r'^(1-0|0-1|1/2-1/2|\*)$')

    def __init__(self):
        self.tokenizer = MovetextTokenizer()

    def parse(self, movetext: str) -> ParseResult:
        """
        Parse the movetext and extract moves and comments.

        Args:
            movetext (str): The movetext to parse.

        Returns:
            ParseResult: An object containing the list of moves and comments.
        """
        tokens = self.tokenizer.tokenize(movetext)
        moves = []
        comments = []
        current_move_number = 0
        current_color = PlayerColor.WHITE
        last_move_color = PlayerColor.BLACK
        current_comment = ""

        if not tokens:
            return ParseResult(moves, comments)

        if all(token.startswith('{') and token.endswith('}') for token in tokens):
            # Special case: only comments
            combined_comment = ' '.join(tokens)
            comments.append((0, PlayerColor.WHITE, combined_comment))
        else:
            i = 0
            while i < len(tokens):
                token = tokens[i]
                if self._is_move_number(token):
                    if current_comment:
                        comments.append((current_move_number, last_move_color, current_comment.strip()))
                        current_comment = ""
                    if '...' in token:
                        current_color = PlayerColor.BLACK
                    else:
                        current_move_number = int(token.rstrip('.'))
                        current_color = PlayerColor.WHITE
                elif self._is_move(token):
                    if current_comment:
                        comments.append((current_move_number, last_move_color, current_comment.strip()))
                        current_comment = ""
                    move, annotation = self._split_move_and_annotation(token)
                    moves.append(move)
                    if annotation:
                        comments.append((current_move_number, current_color, annotation))
                    last_move_color = current_color
                    current_color = PlayerColor.BLACK if current_color == PlayerColor.WHITE else PlayerColor.WHITE
                elif token.startswith('{') and token.endswith('}'):
                    current_comment += f" {token}"
                elif self.ANNOTATION_REGEX.match(token):
                    current_comment += f" {token}"
                elif self.RESULT_REGEX.match(token):
                    current_comment += f" {token}"
                elif token.startswith('(') and token.endswith(')'):
                    current_comment += f" {token}"
                i += 1

            # Add any remaining comment
            if current_comment:
                comments.append((current_move_number, last_move_color, current_comment.strip()))

        return ParseResult(moves, comments)

    def _is_move_number(self, token: str) -> bool:
        """Check if a token is a move number."""
        return bool(self.MOVE_NUMBER_REGEX.match(token))

    def _is_move(self, token: str) -> bool:
        """Check if a token is a chess move."""
        return bool(self.MOVE_REGEX.match(token))

    def _split_move_and_annotation(self, token: str) -> Tuple[str, str]:
        """Split a move token into the move and its annotation (if any)."""
        match = self.MOVE_REGEX.match(token)
        if match:
            move = match.group(1)
            annotation = match.group(4) or ''
            return move, annotation
        return token, ''
