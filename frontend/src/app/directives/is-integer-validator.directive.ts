import { Directive } from '@angular/core';
import { AbstractControl, NG_VALIDATORS, ValidationErrors, Validator, Validators } from "@angular/forms";

@Directive({
  selector: '[appIsIntegerValidator]',
  providers: [{
    provide: NG_VALIDATORS,
    useExisting: IsIntegerValidatorDirective,
    multi: true,
  }]
})
export class IsIntegerValidatorDirective implements Validator {

  validate(control: AbstractControl): ValidationErrors | null {
    return Validators.pattern(/^-?\d+$/)(control);
  }

}
