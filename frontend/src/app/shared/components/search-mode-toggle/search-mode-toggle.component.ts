import { Component, Input, Output, EventEmitter } from '@angular/core';

import { SearchMode } from '../../../core/models/search-request.model';

@Component({
  selector: 'app-search-mode-toggle',
  templateUrl: './search-mode-toggle.component.html',
  styleUrls: ['./search-mode-toggle.component.scss'],
  standalone: false,
})
export class SearchModeToggleComponent {
  @Input() activeMode: SearchMode = 'direct';
  @Output() modeChange = new EventEmitter<SearchMode>();

  setMode(mode: SearchMode): void {
    if (mode !== this.activeMode) {
      this.modeChange.emit(mode);
    }
  }
}
