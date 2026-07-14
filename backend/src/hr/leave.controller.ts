import { Body, Controller, Get, Headers, Param, ParseUUIDPipe, Post, Query } from '@nestjs/common';
import { ApiHeader, ApiOperation, ApiSecurity, ApiTags } from '@nestjs/swagger';
import { RequestContext } from '../auth/auth.types';
import { RequirePermissions } from '../auth/permissions.decorator';
import { CurrentContext } from '../auth/request-context';
import { CreateLeaveRequestDto, LeaveQueryDto, ReviewLeaveRequestDto } from './dto/leave.dto';
import { LeaveService } from './leave.service';

@ApiTags('HR absence')
@ApiSecurity('dev-user-id')
@RequirePermissions('hr.read')
@Controller('api/v1/hr/leave-requests')
export class LeaveController {
  constructor(private readonly leaves: LeaveService) {}

  @Get()
  @ApiOperation({ summary: 'List leave requests within the caller ABAC scope' })
  list(@Query() query: LeaveQueryDto, @CurrentContext() context: RequestContext) {
    return this.leaves.list(query, context);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get a leave request within the caller ABAC scope' })
  get(@Param('id', ParseUUIDPipe) id: string, @CurrentContext() context: RequestContext) {
    return this.leaves.get(id, context);
  }

  @Post()
  @RequirePermissions('hr.leave.request')
  @ApiHeader({ name: 'Idempotency-Key', required: true })
  @ApiOperation({ summary: 'Submit a leave request and start shared document/workflow adapters' })
  create(@Body() dto: CreateLeaveRequestDto, @Headers('idempotency-key') idempotencyKey: string | undefined, @CurrentContext() context: RequestContext) {
    return this.leaves.create(dto, idempotencyKey, context);
  }

  @Post(':id/review')
  @ApiOperation({ summary: 'Approve or reject at manager or HR stage with optimistic locking' })
  review(@Param('id', ParseUUIDPipe) id: string, @Body() dto: ReviewLeaveRequestDto, @CurrentContext() context: RequestContext) {
    return this.leaves.review(id, dto, context);
  }
}
