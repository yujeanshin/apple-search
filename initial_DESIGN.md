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

The user can select rectangular portions of the grid by click-and-drag. If the apples within the rectangle sum to 10, then they are cleared from the board. The resulting, empty space counts as 0 within any subsequent selections.
<!-- The image below shows one clearing move: the rectangular selection contains apples numbered 4-2-4, which sum to 10\.

![][image2]  
A screenshot of a possible move from a later stage in the game -->

The user has 2 minutes to consume as many apples as possible, and a timer on the right counts down the remaining time. The user’s final score is the number of apples removed from the board. The game ends when the timer runs out or when there are no legal moves remaining.

## context and motivation

The mechanics of the game mean that moves may not commute. Cleared apples leave empty space behind, so a user’s next move depends on all previous moves.

I’ve played this game for a couple years now, and I’ve developed a couple of empirical heuristics:

- focusing on removing 9’s
- preferring clearing a few apples at a time
- preferring clearing apples that have fewer selection options (e.g., on the corners or edges of the initial board)

However, I haven’t verified whether these are actually effective. I want to examine these heuristics more rigorously and improve my own strategies.

## assumptions

In this project, I focus on a smaller board of 5 x 8\. I want to compare algorithms against the optimal score; this board size should be small enough to perform an exhaustive search for the optimal score. In the future, I will extend this project to larger versions of the board.

The exact setup of the game is unclear since the game’s code is not publicly available. I make the following assumptions:

- Numbers are uniformly distributed, and  
- All apples initially sum to a multiple of 10\.

As such, I construct each board by

- Generating apples, each equally likely to be an integer between 1 and 9, and  
- Repeating this generation until I get a board that sums to a multiple of 10\.

## goals

- create random boards  
- check that moves are valid
- implement an exhaustive search for the optimal score
- implement algorithms for solving small boards
- build an evaluation pipeline
- ***evaluate the strengths and weaknesses of various algorithms***

## non-goals

The following could be interesting avenues to explore but are not the focus of this iteration of the project.

- optimums for larger boards. We use an exhaustive search to find the optimum in smaller boards as a measuring tool. Finding the optimum is not the research question here.
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
│   └── constrained_first.py
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
- random board generation
- ***str encoding of boards***
- move verification
- move application
- ***efficient identification of all possible moves*** for a board
- game end detection
- current score calculation

More detail on a few items:

> *What is a **"(legal) move"**?*
> 
> First, we define a *move*. Moves are a subset of selections. A selection is any rectangular slice of the board. A corresponding *move* is the smallest selection that contains the same apples; i.e., a move wraps the apples it contains as tightly as possible.
> We use this definition to avoid duplication. Cleared apples leave empty space behind, so multiple selections on a board may map to the same move.
> 
> A *legal* move is a move containing apples that sum to 10. When we say "move", we mean a legal move unless otherwise specified.

> *Why do we have **string encodings of boards**?*
> 
> This is mostly for debugging purposes. If I want to test a specific board, it's easy to copy and paste a one-line string representation.

> *How do we **efficiently** identify all moves for a given board?*
> 
> work in progress..


### algorithms/
`base.py`: stores the algorithm class. The other files in this folder store the specifics of other algorithms.

`exhaustive.py`: an exhaustive search with DFS that finds the best score for a given board. This is a reference for comparison with other search methods.

We define a board's (best) score as max(apples cleared by a move + best score of the resulting board) over its legal moves. A board with no legal moves has a score of 0. We find board scores recursively. To avoid redundant computation, we store each board position we reach and reuse answers where possible.

Other initial strategies we want to implement are
| option | algorithm |
| :---- | :---- 
| random | Choose a random legal move until there are no legal moves remaining. |
| move_fewest | Choose a move that clears the fewest apples. |
| move_most | Choose a move that clears the most apples. |
| large_nums | Choose a move with the largest max number. |
| constrained_first | Count the number of legal moves that include each apple. <br> Sort each move's apple counts from lowest to highest. <br> Choose a move with the most constrained apples. When comparing moves with different numbers of apples, only consider the first $\text{min(number of apples in a move)}$ apples. |
We break ties by random choice.


### evals/

`make_suite.py`: creates suites of randomly generated boards to standardize algorithm evaluation

We make suites of ~20 boards for debugging purposes; these results are not stored.

We use [some number that will be determined later] number of boards for the main evaluations. We store suites of boards and corresponding optimums and in `./evals/suites/` as .json files.

`run_benchmark.py`: runs algorithms on a benchmark suite. We use a derived seed for each {suite, board, algorithm, trial} combination. We calculate an algorithm's score, difference from the optimal score, and time elapsed for each board in a benchmark suite. We compute the total score here, but validity of moves is checked in `core.py`.

The (deterministic) exhaustive algorithm is conducted once for each board. We run $n$ trials of stochastic algorithms per board and record the mean and stdev for each metric. We also estimate the "best of $k$ trials" score for $k\leq n$ from those $n$ trials. ($n$ is undetermined as of writing this initial design doc because I'm not sure what statistical tests to use.)

We do comparisons with the random algorithm to test the hypothesis associated with each algorithm.
1. move_fewest vs. random
2. move_most vs. random
3. large_nums vs. random
4. constrained_first vs. random
I also anticipate move_fewest, large_nums, and constrained_first to prioritize similar moves. In particular, large_nums prioritizes 9-1 combinations, which overlaps with move_fewest. We will conduct ablation for these algorithms, as follows:
5. 


We store results and random seeds in `./evals/results` as json files.

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
- score is $\leq$ the optimal score
- produces same result given the same seed

`test_exhaustive.py`: tests the exhaustive algorithm. We conduct an unmemoized search on small boards to verify our memoized, exhaustive search. We also test the exhaustive algorithm on small boards with optimums I calculate by hand.

`test_algorithm.py`: algorithm-specific tests that check individual moves, step-by-step.

(For example, move_fewest should select a move that clears the fewest apples at any given point.)
