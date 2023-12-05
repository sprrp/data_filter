import unittest
from unittest.mock import MagicMock
from datetime import date
from your_module import ForgerockTokenAuthAlertProcessor, handle_notification

class TestForgerockTokenAuthAlertProcessor(unittest.TestCase):

    def test_process_alerts_with_notifications_enabled(self):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "notifications_enabled": True,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            },
            "flapping_period": 5  # Adjust this to match your actual flapping period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()

        # Mocking alert_config
        alert_config_mock = {
            "notifications_enabled": True,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            }
        }

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock, metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = alert_config_mock

        # Mocking get_metric_data method to return sample data
        forgerock_alert_processor.dynamodb.get_metric_data.return_value = [
            MagicMock(get_value=[{"dc": "dc1", "node": "node1", "lsnode": "lsnode1", "easi": "easi1"}])
        ]

        # Act
        forgerock_alert_processor.process_alerts()

        # Assert
        forgerock_alert_processor.dynamodb.get_metric_data.assert_called_once_with(
            forgerock_alert_processor.MetricType.FORGEROCK_TOKEN_AUTH, metric_date=date.today()
        )
        forgerock_alert_processor.evaluate.assert_called_once_with(
            {"dc": "dc1", "node": "node1", "lsnode": "lsnode1", "easi": "easi1"}
        )
        forgerock_alert_processor.send_notifications.assert_called_once()
        forgerock_alert_processor.save_data.assert_called_once()

    def test_process_alerts_with_notifications_disabled(self):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "notifications_enabled": False,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            },
            "flapping_period": 5  # Adjust this to match your actual flapping period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()

        # Mocking alert_config
        alert_config_mock = {
            "notifications_enabled": False,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            }
        }

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock, metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = alert_config_mock

        # Act
        result = forgerock_alert_processor.process_alerts()

        # Assert
        self.assertIsNone(result)
        forgerock_alert_processor.dynamodb.get_metric_data.assert_not_called()
        forgerock_alert_processor.evaluate.assert_not_called()
        forgerock_alert_processor.send_notifications.assert_not_called()
        forgerock_alert_processor.save_data.assert_not_called()

    def test_slack_new_alert_blocks(self):
        # Arrange
        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = {
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                }
            }
        }
        forgerock_alert_processor.slack_time.return_value = "formatted_time"

        # Act
        blocks, popup_text = forgerock_alert_processor.slack_new_alert_blocks()

        # Assert
        expected_blocks = [
            MagicMock(text="your_slack_event_start_header\n"),
            MagicMock(elements=[MagicMock(text="Updated at formatted_time")])
        ]
        expected_popup_text = "Forge Rock on multiple instances"
        self.assertEqual(blocks, expected_blocks)
        self.assertEqual(popup_text, expected_popup_text)

    # Add more test cases for other methods as needed

if __name__ == '__main__':
    unittest.main()









import unittest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
from your_module import ForgerockTokenAuthAlertProcessor, handle_notification
from perf_common.metric import MetricType
from slackblocks import Block, ContextBlock, Text, SectionBlock
from perf_common.messaging.performance_message import PerformanceMessage
import pytz

class TestForgerockTokenAuthAlertProcessor(unittest.TestCase):

    @patch('your_module.Notifier.send_notifications')
    @patch('your_module.Notifier.save_data')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.dynamodb.get_metric_data')
    def test_process_alerts_with_notifications_enabled(self, mock_get_metric_data, mock_save_data, mock_send_notifications):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "notifications_enabled": True,
            "slack": {
                "event_start": {
                    "header": "Forge Rock Event Start Header"
                },
                "event_clear": {
                    "header": "Forge Rock Event Clear Header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "Forge Rock Event Start Header"
                },
            },
            "flapping_period": 300  # Adjust this to your actual flapping_period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()
        forgerock_processor = ForgerockTokenAuthAlertProcessor(dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock)

        # Mocking get_metric_data method to return sample data
        mock_get_metric_data.return_value = [
            PerformanceMessage(
                MetricType.FORGEROCK_TOKEN_AUTH,
                [
                    {"dc": "dc1", "easi": "easi1", "node": "node1", "lsnode": "lsnode1"},
                    {"dc": "dc2", "easi": "easi2", "node": "node2", "lsnode": "lsnode2"}
                ],
                datetime(2023, 1, 1, 0, 0, 0, tzinfo=pytz.UTC),
                metadata={"metric_date": "2023-01-01"}
            )
        ]

        # Act
        forgerock_processor.process_alerts()

        # Assert
        mock_get_metric_data.assert_called_once_with(MetricType.FORGEROCK_TOKEN_AUTH, metric_date=date.today())
        mock_send_notifications.assert_called_once()
        mock_save_data.assert_called_once()

    @patch('your_module.ForgerockTokenAuthAlertProcessor.dynamodb.get_metric_data')
    def test_process_alerts_with_notifications_disabled(self, mock_get_metric_data):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "notifications_enabled": False
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()
        forgerock_processor = ForgerockTokenAuthAlertProcessor(dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock)

        # Act
        result = forgerock_processor.process_alerts()

        # Assert
        self.assertIsNone(result)
        mock_get_metric_data.assert_not_called()

if __name__ == '__main__':
    unittest.main()



import unittest
from unittest.mock import patch, MagicMock
from datetime import date
from your_module import ForgerockTokenAuthAlertProcessor, handle_notification

class TestForgerockTokenAuthAlertProcessor(unittest.TestCase):

    @patch('your_module.Notifier.send_notifications')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.save_data')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.evaluate')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.dynamodb.get_metric_data')
    def test_process_alerts_with_notifications_enabled(self, mock_get_metric_data, mock_evaluate, mock_save_data, mock_send_notifications):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "notifications_enabled": True,
            "slack": {
                "event_start": {
                    "header": "Start event header"
                },
                "event_clear": {
                    "header": "Clear event header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "Teams event start header"
                },
                "event_clear": {
                    "header": "Teams event clear header"
                }
            }
        }
        secrets_manager_mock = MagicMock()
        sqs_instance_mock = MagicMock()
        
        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(dynamodb_mock, config_mock, secrets_manager_mock, sqs_instance_mock)
        
        # Mocking get_metric_data method to return a sample data
        mock_get_metric_data.return_value = [{"dc": "dc1", "node": "node1", "lsnode": "lsnode1", "easi": "easi1"}]
        
        # Act
        forgerock_alert_processor.process_alerts()
        
        # Assert
        mock_get_metric_data.assert_called_once_with(MetricType.FORGEROCK_TOKEN_AUTH, metric_date=date.today())
        mock_evaluate.assert_called_once_with({"dc": "dc1", "node": "node1", "lsnode": "lsnode1", "easi": "easi1"})
        mock_send_notifications.assert_called_once()
        mock_save_data.assert_called_once()

    @patch('your_module.Notifier.send_notifications')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.save_data')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.evaluate')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.dynamodb.get_metric_data', return_value=[])
    def test_process_alerts_with_no_data(self, mock_get_metric_data, mock_evaluate, mock_save_data, mock_send_notifications):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "notifications_enabled": True,
            "slack": {
                "event_start": {
                    "header": "Start event header"
                },
                "event_clear": {
                    "header": "Clear event header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "Teams event start header"
                },
                "event_clear": {
                    "header": "Teams event clear header"
                }
            }
        }
        secrets_manager_mock = MagicMock()
        sqs_instance_mock = MagicMock()
        
        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(dynamodb_mock, config_mock, secrets_manager_mock, sqs_instance_mock)
        
        # Mocking get_metric_data method to return an empty list
        mock_get_metric_data.return_value = []
        
        # Act
        forgerock_alert_processor.process_alerts()
        
        # Assert
        mock_get_metric_data.assert_called_once_with(MetricType.FORGEROCK_TOKEN_AUTH, metric_date=date.today())
        mock_evaluate.assert_not_called()
        mock_send_notifications.assert_not_called()
        mock_save_data.assert_not_called()

if __name__ == '__main__':
    unittest.main()


import unittest
from unittest.mock import patch, MagicMock
from datetime import date
from your_module import ForgerockTokenAuthAlertProcessor, handle_notification

class TestForgerockTokenAuthAlertProcessor(unittest.TestCase):

    @patch('your_module.Notifier.send_notifications')
    @patch('your_module.Notifier.save_data')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.evaluate')
    @patch('your_module.DynamoDB.get_metric_data')
    def test_process_alerts_with_notifications_enabled(self, mock_get_metric_data, mock_evaluate, mock_save_data, mock_send_notifications):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "notifications_enabled": True,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            },
            "flapping_period": 5  # Adjust this to match your actual flapping period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()

        # Mocking alert_config
        alert_config_mock = {
            "notifications_enabled": True,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            }
        }

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock, metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = alert_config_mock

        # Mocking get_metric_data method to return sample data
        mock_get_metric_data.return_value = [
            MagicMock(get_value=lambda: [{"dc": "dc1", "node": "node1", "lsnode": "lsnode1", "easi": "easi1"}])
        ]

        # Act
        forgerock_alert_processor.process_alerts()

        # Assert
        mock_get_metric_data.assert_called_once_with(MetricType.FORGEROCK_TOKEN_AUTH, metric_date=date.today())
        mock_evaluate.assert_called_once_with(
            {"dc": "dc1", "node": "node1", "lsnode": "lsnode1", "easi": "easi1"}
        )
        mock_send_notifications.assert_called_once()
        mock_save_data.assert_called_once()

    @patch('your_module.Notifier.send_notifications')
    @patch('your_module.Notifier.save_data')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.evaluate')
    @patch('your_module.DynamoDB.get_metric_data')
    def test_process_alerts_with_notifications_disabled(self, mock_get_metric_data, mock_evaluate, mock_save_data, mock_send_notifications):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "notifications_enabled": False,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            },
            "flapping_period": 5  # Adjust this to match your actual flapping period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()

        # Mocking alert_config
        alert_config_mock = {
            "notifications_enabled": False,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            }
        }

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock, metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = alert_config_mock

        # Act
        result = forgerock_alert_processor.process_alerts()

        # Assert
        self.assertIsNone(result)
        mock_get_metric_data.assert_not_called()
        mock_evaluate.assert_not_called()
        mock_send_notifications.assert_not_called()
        mock_save_data.assert_not_called()

if __name__ == '__main__':
    unittest.main()
import unittest
from unittest.mock import patch, MagicMock
from datetime import date
from your_module import ForgerockTokenAuthAlertProcessor, handle_notification

class TestForgerockTokenAuthAlertProcessor(unittest.TestCase):

    @patch('your_module.Notifier.send_notifications')
    @patch('your_module.Notifier.save_data')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.evaluate')
    @patch('your_module.DynamoDB.get_metric_data')
    def test_process_alerts_with_notifications_enabled(self, mock_get_metric_data, mock_evaluate, mock_save_data, mock_send_notifications):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "notifications_enabled": True,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            },
            "flapping_period": 5  # Adjust this to match your actual flapping period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()

        # Mocking alert_config
        alert_config_mock = {
            "notifications_enabled": True,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            }
        }

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock, metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = alert_config_mock

        # Mocking get_metric_data method to return sample data
        mock_get_metric_data.return_value = [
            MagicMock(get_value=lambda: [{"dc": "dc1", "node": "node1", "lsnode": "lsnode1", "easi": "easi1"}])
        ]

        # Act
        forgerock_alert_processor.process_alerts()

        # Assert
        mock_get_metric_data.assert_called_once_with(MetricType.FORGEROCK_TOKEN_AUTH, metric_date=date.today())
        mock_evaluate.assert_called_once_with(
            {"dc": "dc1", "node": "node1", "lsnode": "lsnode1", "easi": "easi1"}
        )
        mock_send_notifications.assert_called_once()
        mock_save_data.assert_called_once()

    @patch('your_module.Notifier.send_notifications')
    @patch('your_module.Notifier.save_data')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.evaluate')
    @patch('your_module.DynamoDB.get_metric_data')
    def test_process_alerts_with_notifications_disabled(self, mock_get_metric_data, mock_evaluate, mock_save_data, mock_send_notifications):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "notifications_enabled": False,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            },
            "flapping_period": 5  # Adjust this to match your actual flapping period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()

        # Mocking alert_config
        alert_config_mock = {
            "notifications_enabled": False,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            }
        }

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock, metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = alert_config_mock

        # Act
        result = forgerock_alert_processor.process_alerts()

        # Assert
        self.assertIsNone(result)
        mock_get_metric_data.assert_not_called()
        mock_evaluate.assert_not_called()
        mock_send_notifications.assert_not_called()
        mock_save_data.assert_not_called()

    @patch('your_module.utils.slack_time')
    def test_slack_new_alert_blocks(self, mock_slack_time):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "flapping_period": 5  # Adjust this to match your actual flapping period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()

        # Mocking alert_config
        alert_config_mock = {
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                }
            }
        }

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock, metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = alert_config_mock

        # Mocking utils.slack_time method
        mock_slack_time.return_value = "mock_slack_time_result"

        # Act
        result_blocks, result_popup_text = forgerock_alert_processor.slack_new_alert_blocks()

        # Assert
        expected_blocks = [
            {"type": "section", "text": {"type": "mrkdwn", "text": 'your_slack_event_start_header\n'}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": "Updated at mock_slack_time_result"}]}
        ]
        self.assertEqual(result_blocks, expected_blocks)
        self.assertEqual(result_popup_text, "Forge Rock on multiple instances")

    @patch('your_module.utils.slack_time')
    def test_slack_cleared_alert_blocks(self, mock_slack_time):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "flapping_period": 5  # Adjust this to match your actual flapping period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()

        # Mocking alert_config
        alert_config_mock = {
            "slack": {
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            }
        }

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock, metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = alert_config_mock

        # Mocking utils.slack_time method
        mock_slack_time.return_value = "mock_slack_time_result"

        # Act
        result_blocks, result_popup_text = forgerock_alert_processor.slack_cleared_alert_blocks("your_channel")

        # Assert
        expected_blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "your_slack_event_clear_header"}}]
        self.assertEqual(result_blocks, expected_blocks)
        self.assertEqual(result_popup_text, "Forge Rock event has cleared")

    @patch('your_module.utils.get_formatted_queues')
    @patch('your_module.utils.slack_time')
    def test_slack_alert_report_blocks(self, mock_slack_time, mock_get_formatted_queues):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "flapping_period": 5  # Adjust this to match your actual flapping period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock, metric_date=date.today()
        )

        # Mocking utils.slack_time method
        mock_slack_time.return_value = "mock_slack_time_result"

        # Mocking utils.get_formatted_queues method
        mock_get_formatted_queues.return_value = [
            {"text": "formatted_queues_text", "type": "mrkdwn"}
        ]

        # Act
        result_blocks = forgerock_alert_processor.slack_alert_report_blocks()

        # Assert
        expected_blocks = [
            {"type": "mrkdwn", "text": "The event lasted from mock_slack_time_result until mock_slack_time_result."},
            {"type": "mrkdwn", "text": "formatted_queues_text"}
        ]
        self.assertEqual(result_blocks, expected_blocks)

    @patch('your_module.utils.teams_cleared_message')
    def test_teams_cleared_alert_message(self, mock_teams_cleared_message):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "flapping_period": 5  # Adjust this to match your actual flapping period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock, metric_date=date.today()
        )

        # Mocking utils.teams_cleared_message method
        mock_teams_cleared_message.return_value = "mock_teams_cleared_message_result"

        # Act
        result = forgerock_alert_processor.teams_cleared_message()

        # Assert
        self.assertEqual(result, "mock_teams_cleared_message_result")

    @patch('your_module.utils.time_from_epoch')
    def test_teams_alert_message(self, mock_time_from_epoch):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "flapping_period": 5  # Adjust this to match your actual flapping period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock, metric_date=date.today()
        )

        # Mocking utils.time_from_epoch method
        mock_time_from_epoch.return_value = "mock_time_from_epoch_result"

        # Act
        result = forgerock_alert_processor.teams_alert_message()

        # Assert
        self.assertEqual(result, "your_teams_event_start_header\nUpdated at mock_time_from_epoch_result")

    @patch('your_module.utils.time_from_epoch')
    def test_metrics_dataframe(self, mock_time_from_epoch):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "flapping_period": 5  # Adjust this to match your actual flapping period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock, metric_date=date.today()
        )

        # Mocking time_from_epoch method
        mock_time_from_epoch.return_value = "mock_time_from_epoch_result"

        # Mocking event.metrics
        forgerock_alert_processor.event.metrics = {
            "metric1": MagicMock(get_metadata=lambda key: "value1"),
            "metric2": MagicMock(get_metadata=lambda key: "value2")
        }

        # Act
        result = forgerock_alert_processor.metrics_dataframe()

        # Assert
        expected_dataframe = {
            "DC": ["value1", "value2"],
            "Easi": ["value1", "value2"],
            "Node": ["value1", "value2"],
            "Lsnode": ["value1", "value2"]
        }
        self.assertEqual(result.to_dict(), expected_dataframe)

if __name__ == '__main__':
    unittest.main()
import unittest
from unittest.mock import patch, MagicMock
from datetime import date
from your_module import ForgerockTokenAuthAlertProcessor, handle_notification

class TestForgerockTokenAuthAlertProcessor(unittest.TestCase):

    @patch('your_module.Notifier.send_notifications')
    @patch('your_module.Notifier.save_data')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.evaluate')
    @patch('your_module.DynamoDB.get_metric_data')
    def test_process_alerts_with_notifications_enabled(self, mock_get_metric_data, mock_evaluate, mock_save_data, mock_send_notifications):
        # ... (same as previous test case)

    @patch('your_module.Notifier.send_notifications')
    @patch('your_module.Notifier.save_data')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.evaluate')
    @patch('your_module.DynamoDB.get_metric_data')
    def test_process_alerts_with_notifications_disabled(self, mock_get_metric_data, mock_evaluate, mock_save_data, mock_send_notifications):
        # ... (same as previous test case)

    @patch('your_module.Notifier.active_breaches')
    def test_evaluate(self, mock_active_breaches):
        # Arrange
        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), metric_date=date.today()
        )
        forgerock_alert_processor.event = MagicMock(active_breaches=mock_active_breaches)

        # Mocking active_breaches method to return a sample dictionary
        mock_active_breaches.return_value = {"sample_breach_key": "sample_breach_value"}

        # Act
        forgerock_alert_processor.evaluate({"dc": "dc1", "node": "node1", "lsnode": "lsnode1", "easi": "easi1"})

        # Assert
        mock_active_breaches.assert_called_once()
        self.assertEqual(forgerock_alert_processor.event.metrics["sample_breach_key"].metadata["node"], "node1")

    @patch('your_module.utils.slack_time')
    def test_slack_new_alert_blocks(self, mock_slack_time):
        # Arrange
        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = {"slack": {"event_start": {"header": "your_slack_event_start_header"}}}
        forgerock_alert_processor.event = MagicMock(should_set_to_cleared=MagicMock(return_value=False))

        # Mocking slack_time method to return a sample time
        mock_slack_time.return_value = "sample_slack_time"

        # Act
        result_blocks, result_popup_text = forgerock_alert_processor.slack_new_alert_blocks()

        # Assert
        expected_blocks = ["your_slack_event_start_header", "Updated at sample_slack_time"]
        self.assertEqual(result_blocks, expected_blocks)
        self.assertEqual(result_popup_text, "Forge Rock on multiple instances")

if __name__ == '__main__':
    unittest.main()
import unittest
from unittest.mock import patch, MagicMock
from datetime import date
from your_module import ForgerockTokenAuthAlertProcessor, handle_notification

class TestForgerockTokenAuthAlertProcessor(unittest.TestCase):

    @patch('your_module.Notifier.send_notifications')
    @patch('your_module.Notifier.save_data')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.evaluate')
    @patch('your_module.DynamoDB.get_metric_data')
    def test_process_alerts_with_notifications_enabled(self, mock_get_metric_data, mock_evaluate, mock_save_data, mock_send_notifications):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "notifications_enabled": True,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            },
            "flapping_period": 5  # Adjust this to match your actual flapping period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()

        # Mocking alert_config
        alert_config_mock = {
            "notifications_enabled": True,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            }
        }

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock, metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = alert_config_mock

        # Mocking get_metric_data method to return sample data
        mock_get_metric_data.return_value = [
            MagicMock(get_value=lambda: [{"dc": "dc1", "node": "node1", "lsnode": "lsnode1", "easi": "easi1"}])
        ]

        # Act
        forgerock_alert_processor.process_alerts()

        # Assert
        mock_get_metric_data.assert_called_once_with(MetricType.FORGEROCK_TOKEN_AUTH, metric_date=date.today())
        mock_evaluate.assert_called_once_with(
            {"dc": "dc1", "node": "node1", "lsnode": "lsnode1", "easi": "easi1"}
        )
        mock_send_notifications.assert_called_once()
        mock_save_data.assert_called_once()

    @patch('your_module.Notifier.send_notifications')
    @patch('your_module.Notifier.save_data')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.evaluate')
    @patch('your_module.DynamoDB.get_metric_data')
    def test_process_alerts_with_notifications_disabled(self, mock_get_metric_data, mock_evaluate, mock_save_data, mock_send_notifications):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "notifications_enabled": False,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            },
            "flapping_period": 5  # Adjust this to match your actual flapping period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()

        # Mocking alert_config
        alert_config_mock = {
            "notifications_enabled": False,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            }
        }

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock, metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = alert_config_mock

        # Act
        result = forgerock_alert_processor.process_alerts()

        # Assert
        self.assertIsNone(result)
        mock_get_metric_data.assert_not_called()
        mock_evaluate.assert_not_called()
        mock_send_notifications.assert_not_called()
        mock_save_data.assert_not_called()

    @patch('your_module.ForgerockTokenAuthAlertProcessor.active_breaches')
    @patch('your_module.Event.should_set_to_cleared')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.send_notifications')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.slack_alert_report_blocks')
    def test_slack_new_alert_blocks(self, mock_slack_alert_report_blocks, mock_send_notifications, mock_should_set_to_cleared, mock_active_breaches):
        # Arrange
        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), metric_date=date.today()
        )
        mock_should_set_to_cleared.return_value = False
        mock_slack_alert_report_blocks.return_value = (["block1", "block2"], "Forge Rock event cleared.")

        # Act
        blocks, popup_text = forgerock_alert_processor.slack_new_alert_blocks()

        # Assert
        self.assertEqual(blocks, ["block1", "block2"])
        self.assertEqual(popup_text, "Forge Rock event cleared.")
        mock_slack_alert_report_blocks.assert_called_once()
        mock_send_notifications.assert_not_called()

    @patch('your_module.ForgerockTokenAuthAlertProcessor.active_breaches')
    @patch('your_module.Event.should_set_to_cleared')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.send_notifications')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.slack_alert_report_blocks')
    def test_slack_new_alert_blocks_event_cleared(self, mock_slack_alert_report_blocks, mock_send_notifications, mock_should_set_to_cleared, mock_active_breaches):
        # Arrange
        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), metric_date=date.today()
        )
        mock_should_set_to_cleared.return_value = True
        mock_slack_alert_report_blocks.return_value = (["block1", "block2"], "Forge Rock event cleared.")

        # Act
        blocks, popup_text = forgerock_alert_processor.slack_new_alert_blocks()

        # Assert
        self.assertEqual(blocks, ["block1", "block2"])
        self.assertEqual(popup_text, "Forge Rock event cleared.")
        mock_slack_alert_report_blocks.assert_called_once()
        mock_send_notifications.assert_called_once()

    @patch('your_module.jinja2.Template')
    def test_teams_alert_message(self, mock_jinja2_template):
        # Arrange
        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), metric_date=date.today()
        )
        mock_jinja2_template.return_value.render.return_value = "your_rendered_message"

        # Act
        result = forgerock_alert_processor.teams_alert_message()

        # Assert
        self.assertEqual(result, "your_rendered_message")
        mock_jinja2_template.assert_called_once_with("your_teams_event_start_header")
        mock_jinja2_template.return_value.render.assert_called_once()

if __name__ == '__main__':
    unittest.main()



import unittest
from unittest.mock import patch, MagicMock
from datetime import date
from your_module import ForgerockTokenAuthAlertProcessor, handle_notification

class TestForgerockTokenAuthAlertProcessor(unittest.TestCase):

    @patch('your_module.Notifier.send_notifications')
    @patch('your_module.Notifier.save_data')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.evaluate')
    @patch('your_module.DynamoDB.get_metric_data')
    def test_process_alerts_with_notifications_enabled(self, mock_get_metric_data, mock_evaluate, mock_save_data, mock_send_notifications):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "notifications_enabled": True,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            },
            "flapping_period": 5  # Adjust this to match your actual flapping period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()

        # Mocking alert_config
        alert_config_mock = {
            "notifications_enabled": True,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            }
        }

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock, metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = alert_config_mock

        # Mocking get_metric_data method to return sample data
        mock_get_metric_data.return_value = [
            MagicMock(get_value=lambda: [{"dc": "dc1", "node": "node1", "lsnode": "lsnode1", "easi": "easi1"}])
        ]

        # Act
        forgerock_alert_processor.process_alerts()

        # Assert
        mock_get_metric_data.assert_called_once_with(MetricType.FORGEROCK_TOKEN_AUTH, metric_date=date.today())
        mock_evaluate.assert_called_once_with(
            {"dc": "dc1", "node": "node1", "lsnode": "lsnode1", "easi": "easi1"}
        )
        mock_send_notifications.assert_called_once()
        mock_save_data.assert_called_once()

    @patch('your_module.Notifier.send_notifications')
    @patch('your_module.Notifier.save_data')
    @patch('your_module.ForgerockTokenAuthAlertProcessor.evaluate')
    @patch('your_module.DynamoDB.get_metric_data')
    def test_process_alerts_with_notifications_disabled(self, mock_get_metric_data, mock_evaluate, mock_save_data, mock_send_notifications):
        # Arrange
        dynamodb_mock = MagicMock()
        config_mock = {
            "notifications_enabled": False,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            },
            "flapping_period": 5  # Adjust this to match your actual flapping period
        }
        secrets_manager_mock = MagicMock()
        sqs_class_mock = MagicMock()

        # Mocking alert_config
        alert_config_mock = {
            "notifications_enabled": False,
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                },
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            },
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            }
        }

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            dynamodb_mock, config_mock, secrets_manager_mock, sqs_class_mock, metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = alert_config_mock

        # Act
        result = forgerock_alert_processor.process_alerts()

        # Assert
        self.assertIsNone(result)
        mock_get_metric_data.assert_not_called()
        mock_evaluate.assert_not_called()
        mock_send_notifications.assert_not_called()
        mock_save_data.assert_not_called()

    @patch('your_module.utils.slack_time')
    def test_slack_new_alert_blocks(self, mock_slack_time):
        # Arrange
        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = {
            "slack": {
                "event_start": {
                    "header": "your_slack_event_start_header"
                }
            }
        }
        mock_slack_time.return_value = "formatted_time"

        # Act
        blocks, popup_text = forgerock_alert_processor.slack_new_alert_blocks()

        # Assert
        expected_blocks = [
            SectionBlock(text="your_slack_event_start_header\n"),
            ContextBlock(elements=[Text("Updated at formatted_time")])
        ]
        expected_popup_text = "Forge Rock on multiple instances"
        self.assertEqual(blocks, expected_blocks)
        self.assertEqual(popup_text, expected_popup_text)
        mock_slack_time.assert_called_once_with(forgerock_alert_processor.report_time)

    @patch('your_module.jinja2.Template')
    def test_slack_cleared_alert_blocks(self, mock_jinja2_template):
        # Arrange
        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = {
            "slack": {
                "event_clear": {
                    "header": "your_slack_event_clear_header"
                }
            }
        }
        mock_jinja2_template_instance = mock_jinja2_template.return_value
        mock_jinja2_template_instance.render.return_value = "rendered_message"

        # Act
        blocks, popup_text = forgerock_alert_processor.slack_cleared_alert_blocks("your_channel_id")

        # Assert
        expected_blocks = [
            SectionBlock(text="rendered_message")
        ]
        expected_popup_text = "Forge Rock event has cleared"
        self.assertEqual(blocks, expected_blocks)
        self.assertEqual(popup_text, expected_popup_text)
        mock_jinja2_template.assert_called_once_with("your_slack_event_clear_header")

    def test_metrics_dataframe(self):
        # Arrange
        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), metric_date=date.today()
        )
        forgerock_alert_processor.event.metrics = {
            "metric1": MagicMock(metadata={"dc": "dc1", "node": "node1", "easi": "easi1", "lsnode": "lsnode1"}),
            "metric2": MagicMock(metadata={"dc": "dc2", "node": "node2", "easi": "easi2", "lsnode": "lsnode2"})
        }

        # Act
        dataframe = forgerock_alert_processor.metrics_dataframe()

        # Assert
        expected_dataframe = pandas.DataFrame({
            "DC": ["dc1", "dc2"],
            "Easi": ["easi1", "easi2"],
            "Node": ["node1", "node2"],
            "Lsnode": ["lsnode1", "lsnode2"]
        })
        pandas.testing.assert_frame_equal(dataframe, expected_dataframe)

    @patch('your_module.utils.slack_time')
    def test_slack_alert_report_blocks(self, mock_slack_time):
        # Arrange
        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), metric_date=date.today()
        )
        forgerock_alert_processor.event.creation_time = 1234567890
        forgerock_alert_processor.event.last_notification_time = 1234567899
        mock_slack_time.side_effect = ["formatted_start_time", "formatted_end_time"]

        # Act
        blocks = forgerock_alert_processor.slack_alert_report_blocks()

        # Assert
        expected_blocks = [
            SectionBlock(text="The event lasted from formatted_start_time until formatted_end_time."),
            # Add more expected blocks based on your actual implementation
        ]
        self.assertEqual(blocks, expected_blocks)
        mock_slack_time.assert_has_calls([unittest.mock.call(1234567890), unittest.mock.call(1234567899)])

    @patch('your_module.utils.teams_cleared_message')
    def test_teams_cleared_alert_blocks(self, mock_teams_cleared_message):
        # Arrange
        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), metric_date=date.today()
        )
        forgerock_alert_processor.event.creation_time = 1234567890
        forgerock_alert_processor.event.last_notification_time = 1234567899
        mock_teams_cleared_message.return_value = "teams_cleared_message"

        # Act
        message = forgerock_alert_processor.teams_cleared_alert_blocks("your_channel")

        # Assert
        expected_message = "teams_cleared_message"
        self.assertEqual(message, expected_message)
        mock_teams_cleared_message.assert_called_once_with("Forge Rock", 1234567890, 1234567899)

    @patch('your_module.utils.time_from_epoch')
    @patch('your_module.pytz.timezone')
    def test_teams_alert_message(self, mock_timezone, mock_time_from_epoch):
        # Arrange
        mock_eastern_timezone = mock_timezone.return_value
        mock_eastern_timezone_instance = mock_eastern_timezone.return_value
        mock_eastern_timezone_instance.zone = "US/Eastern"
        mock_time_from_epoch.return_value = "formatted_time"

        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), metric_date=date.today()
        )
        forgerock_alert_processor.alert_config = {
            "teams": {
                "event_start": {
                    "header": "your_teams_event_start_header"
                }
            }
        }

        # Act
        message = forgerock_alert_processor.teams_alert_message()

        # Assert
        expected_message = 'your_teams_event_start_header\n<li>your_teams_event_start_header</br>Updated at formatted_time'
        self.assertEqual(message, expected_message)
        mock_time_from_epoch.assert_called_once_with(forgerock_alert_processor.report_time, with_timezone=True, display_pytz=mock_eastern_timezone)

    @patch('your_module.utils.get_formatted_queues')
    @patch('your_module.utils.slack_time')
    def test_slack_alert_report_blocks(self, mock_slack_time, mock_get_formatted_queues):
        # Arrange
        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), metric_date=date.today()
        )
        forgerock_alert_processor.event.creation_time = 1234567890
        forgerock_alert_processor.event.last_notification_time = 1234567899
        mock_slack_time.side_effect = ["formatted_start_time", "formatted_end_time"]
        mock_get_formatted_queues.return_value = ["your_formatted_queues"]

        # Act
        blocks = forgerock_alert_processor.slack_alert_report_blocks()

        # Assert
        expected_blocks = [
            # Add expected blocks based on your actual implementation
        ]
        self.assertEqual(blocks, expected_blocks)
        mock_slack_time.assert_has_calls([unittest.mock.call(1234567890), unittest.mock.call(1234567899)])
        mock_get_formatted_queues.assert_called_once_with("The event lasted from formatted_start_time until formatted_end_time.", {"your_queues"}, "Forge Rock")

    @patch('your_module.utils.teams_cleared_message')
    def test_teams_cleared_alert_blocks(self, mock_teams_cleared_message):
        # Arrange
        forgerock_alert_processor = ForgerockTokenAuthAlertProcessor(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), metric_date=date.today()
        )
        forgerock_alert_processor.event.creation_time = 1234567890
        forgerock_alert_processor.event.last_notification_time = 1234567899
        mock_teams_cleared_message.return_value = "teams_cleared_message"

        # Act
        message = forgerock_alert_processor.teams_cleared_alert_blocks("your_channel")

        # Assert
        expected_message = "teams_cleared_message"
        self.assertEqual(message, expected_message)
        mock_teams_cleared_message.assert_called_once_with("Forge Rock", 1234567890, 1234567899)

if __name__ == '__main__':
    unittest.main()
