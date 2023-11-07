import unittest
from unittest.mock import patch, Mock
import io
import run_all_test

class TestRunAllTest(unittest.TestCase):
    @patch('sys.argv', ['run_all_test.py', 'tests_directory'])
    @patch('logging.basicConfig')
    @patch('logging.getLogger')
    @patch('unittest.defaultTestLoader.discover')
    @patch('unittest.TextTestRunner')
    def test_run_all_tests(self, mock_runner, mock_discover, mock_get_logger, mock_basic_config):
        with patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
            # Mock the test result to simulate a successful test run.
            mock_result = Mock()
            mock_result.wasSuccessful.return_value = True
            mock_runner.return_value.run.return_value = mock_result

            run_all_test.__name__ = "__main__"
            run_all_test.main()

            mock_basic_config.assert_called_with(stream=mock_stderr)
            mock_get_logger.return_value.setLevel.assert_called_with(logging.DEBUG)
            mock_discover.assert_called_with('tests_directory', pattern='*_test-py')
            mock_runner.assert_called_with(resultclass=unittest.TextTestResult)
            mock_runner.return_value.run.assert_called_with(mock_discover.return_value)

            # Ensure the exit code is 0 (success) when the test run is successful.
            self.assertEqual(run_all_test.sys.exit.call_args[0][0], 0)

if __name__ == '__main__':
    unittest.main()
