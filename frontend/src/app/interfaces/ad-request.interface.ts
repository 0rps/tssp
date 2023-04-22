import {IBidRequest} from "./bid-request.interface";
import {IBidResponse} from "./bid-response.interface";
import {ITeamsResponse} from "./team.interface";

export interface IAdRequest {
  round: number,
  has_next_round: boolean,
  bidrequest: IBidRequest,
  bidresponse: IBidResponse | null,
  teams: ITeamsResponse,
  logs: any,
}
