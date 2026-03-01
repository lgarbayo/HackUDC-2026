import { Component } from '@angular/core';
import { Observable } from 'rxjs';

import { DocumentSearchService } from '../../../../core/services/document-search.service';
import {
  SearchMode,
  DocumentType,
  FilterChip,
  SearchRequest,
} from '../../../../core/models/search-request.model';
import {
  SearchResult,
  SearchResponse,
} from '../../../../core/models/search-response.model';

const DEFAULT_CHIPS: FilterChip[] = [
  { label: 'PDFs',          value: 'pdf',         iconName: 'document-text-outline' },
  { label: 'Contracts',     value: 'contract',    iconName: 'ribbon-outline'        },
  { label: 'Code snippets', value: 'code_snippet',iconName: 'code-slash-outline'    },
  { label: 'Invoices',      value: 'invoice',     iconName: 'receipt-outline'       },
  { label: 'Proposals',     value: 'proposal',    iconName: 'bulb-outline'          },
];

@Component({
  selector: 'app-search-shell',
  templateUrl: './search-shell.component.html',
  styleUrls: ['./search-shell.component.scss'],
  standalone: false,
})
export class SearchShellComponent {
  query = '';
  activeMode: SearchMode = 'direct';
  activeFilters: DocumentType[] = [];
  results: SearchResult[] = [];
  totalResults = 0;
  hasSearched = false;

  readonly chips: FilterChip[] = DEFAULT_CHIPS;
  readonly isLoading$: Observable<boolean>;
  readonly error$: Observable<string | null>;

  constructor(private readonly searchService: DocumentSearchService) {
    this.isLoading$ = searchService.isLoading$;
    this.error$ = searchService.error$;
  }

  onQueryChange(q: string): void {
    this.query = q;
  }

  onModeChange(mode: SearchMode): void {
    this.activeMode = mode;
  }

  onFilterToggle(type: DocumentType): void {
    const idx = this.activeFilters.indexOf(type);
    this.activeFilters =
      idx > -1
        ? this.activeFilters.filter((f) => f !== type)
        : [...this.activeFilters, type];
  }

  onSearchSubmit(query: string): void {
    const request: SearchRequest = {
      query,
      mode: this.activeMode,
      filters: { documentTypes: this.activeFilters },
      page: 1,
      pageSize: 10,
    };

    this.searchService.search(request).subscribe({
      next: (response: SearchResponse) => {
        this.results = response.results;
        this.totalResults = response.total;
        this.hasSearched = true;
      },
      error: () => {
        this.hasSearched = true;
      },
    });
  }

  onCardClick(documentId: string): void {
    // Future: navigate to document detail or open preview panel
    console.log('[SearchShell] Document selected:', documentId);
  }
}
