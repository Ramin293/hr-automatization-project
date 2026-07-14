export class DomainError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly status: number,
    public readonly details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'DomainError';
  }
}

export const errors = {
  unauthorized: () => new DomainError('AUTH_REQUIRED', 'Authentication context is required', 401),
  forbidden: (permission?: string) => new DomainError('ACCESS_DENIED', 'Access is denied', 403, permission ? { permission } : undefined),
  notFound: (entity: string) => new DomainError(`${entity.toUpperCase()}_NOT_FOUND`, `${entity} was not found`, 404),
  conflict: (code: string, message: string, details?: Record<string, unknown>) => new DomainError(code, message, 409, details),
  integration: (service: string) => new DomainError('INTEGRATION_UNAVAILABLE', `${service} is unavailable`, 502, { service }),
  validation: (code: string, message: string, details?: Record<string, unknown>) => new DomainError(code, message, 422, details)
};
