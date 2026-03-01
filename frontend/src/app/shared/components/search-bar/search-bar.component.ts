import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-search-bar',
  templateUrl: './search-bar.component.html',
  styleUrls: ['./search-bar.component.scss'],
  standalone: false,
})
export class SearchBarComponent {
  @Input() query = '';
  @Input() isLoading = false;

  @Output() queryChange = new EventEmitter<string>();
  @Output() searchSubmit = new EventEmitter<string>();

  onInput(value: string): void {
    this.query = value;
    this.queryChange.emit(value);
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && this.query.trim()) {
      this.searchSubmit.emit(this.query.trim());
    }
  }
}
