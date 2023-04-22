import {Injectable} from "@angular/core";
import {HttpClient} from "@angular/common/http";
import {environment} from "../../environments/environment";
import {Observable} from "rxjs";
import {IGameConfiguration} from "../components/settings-page/game-config-form/types";
import {BaseProvider} from "./base.provider";

@Injectable({ providedIn: 'root'})
export class GameSettingsProvider extends BaseProvider {
  private url = environment.apiUrl + 'config/';

  constructor(protected override http: HttpClient) {
    super(http);
  }

  getConf(): Observable<IGameConfiguration> {
    return this.get<IGameConfiguration>(this.url);
  }

  setConf(configuration: IGameConfiguration): Observable<void> {
    return this.post<void>(this.url, configuration);
  }
}
