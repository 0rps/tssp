import {ITeam} from "./team.interface";

type GameState = 'new_game' | 'in_progress' | 'finished';

export interface IGameState {
  state: GameState;
  round: number;
  teams: ITeam[];
}
