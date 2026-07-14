import { MiddlewareConsumer, Module, NestModule } from '@nestjs/common';
import { APP_GUARD, APP_INTERCEPTOR } from '@nestjs/core';
import { ConfigModule } from '@nestjs/config';
import { ThrottlerGuard, ThrottlerModule } from '@nestjs/throttler';
import { DevAuthMiddleware } from './auth/dev-auth.middleware';
import { PermissionsGuard } from './auth/permissions.guard';
import { CorrelationMiddleware } from './common/correlation.middleware';
import { RequestLoggerInterceptor } from './common/request-logger.interceptor';
import { DatabaseModule } from './database/database.module';
import { HealthController } from './health/health.controller';
import { HrModule } from './hr/hr.module';
import { OutboxPublisherService } from './integrations/outbox-publisher.service';

@Module({
  imports: [ConfigModule.forRoot({ isGlobal: true }), DatabaseModule, ThrottlerModule.forRoot([{ ttl: 60_000, limit: 120 }]), HrModule],
  controllers: [HealthController],
  providers: [
    { provide: APP_GUARD, useClass: ThrottlerGuard },
    { provide: APP_GUARD, useClass: PermissionsGuard },
    { provide: APP_INTERCEPTOR, useClass: RequestLoggerInterceptor },
    OutboxPublisherService
  ]
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer.apply(CorrelationMiddleware, DevAuthMiddleware).forRoutes('*');
  }
}
