import {AfterViewInit, Directive, Host, Input, NgZone, OnChanges, Optional, Self, SimpleChanges} from '@angular/core';
import {NgForm} from "@angular/forms";
import {take} from "rxjs";

@Directive({
  selector: 'form[disabled]'
})
export class FormDisabledDirective implements OnChanges, AfterViewInit {

  @Input() disabled = false;

  constructor(
    private zone: NgZone,
    @Self() @Optional() private form?: NgForm,
  ) {
  }

  ngOnChanges(changes: SimpleChanges) {
    if ('disabled' in changes) {
      this.changeDisabledStatus(this.disabled);
    }
  }

  ngAfterViewInit() {
    this.zone.onStable.pipe(take(1)).subscribe( () => {
      this.changeDisabledStatus(this.disabled);
    })
  }


  private changeDisabledStatus(value: boolean) {
    const form = this.form?.control;
    if (!form || value === form.disabled) return;

    const method = value ? 'disable' : 'enable';
    form[method]({emitEvent: true});
  }
}
