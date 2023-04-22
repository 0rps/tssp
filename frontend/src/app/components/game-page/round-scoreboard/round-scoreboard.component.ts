import {Component, Input} from '@angular/core';
import {ITeamsResponse} from "../../../interfaces/team.interface";
import {UiSettingsService} from "../../../services/ui-settings.service";
import {UntilDestroy, untilDestroyed} from "@ngneat/until-destroy";

@UntilDestroy()
@Component({
  selector: 'app-round-scoreboard',
  templateUrl: './round-scoreboard.component.html',
  styleUrls: ['./round-scoreboard.component.scss']
})
export class RoundScoreboardComponent {
  @Input() teams: ITeamsResponse = [];

  displayedColumns: string[] = [];

  constructor(private uiSettings: UiSettingsService) {
  }

  ngOnInit() {
    this.uiSettings.settings.showTeamImplClConv
      .pipe(untilDestroyed(this))
      .subscribe(value => {
        this.displayedColumns = value ? ['name', 'iclco', 'budget'] : ['name', 'budget']
      })
  }

}
