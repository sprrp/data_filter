import unittest
from unittest.mock import MagicMock, patch, mock_open
from your_module import ForgerockTokenAuthDateProcessor

class TestForgerockTokenAuthDateProcessor(unittest.TestCase):

    @patch('your_module.query_elastic_tracking')
    @patch('builtins.open', new_callable=mock_open)
    def test_collect_data_with_data_enabled(self, mock_open_file, mock_query_elastic_tracking):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "data-sources": {
                "elastic-cluster": "your_elastic_cluster_name"
            }
        }
        secrets_manager_mock = MagicMock()
        forgerock_processor = ForgerockTokenAuthDateProcessor(dynamodb_mock, config_mock, secrets_manager_mock)

        # Mocking data_config to enable data collection
        forgerock_processor.data_config = {"data_enabled": True}

        # Mocking filter_data method to return a sample MetricData
        forgerock_processor.filter_data = MagicMock(return_value="sample_metric_data")

        # Mocking utils.get_current_time_epoch() to return a fixed timestamp
        with patch('your_module.utils.get_current_time_epoch', return_value=1234567890):
            # Act
            forgerock_processor.collect_data()

            # Assert
            forgerock_processor.filter_data.assert_called_once()
            mock_query_elastic_tracking.assert_called_once_with(
                dynamodb_mock,
                forgerock_processor.data_query(),
                forgerock_processor.data_config["index_name"],
                config_mock["data-sources"][forgerock_processor.data_config["datasource"]["name"]],
                forgerock_processor.market_app_creds(),
                verify_certs=True,  # Assuming verify_certs defaults to True
            )
            mock_open_file.assert_called_once_with("../perf_consumer/handlers/forgerock_token_auth/test/elastic_search_result.json", "w")
            handle = mock_open_file()
            handle.write.assert_called_once_with('"sample_metric_data"')

if __name__ == '__main__':
    unittest.main()
