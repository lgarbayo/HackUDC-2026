import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { catchError, finalize } from 'rxjs/operators';

import { environment } from '../../../environments/environment';
import { SearchRequest } from '../models/search-request.model';
import { SearchResponse } from '../models/search-response.model';

@Injectable({
  providedIn: 'root',
})
export class DocumentSearchService {
  private readonly _isLoading$ = new BehaviorSubject<boolean>(false);
  private readonly _error$ = new BehaviorSubject<string | null>(null);

  readonly isLoading$: Observable<boolean> = this._isLoading$.asObservable();
  readonly error$: Observable<string | null> = this._error$.asObservable();

  private readonly apiUrl = `${environment.apiBaseUrl}/api/search`;

  constructor(private http: HttpClient) { }

  search(request: SearchRequest): Observable<SearchResponse> {
    this._isLoading$.next(true);
    this._error$.next(null);

    let params = new HttpParams()
      .set('q', request.query)
      .set('top_k', (request.pageSize || 5).toString());

    if (request.filters?.documentTypes?.length) {
      request.filters.documentTypes.forEach(type => {
        params = params.append('type', type);
      });
    }

    return this.http.get<SearchResponse>(this.apiUrl, { params }).pipe(
      catchError((err: Error) => {
        this._error$.next(err.message);
        throw err;
      }),
      finalize(() => this._isLoading$.next(false))
    );
  }
}
