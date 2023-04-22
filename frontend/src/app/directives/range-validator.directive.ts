import {Directive, Input} from '@angular/core';
import {AbstractControl, NG_VALIDATORS, ValidationErrors, Validator, Validators} from "@angular/forms";

@Directive({
  selector: '[appRangeValidator]',
  providers: [{
    provide: NG_VALIDATORS,
    useExisting: RangeValidatorDirective,
    multi: true,
  }]
})
export class RangeValidatorDirective implements Validator {

  @Input() min?: number;
  @Input() max?: number;

  validate(control: AbstractControl): ValidationErrors | null {
    const errors = {} as ValidationErrors;

    if (this.min !== undefined) {
      Object.assign(errors, Validators.min(this.min)(control));
    }
    if (this.max !== undefined) {
      Object.assign(errors, Validators.max(this.max)(control));
    }

    return Object.keys(errors).length ? errors : null;
  }

}
