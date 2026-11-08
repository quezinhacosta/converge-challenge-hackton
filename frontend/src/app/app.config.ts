import { authInterceptor } from './core/auth/auth.interceptor';
import { ApplicationConfig } from '@angular/core';
import { provideRouter, withInMemoryScrolling } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, withInMemoryScrolling({anchorScrolling:'enabled'})),
    provideHttpClient(withInterceptors([authInterceptor])),
  ],
};
