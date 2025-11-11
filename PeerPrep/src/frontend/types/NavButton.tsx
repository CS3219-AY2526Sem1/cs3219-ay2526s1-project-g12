import type { RoleName } from './Role';

/*
 * Interface representing a navigation button
 */
export interface NavButton {
  label: string;
  role: RoleName;
  route: string;
  style: string;
}
