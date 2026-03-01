import { Component, Input, Output, EventEmitter } from '@angular/core';

import { SearchResult } from '../../../../core/models/search-response.model';

@Component({
  selector: 'app-result-card',
  templateUrl: './result-card.component.html',
  styleUrls: ['./result-card.component.scss'],
  standalone: false,
})
export class ResultCardComponent {
  @Input() result!: SearchResult;
  @Output() cardClick = new EventEmitter<string>();

  onClick(): void {
    this.cardClick.emit(this.result.document.id);
  }

  get scorePercent(): number {
    return Math.round(this.result.relevanceScore * 100);
  }

  getHighlightedHtml(): string {
    const { text, highlights } = this.result.fragment;
    if (!highlights?.length) return this.escapeHtml(text);

    let output = '';
    let cursor = 0;
    const sorted = [...highlights].sort((a, b) => a.start - b.start);

    for (const { start, end } of sorted) {
      output += this.escapeHtml(text.slice(cursor, start));
      output += `<mark>${this.escapeHtml(text.slice(start, end))}</mark>`;
      cursor = end;
    }

    output += this.escapeHtml(text.slice(cursor));
    return output;
  }

  private escapeHtml(s: string): string {
    return s
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }
}
