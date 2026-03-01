import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';

import { SearchBarComponent } from './components/search-bar/search-bar.component';
import { SearchModeToggleComponent } from './components/search-mode-toggle/search-mode-toggle.component';
import { FilterChipsComponent } from './components/filter-chips/filter-chips.component';

const COMPONENTS = [
  SearchBarComponent,
  SearchModeToggleComponent,
  FilterChipsComponent,
];

@NgModule({
  declarations: [...COMPONENTS],
  imports: [CommonModule, IonicModule],
  exports: [...COMPONENTS],
})
export class SharedModule {}
