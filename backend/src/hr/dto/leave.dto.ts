import { LeaveRequestStatus } from '@prisma/client';
import { Type } from 'class-transformer';
import { IsDateString, IsEnum, IsInt, IsOptional, IsString, IsUUID, Max, MaxLength, Min, MinLength } from 'class-validator';

export class LeaveQueryDto {
  @Type(() => Number) @IsInt() @Min(1) @IsOptional() page = 1;
  @Type(() => Number) @IsInt() @Min(1) @Max(100) @IsOptional() pageSize = 20;
  @IsUUID() @IsOptional() employeeId?: string;
  @IsEnum(LeaveRequestStatus) @IsOptional() status?: LeaveRequestStatus;
}

export class CreateLeaveRequestDto {
  @IsUUID() employeeId!: string;
  @IsString() @MinLength(2) @MaxLength(50) leaveType = 'ANNUAL_PAID';
  @IsDateString() startDate!: string;
  @IsDateString() endDate!: string;
  @IsUUID() @IsOptional() substituteEmployeeId?: string;
  @IsString() @MaxLength(1000) @IsOptional() comment?: string;
  @IsString() @MaxLength(250) @IsOptional() contactDuringLeave?: string;
}

export class ReviewLeaveRequestDto {
  @IsEnum(['manager', 'hr']) stage!: 'manager' | 'hr';
  @IsEnum(['approve', 'reject']) decision!: 'approve' | 'reject';
  @Type(() => Number) @IsInt() @Min(1) version!: number;
  @IsString() @MaxLength(1000) @IsOptional() reason?: string;
}
