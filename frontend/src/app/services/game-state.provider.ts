import {Injectable} from "@angular/core";
import {HttpClient} from "@angular/common/http";
import {map, Observable, switchMap} from "rxjs";
import {IGameState} from "../interfaces/game-state.interface";
import {environment} from "../../environments/environment";
import {IAdRequest} from "../interfaces/ad-request.interface";
import {BaseProvider} from "./base.provider";

@Injectable({providedIn: 'root'})
export class GameStateProvider extends BaseProvider {
  private url = environment.apiUrl + 'game/';

  constructor(protected override http: HttpClient) {
    super(http);
  }

  sendAdRequest(): Observable<IAdRequest> {
    return this.post<IAdRequest>(`${this.url}adrequest/`, {}).pipe(
      map(req => {
        if (req.bidresponse && !Object.keys(req.bidresponse).length) {
          req.bidresponse = null;
        }
        return req;
      }),
    );
  }

  getGameState(): Observable<IGameState> {
    return this.get<IGameState>(`${this.url}state/`);
  }

  reset(): Observable<IGameState> {
    return this.post<IGameState>(`${this.url}reset/`, {}).pipe(
      switchMap(() => this.getGameState()),
    );
  }
}
