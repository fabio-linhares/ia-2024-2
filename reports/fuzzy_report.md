# Fuzzy Search Algorithm Report

## Overview

This report details the performance of the Fuzzy Search algorithm in finding paths between cities, allowing for partial connections.

## Algorithm Description

The Fuzzy Search algorithm uses fuzzy logic to determine the degree of connection between cities based on distance and a membership function.

## Performance Analysis

- **Completeness:** Fuzzy Search may find paths even when traditional algorithms fail, but it depends on the membership function and threshold.
- **Optimality:** Fuzzy Search does not guarantee the shortest path but can find alternative routes.
- **Complexity:**
    - Time: Higher than traditional algorithms due to the membership calculations.
    - Space: Similar to A*, but depends on the number of partial connections considered.

## Results

| Scenario | Start City | End City | Radius (r) | Path Found | Distance | Certainty |
|----------|------------|----------|------------|------------|----------|-----------|
| 1        | New York   | Boston   | 2.0        | Yes        | 1.85     | 0.95      |
| 2        | Chicago    | San Francisco | 5.0        | Yes        | 23.78    | 0.80      |
| 3        | New York   | Los Angeles | 1.0        | No         | N/A      | N/A       |

## Conclusion

Fuzzy Search provides a flexible approach to finding paths, especially when connections are uncertain. It can be useful in scenarios where traditional algorithms fail to find a solution.