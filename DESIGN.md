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

    * [strategies](#strategies)

# overview

## game description

The Apple Game, also known as [Fruit Box](https://en.gamesaien.com/game/fruit_box/) or Make10, is a single-player online game. The board consists of a 10 x 17 grid of apples, each labeled with a number between 1 and 9\.

<!-- ![][image1]  
A screenshot from an [online website for Fruit Box](https://en.gamesaien.com/game/fruit_box/) -->

The user can select rectangular portions of the grid by click-and-drag. If the apples within the rectangle sum to 10, then they are cleared from the board. The resulting, empty space counts as 0 within any subsequent selections.
<!-- The image below shows one clearing move: the rectangular selection contains apples numbered 4-2-4, which sum to 10\.

![][image2]  
A screenshot of a possible move from a later stage in the game -->

The user’s final score is the number of apples removed from the board. The user has 2 minutes to consume as many apples as possible, and a timer on the right counts down the remaining time.

## context and motivation

The mechanics of the game mean that moves may not commute. Cleared apples leave empty space behind, so a user’s next move depends on all previous moves.

I’ve played this game for a couple years now, and I’ve developed a couple of empirical heuristics:

- focusing on removing 9’s
- preferring clearing a few apples at a time
- preferring clearing apples on the edges over apples in the center

However, I haven’t verified whether these are actually effective. I’m also curious how much I can improve the score from a baseline greedy algorithm.

## assumptions

In this project, I will focus on a smaller board of 5 x 8\. In the future, I may extend this project to larger versions of the board.

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

Filetree sketch:
```
.
├── README.md
├── DESIGN.md
├── core.py
├── algorithms/
│   ├── base.py
│   ├── bfs.py
│   ├── dfs.py
│   ├── greedy-fewest.py
│   ├── greedy-greatest.py
│   └── random_play.py
├── benchmarks/
│   ├── make_suite.py
│   ├── run_benchmark.py
│   ├── suites/
│   │   └── [json files of benchmark suites]
│   └── results/
│       └── [results of the benchmarks]
└── tests/
    └── test_algorithms.py
```

The main mechanics of the project are in the following files.
| File | Purpose |
| :---- | :---- |
| `core.py` | constants for board size Board class Tracks current state, current score, sum of remaining apples Move class Holds coordinates for the top left and bottom right corners of a rectangular selection Ordered such that we can sort moves chronologically Encoding boards and moves Board generation Verifying moves Applying moves |
| `algorithms/ base.py` | algorithm class |
| `algorithms/..` | specifications of algorithms |


## strategies

BFS is optimal, so it will give us our best possible score. We use it on a small board (3 x 5\) for some initial context on other algorithms’ performance. Of course, BFS will be too inefficient to run on larger grids, such as the game’s original 10 x 17 grid or our planned 5 x 8 grid.

| option | algorithm |
| :---- | :---- |
| BFS | standard breadth-first search |
| DFS | standard depth-first search |
| greedy (fewest apples) | take a valid move that clears the fewest apples Break ties by choosing a move with the smallest rectangular selection by area Break ties by choosing the move whose upper left corner of the rectangle comes first in the grid |
| greedy (greatest apples) | take a valid move that clears the most apples Break ties by choosing a move with the largest rectangular selection by area Break ties by choosing the move whose upper left corner of the rectangle comes first in the grid |
| random | choose a random move out of all possible moves |


