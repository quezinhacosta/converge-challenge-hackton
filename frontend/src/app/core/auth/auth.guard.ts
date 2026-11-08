import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { SessionService } from './session.service';
export const authGuard:CanActivateFn=async()=>{const session=inject(SessionService),router=inject(Router);await session.restore();return session.authenticated()||router.createUrlTree(['/entrar']);};
