type RoleName = 'user' | 'admin' | 'guest';

/**
 * Interface representing a role object
 */
export interface Role {
  /** ID of role */
  readonly id: number;
  /** Name of role */
  readonly role: RoleName;
}
