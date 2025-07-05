# import os
# import sys
# import unittest

# # Add the project root to the Python path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# def run_tests():
#     """Run all tests in the test directory."""
    
#     # Discover and run all tests
#     loader = unittest.TestLoader()
#     start_dir = os.path.dirname(__file__)
#     suite = loader.discover(start_dir, pattern='test_*.py')
    
#     # Run the tests
#     runner = unittest.TextTestRunner(verbosity=2)
#     result = runner.run(suite)
    
#     return result.wasSuccessful()

# def run_unit_tests():
#     """Run only unit tests."""
#     loader = unittest.TestLoader()
#     suite = loader.discover('tests/unit', pattern='test_*.py')
#     runner = unittest.TextTestRunner(verbosity=2)
#     result = runner.run(suite)
#     return result.wasSuccessful()

# def run_integration_tests():
#     """Run only integration tests."""
#     loader = unittest.TestLoader()
#     suite = loader.discover('tests/integration', pattern='test_*.py')
#     runner = unittest.TextTestRunner(verbosity=2)
#     result = runner.run(suite)
#     return result.wasSuccessful()

# def run_functional_tests():
#     """Run only functional tests."""
#     loader = unittest.TestLoader()
#     suite = loader.discover('tests/functional', pattern='test_*.py')
#     runner = unittest.TextTestRunner(verbosity=2)
#     result = runner.run(suite)
#     return result.wasSuccessful()

# if __name__ == '__main__':
#     import sys
    
#     if len(sys.argv) > 1:
#         test_type = sys.argv[1].lower()
#         if test_type == 'unit':
#             success = run_unit_tests()
#         elif test_type == 'integration':
#             success = run_integration_tests()
#         elif test_type == 'functional':
#             success = run_functional_tests()
#         else:
#             print("Unknown test type. Use: unit, integration, or functional")
#             sys.exit(1)
#     else:
#         success = run_tests()
    
#     sys.exit(0 if success else 1)
