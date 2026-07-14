import { Controller, Get } from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import { Public } from '../auth/public.decorator';
import { PrismaService } from '../database/prisma.service';

@ApiTags('health')
@Public()
@Controller('health')
export class HealthController {
  constructor(private readonly prisma: PrismaService) {}

  @Get()
  health() { return { status: 'ok', service: 'ertis-hr-backend', timestamp: new Date().toISOString() }; }

  @Get('live')
  live() { return { status: 'ok' }; }

  @Get('ready')
  async ready() {
    await this.prisma.$queryRaw`SELECT 1`;
    return { status: 'ready', checks: { database: 'up' } };
  }
}
