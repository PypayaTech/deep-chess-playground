import pytest
from src.pgn_parsing.movetext_tokenizer import MovetextTokenizer


@pytest.fixture
def tokenizer():
    return MovetextTokenizer()


def test_basic_tokenization(tokenizer):
    movetext = "1. e4 e5 2. Nf3 Nc6"
    tokens = tokenizer.tokenize(movetext)
    assert tokens == ["1.", "e4", "e5", "2.", "Nf3", "Nc6"]


def test_tokenization_with_comments(tokenizer):
    movetext = "1. e4 {Good move} e5 2. Nf3 {Developing knight} Nc6"
    tokens = tokenizer.tokenize(movetext)
    assert tokens == ["1.", "e4", "{Good move}", "e5", "2.", "Nf3", "{Developing knight}", "Nc6"]


def test_tokenization_with_variations(tokenizer):
    movetext = "1. e4 e5 2. Nf3 (2. f4 exf4 3. Bc4) 2... Nc6"
    tokens = tokenizer.tokenize(movetext)
    assert tokens == ["1.", "e4", "e5", "2.", "Nf3", "(2. f4 exf4 3. Bc4)", "2...", "Nc6"]


def test_tokenization_with_nested_variations(tokenizer):
    movetext = "1. e4 e5 2. Nf3 (2. f4 exf4 3. Bc4 (3. Nf3 g5 4. h4)) 2... Nc6"
    tokens = tokenizer.tokenize(movetext)
    assert tokens == ["1.", "e4", "e5", "2.", "Nf3", "(2. f4 exf4 3. Bc4 (3. Nf3 g5 4. h4))", "2...", "Nc6"]


def test_tokenization_with_result(tokenizer):
    movetext = "1. e4 e5 2. Nf3 Nc6 1-0"
    tokens = tokenizer.tokenize(movetext)
    assert tokens == ["1.", "e4", "e5", "2.", "Nf3", "Nc6", "1-0"]


def test_tokenization_with_annotations(tokenizer):
    movetext = "1. e4! e5? 2. Nf3!! Nc6??"
    tokens = tokenizer.tokenize(movetext)
    assert tokens == ["1.", "e4!", "e5?", "2.", "Nf3!!", "Nc6??"]


def test_tokenization_with_numeric_annotations(tokenizer):
    movetext = "1. e4 $1 e5 $2 2. Nf3 $3 Nc6 $4"
    tokens = tokenizer.tokenize(movetext)
    assert tokens == ["1.", "e4", "$1", "e5", "$2", "2.", "Nf3", "$3", "Nc6", "$4"]


def test_tokenization_with_multiline_comments(tokenizer):
    movetext = """1. e4 {This is a
multiline comment
spanning several lines} e5"""
    tokens = tokenizer.tokenize(movetext)
    assert tokens == ["1.", "e4", "{This is a\nmultiline comment\nspanning several lines}", "e5"]


def test_tokenization_with_multiple_spaces(tokenizer):
    movetext = "1.  e4    e5   2. Nf3    Nc6"
    tokens = tokenizer.tokenize(movetext)
    assert tokens == ["1.", "e4", "e5", "2.", "Nf3", "Nc6"]


def test_tokenization_empty_movetext(tokenizer):
    movetext = ""
    tokens = tokenizer.tokenize(movetext)
    assert tokens == []


def test_tokenization_only_comments(tokenizer):
    movetext = "{Starting comment} {Another comment}"
    tokens = tokenizer.tokenize(movetext)
    assert tokens == ["{Starting comment}", "{Another comment}"]


def test_tokenization_with_castling(tokenizer):
    movetext = "1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. O-O O-O"
    tokens = tokenizer.tokenize(movetext)
    assert tokens == ["1.", "e4", "e5", "2.", "Nf3", "Nc6", "3.", "Bc4", "Bc5", "4.", "O-O", "O-O"]


def test_tokenization_with_pawn_promotion(tokenizer):
    movetext = "1. e4 e5 2. d4 exd4 3. c3 dxc3 4. Bc4 cxb2 5. Bxb2 Nc6 6. Nf3 d6 7. e8=Q+"
    tokens = tokenizer.tokenize(movetext)
    assert "e8=Q+" in tokens


def test_tokenization_with_check_and_mate(tokenizer):
    movetext = "1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6?? 4. Qxf7#"
    tokens = tokenizer.tokenize(movetext)
    assert tokens[-1] == "Qxf7#"
