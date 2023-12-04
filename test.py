import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from your_module import ForgerockTokenAuthDateProcessor, handle_data

class TestForgerockTokenAuthDateProcessor(unittest.TestCase):

    @patch('your_module.query_elastic_tracking')
    @patch('your_module.utils.get_current_time_epoch', return_value=1234567890)
    @patch('your_module.DataCollector.market_app_creds', return_value="your_market_app_creds")  # Adjust this to return the expected value
    def test_collect_data(self, mock_market_app_creds, mock_get_current_time_epoch, mock_query_elastic_tracking):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "data-sources": {
                "elastic-cluster": "your_elastic_cluster_name"
            }
        }
        secrets_manager_mock = MagicMock()

        # Mocking data_config to enable data collection
        data_config_enabled = {
            "data_enabled": True,
            "datasource": {
                "name": "your_datasource_name",  # Adjust this to match your actual data source name
                "verify_certs": True,  # Assuming verify_certs defaults to True
                "template": "your_query_template",  # Adjust this to match your actual query template
            },
            "env": "your_environment",  # Adjust this to match your actual environment
            "timestamp_to": "your_timestamp_to",  # Adjust this to match your actual timestamp_to
            "timestamp_from": "your_timestamp_from",  # Adjust this to match your actual timestamp_from
            "index_name": "your_index_name",  # Adjust this to match your actual index name
            "num_results": 10,  # Adjust this to match your actual number of results
        }

        # Create an instance of ForgerockTokenAuthDateProcessor with mocked dependencies
        with patch('your_module.ForgerockTokenAuthDateProcessor.data_config', data_config_enabled):
            forgerock_processor = ForgerockTokenAuthDateProcessor(dynamodb_mock, config_mock, secrets_manager_mock)

        # Mocking filter_data method to return a sample MetricData
        forgerock_processor.filter_data = MagicMock(return_value="sample_metric_data")

        # Act
        forgerock_processor.collect_data()

        # Assert
        forgerock_processor.filter_data.assert_called_once()
        mock_query_elastic_tracking.assert_called_once_with(
            dynamodb_mock,
            "your_query_template",
            "your_index_name",
            "your_datasource_name",
            "your_market_app_creds",
            verify_certs=True,
        )
        dynamodb_mock.insert_metrics_data.assert_called_once_with("sample_metric_data")

    @patch('your_module.utils.get_current_time_epoch', return_value=1234567890)
    @patch('your_module.query_elastic_tracking')
    def test_get_details(self, mock_query_elastic_tracking, mock_get_current_time_epoch):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "data-sources": {
                "elastic-cluster": "your_elastic_cluster_name"
            }
        }
        secrets_manager_mock = MagicMock()

        # Mocking data_config
        data_config_mock = {
            "datasource": {
                "name": "your_datasource_name",  # Adjust this to match your actual data source name
                "verify_certs": True,  # Assuming verify_certs defaults to True
                "template": "your_query_template",  # Adjust this to match your actual query template
            },
        }

        forgerock_processor = ForgerockTokenAuthDateProcessor(dynamodb_mock, config_mock, secrets_manager_mock)
        forgerock_processor.data_config = data_config_mock

        # Mocking query_elastic_tracking method to return a sample result
        mock_query_elastic_tracking.return_value = {"hits": {"total": {"value": 1}}}

        # Act
        result = forgerock_processor.get_details()

        # Assert
        self.assertEqual(result, {"hits": {"total": {"value": 1}}})
        mock_query_elastic_tracking.assert_called_once_with(
            dynamodb_mock,
            "your_query_template",
            None,  # Adjust this to match your actual index name
            "your_datasource_name",
            None,  # Adjust this to match your actual market app creds
            verify_certs=True,
        )

    @patch('your_module.utils.get_current_time_epoch', return_value=1234567890)
    @patch('your_module.query_elastic_tracking')
    def test_filter_data_no_results(self, mock_query_elastic_tracking, mock_get_current_time_epoch):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "data-sources": {
                "elastic-cluster": "your_elastic_cluster_name"
            }
        }
        secrets_manager_mock = MagicMock()

        # Mocking data_config
        data_config_mock = {
            "datasource": {
                "name": "your_datasource_name",  # Adjust this to match your actual data source name
                "verify_certs": True,  # Assuming verify_certs defaults to True
                "template": "your_query_template",  # Adjust this to match your actual query template
            },
        }

        forgerock_processor = ForgerockTokenAuthDateProcessor(dynamodb_mock, config_mock, secrets_manager_mock)
        forgerock_processor.data_config = data_config_mock

        # Mocking query_elastic_tracking method to return no results
        mock_query_elastic_tracking.return_value = {"hits": {"total": {"value": 0}}}

        # Act
        result = forgerock_processor.filter_data()

        # Assert
        self.assertIsNone(result)
        mock_query_elastic_tracking.assert_called_once_with(
            dynamodb_mock,
            "your_query_template",
            None,  # Adjust this to match your actual index name
            "your_datasource_name",
            None,  # Adjust this to match your actual market app creds
            verify_certs=True,
        )

    @patch('your_module.utils.get_current_time_epoch', return_value=1234567890)
    @patch('your_module.query_elastic_tracking')
    def test_filter_data_with_results(self, mock_query_elastic_tracking, mock_get_current_time_epoch):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "data-sources": {
                "elastic-cluster": "your_elastic_cluster_name"
            }
        }
        secrets_manager_mock = MagicMock()

        # Mocking data_config
        data_config_mock = {
            "datasource": {
                "name": "your_datasource_name",  # Adjust this to match your actual data source name
                "verify_certs": True,  # Assuming verify_certs defaults to True
                "template": "your_query_template",  # Adjust this to match your actual query template
            },
        }

        forgerock_processor = ForgerockTokenAuthDateProcessor(dynamodb_mock, config_mock, secrets_manager_mock)
        forgerock_processor.data_config = data_config_mock

        # Mocking query_elastic_tracking method to return sample results
        mock_query_elastic_tracking.return_value = {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {"_source": {"datacenter": "dc1", "easi": "easi1", "node": "node1", "etl": {"lsnode": "lsnode1"}}},
                    {"_source": {"datacenter": "dc2", "easi": "easi2", "node": "node2", "etl": {"lsnode": "lsnode2"}}},
                ]
            }
        }

        # Act
        result = forgerock_processor.filter_data()

        # Assert
        expected_result = MetricData(
            MetricType.FORGEROCK_TOKEN_AUTH,
            [
                {"dc": "dc1", "easi": "easi1", "node": "node1", "lsnode": "lsnode1"},
                {"dc": "dc2", "easi": "easi2", "node": "node2", "lsnode": "lsnode2"}
            ],
            1234567890,
            {
                "perf_over": (
                    None,  # Adjust this to match your actual num_results
                    "datasource",
                    "your_elastic_cluster_name"
                )
            }
        )
        self.assertEqual(result, expected_result)
        mock_query_elastic_tracking.assert_called_once_with(
            dynamodb_mock,
            "your_query_template",
            None,  # Adjust this to match your actual index name
            "your_datasource_name",
            None,  # Adjust this to match your actual market app creds
            verify_certs=True,
        )

    @patch('your_module.jinja2.Template')
    def test_data_query(self, mock_jinja2_template):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "data-sources": {
                "elastic-cluster": "your_elastic_cluster_name"
            }
        }
        secrets_manager_mock = MagicMock()

        # Mocking data_config
        data_config_mock = {
            "env": "your_environment",  # Adjust this to match your actual environment
            "timestamp_to": "your_timestamp_to",  # Adjust this to match your actual timestamp_to
            "timestamp_from": "your_timestamp_from",  # Adjust this to match your actual timestamp_from
            "datasource": {
                "template": "your_query_template",  # Adjust this to match your actual query template
            },
        }

        forgerock_processor = ForgerockTokenAuthDateProcessor(dynamodb_mock, config_mock, secrets_manager_mock)
        forgerock_processor.data_config = data_config_mock

        # Mocking jinja2.Template method
        mock_template_instance = mock_jinja2_template.return_value
        mock_template_instance.render.return_value = "rendered_query_template"

        # Act
        result = forgerock_processor.data_query()

        # Assert
        self.assertEqual(result, "rendered_query_template")
        mock_jinja2_template.assert_called_once_with("your_query_template")  # Adjust this to match your actual query template

if __name__ == '__main__':
    unittest.main()
