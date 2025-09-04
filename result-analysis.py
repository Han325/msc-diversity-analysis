import re
import os

def is_plausible_long_string(value: str) -> bool:
    """
    Checks if a string matches the 'Plausible Long String' signature.
    Signature: A single word repeated exactly 10 times, separated by spaces.
    """
    words = value.strip().split()
    # Check for exactly 10 words
    if len(words) != 10:
        return False
    # Check if all words are identical
    return len(set(words)) == 1

def is_common_value_swap(value: str) -> bool:
    """
    Checks if a string matches the 'Common Value Swap' signature.
    Signature: The string is an exact match for a common commercial value.
    """
    common_values = {"19.95", "99.99", "49.50", "99.00"}
    return value.strip() in common_values

def analyze_java_file_content(content: str) -> (int, int):
    """
    Analyzes the content of a single Java test file.

    Returns:
        A tuple containing:
        - total_semantic_inputs (int): Count of relevant string variables.
        - gi_mutated_inputs (int): Count of those variables that match a GI signature.
    """
    # Regex to find all declarations like: String stringX = "...";
    # Captures: 1) variable name, 2) string value
    string_declaration_regex = re.compile(r'String\s+([a-zA-Z0-9_]+)\s*=\s*"(.*?)";')
    
    # List of the custom classes we care about
    custom_classes = [
        'Amount', 'Email', 'Goals', 'IncomeDescription', 
        'TransactionDescription', 'WalletNames'
    ]
    
    # Find all string variables and their values in the file
    matches = string_declaration_regex.finditer(content)
    string_variables = {match.group(1): match.group(2) for match in matches}
    
    semantic_count = 0
    mutated_count = 0

    # For each found string variable, check if it's used to create a custom class
    for var_name, var_value in string_variables.items():
        # Exclude variables named 'id' as per the instructions
        if var_name == 'id':
            continue

        # Create a regex to check for the usage of this specific variable
        # Looks for patterns like: WalletNames.fromString(string0)
        usage_pattern = (
            r'(?:' + '|'.join(custom_classes) + 
            r')\.fromString\(\s*' + re.escape(var_name) + r'\s*\)'
        )
        
        # If the variable is used in at least one custom class constructor...
        if re.search(usage_pattern, content):
            semantic_count += 1
            
            # Now, check if its value matches one of our GI mutation signatures
            is_mutated = (is_plausible_long_string(var_value) or 
                          is_common_value_swap(var_value))
            
            if is_mutated:
                mutated_count += 1
    
    return semantic_count, mutated_count

def main():
    """
    Main function to run the analysis.
    """
    input_filename = "all_test_files_combined.txt"
    
    if not os.path.exists(input_filename):
        print(f"Error: The file '{input_filename}' was not found in the current directory.")
        print("Please place the file in the same directory as the script or update the path.")
        return

    with open(input_filename, 'r', encoding='utf-8') as f:
        full_content = f.read()

    # The delimiter that separates each Java file in the combined text file
    delimiter = "================================================================================"
    
    # Split the content into individual files and filter out any empty parts
    file_contents = [content for content in full_content.split(delimiter) if content.strip()]
    
    print(f"Found {len(file_contents)} Java test files to analyze.\n")

    total_semantic_inputs = 0
    total_gi_mutated_inputs = 0

    # Process each file's content
    for i, content in enumerate(file_contents, 1):
        # Extract the source file name for better logging
        source_match = re.search(r'FILE: (run_\d+_ClassUnderTestApogen_ESTest\.txt)', content)
        file_id = source_match.group(1) if source_match else f"File {i}"

        semantic, mutated = analyze_java_file_content(content)
        
        if semantic > 0:
            print(f"-> Analyzing {file_id}: Found {semantic} semantic inputs, {mutated} of which are mutated.")
        
        total_semantic_inputs += semantic
        total_gi_mutated_inputs += mutated

    print("\n--- Analysis Complete ---")

    if total_semantic_inputs == 0:
        print("No semantic inputs were found across all files.")
        percentage = 0.0
    else:
        percentage = (total_gi_mutated_inputs / total_semantic_inputs) * 100

    print(f"Total Semantic Inputs: {total_semantic_inputs}")
    print(f"GI Mutated Inputs:     {total_gi_mutated_inputs}")
    print(f"Percentage:            {percentage:.2f}%")

if __name__ == "__main__":
    main()
