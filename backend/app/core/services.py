import asyncio
import datetime
import logging
from dataclasses import dataclass
from typing import Callable, Optional
from urllib.parse import urljoin

import httpx
from httpx import TimeoutException
from httpx._types import RequestData

from app.core.const import HTTP_CODE_DSP_RESPONSE_UNKNOWN_ERROR, HTTP_CODE_DSP_RESPONSE_TIMEOUT

logger = logging.getLogger(__name__)


@dataclass
class TimeoutResponse:
    request: httpx.Request | None
    text: str = "HttpRequest timed out"
    status_code: int = HTTP_CODE_DSP_RESPONSE_TIMEOUT


@dataclass
class UnknownErrorResponse:
    request: httpx.Request | None
    text: str
    status_code: int = HTTP_CODE_DSP_RESPONSE_UNKNOWN_ERROR


async def log_request(request: httpx.Request):
    # logger.info("[SSP-REQUEST] SENDING %s %s", request.method, request.url)
    pass


async def log_response(response: httpx.Response):
    await response.aread()
    request = response.request
    logger.superinfo(
        "[SSP-RESPONSE] method=%s url=%s status=%s, body=%s",
        request.method,
        request.url,
        response.status_code,
        "%.10000s" % response.text,
    )


class SspApiAggregator:
    def __init__(
        self,
        hosts: list,
        *,
        path: str = "",
        config: dict = None,
        req_kwargs: dict = None,
        response_handler: Callable = None,
    ):
        self.hosts = hosts
        self.path = path
        self.config = self.default_config
        self.config.update(config or dict())
        self.req_kwargs = req_kwargs or dict()
        self.resp_handler = response_handler or self.default_handler

    @property
    def default_config(self) -> dict:
        return dict(timeout=10, event_hooks={"request": [log_request], "response": [log_response]})

    def default_handler(self, response: httpx.Response, duration: datetime.timedelta | None) -> dict:
        return dict(response=response, request_duration=duration)

    async def send_request(self, client: httpx.AsyncClient, method: str, host: str, payload: Optional[RequestData]):
        extra_kwargs = self.req_kwargs.get(host, dict())
        headers = extra_kwargs.get("headers", dict())
        headers["Content-Type"] = "application/json"
        extra_kwargs["headers"] = headers

        url = urljoin(host, self.path)

        logger.superinfo(
            "[SSP-REQUEST] method=%s url=%s payload=%s extra_kwargs=%s", method, url, payload, extra_kwargs
        )
        request = client.build_request(method, url, json=payload, **extra_kwargs)

        request_duration = None
        request_start = datetime.datetime.utcnow()

        try:
            response = await client.send(request)
            request_duration = datetime.datetime.utcnow() - request_start
        except TimeoutException:
            request_duration = datetime.datetime.utcnow() - request_start
            response = TimeoutResponse(request=request)
        except Exception as ex:
            text = f"{ex} ({type(ex).__name__})"
            response = UnknownErrorResponse(request=request, text=text)

        result = self.resp_handler(response, request_duration)
        return host, result

    async def fetch(
        self, method: str, payload: Optional[RequestData] = None, payload_map: Optional[dict] = None
    ) -> dict:
        assert not (payload and payload_map)
        async with httpx.AsyncClient(**self.config) as client:
            tasks = []
            for host in self.hosts:
                if payload_map:
                    payload = payload_map[host]
                tasks.append(self.send_request(client, method, host, payload))
            results = await asyncio.gather(*tasks)
        return dict(results)

    async def get(self) -> dict:
        return await self.fetch("GET")

    async def post(self, *, payload: Optional[RequestData] = None, payload_map: Optional[dict] = None) -> dict:
        return await self.fetch("POST", payload, payload_map)

    async def put(self, *, payload: Optional[RequestData] = None, payload_map: Optional[dict] = None) -> dict:
        return await self.fetch("PUT", payload, payload_map)
