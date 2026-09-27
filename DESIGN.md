# apple game search - design doc

**last updated**: Sun. 9/27/26  
**status**: Draft
**author**: Yujean Shin

**summary**: Evaluating various algorithms for playing the Apple Game.

* [**overview**](#overview)

    * [game description](#game-description)
    * [context and motivation](#context-and-motivation)
    * [assumptions](#assumptions)
    * [goals](#goals)
    * [non-goals](#non-goals)

* [**design and implementation**](#heading=h.dqe41xqxxwm4)

    * [structure](#structure)

    * [detailed design](#detailed-design)
        * [core.py](#corepy)
        * [algorithms/](#algorithms)
        * [evals/](#evals)
        * [tests/](#tests)

# overview

## game description

The Apple Game, also known as [Fruit Box](https://en.gamesaien.com/game/fruit_box/) or Make10, is a single-player online game. The board consists of a 10 x 17 grid of apples, each labeled with a number between 1 and 9\.

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
- preferring clearing apples that have fewer selection options

However, I haven’t verified whether these are actually effective. I’m also curious how much I can improve the score from a baseline greedy algorithm.

## assumptions

In this project, I will focus on a smaller board of 6 x 10\. In the future, I will extend this project to larger versions of the board.

The exact setup of the game is unclear since the game’s code is not publicly available. I make the following assumptions:

- Numbers are uniformly distributed, and  
- All apples initially sum to a multiple of 10\.

As such, I will construct each board by

- Generating apples, each equally likely to be an integer between 1 and 9, and  
- Repeating this generation until I get a board that sums to a multiple of 10\.

## goals

- create random boards  
- check that moves are valid  
- implement algorithms for solving small boards  
- establish a greedy baseline  
- build an evaluation pipeline

## non-goals

The following could be interesting avenues to explore but are not the focus of this iteration of the project.

- finding the best score for a given board  
- expanding to 10 x 17 boards (does this change relative performance of the algorithms?)  
- constraining algorithms to a time limit  
- building a UI to view different algorithms in progress  
- building a UI for users to try the game themselves

# design and implementation

## Structure

```
filetree sketch:
.
├── README.md
├── DESIGN.md
├── core.py
├── algorithms/
│   ├── base.py
│   ├── exhaustive.py
│   ├── greedy-fewest.py
│   ├── greedy-greatest.py
│   └── random_play.py
├── evals/
│   ├── make_suite.py
│   ├── run_benchmark.py
│   ├── suites/
│   │   └── [json files of benchmark suites]
│   └── results/
│       └── [json files of the benchmarks]
└── tests/
    └── test_algorithms.py
```

## detailed design
### core.py
This file contains core components of the game.
- `Board` class to track board state
- random board generation
- `Move` class to hold a legal move, with as tight a selection as possible
- `Sequence` class to hold sequences of moves in chronological order
- board and move str encoding
- move verifiaction and application


### algorithms/
`base.py` stores the algorithm class. The other files in this folder store the specifics of other algorithms.

`exhaustive.py`: The baseline is an exhaustive search with DFS that finds the best score for a given board. This is a reference for comparison with other search methods.

We define a board's (best) score as max(apples cleared by a move, best score of the resulting board) over its legal moves. A board with no legal moves has a score of 0. We find board scores recursively. To avoid redundant computation, we store each board position we reach and reuse answers where possible.

Other initial strategies we want to implement are
| option | algorithm |
| :---- | :---- |
| random | Choose a random legal move until there are no legal removes remaining. |
| greedy (fewest apples) | take a valid move that clears the fewest apples <br> break ties by choosing a move with the smallest rectangular selection by area <br> break ties by choosing a random legal move |
| greedy (greatest apples) | take a valid move that clears the most apples <br> break ties by choosing a move with the largest rectangular selection by area  <br> break ties by choosing a random move |

Deterministic algorithms are only conducted once for a given board. Stochastic algorithms run 5 times for a given board, and we take the max score.

### evals/

`make_suite.py`: Create suites of randomly generated boards to standardize algorithm evaluation. We use 200 boards as the default.

To reproduce results, we store suites in `./benchmarks/suites/` as .json files. 

`run_benchmark.py`: Calculates an algorithm's score, fraction of optimal score, and time elapsed for each board in a benchmark suite. To keep a record of results, we store results in `./benchmarks/results` as json files.

### tests/

