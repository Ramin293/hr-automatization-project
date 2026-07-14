import { CanActivate, ExecutionContext, Injectable } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { errors } from '../common/domain-error';
import { Permission } from './auth.types';
import { IS_PUBLIC } from './public.decorator';
import { REQUIRED_PERMISSIONS } from './permissions.decorator';
import { ContextRequest } from './request-context';

@Injectable()
export class PermissionsGuard implements CanActivate {
  constructor(private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext) {
    if (this.reflector.getAllAndOverride<boolean>(IS_PUBLIC, [context.getHandler(), context.getClass()])) return true;
    const request = context.switchToHttp().getRequest<ContextRequest>();
    if (!request.hrContext) throw errors.unauthorized();
    const required = this.reflector.getAllAndOverride<Permission[]>(REQUIRED_PERMISSIONS, [context.getHandler(), context.getClass()]) ?? [];
    const missing = required.find((permission) => !request.hrContext?.permissions.includes(permission));
    if (missing) throw errors.forbidden(missing);
    return true;
  }
}
