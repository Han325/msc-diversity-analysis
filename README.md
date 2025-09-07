# Java Test Input Analysis Scripts

This repository contains a Python script designed to analyze the characteristics of string inputs within Java test files. It calculates the diversity of inputs using pairwise distance metrics.

## Script Overview

### `input-distance-analysis.py` (Input Diversity Analysis)

This script measures the *variety* of inputs by calculating the average pairwise distance between all unique inputs within a given category (e.g., `WalletNames`, `Amount`, etc.). A score closer to 1.0 indicates high diversity (inputs are very different from each other), while a score closer to 0.0 indicates low diversity (inputs are very similar).

The distance metrics used are:
-   **For strings**: Normalized Levenshtein distance.
-   **For numbers**: Normalized absolute difference.

## Requirements

-   Python 3.x

## How to Use

1.  Ensure the following files are in the same directory:
    -   `input-distance-analysis.py`
    -   `all_test_files_combined.txt` (the data file containing the Java code)

2.  Run the analysis from your terminal:

    ```bash
    python3 input-distance-analysis.py
    ```

3.  To run the tests:

    ```bash
    python3 -m unittest test_input_distance_analysis.py -v
    ```

**Note**: Both scripts expect the Java source code to be in a single file named `all_test_files_combined.txt`, with each test file separated by the delimiter line `================================================================================`.
