from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

############ CONSTANTS ############
TARGET = 10  # > 1
NUM_ROWS = 5
NUM_COLS = 8


############ CLASSES ############
@dataclass(order=True, frozen=True, slots=True)
class Move:
    """
    Records a canonical move by the coordinates of top left, bottom right corners
    """

    r0: int
    c0: int
    r1: int
    c1: int


@dataclass(frozen=True, slots=True)
class Board:
    """
    Records one board configuration
    """

    cells: tuple[int, ...]  # 0 indicates an empty cell
    rows: int = NUM_ROWS
    cols: int = NUM_COLS

    def __post_init__(self):
        if len(self.cells) != self.rows * self.cols:
            raise ValueError(f"expected {self.rows * self.cols} cells for {self.rows}x{self.cols}, got {len(self.cells)}")
        for i in range(len(self.cells)):
            if self.cells[i] < 0 or self.cells[i] >= TARGET:
                raise ValueError(f"Cell value out of bounds: {self.cells[i]} at index {i}")

    def at(self, r: int, c: int) -> int | None:
        """Retrieves the value at r, c of the board"""
        if (0 <= r and r < self.rows) and (0 <= c and c < self.cols):
            return self.cells[r * self.cols + c]
        else:
            return None

    def remaining(self) -> int:
        """Retrieves number of remaining cells"""
        nonzeros = [1 for num in self.cells if num > 0]
        return sum(nonzeros)

    def total(self) -> int:
        """Retrieves sum of the board's cells"""
        return sum(self.cells)

    def contains_rect(self, r0: int, c0: int, r1: int, c1: int) -> bool:
        """True iff the corners are ordered and the rectangle lies inside the board."""
        return (r0 <= r1 and c0 <= c1) and (r0 >= 0 and r1 < self.rows and c0 >= 0 and c1 < self.cols)

    def selection(self, r0: int, c0: int, r1: int, c1: int) -> npt.NDArray:
        """Retrieves selection (top left, bottom right corners) as a list. Raises error if out of bounds."""
        if not self.contains_rect(r0, c0, r1, c1):
            raise ValueError(f"invalid rectangle ({r0},{c0})-({r1},{c1}) on {self.rows}x{self.cols}")
        res = []
        for r in range(r0, r1 + 1):
            row = []
            for c in range(c0, c1 + 1):
                row.append(self.at(r, c))
            res.append(row)
        return np.array(res)


############ FUNCTIONS ############
def is_legal(board: Board, r0: int, c0: int, r1: int, c1: int) -> bool:
    """Returns True iff the move is in bounds and its apples sum to TARGET"""
    return (
        board.contains_rect(r0, c0, r1, c1)
        and bool(np.sum(board.selection(r0, c0, r1, c1)) == TARGET)  # casts np.bool -> bool
    )


########################

if __name__ == "__main__":
    pass
