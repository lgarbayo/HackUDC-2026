import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse,
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

import { environment } from '../../../environments/environment';

@Injectable()
export class ApiErrorInterceptor implements HttpInterceptor {
  intercept(
    request: HttpRequest<unknown>,
    next: HttpHandler
  ): Observable<HttpEvent<unknown>> {
    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        let message = 'An unexpected error occurred.';

        if (error.error?.detail) {
          message = Array.isArray(error.error.detail)
            ? error.error.detail[0]?.msg ?? message
            : String(error.error.detail);
        } else if (error.message) {
          message = error.message;
        }

        if (!environment.production) {
          console.error('[ApiErrorInterceptor]', error.status, message, error);
        }

        return throwError(() => new Error(message));
      })
    );
  }
}
