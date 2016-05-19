import asyncio
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
import types
import psutil


_pool = None


def future_run(f, *args, **kwargs):
    def run():
        v = f(*args, **kwargs)
        if isinstance(v, types.CoroutineType):
            try:
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(v)
            except RuntimeError as _:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return loop.run_until_complete(v)
        return v
    global _pool
    if _pool is None:
        _pool = ThreadPoolExecutor(psutil.cpu_count())

    return _pool.submit(run)


def coroutine_run(f, *args, **kwargs):
        _start_future = Future()
        _future = Future()

        def run():
            v = f(*args, **kwargs)
            if isinstance(v, types.CoroutineType):
                try:
                    loop = asyncio.get_event_loop()
                    v = loop.run_until_complete(v)
                except RuntimeError as _:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    v = loop.run_until_complete(v)
            _future.set_result(v)

        _start_future.add_done_callback(lambda *args, **kwargs: run())
        _start_future.set_result(True)
        return _future
