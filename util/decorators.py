import asyncio
from timeit import default_timer

from loguru import logger


def timeit(func):
    async def timeit_wrapper(*args, **kwargs):
        start_time = default_timer()
        result = await func(*args, **kwargs)
        end_time = default_timer()
        total_time = end_time - start_time

        # logger.info(f"Function {func.__name__}{args} - [{kwargs}]: {total_time:.4f}s")
        #
        logger.info(f"Function {func.__name__}]: {total_time:.4f}s")
        return result

    return timeit_wrapper


def sync_timeit(func):
    def timeit_wrapper(*args, **kwargs):
        start_time = default_timer()
        result = func(*args, **kwargs)
        end_time = default_timer()
        total_time = end_time - start_time

        # logger.info(f"Function {func.__name__}{args} - [{kwargs}]: {total_time:.4f}s")
        logger.info(f"Function {func.__name__}: {total_time:.4f}s")
        return result

    return timeit_wrapper


def debug(func):
    def debug_wrapper(*args, **kwargs):
        logger.debug(f"{func.__name__}{args} - [{kwargs}]: ...")
        return func(*args, **kwargs)

    return debug_wrapper


def ignore_timeout(f):
    async def wrapper(*arg, **kwargs):
        try:
            await f(*arg, **kwargs)
        except Exception as e:
            print("Ignoring timeout:", e)

    return wrapper


# def save_file(self, path, response):
#     Path(path).parent.mkdir(parents=True, exist_ok=True)
#     with open(path, "wb") as f:
#         # f.write(response.content)
#         f.write(response)
#
