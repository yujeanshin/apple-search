import random
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass

############ CONSTANTS ############
TARGET = 10  # > 1
NUM_ROWS = 5
NUM_COLS = 8

############ CLASSES ############
@dataclass(order=True, frozen=True, slots=True)
class Move:
    """
    Records a single move by the coordinates of top left, bottom right corners
    """
    r0: int
    c0: int
    r1: int
    c1: int

    def __post_init__(self):
        assert self.r0 <= self.r1 and self.c0 <= self.c1

dataclass(frozen=True, slots=True)
class Board:
    """
    Records one board configuration
    """
    cells: tuple[int, ...] # 0 indicates an empty cell
    rows: int = NUM_ROWS
    cols: int = NUM_COLS

    def __post_init__(self):
        assert len(self.cells) == self.rows * self.cols

    def at(self, r, c):
        """ Retrieves the value at r, c of the board """
        return self.cells[r * self.cols + c]

    def remaining(self):
        """ Retrieves number of remaining cells """
        nonzeros = [1 for num in self.cells if num > 0]
        return sum(nonzeros)
    
    def total(self):
        """ Retrieves sum of the board's cells """
        return sum(self.cells)

    def selection(self, move: Move) -> npt.NDArray:
        """ Retrieves selection as a list """
        res = []
        for r in range(move.r0, move.r1 + 1):
            row = []
            for c in range(move.c0, move.c1 + 1):
                row.append(self.at(r, c))
            res.append(row)
        return np.array(res)
            

############ FUNCTIONS ############




########################

if __name__ == "__main__":
    pass