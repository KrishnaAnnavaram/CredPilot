"""Timeouts, bounded retries and graceful degradation for external calls.

NFR-04: *"Agent pipeline uses async where it calls tools/models; graceful
degradation on tool/model failure (timeouts, retries, exit conditions)."*

Three things an underwriting system must never do when a dependency misbehaves:

* **hang** — a file that never comes back is worse than one that comes back
  referred, so every external call carries a deadline;
* **retry forever** — an unbounded retry against a paid endpoint is an unbounded
  spend on one applicant's file, so attempts are capped and the cap is reported;
* **fail silently** — a tool that timed out and a tool that returned nothing look
  the same to a caller that only checks for ``None``, so failures come back as a
  typed :class:`ToolFailure` carrying which of the two it was.

What is **not** retried matters as much as what is. A retry is only correct for a
fault that might not recur: a timeout, a transport error, a 5xx. A malformed
response, a validation error or a refusal is deterministic — retrying it spends
money to receive the same answer — so those raise :class:`NonRetryableError` and
stop after one attempt.

Both a sync and an async surface are provided. The graph nodes are synchronous
because LangGraph invokes them that way and the retrieval stack is CPU-bound
local work; the MCP client and the model calls are genuinely I/O-bound and go
through the async surface.
"""

from __future__ import annotations

import asyncio
import functools
import random
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Iterable, Mapping, TypeVar

T = TypeVar("T")

#: Default deadline for one attempt at an external call, in seconds.
DEFAULT_TIMEOUT_SECONDS = 30.0

#: Total attempts, not retries: 3 means one try and two retries.
DEFAULT_MAX_ATTEMPTS = 3

#: First backoff interval. Doubles per attempt, with jitter, capped below.
DEFAULT_BACKOFF_SECONDS = 0.5
DEFAULT_MAX_BACKOFF_SECONDS = 8.0


class ResilienceError(RuntimeError):
    """Base class for the structured failures this module raises."""

    #: Whether another attempt could plausibly succeed.
    retryable = True

    def __init__(self, message: str, *, operation: str = "", cause: BaseException | None = None):
        super().__init__(message)
        self.operation = operation
        self.cause = cause

    @property
    def error_type(self) -> str:
        return type(self).__name__


class OperationTimeout(ResilienceError):
    """One attempt exceeded its deadline."""


class NonRetryableError(ResilienceError):
    """A fault that will recur identically — a malformed response, a bad request.

    Raising this short-circuits the retry loop. Spending three attempts to
    receive the same malformed payload three times is not resilience.
    """

    retryable = False


class RetryExhausted(ResilienceError):
    """Every permitted attempt failed.

    Carries the attempt count and the last cause so a caller can report *why* it
    gave up, which "returned None" cannot.
    """

    def __init__(self, message: str, *, operation: str, attempts: int,
                 cause: BaseException | None = None):
        super().__init__(message, operation=operation, cause=cause)
        self.attempts = attempts


class DependencyUnavailable(ResilienceError):
    """The dependency could not be reached at all — process gone, port closed."""


@dataclass
class RetryPolicy:
    """How many attempts, how long each may take, and how long to wait between.

    ``jitter`` is on by default. Without it, several callers that failed at the
    same moment retry at the same moment, which is how a recovering dependency
    gets knocked over a second time.
    """

    max_attempts: int = DEFAULT_MAX_ATTEMPTS
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    backoff_seconds: float = DEFAULT_BACKOFF_SECONDS
    max_backoff_seconds: float = DEFAULT_MAX_BACKOFF_SECONDS
    jitter: bool = True
    #: Exception types that are worth another attempt. Anything else propagates
    #: on the first failure.
    retry_on: tuple[type[BaseException], ...] = (
        OperationTimeout,
        DependencyUnavailable,
        TimeoutError,
        ConnectionError,
        OSError,
    )

    def delay_for(self, attempt: int) -> float:
        """Backoff before ``attempt`` (1-based); attempt 1 never waits."""
        if attempt <= 1:
            return 0.0
        raw = min(self.backoff_seconds * (2 ** (attempt - 2)), self.max_backoff_seconds)
        if not self.jitter:
            return raw
        # Full jitter. Bounded below by a tenth so a "retry" is never a busy loop.
        return max(raw * 0.1, random.uniform(0.0, raw))

    def as_dict(self) -> dict[str, Any]:
        return {
            "max_attempts": self.max_attempts,
            "timeout_seconds": self.timeout_seconds,
            "backoff_seconds": self.backoff_seconds,
            "max_backoff_seconds": self.max_backoff_seconds,
            "jitter": self.jitter,
        }


#: The policy used where a caller does not supply one.
DEFAULT_POLICY = RetryPolicy()


@dataclass
class ToolFailure:
    """A failure a caller can act on rather than an exception it must catch.

    Graph nodes degrade rather than raise: a retrieval that timed out should
    produce a referred file with "retrieval timed out" on it, not a traceback in
    a checkpoint. So the async helpers return this instead of propagating, and
    the node decides.
    """

    operation: str
    error_type: str
    message: str
    attempts: int = 1
    latency_ms: float = 0.0
    retryable: bool = True
    detail: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return False

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": False,
            "operation": self.operation,
            "error_type": self.error_type,
            "message": self.message,
            "attempts": self.attempts,
            "latency_ms": round(self.latency_ms, 1),
            "retryable": self.retryable,
            **({"detail": self.detail} if self.detail else {}),
        }

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.operation}: {self.error_type}: {self.message}"


@dataclass
class AttemptRecord:
    """One attempt's outcome, for the trace and the tool log."""

    attempt: int
    ok: bool
    latency_ms: float
    error_type: str | None = None
    message: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "attempt": self.attempt,
            "ok": self.ok,
            "latency_ms": round(self.latency_ms, 1),
            **({"error_type": self.error_type} if self.error_type else {}),
            **({"message": self.message[:200]} if self.message else {}),
        }


# ======================================================================================
# Async surface — the one the MCP client and the model calls use
# ======================================================================================


async def call_with_resilience(
    operation: str,
    fn: Callable[[], Awaitable[T]],
    *,
    policy: RetryPolicy | None = None,
    on_attempt: Callable[[AttemptRecord], None] | None = None,
) -> T:
    """Await ``fn`` under a deadline, retrying bounded faults.

    Raises :class:`RetryExhausted` when every attempt failed, or the original
    exception when it was not retryable. Use :func:`safe_call` to get a
    :class:`ToolFailure` back instead.
    """
    policy = policy or DEFAULT_POLICY
    last: BaseException | None = None

    for attempt in range(1, policy.max_attempts + 1):
        delay = policy.delay_for(attempt)
        if delay:
            await asyncio.sleep(delay)

        started = time.perf_counter()
        try:
            result = await asyncio.wait_for(fn(), timeout=policy.timeout_seconds)
        except asyncio.TimeoutError as exc:
            elapsed = (time.perf_counter() - started) * 1000
            last = OperationTimeout(
                f"{operation} exceeded its {policy.timeout_seconds:g}s deadline",
                operation=operation, cause=exc,
            )
            _record(on_attempt, attempt, False, elapsed, last)
        except NonRetryableError:
            raise
        except BaseException as exc:  # noqa: BLE001 - classified immediately below
            elapsed = (time.perf_counter() - started) * 1000
            _record(on_attempt, attempt, False, elapsed, exc)
            if not isinstance(exc, policy.retry_on):
                raise
            last = exc
        else:
            elapsed = (time.perf_counter() - started) * 1000
            _record(on_attempt, attempt, True, elapsed, None)
            return result

    raise RetryExhausted(
        f"{operation} failed after {policy.max_attempts} attempt(s): {last}",
        operation=operation, attempts=policy.max_attempts, cause=last,
    )


async def safe_call(
    operation: str,
    fn: Callable[[], Awaitable[T]],
    *,
    policy: RetryPolicy | None = None,
    on_attempt: Callable[[AttemptRecord], None] | None = None,
) -> "T | ToolFailure":
    """:func:`call_with_resilience`, but returning a :class:`ToolFailure`.

    The form graph nodes use: they have to produce a state update either way, so
    an exception is the wrong shape for them.
    """
    policy = policy or DEFAULT_POLICY
    started = time.perf_counter()
    attempts: list[AttemptRecord] = []

    def track(record: AttemptRecord) -> None:
        attempts.append(record)
        if on_attempt is not None:
            on_attempt(record)

    try:
        return await call_with_resilience(operation, fn, policy=policy, on_attempt=track)
    except RetryExhausted as exc:
        return ToolFailure(
            operation=operation,
            error_type=type(exc.cause).__name__ if exc.cause else "RetryExhausted",
            message=str(exc.cause or exc),
            attempts=exc.attempts,
            latency_ms=(time.perf_counter() - started) * 1000,
            retryable=True,
            detail={"attempts": [a.as_dict() for a in attempts]},
        )
    except ResilienceError as exc:
        return ToolFailure(
            operation=operation,
            error_type=exc.error_type,
            message=str(exc),
            attempts=len(attempts) or 1,
            latency_ms=(time.perf_counter() - started) * 1000,
            retryable=exc.retryable,
            detail={"attempts": [a.as_dict() for a in attempts]},
        )
    except BaseException as exc:  # noqa: BLE001 - the caller gets a value, not a traceback
        return ToolFailure(
            operation=operation,
            error_type=type(exc).__name__,
            message=str(exc)[:400],
            attempts=len(attempts) or 1,
            latency_ms=(time.perf_counter() - started) * 1000,
            retryable=False,
            detail={"attempts": [a.as_dict() for a in attempts]},
        )


# ======================================================================================
# Sync surface — for the graph nodes, which LangGraph calls synchronously
# ======================================================================================


def call_sync_with_resilience(
    operation: str,
    fn: Callable[[], T],
    *,
    policy: RetryPolicy | None = None,
    on_attempt: Callable[[AttemptRecord], None] | None = None,
) -> T:
    """Retry a synchronous call under a wall-clock budget.

    A synchronous call cannot be interrupted at its deadline without a thread, so
    the timeout here is checked **after** the call returns rather than enforced
    during it: an attempt that overran is treated as a failure and, once the
    total budget is spent, no further attempt is made. That is weaker than the
    async deadline and is stated plainly rather than papered over — genuinely
    I/O-bound work belongs on the async surface, which does enforce it.
    """
    policy = policy or DEFAULT_POLICY
    deadline = time.perf_counter() + policy.timeout_seconds * policy.max_attempts
    last: BaseException | None = None

    for attempt in range(1, policy.max_attempts + 1):
        if time.perf_counter() >= deadline:
            break
        delay = policy.delay_for(attempt)
        if delay:
            time.sleep(delay)

        started = time.perf_counter()
        try:
            result = fn()
        except NonRetryableError:
            raise
        except BaseException as exc:  # noqa: BLE001 - classified immediately below
            elapsed = (time.perf_counter() - started) * 1000
            _record(on_attempt, attempt, False, elapsed, exc)
            if not isinstance(exc, policy.retry_on):
                raise
            last = exc
        else:
            elapsed = (time.perf_counter() - started) * 1000
            if elapsed / 1000 > policy.timeout_seconds:
                last = OperationTimeout(
                    f"{operation} took {elapsed / 1000:.1f}s, over its "
                    f"{policy.timeout_seconds:g}s budget",
                    operation=operation,
                )
                _record(on_attempt, attempt, False, elapsed, last)
                continue
            _record(on_attempt, attempt, True, elapsed, None)
            return result

    raise RetryExhausted(
        f"{operation} failed after {policy.max_attempts} attempt(s): {last}",
        operation=operation, attempts=policy.max_attempts, cause=last,
    )


def safe_call_sync(
    operation: str,
    fn: Callable[[], T],
    *,
    policy: RetryPolicy | None = None,
    on_attempt: Callable[[AttemptRecord], None] | None = None,
) -> "T | ToolFailure":
    """:func:`call_sync_with_resilience`, returning a :class:`ToolFailure`."""
    policy = policy or DEFAULT_POLICY
    started = time.perf_counter()
    attempts: list[AttemptRecord] = []

    def track(record: AttemptRecord) -> None:
        attempts.append(record)
        if on_attempt is not None:
            on_attempt(record)

    try:
        return call_sync_with_resilience(operation, fn, policy=policy, on_attempt=track)
    except RetryExhausted as exc:
        return ToolFailure(
            operation=operation,
            error_type=type(exc.cause).__name__ if exc.cause else "RetryExhausted",
            message=str(exc.cause or exc),
            attempts=exc.attempts,
            latency_ms=(time.perf_counter() - started) * 1000,
            detail={"attempts": [a.as_dict() for a in attempts]},
        )
    except BaseException as exc:  # noqa: BLE001
        return ToolFailure(
            operation=operation,
            error_type=type(exc).__name__,
            message=str(exc)[:400],
            attempts=len(attempts) or 1,
            latency_ms=(time.perf_counter() - started) * 1000,
            retryable=isinstance(exc, ResilienceError) and exc.retryable,
            detail={"attempts": [a.as_dict() for a in attempts]},
        )


def run_async(coro: Awaitable[T], *, timeout: float | None = None) -> T:
    """Run a coroutine from synchronous code, including from inside a loop.

    LangGraph nodes are synchronous and the MCP client is not. Calling
    ``asyncio.run`` from a thread that already owns a running loop raises, which
    is exactly what happens when the graph is invoked from the FastAPI app, so
    that case is detected and the coroutine is handed to a worker thread with its
    own loop.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_with_timeout(coro, timeout))

    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(lambda: asyncio.run(_with_timeout(coro, timeout))).result()


async def _with_timeout(coro: Awaitable[T], timeout: float | None) -> T:
    if timeout is None:
        return await coro
    return await asyncio.wait_for(coro, timeout=timeout)


def _record(
    sink: Callable[[AttemptRecord], None] | None,
    attempt: int,
    ok: bool,
    latency_ms: float,
    error: BaseException | None,
) -> None:
    if sink is None:
        return
    sink(
        AttemptRecord(
            attempt=attempt,
            ok=ok,
            latency_ms=latency_ms,
            error_type=type(error).__name__ if error else None,
            message=str(error)[:200] if error else None,
        )
    )


def with_resilience(
    operation: str, *, policy: RetryPolicy | None = None
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Decorator form of :func:`call_with_resilience` for async functions."""

    def decorator(fn: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            return await call_with_resilience(
                operation, lambda: fn(*args, **kwargs), policy=policy
            )

        return wrapper

    return decorator


def first_failure(values: Iterable[Any]) -> ToolFailure | None:
    """The first :class:`ToolFailure` in a sequence of results, if any."""
    for value in values:
        if isinstance(value, ToolFailure):
            return value
    return None


def failure_summary(failures: Iterable[ToolFailure]) -> dict[str, Any]:
    """A compact roll-up of failures, for the state and the report."""
    items = list(failures)
    by_type: dict[str, int] = {}
    for failure in items:
        by_type[failure.error_type] = by_type.get(failure.error_type, 0) + 1
    return {
        "count": len(items),
        "by_error_type": dict(sorted(by_type.items())),
        "operations": sorted({f.operation for f in items}),
        "total_attempts": sum(f.attempts for f in items),
    }


def describe_policy(policy: RetryPolicy | None = None) -> Mapping[str, Any]:
    return (policy or DEFAULT_POLICY).as_dict()


__all__ = [
    "AttemptRecord",
    "DEFAULT_BACKOFF_SECONDS",
    "DEFAULT_MAX_ATTEMPTS",
    "DEFAULT_POLICY",
    "DEFAULT_TIMEOUT_SECONDS",
    "DependencyUnavailable",
    "NonRetryableError",
    "OperationTimeout",
    "ResilienceError",
    "RetryExhausted",
    "RetryPolicy",
    "ToolFailure",
    "call_sync_with_resilience",
    "call_with_resilience",
    "describe_policy",
    "failure_summary",
    "first_failure",
    "run_async",
    "safe_call",
    "safe_call_sync",
    "with_resilience",
]
