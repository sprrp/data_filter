import json
import unittest
from unittest.mock import patch, MagicMock
from perf_common.data_collector import DataCollector, MetricData, MetricType

class TestSurgeQueues(unittest.TestCase):

    def setUp(self):
        self.ddb_mock = MagicMock()
        self.config_mock = {
            "data-sources": {
                "prometheus": "your_prometheus_config_here"
            }
        }
        self.secrets_manager_mock = MagicMock()

    @patch('perf_common.data_sources.prometheus.query_prometheus', return_value={"result": "mocked_result"})
    def test_collect_data(self, query_prometheus_mock):
        # Set up the mocks
        surge_queues = Surgequeues(self.ddb_mock, self.config_mock, self.secrets_manager_mock)

        # Load expected data from mock_data.json
        with open('mock_data.json', 'r') as file:
            expected_data = json.load(file)

        # Create mock objects for dependencies
        logger_mock = MagicMock()
        surge_queues.logger = logger_mock

        # Call the method to be tested
        surge_queues.collect_data()

        # Assertions
        logger_mock.info.assert_called_with("START: Querying Prometheus for Surge Queues")

        query_prometheus_mock.assert_called_once_with(
            self.config_mock["data-sources"]["prometheus"],
            'your_rendered_query',
        )

        metric_data_mock = MetricData(
            MetricType.SURGE_QUEUE,
            {"group1": [{"result": "mocked_result", "query": {"template": "your_template", "time_range": "your_time_range", "threshold": 1}}]},
            surge_queues.report_time
        )
        surge_queues.dynamodb.insert_metrics_data.assert_called_once_with(metric_data_mock)

        logger_mock.info.assert_called_with("END: Querying Prometheus for Surge Queues")

if __name__ == '__main__':
    unittest.main()
