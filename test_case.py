import unittest
from unittest.mock import patch, MagicMock
from your_module_name import email

class TestEmail(unittest.TestCase):

    @patch("your_module_name.smtplib.SMTP")
    def test_email_success(self, mock_smtp):
        # Prepare input data
        server = "mail.example.com"
        sender = "sender@example.com"
        to = ["recipient@example.com"]
        subject = "Test Email"
        text = "This is a test email."

        # Create a mock SMTP instance and mock the sendmail method
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        # Call the email function
        email(server, sender, to, subject, text)

        # Ensure the SMTP instance was created with the correct server
        mock_smtp.assert_called_once_with(server)

        # Ensure the sendmail method was called with the correct arguments
        mock_smtp_instance.sendmail.assert_called_once_with(sender, to, f"From:{sender} \nTo: {';'.join(to)} \nSubject:{subject} \n{text}")

        # Ensure the quit method was called
        mock_smtp_instance.quit.assert_called_once()

if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
from your_module_name import query_elastic, getLogger
from elasticsearch import Elasticsearch

class TestQueryElastic(unittest.TestCase):

    @patch.object(Elasticsearch, "search")
    @patch("your_module_name.getLogger")
    def test_query_elastic_success(self, mock_get_logger, mock_elasticsearch_search):
        # Prepare the mock response from Elasticsearch
        mock_response = {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {"_source": {"field1": "value1"}},
                    {"_source": {"field1": "value2"}}
                ]
            }
        }

        # Create a mock Elasticsearch instance and mock the search method
        mock_elasticsearch_instance = MagicMock()
        mock_elasticsearch_search.return_value = mock_response
        mock_elasticsearch_instance.search = mock_elasticsearch_search
        mock_elasticsearch = MagicMock(return_value=mock_elasticsearch_instance)

        # Mock the getLogger function
        mock_logger_instance = MagicMock()
        mock_get_logger.return_value = mock_logger_instance

        # Mock input parameters
        query = {"query": {"match_all": {}}}
        index = "my_index"
        datasource = "http://localhost:9200"
        credentials = ("username", "password")

        # Call the query_elastic function
        with patch("your_module_name.Elasticsearch", mock_elasticsearch):
            result = query_elastic(query, index, datasource, credentials)

        # Assertions
        self.assertEqual(result, mock_response)

        # Ensure getLogger was called
        mock_get_logger.assert_called_once_with()

        # Ensure the logger was used
        mock_logger_instance.debug.assert_called_once_with("Querying %s", datasource)

        # Ensure Elasticsearch.search was called with the correct arguments
        mock_elasticsearch_search.assert_called_once_with(index=index, body=query, request_timeout=15)

if __name__ == '__main__':
    unittest.main()


import unittest
from unittest.mock import patch
from your_module_name import setup_env, load_json_file, update_environment

class TestSetupEnv(unittest.TestCase):

    @patch("your_module_name.load_json_file")
    @patch("your_module_name.update_environment")
    @patch("sys.path.append")
    def test_setup_env(self, mock_append, mock_update_env, mock_load_json_file):
        # Prepare input data
        lambda_name = "consumer"
        env_file_data = {
            "PerformanceConsumer": {
                "VAR1": "Value1",
                "VAR2": "Value2"
            }
        }

        # Configure mock behavior
        mock_load_json_file.return_value = env_file_data

        # Call the setup_env function
        setup_env(lambda_name)

        # Ensure load_json_file was called with the correct file name
        mock_load_json_file.assert_called_once_with("../localdev/env.json")

        # Ensure update_environment was called with the correct environment variables
        mock_update_env.assert_called_once_with({
            "env": {
                "VAR1": "Value1",
                "VAR2": "Value2"
            }
        })

        # Ensure sys.path.append was called with the correct path
        mock_append.assert_called_once_with("Value1")

if __name__ == '__main__':
    unittest.main()
import unittest
from your_module_name import get_formatted_queues

class TestGetFormattedQueues(unittest.TestCase):

    def test_get_formatted_queues_single_queue(self):
        time_text = "2023-07-20 12:34:56"
        queues = ["Queue1"]
        result = get_formatted_queues(time_text, queues, name="Event")
        expected = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "The Event event has cleared. We saw issues for Queue1."
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "2023-07-20 12:34:56"
                    }
                ]
            }
        ]
        self.assertEqual(result, expected)

    def test_get_formatted_queues_multiple_queues(self):
        time_text = "2023-07-20 12:34:56"
        queues = ["Queue1", "Queue2", "Queue3"]
        result = get_formatted_queues(time_text, queues, name="Event")
        expected = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "The Event event has cleared. We saw issues for Queue1, Queue2, and Queue3."
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "2023-07-20 12:34:56"
                    }
                ]
            }
        ]
        self.assertEqual(result, expected)

    def test_get_formatted_queues_large_number_of_queues(self):
        time_text = "2023-07-20 12:34:56"
        queues = ["Queue" + str(i) for i in range(1, 21)]  # Create 20 queues from Queue1 to Queue20
        result = get_formatted_queues(time_text, queues, name="Event")
        expected = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "The Event event has cleared. We saw issues for Queue1, Queue2, Queue3, Queue4, Queue5, Queue6, Queue7, Queue8, Queue9, Queue10, Queue11, Queue12, Queue13, Queue14, Queue15, Queue16, Queue17, Queue18, Queue19, and Queue20. (see reply for full list)"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "2023-07-20 12:34:56"
                    }
                ]
            }
        ]
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
import unittest
import datetime
from unittest.mock import MagicMock, patch
from your_module_name import (
    get_current_timestamp,
    get_minutes_ago_epoch,
    get_minutes_future_epoch,
    is_market_hours,
    is_market_hours_order_flow,
    is_futures_quiet_period,
    is_market_open,
    is_market_close,
    is_epoch_today,
    query_elastic,
    query_big_panda,
    slack_time,
    teams_cleared_message,
    time_range_message,
    load_yaml_config,
    load_json_file,
    load_file,
    save_json_file,
    git_file_at_reference,
    get_config_file,
    update_environment,
    getLogger,
    test_socket,
    get_formatted_queues,
    setup_env,
    email,
)


class TestYourModuleFunctions(unittest.TestCase):

    # Test case for get_current_timestamp
    def test_get_current_timestamp(self):
        timestamp = get_current_timestamp()
        self.assertIsInstance(timestamp, int)

    # Test case for get_minutes_ago_epoch
    def test_get_minutes_ago_epoch(self):
        minutes_ago = get_minutes_ago_epoch()
        self.assertIsInstance(minutes_ago, int)

    # Test case for get_minutes_future_epoch
    def test_get_minutes_future_epoch(self):
        minutes_future = get_minutes_future_epoch()
        self.assertIsInstance(minutes_future, int)

    # Test case for is_market_hours
    def test_is_market_hours(self):
        market_hours = is_market_hours()
        self.assertIsInstance(market_hours, bool)

    # Test case for is_market_hours_order_flow
    def test_is_market_hours_order_flow(self):
        market_hours_order_flow = is_market_hours_order_flow()
        self.assertIsInstance(market_hours_order_flow, bool)

    # Test case for is_futures_quiet_period
    def test_is_futures_quiet_period(self):
        futures_quiet_period = is_futures_quiet_period()
        self.assertIsInstance(futures_quiet_period, bool)

    # Test case for is_market_open
    def test_is_market_open(self):
        market_open = is_market_open()
        self.assertIsInstance(market_open, bool)

    # Test case for is_market_close
    def test_is_market_close(self):
        market_close = is_market_close()
        self.assertIsInstance(market_close, bool)

    # Test case for is_epoch_today
    def test_is_epoch_today(self):
        epoch = int(datetime.datetime.now().timestamp())
        epoch_today = is_epoch_today(epoch)
        self.assertIsInstance(epoch_today, bool)

    # Test case for query_elastic
    @patch("your_module_name.Elasticsearch")
    def test_query_elastic(self, mock_elasticsearch):
        mock_elastic_search = MagicMock()
        mock_elasticsearch.return_value = mock_elastic_search

        query = {"match": {"field": "value"}}
        index = "your_index"
        datasource = "your_datasource"
        credentials = "your_credentials"
        result = {"your": "query", "result": "data"}
        mock_elastic_search.search.return_value = result

        response = query_elastic(query, index, datasource, credentials)

        mock_elasticsearch.assert_called_once_with(datasource, http_auth=credentials, verify_certs=True)
        mock_elastic_search.search.assert_called_once_with(index=index, body=query, request_timeout=15)
        self.assertEqual(response, result)

    # Test case for query_big_panda
    @patch("your_module_name.requests.get")
    def test_query_big_panda(self, mock_requests_get):
        credentials = "your_credentials"
        environment_id = "your_environment_id"
        tag_name = "your_tag_name"
        tag_value = "your_tag_value"
        from_time = "2023-07-20T00:00:00"
        to_time = "2023-07-20T23:59:59"
        request_timeout = 30
        result = {"your": "query", "result": "data"}
        mock_requests_get.return_value = MagicMock(json=lambda: result)

        response = query_big_panda(
            credentials, environment_id, tag_name, tag_value, from_time, to_time, request_timeout, verify=True
        )

        mock_requests_get.assert_called_once_with(
            f"https://api.bigpanda.io/resources/v2.0/environments/{environment_id}/incidents?query={tag_name} %3D {tag_value}&expand=alerts&from={from_time}&to={to_time}",
            headers={"accept": "application/json", "Authorization": f"Bearer {credentials}"},
            timeout=request_timeout,
            verify=True,
        )
        self.assertEqual(response, result)

    # Test case for slack_time
    def test_slack_time(self):
        epoch = int(datetime.datetime.now().timestamp())
        slack_time_str = slack_time(epoch)
        self.assertIsInstance(slack_time_str, str)

    # Test case for teams_cleared_message
    def test_teams_cleared_message(self):
        application = "your_application"
        start_time = int(datetime.datetime.now().timestamp())
        end_time = int(datetime.datetime.now().timestamp())
        message = teams_cleared_message(application, start_time, end_time)
        self.assertIsInstance(message, str)

    # Test case for time_range_message
    def test_time_range_message(self):
        start_time = int(datetime.datetime.now().timestamp())
        end_time = int(datetime.datetime.now().timestamp())
        time_range_msg = time_range_message(start_time, end_time)
        self.assertIsInstance(time_range_msg, str)

    # Test case for load_yaml_config
    @patch("builtins.open", mock_open(read_data="config_key: config_value"))
    def test_load_yaml_config(self):
        config = load_yaml_config("your_config_file.yaml")
        self.assertIsInstance(config, dict)
        self.assertEqual(config, {"config_key": "config_value"})

    # Test case for load_json_file
    @patch("builtins.open", mock_open(read_data='{"key": "value"}'))
    def test_load_json_file(self):
        data = load_json_file("your_json_file.json")
        self.assertIsInstance(data, dict)
        self.assertEqual(data, {"key": "value"})

    # Test case for load_file
    @patch("builtins.open", mock_open(read_data="file_content"))
    def test_load_file(self):
        file_content = load_file("your_file.txt")
        self.assertIsInstance(file_content, str)
        self.assertEqual(file_content, "file_content")

    # Test case for save_json_file
    @patch("builtins.open", mock_open())
    def test_save_json_file(self):
        data = {"key": "value"}
        save_json_file(data, "your_output_file.json")
        handle = open("your_output_file.json", "r")
        saved_data = json.load(handle)
        handle.close()
        self.assertEqual(data, saved_data)

    # Test case for git_file_at_reference
    @patch("your_module_name.git_repo.git.show")
    def test_git_file_at_reference(self, mock_git_show):
        git_repo = MagicMock()
        reference = "your_reference"
        file = "your_file.txt"
        result = "file_content"
        mock_git_show.return_value = result

        content = git_file_at_reference(git_repo, reference, file)
        mock_git_show.assert_called_once_with(f"{reference}:{file}")
        self.assertEqual(content, result)

    # Test case for get_config_file
    @patch("your_module_name.git_file_at_reference")
    def test_get_config_file(self, mock_git_file_at_reference):
        git_repo = MagicMock()
        reference = "your_reference"
        target_env = "your_target_env"
        path = "your_path"
        default_config = {"key1": "default_value1"}
        env_config = {"key2": "env_value2"}
        merged_config = {"key1": "default_value1", "key2": "env_value2"}
        mock_git_file_at_reference.side_effect = [default_config, env_config]

        config = get_config_file(git_repo, reference, target_env, path)
        self.assertEqual(config, merged_config)

    # Test case for update_environment
    @patch("os.environ", {"ENV_VAR": "existing_value"})
    def test_update_environment(self):
        config = {"env": {"ENV_VAR": "new_value"}}
        update_environment(config)
        self.assertEqual(os.environ["ENV_VAR"], "new_value")

    # Test case for getLogger
    def test_get_logger(self):
        logger = getLogger()
        self.assertIsInstance(logger, logging.Logger)

    # Test case for test_socket
    def test_test_socket(self):
        host = "localhost"
        port = 80
        message, status_code = test_socket(host, port)
        self.assertIsInstance(message, str)
        self.assertIsInstance(status_code, int)
        self.assertIn(status_code, [200, 404])  # Depending on whether the host:port is open or closed

    # Test case for get_formatted_queues
    def test_get_formatted_queues(self):
        time_text = "Your time text"
        queues = ["Queue1", "Queue2", "Queue3"]
        formatted_queues = get_formatted_queues(time_text, queues, name="YourName")
        self.assertIsInstance(formatted_queues, list)
        self.assertEqual(len(formatted_queues), 2)  # Two Slack blocks in the list

    # Test case for setup_env
    @patch("your_module_name.load_json_file")
    def test_setup_env(self, mock_load_json_file):
        lambda_name = "your_consumer"
        test_config = {
            "env": {
                "VAR1": "value1",
                "VAR2": "value2",
            }
        }
        env_file = {
            "PerformanceConsumer": {
                "VAR2": "env_value2",
                "VAR3": "env_value3",
            }
        }
        merged_config = {
            "env": {
                "VAR1": "value1",
                "VAR2": "env_value2",
                "VAR3": "env_value3",
            }
        }
        mock_load_json_file.side_effect = [test_config, env_file]

        setup_env(lambda_name)
        self.assertEqual(os.environ["VAR1"], "value1")
        self.assertEqual(os.environ["VAR2"], "env_value2")
        self.assertEqual(os.environ["VAR3"], "env_value3")

    # Test case for email
    @patch("your_module_name.smtplib.SMTP")
    def test_email(self, mock_smtp):
        server = "your_mail_server"
        sender = "your_sender@example.com"
        to = ["recipient1@example.com", "recipient2@example.com"]
        subject = "Your subject"
        text = "Your email content"
        email(server, sender, to, subject, text)
        mock_smtp.assert_called_once_with(server)
        mock_smtp.return_value.sendmail.assert_called_once_with(sender, to, f"From:{sender} \nTo: {';'.join(to)} \nSubject:{subject} \n\n{text}\n")

if __name__ == '__main__':
    unittest.main()

