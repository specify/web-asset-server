"""Bound thumbnail work and waiting requests without spawning extra workers."""
from threading import BoundedSemaphore


class ThumbnailGate:
    def __init__(self, concurrency=1, queue_size=5):
        if concurrency < 1 or queue_size < 0:
            raise ValueError('Thumbnail concurrency must be positive and queue size nonnegative')
        self.active = BoundedSemaphore(concurrency)
        self.admitted = BoundedSemaphore(concurrency + queue_size)

    def acquire(self, timeout=20):
        if timeout < 0:
            raise ValueError('Thumbnail queue timeout must be nonnegative')
        if not self.admitted.acquire(blocking=False):
            return False
        try:
            if self.active.acquire(timeout=timeout):
                return True
        except BaseException:
            self.admitted.release()
            raise
        self.admitted.release()
        return False

    def release(self):
        self.active.release()
        self.admitted.release()
