import { EmployeeStatus } from '@prisma/client';
import { Type } from 'class-transformer';
import { IsArray, IsDateString, IsEmail, IsEnum, IsInt, IsNumber, IsOptional, IsString, IsUUID, Max, MaxLength, Min, MinLength } from 'class-validator';

export class EmployeeQueryDto {
  @Type(() => Number) @IsInt() @Min(1) @IsOptional() page = 1;
  @Type(() => Number) @IsInt() @Min(1) @Max(100) @IsOptional() pageSize = 20;
  @IsString() @MaxLength(100) @IsOptional() search?: string;
  @IsEnum(EmployeeStatus) @IsOptional() status?: EmployeeStatus;
  @IsUUID() @IsOptional() departmentId?: string;
  @IsEnum(['fullName', 'employeeNumber', 'startDate', 'status']) @IsOptional() sortBy: 'fullName' | 'employeeNumber' | 'startDate' | 'status' = 'fullName';
  @IsEnum(['asc', 'desc']) @IsOptional() sortOrder: 'asc' | 'desc' = 'asc';
}

export class CreateEmployeeDto {
  @IsString() @MinLength(2) @MaxLength(30) employeeNumber!: string;
  @IsString() @MinLength(3) @MaxLength(160) fullName!: string;
  @IsString() @MinLength(2) @MaxLength(12) initials!: string;
  @IsEmail() @MaxLength(160) workEmail!: string;
  @IsString() @MinLength(5) @MaxLength(30) workPhone!: string;
  @IsUUID() departmentId!: string;
  @IsUUID() positionId!: string;
  @IsUUID() staffingPositionId!: string;
  @IsUUID() @IsOptional() managerId?: string;
  @IsString() @MaxLength(80) legalEntityId!: string;
  @IsString() @MaxLength(80) locationId!: string;
  @IsString() @MaxLength(50) employmentType!: string;
  @IsString() @MaxLength(80) workScheduleId!: string;
  @IsDateString() startDate!: string;
  @IsDateString() @IsOptional() contractEndDate?: string;
  @IsDateString() @IsOptional() probationEndDate?: string;
  @Type(() => Number) @IsNumber({ maxDecimalPlaces: 2 }) @Min(0) @IsOptional() salary?: number;
  @IsArray() @IsString({ each: true }) @IsOptional() candidateGroups: string[] = [];
  @IsArray() @IsString({ each: true }) @IsOptional() skills: string[] = [];
}
