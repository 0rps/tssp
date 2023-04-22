import json

import httpx
from app.celery_app import app
from app.configurator.constants import get_game_settings
from app.core.services import TimeoutResponse, UnknownErrorResponse
from celery.utils.log import get_task_logger
from httpx import TimeoutException
from starlette import status

logger = get_task_logger(__name__)


@app.task()
def notify(url, payload, win, bearer_token):
    _notify(url, payload, win, bearer_token)


def _notify(url, payload, win, bearer_token):
    game_settings = get_game_settings()

    headers = {
        "Content-Type": "application/json",
    }
    if bearer_token:
        headers["Authorization"] = "Bearer " + bearer_token

    try:
        _type = "win" if win else "loss"
        logger.info(f"[notify] sending {_type} to url {url}")
        if isinstance(payload, str):
            payload = json.loads(payload)

        r = httpx.post(url, json=payload, headers=headers, timeout=game_settings.DSP_RESPONSE_TIMEOUT)
        if r.status_code == status.HTTP_200_OK:
            logger.info(f"[notify] got OK response from url {url}")
        else:
            logger.warning(f"[notify] got response {r.status_code} from url {url}")
    except TimeoutException as ex:
        logger.warning(f"[notify] request was timed out from url {url}: {ex}")
        r = TimeoutResponse(request=None)
    except Exception as ex:
        logger.warning(f"[notify] got error from url {url}: {ex}")
        r = UnknownErrorResponse(request=None, text=f"{ex} ({type(ex).__name__})")
    return r
