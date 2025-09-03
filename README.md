# GA Mutation Signature Analyzer (Diversity Analysis)

This script analyzes Java test files to identify string inputs that match a predefined "Genetic Algorithm (GA) Mutation" signature. It parses the files, finds string variables used to instantiate specific custom classes, and calculates the percentage of those strings that appear to be mutated based on a set of rules.

## Requirements

- Python 3.x

No external libraries are needed.

## Usage

1.  Place the script `gi_mutation_analyzer.py` in a directory.
2.  Place your data file, `all_test_files_combined.txt`, in the same directory.
3.  Open a terminal and navigate to the directory containing the files.
4.  Run the script using the following command:
    ```bash
    python gi_mutation_analyzer.py
    ```

## Input File Format

The script expects a single text file named `all_test_files_combined.txt`. This file should contain the complete source code of multiple Java test files, with each file's content separated by the following delimiter line:
`================================================================================`

## Analysis Logic

The script keeps two main counters:

-   **Total Semantic Inputs:** Incremented for every `String stringX = "...";` variable that is used to create an object of a `custom_class` (e.g., `WalletNames`, `Email`, `Amount`, `Goals`, `IncomeDescription`, `TransactionDescription`).

-   **GA Mutated Inputs:** A "semantic input" is counted as mutated if its value matches one of the following detectable GA signatures:
    -   **`Plausible Long String`**: A single word repeated exactly 10 times.
    -   **`Common Value Swap`**: A numeric string that is an exact match for a common commercial value (e.g., `"19.95"`, `"99.99"`).

