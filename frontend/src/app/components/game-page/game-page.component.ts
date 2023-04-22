import {Component, OnInit} from "@angular/core";
import {UntilDestroy, untilDestroyed} from "@ngneat/until-destroy";
import {GameStateService} from "../../services/game-state.service";
import {UiSettingsService} from "../../services/ui-settings.service";
import {filter, take} from "rxjs";
import {Router} from "@angular/router";


@UntilDestroy()
@Component({
  selector: 'app-game-page',
  templateUrl: './game-page.component.html',
  styleUrls: ['./game-page.component.scss']
})
export class GamePageComponent implements OnInit {

  showScoreboard = false;
  nextRoundButtonIsActive = true;

  scoreBoard$ = this.gameState.getScoreboard();

  constructor(
    private router: Router,
    public gameState: GameStateService,
    public uiSettings: UiSettingsService,
  ) {
  }

  ngOnInit() {
    this.gameState.state$.subscribe((state) => {
      // if (!this.nextRoundButtonIsActive && state?.has_next_round && this.uiSettings.getSettings().autoAuction) {
      //   this.nextRound();
      // }
      this.nextRoundButtonIsActive = true;
    })
  }

  startGame() {
    // this.gameState.nextRound();
    this.nextRound()
  }

  nextRound() {
    this.nextRoundButtonIsActive = false;
    this.gameState.nextRound().subscribe(
      (state) => {
        this.nextRoundButtonIsActive = true;
        if (state?.has_next_round && this.uiSettings.getSettings().autoAuction) {
          this.nextRound();
        }
      }
    );
  }

  onScoreboardButtonClick() {
    this.showScoreboard = true;
    this.gameState.state$
      .pipe(
        untilDestroyed(this),
        filter(state => state === null || state.has_next_round),
        take(1),
      )
      .subscribe(() => {
        this.showScoreboard = false;
      })
  }

  reset() {
    this.nextRoundButtonIsActive = true;
    this.gameState.resetGame()
      .pipe(untilDestroyed(this))
      .subscribe(() => {
        this.showScoreboard = false;
        this.router.navigate(['/settings'])
      });
  }
}
