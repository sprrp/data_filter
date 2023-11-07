import unittest
from unittest.mock import patch
import io
import sys
import os

class TestRunAllTestScript(unittest.TestCase):
    def test_run_all_tests(self):
        # Create a temporary test directory
        test_directory = "temp_test_dir"
        os.mkdir(test_directory)

        # Create a dummy test file in the temporary directory
        with open(f"{test_directory}/dummy_test.py", "w") as f:
            f.write("import unittest\n\n"
                    "class DummyTest(unittest.TestCase):\n"
                    "    def test_dummy(self):\n"
                    "        self.assertTrue(True)\n")

        # Redirect stdout to capture the script's output
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            with patch("sys.argv", ["run_all_test.py", test_directory]):
                import run_all_test  # Run the script

        # Clean up the temporary directory
        os.rmdir(test_directory)

        # Check the script's exit code
        self.assertEqual(run_all_test.sys.exit_code, 0)

        # Check that the script output contains test results
        script_output = mock_stdout.getvalue()
        self.assertIn("Ran 1 test", script_output)
        self.assertIn("OK", script_output)

if __name__ == '__main__':
    unittest.main()



import unittest
import subprocess
import os

class TestRunAllTestScript(unittest.TestCase):

    def test_script_runs_tests_successfully(self):
        # Define the test directory where your test files are located
        test_directory = "path/to/your/test_directory"

        # Run the run_all_test.py script with the test directory as an argument
        cmd = ["python3", "run_all_test.py", test_directory]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Check if the script returned a successful exit status (0)
        self.assertEqual(result.returncode, 0)

        # Optionally, you can check for specific messages in stdout or stderr
        # For example, if your script prints "All tests passed." on success
        self.assertIn(b'All tests passed.', result.stdout)

if __name__ == "__main__":
    unittest.main()
