import time
import random
from typing import Callable, Optional, Type, Tuple

import httpx


class CircuitBreaker:
    """Simple circuit breaker with rolling window.
    - open after `failure_threshold` consecutive failures
    - half-open after `open_timeout` seconds
    - close after one success in half-open
    """
    def __init__(self, failure_threshold: int = 5, open_timeout: float = 30.0):
        self.failure_threshold = max(1, failure_threshold)
        self.open_timeout = max(1.0, open_timeout)
        self._failures = 0
        self._state = 'closed'  # closed | open | half-open
        self._opened_at: Optional[float] = None

    def allow(self) -> bool:
        if self._state == 'closed':
            return True
        if self._state == 'open':
            if self._opened_at is None:
                return False
            if time.time() - self._opened_at >= self.open_timeout:
                self._state = 'half-open'
                return True
            return False
        if self._state == 'half-open':
            return True
        return True

    def on_success(self):
        self._failures = 0
        self._state = 'closed'
        self._opened_at = None

    def on_failure(self):
        self._failures += 1
        if self._failures >= self.failure_threshold:
            self._state = 'open'
            self._opened_at = time.time()


def retry_with_jitter(
    func: Callable[[], any],
    retries: int = 3,
    base_delay: float = 0.2,
    max_delay: float = 2.0,
    retry_on: Tuple[Type[Exception], ...] = (Exception,),
):
    last_exc = None
    for attempt in range(retries + 1):
        try:
            return func()
        except retry_on as exc:
            last_exc = exc
            if attempt >= retries:
                break
            # decorrelated jitter backoff
            sleep_for = min(max_delay, base_delay + random.random() * (2 ** attempt) * base_delay)
            time.sleep(sleep_for)
    if last_exc:
        raise last_exc


def resilient_http_get(
    url: str,
    *,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: float = 5.0,
    retries: int = 3,
    circuit: Optional[CircuitBreaker] = None,
) -> httpx.Response:
    """HTTP GET with retry + optional circuit breaker."""
    if circuit and not circuit.allow():
        raise RuntimeError('circuit_open')

    def _do():
        resp = httpx.get(url, params=params, headers=headers, timeout=timeout)
        # Consider 5xx and 429 retriable
        if resp.status_code >= 500 or resp.status_code == 429:
            raise RuntimeError(f"http_{resp.status_code}")
        return resp

    try:
        resp = retry_with_jitter(_do, retries=retries)
        if circuit:
            circuit.on_success()
        return resp
    except Exception:
        if circuit:
            circuit.on_failure()
        raise
