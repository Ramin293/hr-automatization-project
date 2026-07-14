import { SetMetadata } from '@nestjs/common';
import { Permission } from './auth.types';

export const REQUIRED_PERMISSIONS = 'requiredPermissions';
export const RequirePermissions = (...permissions: Permission[]) => SetMetadata(REQUIRED_PERMISSIONS, permissions);
