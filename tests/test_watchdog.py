"""Watchdog policy tests."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('watchdog', Path(__file__).resolve().parents[1] / 'deploy/watchdog.py')
watchdog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watchdog)


class WatchdogTests(unittest.TestCase):
    def test_healthy_starting_and_stopped_are_untouched(self):
        for status in ['healthy', 'starting', None]:
            with tempfile.TemporaryDirectory() as d, patch.object(watchdog, 'container_state', return_value={'Health': {'Status': status}}), patch.object(watchdog.subprocess, 'run') as restart:
                watchdog.check(Path(d))
                restart.assert_not_called()

    def test_unhealthy_restarts_only_once_during_cooldown(self):
        with tempfile.TemporaryDirectory() as d, patch.object(watchdog, 'container_state', return_value={'Health': {'Status': 'unhealthy'}}), patch.object(watchdog.subprocess, 'run') as restart, patch.object(watchdog.time, 'time', return_value=10000):
            watchdog.check(Path(d))
            watchdog.check(Path(d))
            restart.assert_called_once()
            with patch.object(watchdog.time, 'time', return_value=10601):
                watchdog.check(Path(d))
            self.assertEqual(restart.call_count, 2)

    def test_failed_attempt_still_sets_cooldown(self):
        with tempfile.TemporaryDirectory() as d, patch.object(watchdog, 'container_state', return_value={'Health': {'Status': 'unhealthy'}}), patch.object(watchdog.subprocess, 'run', side_effect=RuntimeError('failed')) as restart, patch.object(watchdog.time, 'time', return_value=10000):
            with self.assertRaises(RuntimeError):
                watchdog.check(Path(d))
            watchdog.check(Path(d))
            restart.assert_called_once()

    def test_recent_container_start_is_protected(self):
        state = {'Health': {'Status': 'unhealthy'}, 'StartedAt': '1970-01-01T02:45:00.123456789Z'}
        with tempfile.TemporaryDirectory() as d, patch.object(watchdog, 'container_state', return_value=state), patch.object(watchdog.subprocess, 'run') as restart, patch.object(watchdog.time, 'time', return_value=10000):
            watchdog.check(Path(d))
            restart.assert_not_called()

    def test_docker_query_timeout_does_not_restart(self):
        with tempfile.TemporaryDirectory() as d, patch.object(watchdog.subprocess, 'check_output', side_effect=watchdog.subprocess.TimeoutExpired('docker', 10)) as query, patch.object(watchdog.subprocess, 'run') as restart:
            watchdog.check(Path(d))
            self.assertEqual(query.call_args.kwargs['timeout'], 10)
            restart.assert_not_called()
            self.assertFalse((Path(d) / 'last-attempt').exists())

    def test_inspect_query_is_also_bounded(self):
        with tempfile.TemporaryDirectory() as d, patch.object(watchdog.subprocess, 'check_output', side_effect=['container-id', watchdog.subprocess.TimeoutExpired('docker', 10)]) as query, patch.object(watchdog.subprocess, 'run') as restart:
            watchdog.check(Path(d))
            self.assertEqual(query.call_args.kwargs['timeout'], 10)
            restart.assert_not_called()

    def test_nanoseconds_are_normalized_for_older_host_python(self):
        from datetime import datetime
        real_parse = datetime.fromisoformat
        def strict_parse(value):
            self.assertIn('.123456+', value)
            return real_parse(value)
        state = {'Health': {'Status': 'unhealthy'}, 'StartedAt': '1970-01-01T02:45:00.123456789Z'}
        with tempfile.TemporaryDirectory() as d, patch.object(watchdog, 'container_state', return_value=state), patch('datetime.datetime') as parser, patch.object(watchdog.subprocess, 'run') as restart, patch.object(watchdog.time, 'time', return_value=10000):
            parser.fromisoformat.side_effect = strict_parse
            watchdog.check(Path(d))
            parser.fromisoformat.assert_called_once()
            restart.assert_not_called()
