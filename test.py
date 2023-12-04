import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from forgerock_token_auth import ForgerockTokenAuthDateProcessor, ForgerockTokenAuthAlertProcessor

class TestForgerockTokenAuth(unittest.TestCase):

    def setUp(self):
        # Mocking dependencies for data collection
        self.dynamodb_mock = MagicMock()
        self.config_mock = {
            "data-sources": {
                "elastic-cluster": "your_elastic_cluster_config",
            }
            # Add other required configurations
        }
        self.secrets_manager_mock = MagicMock()

    def test_forgerock_data_collection(self):
        # Set up
        with patch("consumer_utils.query_elastic_tracking") as query_elastic_mock:
            # Mock the ElasticSearch query result
            query_elastic_mock.return_value = {
                "hits": {
                    "total": {
                        "value": 1
                    },
                    "hits": [
                        {
                            "_source": {
                                "datacenter": "DC1",
                                "easi": "easi123",
                                "node": "node1",
                                "etl": {
                                    "lsnode": "lsnode123"
                                }
                            }
                        }
                    ]
                }
            }

            # Create an instance of the data collector
            data_collector = ForgerockTokenAuthDateProcessor(
                self.dynamodb_mock, self.config_mock, self.secrets_manager_mock
            )

            # Call the collect_data method
            data_collector.collect_data()

            # Assertions
            self.dynamodb_mock.insert_metrics_data.assert_called_once()
            args, kwargs = self.dynamodb_mock.insert_metrics_data.call_args
            metric_data = args[0]
            self.assertEqual(metric_data.metric_type, "FORGEROCK_TOKEN_AUTH")
            self.assertEqual(metric_data.data[0]["dc"], "DC1")
            self.assertEqual(metric_data.data[0]["easi"], "easi123")
            self.assertEqual(metric_data.data[0]["node"], "node1")
            self.assertEqual(metric_data.data[0]["lsnode"], "lsnode123")

    def test_forgerock_alerts(self):
        # Set up
        with patch("perf_common.data_collector.DataCollector.filter_data") as filter_data_mock:
            # Mock the filter_data method to return sample MetricData
            filter_data_mock.return_value = MagicMock(spec=MetricData)

            # Create an instance of the alert processor
            alert_processor = ForgerockTokenAuthAlertProcessor(
                self.dynamodb_mock, self.config_mock, self.secrets_manager_mock, MagicMock()
            )

            # Call the process_alerts method
            alert_processor.process_alerts()

            # Assertions
            self.assertTrue(filter_data_mock.called)
            self.assertTrue(self.dynamodb_mock.get_metric_data.called)
            self.assertTrue(self.dynamodb_mock.insert_metrics_data.called)

if __name__ == "__main__":
    unittest.main()
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from forgerock_token_auth import ForgerockTokenAuthDateProcessor, MetricData

class TestForgerockTokenAuthDateProcessor(unittest.TestCase):

    def setUp(self):
        # Mocking dependencies
        self.dynamodb_mock = MagicMock()
        self.config_mock = {
            "data-sources": {
                "elastic-cluster": "your_elastic_cluster_config",
            }
            # Add other required configurations
        }
        self.secrets_manager_mock = MagicMock()

    @patch("consumer_utils.query_elastic_tracking")
    def test_data_collection(self, query_elastic_mock):
        # Mock the ElasticSearch query result
        query_elastic_mock.return_value = {
            "hits": {
                "total": {
                    "value": 1
                },
                "hits": [
                    {
                        "_source": {
                            "datacenter": "DC1",
                            "easi": "easi123",
                            "node": "node1",
                            "etl": {
                                "lsnode": "lsnode123"
                            }
                        }
                    }
                ]
            }
        }

        # Create an instance of the data collector
        data_collector = ForgerockTokenAuthDateProcessor(
            self.dynamodb_mock, self.config_mock, self.secrets_manager_mock
        )

        # Call the collect_data method
        data_collector.collect_data()

        # Assertions
        self.dynamodb_mock.insert_metrics_data.assert_called_once()
        args, kwargs = self.dynamodb_mock.insert_metrics_data.call_args
        metric_data = args[0]
        self.assertIsInstance(metric_data, MetricData)
        self.assertEqual(metric_data.metric_type, "FORGEROCK_TOKEN_AUTH")
        self.assertEqual(metric_data.data[0]["dc"], "DC1")
        self.assertEqual(metric_data.data[0]["easi"], "easi123")
        self.assertEqual(metric_data.data[0]["node"], "node1")
        self.assertEqual(metric_data.data[0]["lsnode"], "lsnode123")

    def test_data_query(self):
        # Create an instance of the data collector
        data_collector = ForgerockTokenAuthDateProcessor(
            self.dynamodb_mock, self.config_mock, self.secrets_manager_mock
        )

        # Call the data_query method
        query = data_collector.data_query()

        # Assertions
        self.assertIsNotNone(query)
        # Add more specific assertions based on your data_query method

    @patch("consumer_utils.query_elastic_tracking")
    def test_get_details(self, query_elastic_mock):
        # Mock the ElasticSearch query result
        query_elastic_mock.return_value = {
            "hits": {
                "total": {
                    "value": 1
                },
                "hits": [
                    {
                        "_source": {
                            "datacenter": "DC1",
                            "easi": "easi123",
                            "node": "node1",
                            "etl": {
                                "lsnode": "lsnode123"
                            }
                        }
                    }
                ]
            }
        }

        # Create an instance of the data collector
        data_collector = ForgerockTokenAuthDateProcessor(
            self.dynamodb_mock, self.config_mock, self.secrets_manager_mock
        )

        # Call the get_details method
        result = data_collector.get_details()

        # Assertions
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["dc"], "DC1")
        self.assertEqual(result[0]["easi"], "easi123")
        self.assertEqual(result[0]["node"], "node1")
        self.assertEqual(result[0]["lsnode"], "lsnode123")

    @patch("consumer_utils.query_elastic_tracking")
    def test_filter_data(self, query_elastic_mock):
        # Mock the ElasticSearch query result
        query_elastic_mock.return_value = {
            "hits": {
                "total": {
                    "value": 1
                },
                "hits": [
                    {
                        "_source": {
                            "datacenter": "DC1",
                            "easi": "easi123",
                            "node": "node1",
                            "etl": {
                                "lsnode": "lsnode123"
                            }
                        }
                    }
                ]
            }
        }

        # Create an instance of the data collector
        data_collector = ForgerockTokenAuthDateProcessor(
            self.dynamodb_mock, self.config_mock, self.secrets_manager_mock
        )

        # Call the filter_data method
        metric_data = data_collector.filter_data()

        # Assertions
        self.assertIsInstance(metric_data, MetricData)
        self.assertEqual(metric_data.metric_type, "FORGEROCK_TOKEN_AUTH")
        self.assertEqual(metric_data.data[0]["dc"], "DC1")
        self.assertEqual(metric_data.data[0]["easi"], "easi123")
        self.assertEqual(metric_data.data[0]["node"], "node1")
        self.assertEqual(metric_data.data[0]["lsnode"], "lsnode123")

if __name__ == "__main__":
    unittest.main()
import unittest
from unittest.mock import MagicMock, patch
from forgerock_token_auth import ForgerockTokenAuthDateProcessor, MetricData

class TestForgerockTokenAuthDateProcessor(unittest.TestCase):

    def setUp(self):
        # Mocking dependencies
        self.dynamodb_mock = MagicMock()
        self.config_mock = {
            "data-sources": {
                "elastic-cluster": "your_elastic_cluster_config",
            }
            # Add other required configurations
        }
        self.secrets_manager_mock = MagicMock()

    @patch("consumer_utils.query_elastic_tracking")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    @patch("forgerock_token_auth.ForgerockTokenAuthDateProcessor.logger")
    def test_data_collection(self, logger_mock, open_mock, query_elastic_mock):
        # Mock the ElasticSearch query result
        query_elastic_mock.return_value = {
            "hits": {
                "total": {
                    "value": 1
                },
                "hits": [
                    {
                        "_source": {
                            "datacenter": "DC1",
                            "easi": "easi123",
                            "node": "node1",
                            "etl": {
                                "lsnode": "lsnode123"
                            }
                        }
                    }
                ]
            }
        }

        # Create an instance of the data collector
        data_collector = ForgerockTokenAuthDateProcessor(
            self.dynamodb_mock, self.config_mock, self.secrets_manager_mock
        )

        # Call the collect_data method
        data_collector.collect_data()

        # Assertions
        self.assertTrue(query_elastic_mock.called)
        self.assertTrue(logger_mock.debug.called)
        self.assertTrue(open_mock.called)

        # Check the arguments passed to query_elastic_tracking
        args, kwargs = query_elastic_mock.call_args
        self.assertEqual(args[0], self.dynamodb_mock)
        self.assertEqual(args[1], data_collector.data_query())
        self.assertEqual(args[2], data_collector.data_config["index_name"])
        self.assertEqual(
            args[3], self.config_mock["data-sources"][data_collector.data_config["datasource"]["name"]]
        )
        self.assertEqual(args[4], data_collector.market_app_creds())
        self.assertEqual(kwargs["verify_certs"], True)  # assuming verify_certs is set to True

        # Check the arguments and content passed to open
        open_mock.assert_called_once_with(
            "../perf_consumer/handlers/forgerock_token_auth/test/elastic_search_result.json", "w"
        )
        file_handle = open_mock()
        file_handle.write.assert_called_once_with(json.dumps(query_elastic_mock.return_value))
