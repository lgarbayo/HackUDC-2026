import { DocumentType } from './search-request.model';

export interface DocumentMetadata {
  id: string;
  title: string;
  type: DocumentType;
  source: string;
  author?: string;
  createdAt: string;
  updatedAt: string;
  tags: string[];
  sizeBytes?: number;
}

export interface HighlightedFragment {
  text: string;
  highlights: Array<{ start: number; end: number }>;
  pageNumber?: number;
}

export interface SearchResult {
  document: DocumentMetadata;
  fragment: HighlightedFragment;
  relevanceScore: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  page: number;
  pageSize: number;
  durationMs: number;
  queryEchoed: string;
}
