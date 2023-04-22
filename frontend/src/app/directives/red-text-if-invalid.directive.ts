import {Directive, HostBinding, Input} from '@angular/core';
import {AbstractControl} from "@angular/forms";

@Directive({
  selector: '[appRedTextIfInvalid][control]'
})
export class RedTextIfInvalidDirective {

  @HostBinding('class.text-red-500') showInvalidity = false;

  @Input() public control!: AbstractControl;

  ngDoCheck() {
    if (this.control) {
      this.showInvalidity = this.control.invalid && this.control.touched;
    }
  }

}
