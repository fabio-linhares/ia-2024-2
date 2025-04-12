# A* Algorithm Report

## Overview

This report details the performance of the A* search algorithm in finding the shortest path between cities.

## Algorithm Description

A* is an informed search algorithm that uses a heuristic to guide its search. It combines the actual cost from the start node to the current node (g(n)) and the estimated cost from the current node to the goal node (h(n)).

## Performance Analysis

- **Completeness:** A* is complete if the heuristic is admissible (never overestimates the cost to reach the goal).
- **Optimality:** A* is optimal if the heuristic is admissible.
- **Complexity:**
    - Time: O(b^d) in the worst case, but typically much faster with a good heuristic.
    - Space: O(b^d), where b is the branching factor and d is the depth of the solution.

## Results

| Scenario | Start City | End City | Radius (r) | Path Found | Distance |
|----------|------------|----------|------------|------------|----------|
| 1        | New York   | Boston   | 2.0        | Yes        | 1.85     |
| 2        | Chicago    | San Francisco | 5.0        | Yes        | 23.78    |
| 3        | New York   | Los Angeles | 1.0        | No         | N/A      |

## Conclusion

A* is an efficient algorithm for finding the shortest path, especially when a good heuristic is available.