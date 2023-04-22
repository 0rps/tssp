from app.ssp import crud as ssp_crud
from app.ssp.documents import Team, Website
from fastapi import Depends


def get_random_website() -> Website:
    return Website.get_random_active()


async def get_team(team_name: str | None = None):
    team = None
    if team_name:
        team = ssp_crud.get_teams(name=team_name).first()
    return team


def get_teams(team: Team | None = Depends(get_team)):
    if team:
        teams = [team]
    else:
        teams = list(ssp_crud.get_teams())
    return teams
