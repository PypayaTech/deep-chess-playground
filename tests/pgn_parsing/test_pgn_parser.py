import io
import pytest
from src.pgn_parsing.pgn_parser import PGNParser


@pytest.fixture
def parser():
    return PGNParser()


def test_parse_headers(parser):
    pgn = '''[Event "Test Event"]
[Site "Test Site"]
[Date "2023.07.21"]
[Round "1"]
[White "Player 1"]
[Black "Player 2"]
[Result "1-0"]
[WhiteElo "2000"]
[BlackElo "1900"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0'''

    stream = io.StringIO(pgn)
    result = parser.parse(stream)
    assert result is not None, "Parser returned None instead of a tuple"

    game_info, moves = result
    expected_game_info = ["Test Event", "Test Site", "2023.07.21", "1", "Player 1", "Player 2", "1-0", "?", "?",
                          "2000", "1900", "?", "?", "?", "?", "?", "?"]
    assert game_info == expected_game_info, f"Mismatch in game_info. Expected: {expected_game_info}, Got: {game_info}"

    expected_moves = "e4 e5 Nf3 Nc6 Bb5"
    assert moves == expected_moves, f"Mismatch in moves. Expected: {expected_moves}, Got: {moves}"


def test_parse_moves(parser):
    pgn = '''[Event "Test Event"]
1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 1-0'''

    stream = io.StringIO(pgn)
    result = parser.parse(stream)
    assert result is not None
    game_info, moves = result

    assert game_info[0] == "Test Event", f"Expected 'Test Event', got {game_info[0]}"
    expected_moves = "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7 Re1 b5 Bb3 d6 c3 O-O"
    assert moves == expected_moves, f"Mismatch in moves. Expected: {expected_moves}, Got: {moves}"


def test_parse_with_comments_and_variations(parser):
    pgn = '''[Event "Test Event"]
1. e4 e5 2. Nf3 {A common move} Nc6 (2... d6 3. d4 {The Philidor Defense}) 3. Bb5 1-0'''

    stream = io.StringIO(pgn)
    result = parser.parse(stream)
    assert result is not None
    game_info, moves = result

    assert game_info[0] == "Test Event", f"Expected 'Test Event', got {game_info[0]}"
    expected_moves = "e4 e5 Nf3 Nc6 Bb5"
    assert moves == expected_moves, f"Mismatch in moves. Expected: {expected_moves}, Got: {moves}"


def test_parse_with_special_moves(parser):
    pgn = '''[Event "Test Event"]
1. e4 e5 2. Nf3 Nc6 3. O-O Nf6 4. d4 exd4 5. e5 Ne4 6. Nxd4 d5 7. f3 Ng5 8. f4 Ne6 9. Nxe6 Bxe6 10. Qd4 1-0'''

    stream = io.StringIO(pgn)
    result = parser.parse(stream)
    assert result is not None
    game_info, moves = result

    assert game_info[0] == "Test Event", f"Expected 'Test Event', got {game_info[0]}"
    expected_moves = "e4 e5 Nf3 Nc6 O-O Nf6 d4 exd4 e5 Ne4 Nxd4 d5 f3 Ng5 f4 Ne6 Nxe6 Bxe6 Qd4"
    assert moves == expected_moves, f"Mismatch in moves. Expected: {expected_moves}, Got: {moves}"


def test_parse_incomplete_game(parser):
    pgn = '''[Event "Test Event"]
1. e4 e5 2. Nf3'''

    stream = io.StringIO(pgn)
    result = parser.parse(stream)
    assert result is not None
    game_info, moves = result

    assert game_info[0] == "Test Event", f"Expected 'Test Event', got {game_info[0]}"
    expected_moves = "e4 e5 Nf3"
    assert moves == expected_moves, f"Mismatch in moves. Expected: {expected_moves}, Got: {moves}"


def test_parse_empty_game(parser):
    pgn = '''[Event "Test Event"]
[Result "*"]

*'''

    stream = io.StringIO(pgn)
    result = parser.parse(stream)
    assert result is not None, "Parser returned None"

    game_info, moves = result
    assert game_info[0] == "Test Event", f"Expected 'Test Event', got {game_info[0]}"
    assert game_info[6] == "*", f"Expected '*', got {game_info[6]}"
    assert moves == "", f"Expected empty string for moves, got {moves}"


def test_parse_game_with_promotions(parser):
    pgn = '''[Event "Test Event"]
1. e4 e5 2. d4 exd4 3. c3 dxc3 4. Bc4 cxb2 5. Bxb2 d6 6. Nf3 Nc6 7. e5 dxe5 8. Qxd8+ Kxd8 9. Ng5 f6 10. Ne6+ Ke8 11. a4 a5 12. h4 h5 13. Nc3 b6 14. O-O-O Bb7 15. Kb1 Rd8 16. g3 Nd4 17. Nxd4 exd4 18. Rxd4 c5 19. Rd7 Rxd7 20. Nxd7 Kxd7 21. f4 Kc6 22. Rc1 Kb7 23. Bd5+ Ka6 24. Rxc5 bxc5 25. Bxg7 c4 26. Bxf6 c3 27. Bxh8 c2+ 28. Kxc2 Nf6 29. Bxf6 Bd6 30. g4 hxg4 31. h5 Bxf4 32. h6 g3 33. h7 g2 34. h8=Q g1=Q 35. Qh6+ Ka7 36. Qxf4 Qg6 37. Qc7+ Ka8 38. Bf7 Qg2+ 39. Kb3 Qf3+ 40. Ka2 Qe2+ 41. Bb2 Qxb2+ 42. Kxb2 1-0'''

    stream = io.StringIO(pgn)
    result = parser.parse(stream)
    assert result is not None
    game_info, moves = result

    assert game_info[0] == "Test Event", f"Expected 'Test Event', got {game_info[0]}"
    assert "h8=Q" in moves, "Expected promotion to Queen (h8=Q) in moves"
    assert "g1=Q" in moves, "Expected promotion to Queen (g1=Q) in moves"


def test_parse_game_with_annotations(parser):
    pgn = '''[Event "Test Event"]
1. e4! e5 2. Nf3 Nc6 3. Bb5 a6?! 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Na5 10. Bc2 c5 11. d4 Qc7 12. Nbd2 cxd4 13. cxd4 Nc6 14. Nb3 a5 15. Be3 a4 16. Nbd2 Bd7?? 17. Rc1 Rfc8 18. Bb1! 1-0'''

    stream = io.StringIO(pgn)
    result = parser.parse(stream)
    assert result is not None
    game_info, moves = result

    assert game_info[0] == "Test Event", f"Expected 'Test Event', got {game_info[0]}"
    expected_moves = "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7 Re1 b5 Bb3 d6 c3 O-O h3 Na5 Bc2 c5 d4 Qc7 Nbd2 cxd4 cxd4 Nc6 Nb3 a5 Be3 a4 Nbd2 Bd7 Rc1 Rfc8 Bb1"
    assert moves == expected_moves, f"Mismatch in moves. Expected: {expected_moves}, Got: {moves}"


def test_parse_game_no_headers(parser):
    pgn = '''1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 1-0'''

    stream = io.StringIO(pgn)
    result = parser.parse(stream)
    assert result is not None
    game_info, moves = result

    # Check that all header fields are '?'
    assert all(info == '?' for info in game_info), f"Expected all '?' in game_info, got {game_info}"

    expected_moves = "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7"
    assert moves == expected_moves, f"Mismatch in moves. Expected: {expected_moves}, Got: {moves}"


if __name__ == "__main__":
    pytest.main()
