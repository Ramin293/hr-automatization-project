import { Injectable, NestMiddleware } from '@nestjs/common';
import { NextFunction, Response } from 'express';
import { errors } from '../common/domain-error';
import { permissionsByRole, Role } from './auth.types';
import { ContextRequest } from './request-context';

const roles: Role[] = ['HR_SPECIALIST', 'EMPLOYEE', 'MANAGER', 'PROCESS_ADMIN'];

@Injectable()
export class DevAuthMiddleware implements NestMiddleware {
  use(request: ContextRequest, _response: Response, next: NextFunction) {
    if (request.originalUrl.startsWith('/health') || request.originalUrl.startsWith('/api/docs')) return next();

    const production = process.env.NODE_ENV === 'production';
    const devEnabled = process.env.DEV_AUTH_ENABLED !== 'false';
    const header = (name: string) => request.header(production || !devEnabled ? `x-${name}` : `x-dev-${name}`);
    const userId = header('user-id');
    const roleHeader = header('role') as Role | undefined;
    if (!userId || !roleHeader || !roles.includes(roleHeader)) throw errors.unauthorized();

    request.hrContext = {
      userId,
      employeeId: header('employee-id') ?? undefined,
      role: roleHeader,
      departmentId: header('department-id') ?? undefined,
      permissions: permissionsByRole[roleHeader],
      correlationId: request.header('x-correlation-id') ?? 'unknown'
    };
    next();
  }
}
