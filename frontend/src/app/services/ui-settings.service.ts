import {Injectable} from "@angular/core";
import {Observable, ReplaySubject, skip, Subject, takeUntil} from "rxjs";

export type SettingProp =
  | 'showTeamImplClConv'
  | 'showFinalProbabilities'
  | 'showCreativeExtraMeta'
  | 'showLogs'
  | 'autoAuction';

type IUISettings = Record<SettingProp, boolean>;

type IUISettings$ = Record<SettingProp, Observable<boolean>>;

@Injectable({ providedIn: 'root' })
export class UiSettingsService {
  private initialSettings: IUISettings = {
    showTeamImplClConv: true,
    showFinalProbabilities: true,
    showLogs: true,
    showCreativeExtraMeta: true,
    // showExtraParam1: false,
    autoAuction: false
  };

  private readonly state!: IUISettings;
  private readonly subjects: Record<SettingProp, ReplaySubject<boolean>>;
  public readonly settings: IUISettings$;
  private destroy$ = new Subject<void>();


  constructor() {
    this.subjects = Object.keys(this.initialSettings)
      .reduce((acc, cur) =>
        Object.assign(acc, {[cur]: new ReplaySubject(1)}),
        {} as UiSettingsService['subjects']
      );

    this.settings = { ...this.subjects };

    const localStoreValue = localStorage.getItem('ui-settings');
    this.state = localStoreValue ? JSON.parse(localStoreValue) : { ...this.initialSettings };

    Object.entries(this.subjects).forEach(([_key , sub$]) => {
      const key = _key as SettingProp;

      sub$.next(this.state[key]);

      sub$.pipe(
        skip(1),
        takeUntil(this.destroy$)
      ).subscribe((value) => {
        this.state[key] = value;
        localStorage.setItem('ui-settings', JSON.stringify(this.getSettings()));
      });
    })
  }


  setSetting(prop: SettingProp, value: boolean) {
    this.subjects[prop].next(value);
  }

  getSettings() {
    return { ...this.state }
  }

  ngOnDestroy() {
    this.destroy$.next();
  }
}
