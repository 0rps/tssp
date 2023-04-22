import {HttpClient, HttpErrorResponse} from "@angular/common/http";
import {catchError, Observable, throwError} from "rxjs";

export class BaseProvider {
  constructor(protected http: HttpClient) {
  }

  protected get<T>(url: string): Observable<T> {
    return this.http.get<T>(url).pipe(
      catchError(this.handleErrorAndAlert)
    );
  }

  protected post<T>(url: string, data: any): Observable<T> {
    return this.http.post<T>(url, data).pipe(
      catchError(this.handleErrorAndAlert)
    );
  }

  protected delete<T>(url: string): Observable<T> {
    return this.http.delete<T>(url).pipe(
      catchError(this.handleErrorAndAlert)
    )
  }

  protected put<T>(url: string, data: any): Observable<T> {
    return this.http.put<T>(url, data).pipe(
      catchError(this.handleErrorAndAlert)
    )
  }

  private handleErrorAndAlert(err: HttpErrorResponse) {
    let str =
      `${err.message || ''}\n` +
      `${err.error?.detail || ''}`;

    alert(str);
    return throwError(err);
  }
}
