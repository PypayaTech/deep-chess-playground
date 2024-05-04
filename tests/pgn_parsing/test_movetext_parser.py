import pytest
from src.pgn_parsing.movetext_parser import MovetextParser, PlayerColor


@pytest.fixture
def parser():
    return MovetextParser()


def test_basic_moves(parser):
    movetext = "1. e4 e5 2. Nf3 Nc6 3. Bb5"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3", "Nc6", "Bb5"]
    assert result.comments == []


def test_moves_with_simple_comments(parser):
    movetext = "1. e4 {King's Pawn opening} e5 2. Nf3 {Knight development} Nc6 {Another knight}"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3", "Nc6"]
    assert result.comments == [
        (1, PlayerColor.WHITE, "{King's Pawn opening}"),
        (2, PlayerColor.WHITE, "{Knight development}"),
        (2, PlayerColor.BLACK, "{Another knight}")
    ]


def test_moves_with_annotations(parser):
    movetext = "1. e4! e5? 2. Nf3!! Nc6??"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3", "Nc6"]
    assert result.comments == [
        (1, PlayerColor.WHITE, "!"),
        (1, PlayerColor.BLACK, "?"),
        (2, PlayerColor.WHITE, "!!"),
        (2, PlayerColor.BLACK, "??")
    ]


def test_moves_with_check_and_mate(parser):
    movetext = "1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6?? 4. Qxf7#"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Qh5", "Nc6", "Bc4", "Nf6", "Qxf7#"]
    assert result.comments == [(3, PlayerColor.BLACK, "??")]


def test_castling(parser):
    movetext = "1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. O-O O-O"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "O-O", "O-O"]
    assert result.comments == []


def test_pawn_promotion(parser):
    movetext = "1. e4 e5 2. d4 exd4 3. c3 dxc3 4. Bc4 cxb2 5. Bxb2 Nc6 6. Nf3 d6 7. e8=Q+"
    result = parser.parse(movetext)
    assert result.moves[-1] == "e8=Q+"
    assert result.comments == []


def test_numeric_annotation_glyphs(parser):
    movetext = "1. e4 $1 e5 $2 2. Nf3 $3 Nc6 $4"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3", "Nc6"]
    assert result.comments == [
        (1, PlayerColor.WHITE, "$1"),
        (1, PlayerColor.BLACK, "$2"),
        (2, PlayerColor.WHITE, "$3"),
        (2, PlayerColor.BLACK, "$4")
    ]


def test_variations(parser):
    movetext = "1. e4 e5 2. Nf3 (2. f4 exf4 3. Bc4 Qh4+) 2... Nc6 3. Bb5"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3", "Nc6", "Bb5"]
    assert result.comments == [(2, PlayerColor.WHITE, "(2. f4 exf4 3. Bc4 Qh4+)")]


def test_nested_variations(parser):
    movetext = "1. e4 e5 2. Nf3 (2. f4 exf4 3. Bc4 (3. Nf3 g5 4. h4) 3... Qh4+) 2... Nc6 3. Bb5"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3", "Nc6", "Bb5"]
    assert result.comments == [(2, PlayerColor.WHITE, "(2. f4 exf4 3. Bc4 (3. Nf3 g5 4. h4) 3... Qh4+)")]


def test_comments_with_special_characters(parser):
    movetext = "1. e4 {This move (e4) is strong! It controls the center.} e5 2. Nf3 {The knight comes out, attacking e5.}"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3"]
    assert result.comments == [
        (1, PlayerColor.WHITE, "{This move (e4) is strong! It controls the center.}"),
        (2, PlayerColor.WHITE, "{The knight comes out, attacking e5.}")
    ]


def test_empty_movetext(parser):
    movetext = ""
    result = parser.parse(movetext)
    assert result.moves == []
    assert result.comments == []


def test_only_comments(parser):
    movetext = "{This game never started} {Another comment}"
    result = parser.parse(movetext)
    assert result.moves == []
    assert result.comments == [(0, PlayerColor.WHITE, "{This game never started} {Another comment}")]


def test_mixed_comments_and_variations(parser):
    movetext = "1. e4 {Good move} (1. d4 {Queen's Pawn Game}) 1... e5 {Symmetric response}"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5"]
    assert result.comments == [
        (1, PlayerColor.WHITE, "{Good move} (1. d4 {Queen's Pawn Game})"),
        (1, PlayerColor.BLACK, "{Symmetric response}")
    ]


def test_multiline_comments(parser):
    movetext = """1. e4 {This is a
multiline comment
spanning several lines} e5"""
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5"]
    assert result.comments == [(1, PlayerColor.WHITE, "{This is a\nmultiline comment\nspanning several lines}")]


def test_comments_with_brackets(parser):
    movetext = "1. e4 {This comment contains [brackets] (and parentheses)} e5"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5"]
    assert result.comments == [(1, PlayerColor.WHITE, "{This comment contains [brackets] (and parentheses)}")]


def test_moves_with_dots(parser):
    movetext = "1. e4 ... e5"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5"]
    assert result.comments == []


def test_incomplete_movetext(parser):
    movetext = "1. e4 e5 2. Nf3"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3"]
    assert result.comments == []


def test_result_at_end(parser):
    movetext = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 1-0"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6"]
    assert result.comments == [(3, PlayerColor.BLACK, '1-0')]


def test_multiple_spaces_between_moves(parser):
    movetext = "1.  e4    e5   2. Nf3    Nc6"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3", "Nc6"]
    assert result.comments == []


def test_parse_with_multiple_comments_per_move(parser):
    movetext = "1. e4 {First comment} {Second comment} e5 2. Nf3 Nc6 {Third comment}"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3", "Nc6"]
    assert result.comments == [
        (1, PlayerColor.WHITE, "{First comment} {Second comment}"),
        (2, PlayerColor.BLACK, "{Third comment}")
    ]


def test_parse_with_comments_between_moves(parser):
    movetext = "1. e4 {White's first move} e5 {Black's response} 2. Nf3 {White's second move}"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3"]
    assert result.comments == [
        (1, PlayerColor.WHITE, "{White's first move}"),
        (1, PlayerColor.BLACK, "{Black's response}"),
        (2, PlayerColor.WHITE, "{White's second move}")
    ]


def test_parse_with_multiple_variations(parser):
    movetext = "1. e4 e5 2. Nf3 (2. f4 exf4 3. Bc4) (2. Nc3 Nc6 3. Bc4) Nc6"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3", "Nc6"]
    assert result.comments == [
        (2, PlayerColor.WHITE, "(2. f4 exf4 3. Bc4) (2. Nc3 Nc6 3. Bc4)")
    ]


def test_parse_with_result_and_final_comment(parser):
    movetext = "1. e4 e5 2. Nf3 Nc6 3. Bb5 {Final position} 1-0"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3", "Nc6", "Bb5"]
    assert result.comments == [
        (3, PlayerColor.WHITE, "{Final position} 1-0"),
    ]


def test_parse_with_move_numbers_for_black(parser):
    movetext = "1. e4 e5 2. Nf3 2... Nc6 3. Bb5"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3", "Nc6", "Bb5"]
    assert result.comments == []


def test_parse_with_ellipsis(parser):
    movetext = "1. e4 ... e5 2. Nf3"
    result = parser.parse(movetext)
    assert result.moves == ["e4", "e5", "Nf3"]
    assert result.comments == []
