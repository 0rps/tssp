import {Component, Input} from '@angular/core';
import {TeamsProvider} from "../../../services/teams.provider";

@Component({
  selector: 'app-list-of-teams',
  templateUrl: './list-of-teams.component.html',
  styleUrls: ['./list-of-teams.component.scss']
})
export class ListOfTeamsComponent {
  @Input() disabled = false;

  list$ = this.provider.getList();

  constructor(private provider: TeamsProvider) {
  }

  remove(id: string) {
    this.provider.remove(id).subscribe(() => {
      console.log('success');
    });
  }

}
