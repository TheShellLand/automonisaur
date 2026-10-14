import unittest

from automon.integrations.openTelemetryWrapper import OpenTelemetryConfig


class MyTestCase(unittest.TestCase):
    config = OpenTelemetryConfig().enable_memory_processor()

    def test_something(self):
        if self.config.is_ready():
            with self.config.tracer.start_as_current_span(name='rootSpan') as trace_root:
                trace_root.add_event('AAAAAAAA')

                with self.config.tracer.start_as_current_span(name='childSpan') as trace_child:
                    trace_child.add_event('BBBBBBBB')
                    trace_child.add_event('CCCCCCCC')


if __name__ == '__main__':
    unittest.main()
