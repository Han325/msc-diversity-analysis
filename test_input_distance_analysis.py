import unittest
import os
import tempfile
from unittest.mock import patch, mock_open
import sys
import importlib.util

spec = importlib.util.spec_from_file_location("input_distance_analysis", "input-distance-analysis.py")
input_distance_analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(input_distance_analysis)

levenshtein_distance = input_distance_analysis.levenshtein_distance
normalized_levenshtein_distance = input_distance_analysis.normalized_levenshtein_distance
analyze_diversity = input_distance_analysis.analyze_diversity
main = input_distance_analysis.main


class TestLevenshteinDistance(unittest.TestCase):
    
    def test_identical_strings(self):
        self.assertEqual(levenshtein_distance("hello", "hello"), 0)
        self.assertEqual(levenshtein_distance("", ""), 0)
    
    def test_empty_strings(self):
        self.assertEqual(levenshtein_distance("", "hello"), 5)
        self.assertEqual(levenshtein_distance("hello", ""), 5)
    
    def test_completely_different_strings(self):
        self.assertEqual(levenshtein_distance("cat", "dog"), 3)
    
    def test_single_character_differences(self):
        self.assertEqual(levenshtein_distance("cat", "bat"), 1)
        self.assertEqual(levenshtein_distance("kitten", "sitting"), 3)
    
    def test_length_difference(self):
        self.assertEqual(levenshtein_distance("hello", "helloworld"), 5)
        self.assertEqual(levenshtein_distance("world", "helloworld"), 5)
    
    def test_case_sensitivity(self):
        self.assertEqual(levenshtein_distance("Hello", "hello"), 1)


class TestNormalizedLevenshteinDistance(unittest.TestCase):
    
    def test_identical_strings(self):
        self.assertEqual(normalized_levenshtein_distance("hello", "hello"), 0.0)
        self.assertEqual(normalized_levenshtein_distance("", ""), 0.0)
    
    def test_completely_different_same_length(self):
        result = normalized_levenshtein_distance("abc", "xyz")
        self.assertEqual(result, 1.0)
    
    def test_normalized_range(self):
        result = normalized_levenshtein_distance("kitten", "sitting")
        self.assertGreater(result, 0.0)
        self.assertLessEqual(result, 1.0)
        self.assertAlmostEqual(result, 3/7, places=5)
    
    def test_empty_strings(self):
        self.assertEqual(normalized_levenshtein_distance("", "hello"), 1.0)
        self.assertEqual(normalized_levenshtein_distance("hello", ""), 1.0)


class TestAnalyzeDiversity(unittest.TestCase):
    
    def test_empty_file_contents(self):
        result = analyze_diversity([])
        self.assertEqual(result, {})
    
    def test_no_matching_patterns(self):
        file_contents = [
            "public class TestClass { }",
            "// No string declarations here"
        ]
        result = analyze_diversity(file_contents)
        self.assertEqual(result, {})
    
    def test_single_input_per_category(self):
        file_contents = [
            '''
            String emailInput = "test@example.com";
            Email.fromString(emailInput);
            '''
        ]
        result = analyze_diversity(file_contents)
        expected = {'Email': {'unique_count': 1, 'avg_distance': 0.0}}
        self.assertEqual(result, expected)
    
    def test_multiple_inputs_same_category(self):
        file_contents = [
            '''
            String email1 = "test1@example.com";
            String email2 = "test2@example.com";
            Email.fromString(email1);
            Email.fromString(email2);
            '''
        ]
        result = analyze_diversity(file_contents)
        self.assertIn('Email', result)
        self.assertEqual(result['Email']['unique_count'], 2)
        self.assertGreater(result['Email']['avg_distance'], 0.0)
    
    def test_duplicate_inputs_are_handled(self):
        file_contents = [
            '''
            String email1 = "test@example.com";
            String email2 = "test@example.com";
            Email.fromString(email1);
            Email.fromString(email2);
            '''
        ]
        result = analyze_diversity(file_contents)
        expected = {'Email': {'unique_count': 1, 'avg_distance': 0.0}}
        self.assertEqual(result, expected)
    
    def test_amount_numeric_calculation(self):
        file_contents = [
            '''
            String amount1 = "100.0";
            String amount2 = "200.0";
            String amount3 = "300.0";
            Amount.fromString(amount1);
            Amount.fromString(amount2);
            Amount.fromString(amount3);
            '''
        ]
        result = analyze_diversity(file_contents)
        self.assertIn('Amount', result)
        self.assertEqual(result['Amount']['unique_count'], 3)
        self.assertGreater(result['Amount']['avg_distance'], 0.0)
    
    def test_amount_with_non_numeric_values(self):
        file_contents = [
            '''
            String amount1 = "invalid_amount";
            String amount2 = "also_invalid";
            Amount.fromString(amount1);
            Amount.fromString(amount2);
            '''
        ]
        result = analyze_diversity(file_contents)
        expected = {'Amount': {'unique_count': 2, 'avg_distance': 0.0}}
        self.assertEqual(result, expected)
    
    def test_amount_zero_range(self):
        file_contents = [
            '''
            String amount1 = "100.0";
            String amount2 = "100.0";
            Amount.fromString(amount1);
            Amount.fromString(amount2);
            '''
        ]
        result = analyze_diversity(file_contents)
        expected = {'Amount': {'unique_count': 1, 'avg_distance': 0.0}}
        self.assertEqual(result, expected)
    
    def test_multiple_categories(self):
        file_contents = [
            '''
            String email1 = "user1@test.com";
            String email2 = "user2@test.com";
            String goal1 = "Save money";
            String goal2 = "Invest wisely";
            Email.fromString(email1);
            Email.fromString(email2);
            Goals.fromString(goal1);
            Goals.fromString(goal2);
            '''
        ]
        result = analyze_diversity(file_contents)
        self.assertIn('Email', result)
        self.assertIn('Goals', result)
        self.assertEqual(len(result), 2)
    
    def test_variable_not_declared_in_same_file(self):
        file_contents = [
            '''
            Email.fromString(undeclaredVariable);
            '''
        ]
        result = analyze_diversity(file_contents)
        self.assertEqual(result, {})
    
    def test_complex_amount_parsing(self):
        file_contents = [
            '''
            String amount1 = "123.45 USD";
            String amount2 = "678.90 EUR";
            Amount.fromString(amount1);
            Amount.fromString(amount2);
            '''
        ]
        result = analyze_diversity(file_contents)
        self.assertIn('Amount', result)
        self.assertEqual(result['Amount']['unique_count'], 2)
        self.assertGreater(result['Amount']['avg_distance'], 0.0)


class TestMainFunction(unittest.TestCase):
    
    @patch('builtins.print')
    @patch('os.path.exists')
    def test_file_not_found(self, mock_exists, mock_print):
        mock_exists.return_value = False
        main()
        mock_print.assert_called_with("Error: The file 'all_test_files_combined.txt' was not found.")
    
    @patch('builtins.print')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="String test = \"value\";\nEmail.fromString(test);\n================================================================================\nString test2 = \"value2\";\nGoals.fromString(test2);")
    def test_successful_analysis(self, mock_file, mock_exists, mock_print):
        mock_exists.return_value = True
        
        main()
        
        mock_print.assert_any_call("Analyzing 2 Java test files for input diversity...\n")
        mock_print.assert_any_call("--- Diversity Analysis Results ---")
    
    @patch('builtins.print')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="")
    def test_empty_file_content(self, mock_file, mock_exists, mock_print):
        mock_exists.return_value = True
        
        main()
        
        mock_print.assert_any_call("Analyzing 0 Java test files for input diversity...\n")


if __name__ == '__main__':
    unittest.main()