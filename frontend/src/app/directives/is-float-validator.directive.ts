import { Directive } from '@angular/core';
import { AbstractControl, NG_VALIDATORS, ValidationErrors, Validator, Validators } from "@angular/forms";

@Directive({
  selector: '[appIsFloatValidator]',
  providers: [{
    provide: NG_VALIDATORS,
    useExisting: IsFloatValidatorDirective,
    multi: true,
  }]
})
export class IsFloatValidatorDirective implements Validator {
  validate(control: AbstractControl): ValidationErrors | null {
    return Validators.pattern(/^-?\d+$/)(control);
  }
}
