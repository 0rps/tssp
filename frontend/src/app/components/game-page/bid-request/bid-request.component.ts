import {Component, Input} from '@angular/core';
import {IBidRequest} from "../../../interfaces/bid-request.interface";
import {UiSettingsService} from "../../../services/ui-settings.service";

@Component({
  selector: 'app-bid-request',
  templateUrl: './bid-request.component.html',
  styleUrls: ['./bid-request.component.scss']
})
export class BidRequestComponent {
  @Input() bidRequest?: IBidRequest;

  constructor(public uiSettings: UiSettingsService) {
  }

  showCreativeExtraMeta() {
    if (this.uiSettings.getSettings().showCreativeExtraMeta === false) {
      return false
    }

    if (this.bidRequest?.bcat) {
      return this.bidRequest.bcat.length > 0
    }
    return false
  }
}
