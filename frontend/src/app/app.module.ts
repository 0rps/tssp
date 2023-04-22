import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {MatTabsModule} from "@angular/material/tabs";
import {MatSidenavModule} from "@angular/material/sidenav";
import {MatButtonModule} from "@angular/material/button";
import {MatIconModule} from "@angular/material/icon";
import {SettingsPageComponent} from "./components/settings-page/settings-page.component";
import {GamePageComponent} from "./components/game-page/game-page.component";
import { NavigationComponent } from './components/navigation/navigation.component';
import { HeaderComponent } from './components/header/header.component';
import { UiSettingsComponent } from './components/ui-settings/ui-settings.component';
import { GameConfigFormComponent } from './components/settings-page/game-config-form/game-config-form.component';
import { AddTeamFormComponent } from './components/settings-page/add-team-form/add-team-form.component';
import { ListOfTeamsComponent } from './components/settings-page/list-of-teams/list-of-teams.component';
import {FormsModule} from "@angular/forms";
import {MatFormFieldModule} from "@angular/material/form-field";
import {MatInputModule} from "@angular/material/input";
import {MatSelectModule} from "@angular/material/select";
import {MatRadioModule} from "@angular/material/radio";
import {CommonModule} from "@angular/common";
import {HttpClientModule} from "@angular/common/http";
import {MatCheckboxModule} from "@angular/material/checkbox";
import { RangeValidatorDirective } from './directives/range-validator.directive';
import { IsIntegerValidatorDirective } from './directives/is-integer-validator.directive';
import { IsFloatValidatorDirective } from './directives/is-float-validator.directive';
import { RedTextIfInvalidDirective } from './directives/red-text-if-invalid.directive';
import { TeamsConfigurationComponent } from './components/settings-page/teams-configuration/teams-configuration.component';
import { BidRequestComponent } from './components/game-page/bid-request/bid-request.component';
import { BidResponseComponent } from './components/game-page/bid-response/bid-response.component';
import { RoundScoreboardComponent } from './components/game-page/round-scoreboard/round-scoreboard.component';
import {ParameterComponent} from "./components/game-page/parameter.component";
import {MatTableModule} from "@angular/material/table";
import { ShowLogsComponent } from './components/game-page/show-logs/show-logs.component';
import { FormDisabledDirective } from './directives/form-disabled.directive';
import { ScoreboardComponent } from './components/game-page/scoreboard/scoreboard.component';

@NgModule({
  declarations: [
    AppComponent,
    SettingsPageComponent,
    GamePageComponent,
    NavigationComponent,
    HeaderComponent,
    UiSettingsComponent,
    GameConfigFormComponent,
    AddTeamFormComponent,
    ListOfTeamsComponent,
    RangeValidatorDirective,
    IsIntegerValidatorDirective,
    IsFloatValidatorDirective,
    RedTextIfInvalidDirective,
    TeamsConfigurationComponent,
    BidRequestComponent,
    BidResponseComponent,
    RoundScoreboardComponent,
    ParameterComponent,
    ShowLogsComponent,
    FormDisabledDirective,
    ScoreboardComponent,
  ],
  imports: [
    CommonModule,
    HttpClientModule,
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MatTabsModule,
    MatSidenavModule,
    MatButtonModule,
    MatIconModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatRadioModule,
    MatCheckboxModule,
    MatTableModule,
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
