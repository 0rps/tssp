import {Component, Input} from '@angular/core';
import {TeamsProvider} from "../../../services/teams.provider";
import {HttpClient} from "@angular/common/http";
import {Observable, Subject, switchMap, tap} from "rxjs";
import {ITeamConfiguration, ITeamResponse} from "../../../interfaces/team.interface";

@Component({
  selector: 'app-teams-configuration',
  templateUrl: './teams-configuration.component.html',
  styleUrls: ['./teams-configuration.component.scss'],
  providers: [{
    provide: TeamsProvider,
    useFactory: (httpClient: HttpClient) => {
      return new (
        class extends TeamsProvider {
          private fetch$ = new Subject<void>();

          override getList() {
            return new Observable<ITeamResponse[]>(observer => {
              const subscription = this.fetch$
                .pipe(switchMap(() => super.getList()))
                .subscribe(observer);
              this.fetch$.next();
              return subscription;
            });
          }

          override addTeam(configuration: ITeamConfiguration) {
            return super.addTeam(configuration).pipe(tap(() => this.fetch$.next()));
          }

          override remove(id: string) {
            return super.remove(id).pipe(tap(() => this.fetch$.next()))
          }
        }
      )(httpClient);
    }
    ,
    deps: [HttpClient]
  }]
})
export class TeamsConfigurationComponent {
  @Input() disabled = false;

}
