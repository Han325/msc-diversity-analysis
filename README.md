GA Mutation Signature Analyzer
This script analyzes Java test files to identify string inputs that match a predefined "Genetic Algorithm (GA) Mutation" signature. It parses the files, finds string variables used to instantiate specific custom classes, and calculates the percentage of those strings that appear to be mutated based on a set of rules.
Requirements
Python 3.x
No external libraries are needed.
Usage
Place the script gi_mutation_analyzer.py in a directory.
Place your data file, all_test_files_combined.txt, in the same directory.
Open a terminal and navigate to the directory containing the files.
Run the script using the following command:
code
Bash
python gi_mutation_analyzer.py
Input File Format
The script expects a single text file named all_test_files_combined.txt. This file should contain the complete source code of multiple Java test files, with each file's content separated by the following delimiter line:
================================================================================
Analysis Logic
The script keeps two main counters:
Total Semantic Inputs: Incremented for every String stringX = "..."; variable that is used to create an object of a custom_class (e.g., WalletNames, Email, Amount, Goals, IncomeDescription, TransactionDescription).
GA Mutated Inputs: A "semantic input" is counted as mutated if its value matches one of the following detectable GA signatures:
Plausible Long String: A single word repeated exactly 10 times.
Common Value Swap: A numeric string that is an exact match for a common commercial value (e.g., "19.95", "99.99").
Example Output
The script will print its progress for each file and a final summary of the analysis.
code
Code
Found 20 Java test files to analyze.

-> Analyzing run_01_ClassUnderTestApogen_ESTest.txt: Found 12 semantic inputs, 3 of which are mutated.
-> Analyzing run_02_ClassUnderTestApogen_ESTest.txt: Found 10 semantic inputs, 8 of which are mutated.
...

--- Analysis Complete ---
Total Semantic Inputs: 176
GA Mutated Inputs:     144
Percentage:            81.82%
