import json
import logging
from base64 import b64encode

import mongoengine as me

from app.adstxt.router import ads_txt_router
from app.configurator.router import configurator_router
from app.core.db import connect_to_db
from app.core.logging import configure_logging
from app.core.middleware import ACASessionMiddleware, RequestIdMiddleware
from app.settings import get_app_settings
from app.ssp.router import ssp_router
from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from starlette.responses import RedirectResponse, Response

from aioprometheus import MetricsMiddleware
from aioprometheus.asgi.starlette import metrics

# NOTE: it is needed to register all counters/gauges/histograms
import app.metrics as _

logger = logging.getLogger(__name__)

app = FastAPI(
    title="RTB game SSP",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)

# FIXME: turn on
# app.add_middleware(ACASessionMiddleware)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(MetricsMiddleware)

@app.on_event("startup")
async def start_app():
    connect_to_db()
    configure_logging()


@app.on_event("shutdown")
async def disconnect_from_db():
    me.disconnect()


app.add_route("/metrics", metrics)
app.include_router(ssp_router, prefix="/api")
app.include_router(configurator_router, prefix="/api/config", tags=["config"])
app.include_router(ads_txt_router, tags=["ads_txt"])


@app.get("/api/")
async def root():
    return {"status": "ok"}


@app.post("/api/auth/", tags=["auth"], status_code=302)
async def login(password: str = Body(embed=True)):
    s = get_app_settings()

    if password == s.VALID_PASSWORD:
        data = b64encode(json.dumps(s.VALID_PASSKEY).encode("utf-8"))
        max_age = 3 * 24 * 60 * 60  # 3 days, in seconds
        response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key=s.SESSION_COOKIE, value=data.decode("utf-8"), max_age=max_age, httponly=True)
        return response
    else:
        return Response("wrong password", status_code=status.HTTP_400_BAD_REQUEST)
