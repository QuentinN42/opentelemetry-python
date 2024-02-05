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
from unittest import TestCase

from opentelemetry.trace import (
    INVALID_SPAN,
    NoOpTracer,
    Span,
    Tracer,
    _agnosticcontextmanager,
    get_current_span,
)


class TestTracer(TestCase):
    def setUp(self):
        self.tracer = NoOpTracer()

    def test_start_span(self):
        with self.tracer.start_span("") as span:
            self.assertIsInstance(span, Span)

    def test_start_as_current_span_context_manager(self):
        with self.tracer.start_as_current_span("") as span:
            self.assertIsInstance(span, Span)

    def test_start_as_current_span_decorator(self):
        # using a list to track the mock call order
        lst = []

        class MockTracer(Tracer):
            def start_span(self, *args, **kwargs):
                return INVALID_SPAN

            @_agnosticcontextmanager  # pylint: disable=protected-access
            def start_as_current_span(self, *args, **kwargs):  # type: ignore
                lst.append(1)
                yield INVALID_SPAN
                lst.append(9)

        mock_tracer = MockTracer()

        # test 1 : sync function
        @mock_tracer.start_as_current_span("name")
        def function_sync():  # type: ignore
            lst.append(5)

        lst = []
        function_sync()
        self.assertEqual(lst, [1, 5, 9])

        # test 2 : async function
        @mock_tracer.start_as_current_span("name")
        async def function_async():  # type: ignore
            lst.append(5)

        lst = []
        asyncio.run(function_async())
        self.assertEqual(lst, [1, 5, 9])

    def test_get_current_span(self):
        with self.tracer.start_as_current_span("test") as span:
            get_current_span().set_attribute("test", "test")
            self.assertEqual(span, INVALID_SPAN)
            self.assertFalse(hasattr("span", "attributes"))
