from unittest import TestCase, main
from unittest.mock import patch, MagicMock, call

from metricslib.decorators import capture_metrics


class CaptureMetricsTests(TestCase):
    @patch("metricslib.decorators.metrics._listeners.incr")
    @patch("metricslib.decorators.metrics._listeners.duration")
    @patch("metricslib.metrics.time.perf_counter")
    def test_capture_metrics(self, perf_counter_mock, duration_mock,
                             incr_mock):
        perf_counter_mock.side_effect = [1.0, 2.5]

        f = MagicMock()

        decorated_function = capture_metrics(
            "test.request", "test.error", "test.success", "test.timing")(f)
        decorated_function("arg1", "arg2", "arg3")

        f.assert_called_once_with("arg1", "arg2", "arg3")
        duration_mock.assert_called_once_with("test.timing", 1.5)
        incr_mock.assert_has_calls(
            [call("test.request"), call("test.success")])
        perf_counter_mock.assert_has_calls([call(), call()])

    @patch("metricslib.decorators.metrics._listeners.incr")
    @patch("metricslib.decorators.metrics._listeners.duration")
    @patch("metricslib.metrics.time.perf_counter")
    def test_wrapped_function_raised_exception(
            self, perf_counter_mock, duration_mock, incr_mock):
        perf_counter_mock.return_value = 1.0

        f = MagicMock()
        f.side_effect = ValueError

        with self.assertRaises(ValueError):
            decorated_function = capture_metrics(
                "test.request", "test.error", "test.success", "test.timing")(f)
            decorated_function("arg1", "arg2", "arg3")

        f.assert_called_once_with("arg1", "arg2", "arg3")
        duration_mock.assert_not_called()
        incr_mock.assert_has_calls([call("test.request"), call("test.error")])
        perf_counter_mock.assert_called_once_with()


if __name__ == "__main__":
    main()
