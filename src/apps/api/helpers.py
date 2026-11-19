import functools
import inspect
import time
from contextlib import contextmanager

from pyinstrument import Profiler


def do_profiling(func):

    def save_profile(profiler, func):
        filename = f"profiling_{func.__name__}_{time.time()}.html"
        profiler.write_html(filename)
        print(f"Profile saved to {filename}")

    @contextmanager
    def profiling(func, *, async_mode: bool = False):
        profiler = Profiler(
            interval=0.001, async_mode="enabled" if async_mode else "disabled"
        )
        profiler.start()
        try:
            yield
        finally:
            profiler.stop()
            save_profile(profiler, func)

    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def sync_wrapper(*args, **kwargs):
            with profiling(func, async_mode=True):
                return await func(*args, **kwargs)

        return sync_wrapper
    else:

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with profiling(func):
                return func(*args, **kwargs)

        return sync_wrapper
