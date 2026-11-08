import { inject } from '@angular/core';
import { HttpInterceptorFn } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { SessionService } from './session.service';
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const session = inject(SessionService);
  const base = environment.apiUrl.replace(/\/$/, '');
  if (req.url === base || req.url.startsWith(base + '/')) {
    return next(req.clone({ setHeaders: session.headers() }));
  }
  return next(req);
};
