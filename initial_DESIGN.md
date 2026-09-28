# apple game search - design doc

**last updated**: sun. 9/27/26  

**status**: draft

**author**: yujean shin

**summary**: evaluating various algorithms for playing the Apple Game.

* [**overview**](#overview)

    * [game description](#game-description)
    * [context and motivation](#context-and-motivation)
    * [assumptions](#assumptions)
    * [goals](#goals)
    * [non-goals](#non-goals)

* [**design and implementation**](#design-and-implementation)

    * [structure](#structure)

    * [detailed design](#detailed-design)
        * [core.py](#corepy)
        * [algorithms/](#algorithms)
        * [evals/](#evals)
        * [tests/](#tests)

# overview

## game description

The Apple Game, a.k.a. [Fruit Box](https://en.gamesaien.com/game/fruit_box/) or Make10, is a single-player online game. The board consists of a 10 x 17 grid of apples, each labeled with a number between 1 and 9\.

<!-- ![][image1]  
A screenshot from an [online website for Fruit Box](https://en.gamesaien.com/game/fruit_box/) -->

The user can select rectangular portions of the grid by click-and-drag. If the apples within the rectangle sum to 10, then they are cleared from the board. Cleared cells stay empty and count as 0 in subsequent selections.
<!-- The image below shows one clearing move: the rectangular selection contains apples numbered 4-2-4, which sum to 10\.

![][image2]  
A screenshot of a possible move from a later stage in the game -->

Players have 2 minutes to clear apples. The user’s final score is the number of apples removed from the board. The game ends when the timer runs out or when there are no legal moves remaining.

## context and motivation

Move order matters because moves may not commute. Cleared apples leave empty space that later moves can span. After a couple years of playing, I’ve developed a three heuristics:

1. focusing on removing 9’s
2. preferring clearing a few apples at a time
3. preferring clearing apples that have fewer selection options (e.g., on the corners or edges of the initial board)

However, I haven’t verified whether these are actually effective. I want to examine these heuristics more rigorously and improve my own strategies.

## assumptions

In this project, I focus on a smaller board of 5 x 8\. I want to compare algorithms against the optimal score; this board size should be small enough to perform an exhaustive search for the optimum. In the future, I will extend this project to larger versions of the board.

The exact setup of the game is unclear since the game’s code is not publicly available. I assume the numbers are uniformly distributed from 1 to 9 and that each board's total is a multiple of 10\.

## goals

- create random boards  
- check that moves are valid
- implement an exhaustive search for the optimal score
- implement algorithms for solving small boards
- build an evaluation pipeline
- ***evaluate the strengths and weaknesses of various algorithms***

## non-goals

The following could be interesting avenues to explore but are not the focus of this iteration of the project.

- optimums for larger boards. Exhaustive search is a measuring tool for smaller boards; finding the optimum is not our current research question.
- expanding to 10 x 17 boards (does this change relative performance of the algorithms?)  
- constraining algorithms to a time limit  
- building a UI to view different algorithms in progress  
- building a UI for users to try the game themselves

# design and implementation

## structure

```
filetree sketch:
.
├── README.md
├── DESIGN.md
├── core.py
├── algorithms/
│   ├── base.py
│   ├── exhaustive.py
│   ├── random_play.py
│   ├── move_fewest.py
│   ├── move_most.py
│   ├── large_nums.py
│   ├── constrained_first.py
│   └── combination.py
├── evals/
│   ├── make_suite.py
│   ├── run_benchmark.py
│   ├── suites/
│   │   └── [json files of benchmark suites]
│   └── results/
│       └── [json files of the benchmarks]
└── tests/
    ├── test_core.py
    ├── test_exhaustive.py
    └── test_algorithm.py
```

## detailed design

### core.py
This file contains core components of the game.
- `Board` class for board configurations
- `Move` class for ***(legal) moves*** (with as tight a selection as possible)
- `Sequence` class to hold sequences of moves in chronological order
- random board generation (we keep drawing until we get a valid board)
- ***str encoding of boards***
- move verification
- move application
- ***efficient identification of all possible moves*** for a board
- game end detection
- current score calculation

More detail on a few items:

> *What is a **"(legal) move"**?*
> 
> A *selection* is any rectangular portion of the board. A corresponding *move* is the smallest selection containing the same apples. Many selections can clear the same apples since they can span empty space. We store only the move, which avoids duplicates.
> 
> A *legal* move is a move containing apples that sum to 10. When we say "move", we mean a legal move unless otherwise specified.

> *Why do we have **string encodings of boards**?*
> 
> for debugging. A board's one-line string can be pasted directly into a test.

> *How do we **efficiently** identify all moves for a given board?*
> 
> TBD.


### algorithms/
`base.py`: stores the algorithm class. The other files in this folder store the specifics of other algorithms.

`exhaustive.py`: an exhaustive search with DFS that finds the optimum of a given board. This is a reference for comparison with other search methods.

We define a board's optimum as max(apples cleared by a move + optimum of the resulting board) over its legal moves. A board with no legal moves has a score of 0. We find board scores recursively. To avoid redundant computation, we store each board position we reach and reuse answers where possible.

Other initial strategies we want to implement are
| option | algorithm |
| :---- | :---- 
| random | Choose a random legal move until there are no legal moves remaining. |
| move_fewest | Choose the move that clears the fewest apples. |
| move_most | Choose the move that clears the most apples. |
| large_nums | Choose the move with the largest numbers. <br> Sort each move's numbers from largest to smallest. Compare only the first 2 apples. |
| constrained_first | Count the number of moves that include each apple. <br> Sort each move's number-of-moves-per-apple counts from lowest to highest. <br> Choose the move with the lowest counts. When comparing moves with different numbers of apples, only consider the $\text{min(number of apples in a move)}$ lowest counts. |
| combination | We do several combinations of algorithms as mentioned in the evals/ section. <br> A combination of algorithms A and B into `A -> B -> random` will first find best moves for A; among those, keep the best under B; and then pick at random.

We break ties by random choice.


### evals/

`make_suite.py`: creates suites of randomly generated boards to standardize algorithm evaluation. We calculate the optimum for each board.

We make suites of ~20 boards for debugging purposes; these results are not stored.

We use [TBD] number of boards for the main evaluations. Suites (boards and corresponding optimums) are stored in `evals/suites/` as .json files.

`run_benchmark.py`: runs algorithms on a benchmark suite. We use a derived seed for each {suite, board, algorithm, trial} combination. We calculate an algorithm's score, difference from the optimal score, and time elapsed for each board in a benchmark suite. We compute the total score here, but validity of moves is checked in `core.py`.

Exhaustive search is deterministic, so it runs once per board. We run $n$ trials of stochastic algorithms per board and record the mean and stdev for each metric. We also estimate the "best of $k$ trials" score for $k\leq n$ from those $n$ trials. ($n$ is undetermined as of writing this initial design doc because I'm not sure what statistical tests to use.)

We test each heuristic against random.
1. move_fewest vs. random
2. move_most vs. random
3. large_nums vs. random
4. constrained_first vs. random

We note that move_fewest, large_nums, and constrained_first often choose the same move. 
For example, large_nums and move_fewest would both prioritize a (9+1) move, since it contains the largest single number and clears the fewest possible apples.
We ablate and compare these algorithms as follows.

5. Does the constraint step improve score? `constrained_first -> large_nums -> random` vs. `large_nums -> random`
6. Does the value step improve score? constrained_first -> `large_nums -> random` vs. `constrained_first -> random`
7. Does the combination beat move_fewest? constrained_first -> `large_nums -> random` vs. `move_fewest -> random`

Our motivation for (7.) is that move_fewest is---anecdotally, for me---the easiest heuristic when playing by hand. I want to see if the added complexity from constrained_first or large_nums improves move_fewest at all.

We store results and random seeds in `evals/results` as json files.

### tests/

`test_core.py`: tests the core gameplay logic in core.py. These include tests for the following areas.

moves:
- detect whether a selection constitutes a legal move
- raise an error for illegal moves
- reduce a large selection into the canonical "move" that wraps the apples tightly
- handle selections and moves containing empty cells
- find all legal moves for a given board

board:
- encodings and decodings both work
- numbers in a board sum to a multiple of 10
- numbers in a board follow an approximately uniform distribution

game:
- remove the correct apples from a board after a move
- return a new board without affecting the old one after a move
- stop at an empty board
- detect and stop when there are no legal moves remaining
- give the correct score from a move sequence

`test_exhaustive.py`: tests the exhaustive algorithm. We conduct an unmemoized search on small boards to verify our memoized, exhaustive search. We also test the exhaustive algorithm on small boards with optimums I calculate by hand.

`test_algorithm.py`: algorithm-specific tests that check
- step-by-step individual moves
    - For example, move_fewest should select a move that clears the fewest apples at any given point.
- score is $\leq$ the optimum
- the same seed produces the same result
