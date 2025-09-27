#!/usr/bin/env python3
"""
Test runner for Xiaozhi ESP32 Server functionality.
This script runs all tests for the weather plugin, news plugin, and other added functionality.
"""

import unittest
import sys
import os
from io import StringIO

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

def run_tests():
    """Run all tests and return results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test modules
    try:
        from test_weather_plugin import TestWeatherPlugin
        suite.addTests(loader.loadTestsFromTestCase(TestWeatherPlugin))
        print("✓ Weather plugin tests loaded")
    except ImportError as e:
        print(f"✗ Failed to load weather plugin tests: {e}")
    
    try:
        from test_news_plugin import TestNewsPlugin
        suite.addTests(loader.loadTestsFromTestCase(TestNewsPlugin))
        print("✓ News plugin tests loaded")
    except ImportError as e:
        print(f"✗ Failed to load news plugin tests: {e}")
    
    # Run tests
    print("\n" + "="*50)
    print("Running Tests")
    print("="*50)
    
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=StringIO(),
        descriptions=True,
        failfast=False
    )
    
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return result.wasSuccessful()

def run_specific_test(test_name):
    """Run a specific test class or method."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    try:
        if test_name == "weather":
            from test_weather_plugin import TestWeatherPlugin
            suite.addTests(loader.loadTestsFromTestCase(TestWeatherPlugin))
        elif test_name == "news":
            from test_news_plugin import TestNewsPlugin
            suite.addTests(loader.loadTestsFromTestCase(TestNewsPlugin))
        else:
            print(f"Unknown test: {test_name}")
            return False
            
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
        
    except ImportError as e:
        print(f"Failed to load test {test_name}: {e}")
        return False

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
