import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';

import { SharedModule } from '../../shared/shared.module';
import { SearchRoutingModule } from './search-routing.module';
import { SearchShellComponent } from './containers/search-shell/search-shell.component';
import { ResultCardComponent } from './components/result-card/result-card.component';

@NgModule({
  declarations: [SearchShellComponent, ResultCardComponent],
  imports: [CommonModule, IonicModule, SharedModule, SearchRoutingModule],
})
export class SearchModule {}
