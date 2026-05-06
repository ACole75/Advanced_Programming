import unittest
from studio5000_parser import Step_Token, extract_dev_token, StepRecord
from studio5000_formatter import parse_evaluation, format_studio5000

''' 
Python unit testing format taken from company standards, they include basic tests for validating inputs 
and outputs of the program and ensuring the program handles edge cases.
'''

# Testing of the validity of step tokens, which are required to be an integer or numeric range
class TestStepToken(unittest.TestCase):
    
    def test_valid_single_step(self):
        """Test valid single step number"""
        self.assertTrue(Step_Token("1"))
        self.assertTrue(Step_Token("42"))
        self.assertTrue(Step_Token("  10  "))
    
    def test_valid_step_range(self):
        """Test valid step ranges"""
        self.assertTrue(Step_Token("1-5"))
        self.assertTrue(Step_Token("1 - 5"))
        self.assertTrue(Step_Token("S1-5"))
    
    def test_invalid_step_tokens(self):
        """Test invalid step tokens"""
        self.assertFalse(Step_Token("ABC"))
        self.assertFalse(Step_Token(""))
        self.assertFalse(Step_Token("  "))

# Testing of the device detection and extraction from input document
class TestDeviceDetection(unittest.TestCase):
    
    def test_extract_single_device(self):
        """Test extraction of single device"""
        result = extract_dev_token("AB_CD")
        self.assertEqual(result, ["AB_CD"])
    
    def test_extract_multiple_devices(self):
        """Test extraction of multiple devices"""
        result = extract_dev_token("AB_CD and XY_ZW")
        self.assertIn("AB_CD", result)
        self.assertIn("XY_ZW", result)
    
    def test_extract_no_devices(self):
        """Test extraction with no valid device tokens"""
        result = extract_dev_token("no devices here")
        self.assertEqual(result, [])
    
    def test_no_duplicates(self):
        """Test that duplicate devices are not repeated"""
        result = extract_dev_token("AB_CD AB_CD XY_ZW")
        self.assertEqual(len(result), 2)

# Testing of the parse logic which will convert extracted device related text into ASCII device instruction text
class TestEvaluationParsing(unittest.TestCase):
    
    def test_device_off(self):
        """Test parsing 'Device OFF'"""
        result = parse_evaluation("PUMP_01 OFF")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("PUMP_01", "XIC"))
    
    def test_device_on(self):
        """Test parsing 'Device ON'"""
        result = parse_evaluation("VALVE_A ON")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("VALVE_A", "XIO"))
    
    def test_multiple_conditions(self):
        """Test parsing multiple conditions separated by AND"""
        result = parse_evaluation("PUMP_01 OFF AND VALVE_A ON")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("PUMP_01", "XIC"))
        self.assertEqual(result[1], ("VALVE_A", "XIO"))
    
    def test_empty_evaluation(self):
        """Test parsing empty evaluation text"""
        result = parse_evaluation("")
        self.assertEqual(result, [])
