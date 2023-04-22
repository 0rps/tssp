import logging

from app.configurator import crud
from app.configurator.documents import GameConfig
from app.configurator.schemas import (
    GameCfgDSPSchema,
    GameCfgSSPSchema,
    SetDspConfigRespSchema,
)
from app.ssp.dependencies import get_teams
from fastapi import APIRouter, Depends, HTTPException

logger = logging.getLogger(__name__)

configurator_router = r = APIRouter()


@r.get("/", response_model=GameCfgSSPSchema)
async def read_ssp_config():
    cfg = crud.get_game_config()
    if not cfg:
        cfg = GameConfig.apply_template()
    return cfg


@r.post("/", response_model=GameCfgSSPSchema, status_code=200)
async def set_ssp_config(
        updated_cfg: GameCfgSSPSchema, teams: list = Depends(get_teams),
        game_cfg: GameConfig = Depends(crud.get_game_config)
):
    if game_cfg and game_cfg.current_round != 0:
        raise HTTPException(status_code=400, detail="Forbidden: game has already started, reset game to change config")
    cfg = crud.update_game_config(updated_cfg, game_cfg)
    await crud.send_cfg_to_dsps(teams, game_cfg=cfg)
    return cfg


@r.get("/dsp/", response_model=GameCfgDSPSchema)
async def read_dsp_config():
    cfg = crud.get_game_config()
    return cfg


@r.post("/dsp/", response_model=SetDspConfigRespSchema)
async def set_dsp_config(teams: list = Depends(get_teams)):
    response = await crud.send_cfg_to_dsps(teams)
    return response
