import json
from base64 import b64decode
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Callable, Optional
from uuid import uuid4

from app.settings import get_app_settings
from starlette.datastructures import URL, MutableHeaders
from starlette.requests import HTTPConnection
from starlette.responses import RedirectResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

x_request_id: ContextVar[Optional[str]] = ContextVar("x_request_id", default=None)
x_current_round: ContextVar[Optional[str]] = ContextVar("x_current_round", default=None)


@dataclass
class RequestIdMiddleware:
    app: ASGIApp
    header_name: str = "X-Request-ID"
    generator: Callable[[], str] = field(default=lambda: uuid4().hex)  # ID-generating callable

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Load request ID from headers if present. Generate one otherwise.
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Try to load request ID from the request headers
        headers = MutableHeaders(scope=scope)
        header_value = headers.get(self.header_name.lower())
        id_value = header_value or self.generator()

        # Update the request headers if needed
        if id_value != header_value:
            headers[self.header_name] = id_value

        x_request_id.set(id_value)

        async def handle_outgoing_request(message: "Message") -> None:
            if message["type"] == "http.response.start" and x_request_id.get():
                headers = MutableHeaders(scope=message)
                headers.append(self.header_name, x_request_id.get())

            await send(message)

        await self.app(scope, receive, handle_outgoing_request)
        return


class ACASessionMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        s = get_app_settings()

        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)
        url = URL(scope=scope)

        if not url.path.startswith("/api/"):
            await self.app(scope, receive, send)
            return

        value = None
        if s.SESSION_COOKIE in connection.cookies:
            try:
                data = connection.cookies[s.SESSION_COOKIE].encode("utf-8")
                value = json.loads(b64decode(data))
            except Exception:
                pass

        is_logged_in = value == s.VALID_PASSKEY
        is_on_login = url.path == "/api/auth/"

        if (is_logged_in and not is_on_login) or (not is_logged_in and is_on_login):
            await self.app(scope, receive, send)
        else:
            if is_logged_in and url.path == "/api/auth/":
                url = url.replace(path="/")
            if not is_logged_in and url.path != "/api/auth/":
                url = url.replace(path="/login/")
            response = RedirectResponse(url, status_code=302)
            await response(scope, receive, send)
