from concurrent.futures import ThreadPoolExecutor
from threading import Event, Lock
import time
import unittest
from thumbnail_gate import ThumbnailGate


class ThumbnailGateTests(unittest.TestCase):
    def test_six_parallel_requests_are_serialized_without_rejection(self):
        gate = ThumbnailGate(1, 5)
        lock = Lock()
        active = maximum = 0
        def job(_):
            nonlocal active, maximum
            if not gate.acquire(timeout=2):
                return False
            try:
                with lock:
                    active += 1
                    maximum = max(maximum, active)
                time.sleep(.02)
                with lock:
                    active -= 1
                return True
            finally:
                gate.release()
        with ThreadPoolExecutor(6) as pool:
            self.assertTrue(all(pool.map(job, range(6))))
        self.assertEqual(maximum, 1)

    def test_full_queue_rejects_and_timeout_frees_capacity(self):
        gate = ThumbnailGate(1, 1)
        self.assertTrue(gate.acquire(timeout=0))
        queued = Event()
        def waiter():
            queued.set()
            return gate.acquire(timeout=.1)
        with ThreadPoolExecutor(1) as pool:
            result = pool.submit(waiter)
            queued.wait()
            # Wait until the pending request has consumed its admission slot.
            deadline = time.monotonic() + 1
            while gate.admitted._value and time.monotonic() < deadline:
                time.sleep(.001)
            self.assertFalse(gate.acquire(timeout=0))
            self.assertFalse(result.result())
        gate.release()
        self.assertTrue(gate.acquire(timeout=0))
        gate.release()
