"""Unit tests for apple_search.core"""

import dataclasses 

import numpy as np
import pytest

from apple_search.core import NUM_COLS, NUM_ROWS, TARGET, Board, Move, is_legal


############ HELPERS AND FIXTURES ############
def board_from_rows(*rows: str) -> Board:
    """Build a Board from digit strings, one per row ('0' = empty). Test-only helper."""
    assert len({len(row) for row in rows}) == 1, "rows must have equal length"
    cells = tuple(int(ch) for row in rows for ch in row)
    return Board(cells, rows=len(rows), cols=len(rows[0]))


@pytest.fixture
def fresh_board() -> Board:
    """A full 5x8 board as the generator would produce it: values 1-9, total 180."""
    return board_from_rows(
        "91462835",
        "73526419",
        "28173364",
        "55924182",
        "36287414",
    )


@pytest.fixture
def mid_game_board() -> Board:
    """fresh_board after five real moves: (0,0)-(0,1) 9+1, (0,2)-(0,3) 4+6,
    (1,0)-(1,1) 7+3, (1,4)-(1,5) 6+4, (3,0)-(3,1) 5+5. Reachable by legal play.

    Rows 1-2, cols 5-6 hold [_ 1 / 3 6]: a tight move that is only legal because
    the cleared cell at (1,5) counts as 0.
    """
    return board_from_rows(
        "00002835",
        "00520019",
        "28173364",
        "00924182",
        "36287414",
    )


@pytest.fixture
def last_pair_board() -> Board:
    """A nearly cleared 5x8 board: only a 3 in the top-left and a 7 in the bottom-right."""
    return board_from_rows(
        "30000000",
        "00000000",
        "00000000",
        "00000000",
        "00000007",
    )


@pytest.fixture
def cleared_board() -> Board:
    """A fully cleared 5x8 board."""
    return Board((0,) * (NUM_ROWS * NUM_COLS))


############ MOVE ############
# The project relies on moves deduplicating in sets and sorting in a fixed order.
def test_duplicate_moves_collapse_in_a_set():
    moves = {Move(0, 0, 0, 1), Move(1, 3, 2, 3), Move(0, 0, 0, 1)}
    assert moves == {Move(0, 0, 0, 1), Move(1, 3, 2, 3)}


def test_moves_sort_by_r0_then_c0_then_r1_then_c1():
    unsorted = [Move(2, 0, 2, 1), Move(0, 4, 0, 5), Move(0, 0, 1, 0), Move(0, 0, 0, 1)]
    assert sorted(unsorted) == [
        Move(0, 0, 0, 1),
        Move(0, 0, 1, 0),
        Move(0, 4, 0, 5),
        Move(2, 0, 2, 1),
    ]


############ BOARD CONSTRUCTION ############
# The shape defaults to 5x8, and the cell count must match the shape.
def test_board_defaults_to_five_by_eight_when_shape_omitted(fresh_board):
    board = Board(fresh_board.cells)
    assert (board.rows, board.cols) == (5, 8)


@pytest.mark.parametrize(
    "cells",
    [
        pytest.param((9, 1) * 19, id="38_cells_one_short"),
        pytest.param((9, 1) * 21, id="42_cells_two_over"),
    ],
)
def test_board_rejects_cell_count_not_matching_shape(cells):
    with pytest.raises(ValueError, match="expected 40 cells"):
        Board(cells)


# Values just outside 0 to TARGET-1. A negative value would also break the lister's early exit
# on sums above TARGET. (0 and TARGET-1 are accepted: every fixture board relies on both.)
@pytest.mark.parametrize(
    "bad_value", [pytest.param(TARGET+1, id="target+1"), pytest.param(-1, id="negative_one")]
)
def test_board_rejects_cell_values_outside_zero_to_target(fresh_board, bad_value):
    cells = fresh_board.cells[:17] + (bad_value,) + fresh_board.cells[18:]
    with pytest.raises(ValueError, match="index 17"):
        Board(cells)


############ BOARD EQUALITY AND HASHING ############
# The exhaustive search memoizes on the board, so equality must mean "same position"
# and boards must be usable as dict keys.
def test_board_works_as_memo_dict_key(fresh_board, mid_game_board):
    memo = {fresh_board: 32, mid_game_board: 21}
    assert memo[Board(fresh_board.cells)] == 32
    assert memo[Board(mid_game_board.cells)] == 21


def test_boards_with_same_cells_but_transposed_shape_are_not_equal():
    # Same flat tuple, different geometry: a 1x2 strip vs a 2x1 column.
    assert Board((1, 9), rows=1, cols=2) != Board((1, 9), rows=2, cols=1)


@pytest.mark.xfail(
    strict=True,
    reason="Board accepts a list for cells, which makes it unhashable and breaks the memo. "
    "Convert to tuple in __post_init__ (object.__setattr__) or reject non-tuples.",
)
def test_board_built_from_list_is_hashable(fresh_board):
    board = Board(list(fresh_board.cells))  # type: ignore[arg-type]
    hash(board)


############ BOARD.AT ############
# at(r, c) reads row-major cells and returns None outside the grid, including the
# cases where the flat index would silently wrap into the neighbouring row.
@pytest.mark.parametrize(
    "r, c, expected",
    [
        pytest.param(0, 0, 9, id="top_left"),
        pytest.param(0, 7, 5, id="top_right"),
        pytest.param(4, 0, 3, id="bottom_left"),
        pytest.param(4, 7, 4, id="bottom_right"),
    ],
)
def test_at_reads_all_four_corners(fresh_board, r, c, expected):
    assert fresh_board.at(r, c) == expected


def test_at_returns_zero_for_cleared_cell(mid_game_board):
    assert mid_game_board.at(0, 0) == 0


@pytest.mark.parametrize(
    "r, c",
    [
        pytest.param(-1, 0, id="row_minus_one"),
        pytest.param(0, -1, id="col_minus_one"),
        pytest.param(5, 0, id="row_equals_rows"),
        pytest.param(0, 8, id="col_equals_cols_would_wrap_to_next_row"),
        pytest.param(4, 8, id="col_equals_cols_on_last_row"),
        pytest.param(100, 100, id="far_outside"),
    ],
)
def test_at_returns_none_outside_grid(fresh_board, r, c):
    # Negative indices must not fall through to Python's from-the-end indexing, and
    # c == cols must not read cell (r + 1, 0).
    assert fresh_board.at(r, c) is None


############ BOARD.REMAINING AND BOARD.TOTAL ############
# remaining() counts apples (nonzero cells); total() sums values.
def test_remaining_skips_cleared_cells(mid_game_board):
    assert mid_game_board.remaining() == 30


def test_remaining_is_zero_on_cleared_board(cleared_board):
    assert cleared_board.remaining() == 0


def test_total_sums_all_values_on_fresh_board(fresh_board):
    assert fresh_board.total() == 180


############ BOARD.SELECTION ############
# selection(r0, c0, r1, c1) returns the inclusive rectangle as a 2-D numpy array.
def test_selection_returns_inclusive_rectangle_as_2d_array(fresh_board):
    sel = fresh_board.selection(1, 2, 2, 4)
    assert isinstance(sel, np.ndarray)
    np.testing.assert_array_equal(sel, [[5, 2, 6], [1, 7, 3]])


def test_selection_of_single_cell_keeps_shape_one_by_one(fresh_board):
    # Guards against the array being squeezed to a scalar or 1-D shape.
    sel = fresh_board.selection(3, 2, 3, 2)
    assert sel.shape == (1, 1)
    assert sel[0, 0] == 9


def test_selection_includes_cleared_cells_as_zero(mid_game_board):
    np.testing.assert_array_equal(mid_game_board.selection(1, 5, 2, 6), [[0, 1], [3, 6]])


@pytest.mark.parametrize(
    "r0, c0, r1, c1",
    [
        pytest.param(0, 6, 0, 9, id="past_right_edge"),
        pytest.param(3, 2, 2, 2, id="rows_swapped"),
    ],
)
def test_selection_raises_for_invalid_rectangle(fresh_board, r0, c0, r1, c1):
    # Without the check these returned a None-padded array and an empty array.
    with pytest.raises(ValueError, match="invalid rectangle"):
        fresh_board.selection(r0, c0, r1, c1)


############ BOARD.CONTAINS_RECT ############
# Corner order is tested here directly; bounds are covered through is_legal below, whose
# out-of-bounds tests fail if contains_rect lets a bad rectangle reach selection.
@pytest.mark.parametrize(
    "r0, c0, r1, c1",
    [
        pytest.param(0, 1, 0, 0, id="columns_swapped"),
        pytest.param(3, 2, 2, 2, id="rows_swapped"),
    ],
)
def test_contains_rect_rejects_swapped_corners(fresh_board, r0, c0, r1, c1):
    assert fresh_board.contains_rect(r0, c0, r1, c1) is False


def test_contains_rect_accepts_whole_board(fresh_board):
    assert fresh_board.contains_rect(0, 0, 4, 7) is True


############ IS_LEGAL: LEGAL RECTANGLES ############
# In-bounds rectangles whose remaining apples sum to exactly 10.
@pytest.mark.parametrize(
    "r0, c0, r1, c1",
    [
        pytest.param(0, 0, 0, 1, id="horizontal_9_1"),
        pytest.param(2, 2, 3, 2, id="vertical_1_over_9"),
    ],
)
def test_is_legal_accepts_pair_summing_to_ten(fresh_board, r0, c0, r1, c1):
    assert is_legal(fresh_board, r0, c0, r1, c1) is True


def test_is_legal_accepts_two_by_two_block():
    board = board_from_rows(
        "2359",
        "4169",
    )
    assert is_legal(board, 0, 0, 1, 1) is True  # 2 + 3 + 4 + 1 = 10


def test_is_legal_accepts_rectangle_spanning_cleared_cells(mid_game_board):
    # [_ 1 / 3 6]: a tight box around three apples, legal because (1,5) counts as 0.
    assert is_legal(mid_game_board, 1, 5, 2, 6) is True


def test_is_legal_accepts_loose_rectangle_around_a_legal_move(mid_game_board):
    # Row 0, cols 0-5 adds only cleared cells to the 2+8 move at (0,4)-(0,5). is_legal
    # checks the drawn rectangle; shrinking it to the tight box is canonicalization's job.
    assert is_legal(mid_game_board, 0, 0, 0, 5) is True


def test_is_legal_accepts_whole_board_when_last_apples_sum_to_ten(last_pair_board):
    assert is_legal(last_pair_board, 0, 0, 4, 7) is True


def test_is_legal_returns_builtin_bool_not_numpy_bool(fresh_board):
    # np.bool_ fails `is True` checks and some JSON encoders; core.py casts on purpose.
    assert type(is_legal(fresh_board, 0, 0, 0, 1)) is bool
    assert type(is_legal(fresh_board, 0, 0, 0, 2)) is bool


############ IS_LEGAL: IN-BOUNDS BUT NOT LEGAL ############
# Sums just either side of 10, and rectangles that hold too few apples to reach it.
@pytest.mark.parametrize(
    "r0, c0, r1, c1",
    [
        pytest.param(1, 3, 2, 3, id="vertical_2_7_sums_to_9"),
        pytest.param(2, 4, 3, 5, id="square_sums_to_11"),
    ],
)
def test_is_legal_rejects_sum_just_off_ten(fresh_board, r0, c0, r1, c1):
    assert is_legal(fresh_board, r0, c0, r1, c1) is False


def test_is_legal_rejects_single_apple(fresh_board):
    # A single apple is at most 9, so it can never reach 10.
    assert is_legal(fresh_board, 0, 0, 0, 0) is False


def test_is_legal_rejects_rectangle_of_only_cleared_cells(mid_game_board):
    assert is_legal(mid_game_board, 0, 0, 0, 3) is False


############ IS_LEGAL: OUT OF BOUNDS ############
# Rectangles that leave the grid must return False rather than raising, even when their
# in-bounds part sums to 10.
@pytest.mark.parametrize(
    "r0, c0, r1, c1",
    [
        pytest.param(-1, 0, 0, 1, id="r0_negative"),
        pytest.param(0, -1, 0, 1, id="c0_negative"),
        pytest.param(0, 0, 5, 1, id="r1_equals_rows"),
        pytest.param(0, 0, 0, 8, id="c1_equals_cols"),
        pytest.param(0, 0, 99, 99, id="far_past_bottom_right"),
    ],
)
def test_is_legal_rejects_out_of_bounds_rectangle_containing_a_legal_pair(
    fresh_board, r0, c0, r1, c1
):
    # Each rectangle's in-bounds part includes the 9-1 pair at (0,0)-(0,1).
    assert is_legal(fresh_board, r0, c0, r1, c1) is False