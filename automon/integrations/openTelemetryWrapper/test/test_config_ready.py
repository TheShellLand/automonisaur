import unittest

from automon.integrations.openTelemetryWrapper import OpenTelemetryConfig

from automon.helpers.loggingWrapper import LoggingClient

LoggingClient.logging.getLogger('opentelemetry.exporter.otlp.proto.grpc.exporter').setLevel(LoggingClient.DEBUG)


class MyTestCase(unittest.TestCase):
    config = OpenTelemetryConfig()
    config.enable_batch_processor_grpc()

    def test_client(self):
        if self.config.is_ready():
            self.assertTrue(
                self.config.test()
            )


if __name__ == '__main__':
    unittest.main()
