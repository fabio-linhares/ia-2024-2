# BFS Algorithm Report

## Overview

This report details the performance of the Breadth-First Search (BFS) algorithm in finding the shortest path between cities.

## Algorithm Description

BFS explores all the neighbor nodes at the present depth prior to moving on to the nodes at the next depth level.

## Performance Analysis

- **Completeness:** BFS is complete, meaning it will find a solution if one exists.
- **Optimality:** BFS finds the shortest path in terms of the number of edges, but not necessarily the shortest distance.
- **Complexity:**
    - Time: O(V + E), where V is the number of vertices (cities) and E is the number of edges (roads).
    - Space: O(V), as it needs to store all visited nodes.

## Results

| Scenario | Start City | End City | Radius (r) | Path Found | Distance |
|----------|------------|----------|------------|------------|----------|
| 1        | New York   | Boston   | 2.0        | Yes        | 1.85     |
| 2        | Chicago    | San Francisco | 5.0        | Yes        | 23.78    |
| 3        | New York   | Los Angeles | 1.0        | No         | N/A      |

## Conclusion

BFS is a reliable algorithm for finding paths but may not be the most efficient for large graphs or when the shortest distance is required.