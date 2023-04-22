import {Injectable} from "@angular/core";
import {
  catchError, EMPTY, Observable,
  ReplaySubject,
  switchMap, take, tap,
} from "rxjs";
import {IAdRequest} from "../interfaces/ad-request.interface";
import {GameService} from "./game.service";
import {ITeamsResponse} from "../interfaces/team.interface";
import {fromPromise} from "rxjs/internal/observable/innerFrom";

@Injectable({providedIn: 'root'})
export class GameStateService {
  constructor(private gameService: GameService) {
    this.gameService.currentRound()
      .pipe(take(1))
      .subscribe(state => {
        this.state$.next(state);
      });
  }

  state$ = new ReplaySubject<IAdRequest | null>(1);

  nextRound() {
    return this.gameService.nextRound()
      .pipe(
        catchError((error) => {
          console.error('Error while fetching data:', error);
          return EMPTY; // In case of error, return an empty observable
        }),
        tap((data) => {
          this.state$.next(data); // Emit the fetched data on the data$ stream
        })
      )
  }

  resetGame(): Observable<void> {
    const promise = new Promise<void>((resolve, reject) => {
      this.gameService.reset().pipe(
        switchMap(() => this.gameService.currentRound()),
        take(1),
      ).subscribe(
        {
          next: (state) => {
            this.state$.next(state);
            resolve(void 0);
          },
          error: (error) => reject(error),
        }
      )
    });

    return fromPromise(promise);
  }

  getScoreboard(): Observable<ITeamsResponse> {
    return this.gameService.getScoreboard();
  }
}
