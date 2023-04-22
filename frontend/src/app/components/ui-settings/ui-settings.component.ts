import { Component } from '@angular/core';
import {SettingProp, UiSettingsService} from "../../services/ui-settings.service";
import {GameStateService} from "../../services/game-state.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-ui-settings',
  templateUrl: './ui-settings.component.html',
  styleUrls: ['./ui-settings.component.scss']
})
export class UiSettingsComponent {

  constructor(
    private router: Router,
    private gameState: GameStateService,
    public uiSettings: UiSettingsService,
  ) {
  }

  model = this.uiSettings.getSettings();

  settingsList: { prop: SettingProp, label: string}[] = [
    { prop: 'showTeamImplClConv', label: 'Show team imp, click, conv' },
    { prop: 'showFinalProbabilities', label: 'Show final probabilities' },
    { prop: 'showLogs', label: 'Show logs' },
    { prop: 'showCreativeExtraMeta', label: 'Show creative extra meta' },
    { prop: 'autoAuction', label: 'Auto auction' },
    // { prop: 'showExtraParam1', label: '*Show additional parameter 1%' },
  ]

  onGameResetClick() {
    this.gameState.resetGame().subscribe(
      () =>  this.router.navigate(['/settings'])
    );
  }
}
