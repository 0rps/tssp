import {Injectable} from "@angular/core";
import {HttpClient} from "@angular/common/http";
import {environment} from "../../environments/environment";
import {Observable} from "rxjs";
import {ITeamConfiguration, ITeamResponse} from "../interfaces/team.interface";
import {BaseProvider} from "./base.provider";

@Injectable({ providedIn: 'root'})
export class TeamsProvider extends BaseProvider {
  private url = environment.apiUrl + 'teams/';

  constructor(protected override http: HttpClient) {
    super(http);
  }

  getList(): Observable<ITeamResponse[]> {
    return this.get<ITeamResponse[]>(this.url);
  }

  addTeam(configuration: ITeamConfiguration): Observable<void> {
    return this.post<void>(this.url, configuration);
  }

  remove(id: string): Observable<void> {
    return this.delete<void>(`${this.url}${id}/`);
  }
}
