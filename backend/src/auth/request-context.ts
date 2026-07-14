import { createParamDecorator, ExecutionContext } from '@nestjs/common';
import { Request } from 'express';
import { RequestContext } from './auth.types';

export type ContextRequest = Request & { hrContext?: RequestContext };

export const CurrentContext = createParamDecorator((_data: unknown, context: ExecutionContext): RequestContext => {
  const request = context.switchToHttp().getRequest<ContextRequest>();
  if (!request.hrContext) throw new Error('Request context was not initialized');
  return request.hrContext;
});
