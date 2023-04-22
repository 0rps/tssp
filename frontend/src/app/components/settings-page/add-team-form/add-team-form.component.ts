import {Component, Input, ViewChild} from '@angular/core';
import {NgForm} from "@angular/forms";
import {ITeamConfiguration} from "../../../interfaces/team.interface";
import {TeamsProvider} from "../../../services/teams.provider";

@Component({
  selector: 'app-add-team-form',
  templateUrl: './add-team-form.component.html',
  styleUrls: ['./add-team-form.component.scss']
})
export class AddTeamFormComponent {
  @Input() disabled = false;

  model = {} as ITeamConfiguration;

  @ViewChild(NgForm) private form!: NgForm;

  constructor(private provider: TeamsProvider) {
  }

  onSubmit() {
    this.form.control.markAllAsTouched();

    if (this.form.valid) {
      const data = transformFormDataToTeamConfig(this.model);
      this.provider.addTeam(data).subscribe(() => {
        console.log('success');
        this.form.resetForm({});
      });
    }
  }
}

function transformFormDataToTeamConfig(data: any) {
  const result = {...data};

  if (!data.bearer_token) {
    result['bearer_token'] = '';
  }

  return result;
}
