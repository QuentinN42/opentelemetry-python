# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import contextlib
import functools
from typing import TYPE_CHECKING, Awaitable, Callable, Iterator, Union


if TYPE_CHECKING:
    from typing import TypeVar
    R = TypeVar("R")  # Return type
    P = TypeVar("P")  # Generic type for all arguments
    Pargs = TypeVar("Pargs")  # Generic type for arguments
    Pkwargs = TypeVar("Pkwargs")  # Generic type for arguments


class _AgnosticContextManager(
    contextlib._GeneratorContextManager[R]
):

    def __call__(  # type: ignore
        self, func: Callable[..., Union[R, Awaitable[R]]]
    ) -> Callable[..., Union[R, Awaitable[R]]]:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Pargs, **kwargs: Pkwargs) -> R:
                with self._recreate_cm():  # type: ignore
                    return await func(*args, **kwargs)  # type: ignore

            return async_wrapper
        return super().__call__(func)


def _agnosticcontextmanager(
    func: Callable[..., Iterator[R]]
) -> Callable[..., _AgnosticContextManager[R]]:
    @functools.wraps(func)
    def helper(*args: Pargs, **kwargs: Pkwargs) -> _AgnosticContextManager[R]:
        return _AgnosticContextManager(func, args, kwargs)  # type: ignore

    return helper
