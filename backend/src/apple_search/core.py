import random
from dataclasses import dataclass

############ CONSTANTS ############
TARGET = 10 # > 1
NUM_ROWS = 5
NUM_COLS = 8

############ CLASSES ############
@dataclass(frozen=True, slots=True)
class Board:
    """
    Records one board configuration
    """
    cells: tuple[int, ...] # 0 indicates an empty cell
    rows: int = NUM_ROWS
    cols: int = NUM_COLS

    def at(self, r, c):
        """ Retrieves the value at r, c of the board """
        return self.cells[r * self.cols + c]

    def remaining(self):
            """ Retrieves number of remaining cells """
            return None
    
    def total(self):
        """ Retrieves sum of the board's cells """
        return None

    
@dataclass(order=True, frozen=True, slots=True)
class Move:
    """
    Records a single move by the coordinates of two opposite corners
    """
    r0: int
    c0: int
    r1: int
    c1: int

############ FUNCTIONS ############

###### Encoding ######
# Board -> str
def board_to_str(board: Board) -> str:
    """ Converts a Board instance into a string for easy storage
    Format: ROWSxCOLS.CELL,CELL,CELL,...
    
    Example input: board = Board((1, 4, 9, 3, 8, 0), rows=2, cols=3)
        This is a 2 x 3 board with values
        1 4 9
        3 8 0
    
    Expected output: board_to_str(board) = "2x3.1,4,9,3,8,0"
    """
    size = str(board.rows) + "x" + str(board.cols)
    cells = ",".join(map(str, board.cells))
    return size + "." + cells

# str -> Board
def str_to_board(code: str) -> Board:
    size, cells = code.split(".")
    rows, cols = size.split("x")
    cells = tuple(int(cell) for cell in cells.split(","))
    
    return Board(cells, int(rows), int(cols))

# list[Move] -> str
def sequence_to_str(moves: list[Move]) -> str:
    return "hi"

# str -> Sequence[Move]
def str_to_sequence(seq: str) -> list[Move]:
    return [Move(1, 1, 1, 1)]

# Board generation
def generate_board(rows=NUM_ROWS, cols=NUM_COLS) -> Board:
    """
    Generates a random board of rows x columns integers.
    Each integer is uniform random between 1 and TARGET - 1
    All numbers sum to multiple of 10
    """
    cells = []
    

    return Board(cells, rows, cols)


if __name__ == "main":
    board = Board((1, 4, 9, 3, 8, 0), rows=2, cols=3)
    print(board_to_str(board))