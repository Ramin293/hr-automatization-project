import { Injectable, NestMiddleware } from '@nestjs/common';
import { randomUUID } from 'crypto';
import { NextFunction, Request, Response } from 'express';

@Injectable()
export class CorrelationMiddleware implements NestMiddleware {
  use(request: Request, response: Response, next: NextFunction) {
    const incoming = request.header('x-correlation-id');
    const correlationId = incoming && /^[a-zA-Z0-9._:-]{8,128}$/.test(incoming) ? incoming : randomUUID();
    request.headers['x-correlation-id'] = correlationId;
    response.setHeader('x-correlation-id', correlationId);
    next();
  }
}
