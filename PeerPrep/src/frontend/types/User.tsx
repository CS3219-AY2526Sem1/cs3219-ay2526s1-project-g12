import type { Role } from './Role';

/**
 * Interface representing a user object
 */
export interface User {
  /** ID of user */
  readonly id: string;
  /** Email of user */
  readonly email?: string;
  /** First name of user */
  readonly first_name: string;
  /** Last name of user */
  readonly last_name: string;
  /** Role of user */
  readonly role: Role;
  /** Whether the user is active */
  readonly is_active: boolean;
  /** Whether the user's email is verified */
  readonly is_verified: boolean;
  /** Whether the user is a superuser */
  readonly is_superuser: boolean;
}
