import { INestApplication, MiddlewareConsumer, Module, NestModule, ValidationPipe } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { Test } from '@nestjs/testing';
import request = require('supertest');
import { DevAuthMiddleware } from '../src/auth/dev-auth.middleware';
import { PermissionsGuard } from '../src/auth/permissions.guard';
import { CorrelationMiddleware } from '../src/common/correlation.middleware';
import { DomainErrorFilter } from '../src/common/domain-error.filter';
import { EmployeeController } from '../src/hr/employee.controller';
import { EmployeeService } from '../src/hr/employee.service';
import { HR_REPOSITORY } from '../src/hr/hr.repository';
import { employeeFixture, repositoryMock } from '../src/hr/test-fixtures';

const repository = repositoryMock();

@Module({
  controllers: [EmployeeController],
  providers: [EmployeeService, { provide: HR_REPOSITORY, useValue: repository }, { provide: APP_GUARD, useClass: PermissionsGuard }]
})
class TestAppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) { consumer.apply(CorrelationMiddleware, DevAuthMiddleware).forRoutes('*'); }
}

describe('Employee API', () => {
  let app: INestApplication;

  beforeAll(async () => {
    repository.getEmployee.mockResolvedValue(employeeFixture);
    app = (await Test.createTestingModule({ imports: [TestAppModule] }).compile()).createNestApplication();
    app.useGlobalPipes(new ValidationPipe({ transform: true, whitelist: true, forbidNonWhitelisted: true }));
    app.useGlobalFilters(new DomainErrorFilter());
    await app.init();
  });

  afterAll(async () => app.close());

  it('returns a self profile and propagates correlation id', async () => {
    const response = await request(app.getHttpServer())
      .get(`/api/v1/hr/employees/${employeeFixture.id}`)
      .set('X-Dev-User-Id', 'user-11').set('X-Dev-Role', 'EMPLOYEE').set('X-Dev-Employee-Id', employeeFixture.id)
      .set('X-Correlation-Id', 'test-correlation-001')
      .expect(200);
    expect(response.headers['x-correlation-id']).toBe('test-correlation-001');
    expect(response.body.fullName).toBe(employeeFixture.fullName);
    expect(response.body.salary).toBeUndefined();
  });

  it('rejects a request without identity headers', async () => {
    const response = await request(app.getHttpServer()).get(`/api/v1/hr/employees/${employeeFixture.id}`).expect(401);
    expect(response.body.error.code).toBe('AUTH_REQUIRED');
  });
});
