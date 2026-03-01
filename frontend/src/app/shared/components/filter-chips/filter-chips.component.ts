import { Component, Input, Output, EventEmitter } from '@angular/core';

import {
  FilterChip,
  DocumentType,
} from '../../../core/models/search-request.model';

@Component({
  selector: 'app-filter-chips',
  templateUrl: './filter-chips.component.html',
  styleUrls: ['./filter-chips.component.scss'],
  standalone: false,
})
export class FilterChipsComponent {
  @Input() chips: FilterChip[] = [];
  @Input() activeFilters: DocumentType[] = [];

  @Output() filterToggle = new EventEmitter<DocumentType>();

  isActive(value: DocumentType): boolean {
    return this.activeFilters.includes(value);
  }

  toggle(value: DocumentType): void {
    this.filterToggle.emit(value);
  }
}
