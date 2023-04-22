import {Router} from '@angular/router'
import {Component, Input, OnInit, ViewChild} from '@angular/core';
import {GameSettingsProvider} from "../../../services/game-settings.provider";
import {IGameConfiguration} from "./types";
import {NgForm} from "@angular/forms";


@Component({
  selector: 'app-game-config-form',
  templateUrl: './game-config-form.component.html',
  styleUrls: ['./game-config-form.component.scss']
})
export class GameConfigFormComponent implements OnInit {
  @Input() disabled = false;

  model = {} as IGameConfiguration;

  @ViewChild(NgForm) private form!: NgForm;

  constructor(
    private router: Router,
    private provider: GameSettingsProvider) {
  }

  ngOnInit() {
    this.provider.getConf().subscribe(config => {
      this.model = config;
    });
  }

  onSubmit() {
    this.form.control.markAllAsTouched();

    if (this.form.valid) {
      const data = transformFormDataToGameConfig(this.model);
      this.provider.setConf(data).subscribe(() => {
        this.router.navigate(['/game'])
      });
    }
  }

  gameModeChanged(event: any) {
    if (event === 'free') {
      this.model.frequency_capping_enabled = false
      this.model.blocked_categories_enabled = false
      this.model.frequency_capping = this.model.impressions_total
    } else {
      this.model.frequency_capping_enabled = true
      this.model.blocked_categories_enabled = true
    }
  }
}

function transformFormDataToGameConfig(data: any) {
  const fieldsToTransform: Array<keyof IGameConfiguration> = ['budget', 'click_revenue', 'conversion_revenue', 'frequency_capping', 'impression_revenue', 'impressions_total'];
  const result = {...data};

  for (const field of fieldsToTransform) {
    const value = result[field];
    if (typeof value === 'string') {
      result[field] = parseFloat(value);
    }
  }

  return result;
}
