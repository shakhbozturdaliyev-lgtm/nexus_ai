"""Bounded retry mechanism with exponential backoff and jitter."""

import asyncio
import random
from typing import Any, Callable, Tuple, Type
from backend.app.core.logging import logger


async def retry_async(
    func: Callable[..., Any],
    *args: Any,
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 3.0,
    retryable_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    **kwargs: Any,
) -> Any:
    """Execute async function with exponential backoff and random jitter."""
    attempt = 0
    while True:
        attempt += 1
        try:
            return await func(*args, **kwargs)
        except retryable_exceptions as e:
            if attempt >= max_attempts:
                logger.error(
                    f"Action failed after {attempt} attempts. Final error: {e}"
                )
                raise

            # Exponential backoff with jitter
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            jitter = random.uniform(0, delay * 0.2)
            sleep_time = delay + jitter

            logger.warning(
                f"Attempt {attempt}/{max_attempts} failed ({e}). Retrying in {sleep_time:.2f}s..."
            )
            await asyncio.sleep(sleep_time)
