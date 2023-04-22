import logging

from app.configurator import crud
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

logger = logging.getLogger(__name__)

ads_txt_router = r = APIRouter()


@r.get("/ads.txt", response_class=PlainTextResponse, status_code=200)
async def read_ssp_config(publisher: str = "unknown_publisher"):
    if publisher == "unknown_publisher":
        raise HTTPException(status_code=404, detail="publisher is not found")

    sites = crud.Website.objects(site__domain=publisher)
    if sites.count() == 0:
        raise HTTPException(status_code=404, detail="publisher is not found")

    return PlainTextResponse(sites[0].ads_txt_data)
