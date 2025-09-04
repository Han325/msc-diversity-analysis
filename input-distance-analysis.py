import re
import os
import itertools
import math

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculates the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def normalized_levenshtein_distance(s1: str, s2: str) -> float:
    """Calculates the Levenshtein distance normalized to be between 0.0 and 1.0."""
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 0.0
    return levenshtein_distance(s1, s2) / max_len

def analyze_diversity(file_contents: list) -> dict:
    """
    Parses Java test files, groups inputs by class, and calculates 
    the average pairwise distance for each group.
    
    Returns:
        A dictionary with analysis results for each category.
    """
    custom_classes = [
        'Amount', 'Email', 'Goals', 'IncomeDescription', 
        'TransactionDescription', 'WalletNames'
    ]
    
    input_groups = {class_name: [] for class_name in custom_classes}

    # Regex to find all string variable declarations
    string_declaration_regex = re.compile(r'String\s+([a-zA-Z0-9_]+)\s*=\s*"(.*?)";')
    
    # Regex to find where those variables are used
    usage_pattern = re.compile(
        r'(' + '|'.join(custom_classes) + 
        r')\.fromString\(\s*([a-zA-Z0-9_]+)\s*\)'
    )

    for content in file_contents:
        # Step 1: Find all string declarations in the current file
        string_variables = {
            match.group(1): match.group(2) 
            for match in string_declaration_regex.finditer(content)
        }
        
        # Step 2: Find all usages and map them to their values
        for usage_match in usage_pattern.finditer(content):
            class_name, var_name = usage_match.groups()
            if var_name in string_variables:
                input_groups[class_name].append(string_variables[var_name])

    # --- Perform Diversity Calculation ---
    results = {}
    for category, values in input_groups.items():
        if not values:
            continue

        unique_values = sorted(list(set(values)))
        num_unique = len(unique_values)

        if num_unique < 2:
            results[category] = {'unique_count': num_unique, 'avg_distance': 0.0}
            continue

        total_distance = 0.0
        pairs = list(itertools.combinations(unique_values, 2))
        
        if category == 'Amount':
            # --- Numeric Distance Calculation ---
            numeric_values = []
            for v in unique_values:
                try:
                    # Handle values that might be complex strings
                    numeric_part = v.strip().split()[0]
                    numeric_values.append(float(numeric_part))
                except (ValueError, IndexError):
                    # Skip non-numeric values gracefully
                    continue
            
            if len(numeric_values) < 2:
                results[category] = {'unique_count': num_unique, 'avg_distance': 0.0}
                continue

            min_val, max_val = min(numeric_values), max(numeric_values)
            value_range = max_val - min_val

            if value_range == 0:
                avg_distance = 0.0
            else:
                numeric_pairs = itertools.combinations(numeric_values, 2)
                total_distance = sum(abs(p1 - p2) / value_range for p1, p2 in numeric_pairs)
                avg_distance = total_distance / len(pairs)
        else:
            # --- String Distance Calculation ---
            total_distance = sum(normalized_levenshtein_distance(p1, p2) for p1, p2 in pairs)
            avg_distance = total_distance / len(pairs)
            
        results[category] = {'unique_count': num_unique, 'avg_distance': avg_distance}

    return results

def main():
    """
    Main function to run the diversity analysis.
    """
    input_filename = "all_test_files_combined.txt"
    
    if not os.path.exists(input_filename):
        print(f"Error: The file '{input_filename}' was not found.")
        return

    with open(input_filename, 'r', encoding='utf-8') as f:
        full_content = f.read()

    delimiter = "================================================================================"
    file_contents = [content for content in full_content.split(delimiter) if content.strip()]
    
    print(f"Analyzing {len(file_contents)} Java test files for input diversity...\n")

    diversity_results = analyze_diversity(file_contents)
    
    # --- Print Results Table ---
    print("--- Diversity Analysis Results ---")
    print(f"{'Input Category':<25} | {'# of Unique Inputs':<20} | {'Average Pairwise Distance':<25}")
    print("-" * 75)
    
    # Sort results for consistent output
    sorted_categories = sorted(diversity_results.keys(), key=lambda k: diversity_results[k]['avg_distance'], reverse=True)

    for category in sorted_categories:
        res = diversity_results[category]
        unique_count = res['unique_count']
        avg_dist = f"{res['avg_distance']:.4f}"
        print(f"{category:<25} | {unique_count:<20} | {avg_dist:<25}")

if __name__ == "__main__":
    main()
