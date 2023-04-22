import {Component, Input} from "@angular/core";

@Component({
  selector: 'app-parameter[name]',
  template: `
    <span class="text-lg font-medium">{{name}}:&nbsp;<ng-content></ng-content></span>
  `,
  styles: [`
    :host {
      display: block;
    }
  `]
})
export class ParameterComponent {
  @Input() public name!: string;
}
