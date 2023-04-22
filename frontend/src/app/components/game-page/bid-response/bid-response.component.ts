import {
  AfterViewChecked,
  Component,
  ElementRef,
  Input,
  OnChanges, OnInit,
  SimpleChanges,
  ViewChild
} from '@angular/core';
import {IBidResponse} from "../../../interfaces/bid-response.interface";
import {UiSettingsService} from "../../../services/ui-settings.service";

@Component({
  selector: 'app-bid-response',
  templateUrl: './bid-response.component.html',
  styleUrls: ['./bid-response.component.scss']
})
export class BidResponseComponent implements OnInit, OnChanges, AfterViewChecked {
  @Input() bidResponse?: IBidResponse | null;
  @Input() creativeWidth = 400;
  @Input() creativeHeight = 300;

  private observer = new ResizeObserver(() => {
    const {width} = this.hostRef.nativeElement.getBoundingClientRect();
    const ratio = width / this.creativeWidth;
    if (ratio > 1) return;

    this._transformCreative(ratio, (width - this.creativeWidth) / 2);
  });

  @ViewChild('creative') private creativeElRef?: ElementRef<HTMLElement>;

  constructor(
    private hostRef: ElementRef<HTMLElement>,
    public uiSettings: UiSettingsService,
  ) {
  }

  private _updateSize = true;
  private _updateBackground = true;

  ngOnInit() {
    this.observer.observe(this.hostRef.nativeElement);
  }

  ngOnChanges(changes: SimpleChanges) {
    if ('creativeWidth' in changes || 'creativeHeight' in changes) {
      this._updateSize = true;
    }

    if ('bidResponse' in changes) {
      this._updateBackground = true;
      if (changes['bidResponse'].previousValue === null && changes['bidResponse'].currentValue) {
        this._updateSize = true;
      }
    }
  }

  ngAfterViewChecked() {
    if (this._updateSize) {
      this._resizeCreative({ width: this.creativeWidth, height: this.creativeHeight });
    }

    if (this._updateBackground && this.bidResponse?.image_url) {
      this._setBackground(this.bidResponse.image_url);
    }

    this._updateSize = false;
    this._updateBackground = false;
  }

  showCreativeExtraMeta() {
    if (this.uiSettings.getSettings().showCreativeExtraMeta === false) {
      return false
    }

    if (this.bidResponse?.cat) {
      return this.bidResponse.cat.length > 0
    }
    return false
  }

  private _resizeCreative(size: { width?: number; height?: number }) {
    const elStyle = this.creativeElRef?.nativeElement.style;
    if (!elStyle) return;

    elStyle.width = size.width + 'px';
    elStyle.height = size.height + 'px';
  }

  private _setBackground(url: string) {
    const elStyle = this.creativeElRef?.nativeElement.style;
    if (!elStyle) return;

    elStyle.backgroundImage = `url('${url}')`;
  }

  private _transformCreative(scaleRatio: number, leftShift = 0) {
    const elStyle = this.creativeElRef?.nativeElement.style;
    if (!elStyle) return;

    elStyle.transform = `translate(${leftShift}px) scale(${scaleRatio})`;
  }
}
