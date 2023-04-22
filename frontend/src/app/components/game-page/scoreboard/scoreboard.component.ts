import {Component, Input} from '@angular/core';
import {ITeamsResponse} from "../../../interfaces/team.interface";

@Component({
  selector: 'app-scoreboard',
  templateUrl: './scoreboard.component.html',
  styleUrls: ['./scoreboard.component.scss']
})
export class ScoreboardComponent {
  @Input() teams: ITeamsResponse = [];

  displayedColumns: string[] = ['name', 'imps', 'clicks', 'conversions', 'score'];

  constructor() {
  }

  ngOnInit() {
  }

}
