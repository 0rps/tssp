import {Injectable} from "@angular/core";
import {GameStateProvider} from "./game-state.provider";
import {catchError, map, Observable, of, switchMap, tap, throwError} from "rxjs";
import {IAdRequest} from "../interfaces/ad-request.interface";
import {ITeamsResponse} from "../interfaces/team.interface";

@Injectable({ providedIn: 'root'})
export class GameService {
  constructor(private provider: GameStateProvider) {
    this._loadFromLocalStorage();
  }

  private _loadFromLocalStorage() {
    const storedAdResponse = localStorage.getItem('lastAdResponse');
    if (storedAdResponse) {
      this.lastAdResponse = JSON.parse(storedAdResponse);
    }
  }

  private _saveToLocalStorage() {
    localStorage.setItem('lastAdResponse', JSON.stringify(this.lastAdResponse))
  }

  lastAdResponse: IAdRequest | null = null;

  nextRound(): Observable<IAdRequest> {
    return this.checkConsistency().pipe(
      switchMap(() => this.provider.sendAdRequest()),
      tap(data => {
        this.lastAdResponse = data;
        this._saveToLocalStorage();
      })
    );
  }

  currentRound(): Observable<IAdRequest | null> {
    return this.checkConsistency().pipe(map(() => this.lastAdResponse));
  }

  getScoreboard(): Observable<ITeamsResponse> {
    return this.provider.getGameState().pipe(map(state => state.teams));
  }

  checkConsistency(): Observable<boolean> {
    return this.provider.getGameState().pipe(
      map(actualState =>
        (this.lastAdResponse && this.lastAdResponse.round === actualState.round) ||
        (this.lastAdResponse === null && actualState.round == 0)
      ),
      switchMap(isStateConsistent => isStateConsistent ? of(true) : throwError(() => "Not consistent state. Reset the game.")),
      catchError(err => {
        if (typeof err === 'string') {
          alert(err);
        }
        return throwError(err);
      })
    )
  }

  reset(): Observable<void> {
    return this.provider.reset().pipe(
      tap(() => {
        this.lastAdResponse = null;
        this._saveToLocalStorage();
      }),
      map(() => void 0),
    );
  }
}
