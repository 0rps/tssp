import {Component} from "@angular/core";
import {GameStateService} from "../../services/game-state.service";

@Component({
  selector: 'app-settings-page',
  templateUrl: './settings-page.component.html',
  styleUrls: ['./settings-page.component.scss']
})
export class SettingsPageComponent {
  constructor(public gameState: GameStateService) {
  }
}
