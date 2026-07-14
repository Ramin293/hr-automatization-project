import { CallHandler, ExecutionContext, Injectable, NestInterceptor } from '@nestjs/common';
import { Request, Response } from 'express';
import { Observable, tap } from 'rxjs';

@Injectable()
export class RequestLoggerInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const request = context.switchToHttp().getRequest<Request>();
    const response = context.switchToHttp().getResponse<Response>();
    const startedAt = Date.now();
    return next.handle().pipe(tap({
      finalize: () => {
        process.stdout.write(`${JSON.stringify({ level: 'info', event: 'http.request', method: request.method, path: request.path, status: response.statusCode, durationMs: Date.now() - startedAt, correlationId: response.getHeader('x-correlation-id') })}\n`);
      }
    }));
  }
}
