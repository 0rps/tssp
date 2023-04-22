import { Component } from '@angular/core';
import {NavigationEnd, Router} from "@angular/router";

@Component({
  selector: 'app-navigation',
  templateUrl: './navigation.component.html',
  styleUrls: ['./navigation.component.scss']
})
export class NavigationComponent {
  links = [{
    path: 'game',
    label: 'Game',
  }, {
    path: 'settings',
    label: 'Settings',
  }];

  activeLink = this.links[0].path;

  constructor(private router: Router) {

  }

  ngOnInit() {
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.activeLink = event.url.split('/')[1].split('?')[0];
      }
    });
  }
}
