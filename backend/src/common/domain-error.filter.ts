import { ArgumentsHost, Catch, ExceptionFilter, HttpException } from '@nestjs/common';
import { Request, Response } from 'express';
import { Prisma } from '@prisma/client';
import { DomainError } from './domain-error';

@Catch()
export class DomainErrorFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const response = host.switchToHttp().getResponse<Response>();
    const request = host.switchToHttp().getRequest<Request>();
    const correlationId = response.getHeader('x-correlation-id')?.toString();

    if (exception instanceof DomainError) {
      response.status(exception.status).json({
        error: { code: exception.code, message: exception.message, details: exception.details ?? null },
        correlationId,
        path: request.path,
        timestamp: new Date().toISOString()
      });
      return;
    }

    if (exception instanceof HttpException) {
      const status = exception.getStatus();
      const body = exception.getResponse();
      response.status(status).json({
        error: { code: status === 400 ? 'VALIDATION_ERROR' : 'HTTP_ERROR', message: exception.message, details: typeof body === 'object' ? body : null },
        correlationId,
        path: request.path,
        timestamp: new Date().toISOString()
      });
      return;
    }

    if (exception instanceof Prisma.PrismaClientKnownRequestError) {
      const status = exception.code === 'P2025' ? 404 : exception.code === 'P2002' || exception.code === 'P2003' ? 409 : 500;
      response.status(status).json({
        error: { code: status === 404 ? 'RESOURCE_NOT_FOUND' : status === 409 ? 'DATA_CONFLICT' : 'DATABASE_ERROR', message: status === 500 ? 'An unexpected database error occurred' : 'The requested data operation could not be completed', details: null },
        correlationId,
        path: request.path,
        timestamp: new Date().toISOString()
      });
      return;
    }

    response.status(500).json({
      error: { code: 'INTERNAL_ERROR', message: 'An unexpected error occurred', details: null },
      correlationId,
      path: request.path,
      timestamp: new Date().toISOString()
    });
  }
}
