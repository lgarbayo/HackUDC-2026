export type SearchMode = 'direct' | 'descriptive';

export type DocumentType =
  | 'pdf'
  | 'contract'
  | 'code_snippet'
  | 'invoice'
  | 'proposal';

export interface FilterChip {
  label: string;
  value: DocumentType;
  iconName: string;
}

export interface ActiveFilters {
  documentTypes: DocumentType[];
}

export interface SearchRequest {
  query: string;
  mode: SearchMode;
  filters: ActiveFilters;
  page: number;
  pageSize: number;
}
