import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-logs',
  templateUrl: './show-logs.component.html',
  styleUrls: ['./show-logs.component.scss']
})
export class ShowLogsComponent {
  @Input() logs: any = {};
}
