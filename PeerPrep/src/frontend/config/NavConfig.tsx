import type { NavButton } from '../types/NavButton';

export const NAV_BUTTONS: NavButton[] = [
  {
    label: '⚠ Manage Qns',
    role: 'admin',
    route: '/questions',
    style: 'btn-warning',
  },
  {
    label: '✈ Initiate Match',
    role: 'user',
    route: '/matching',
    style: 'btn-primary',
  },
  {
    label: '👤 Account Setting',
    role: 'user',
    route: '/account',
    style: 'btn-success',
  },
  {
    label: '🚪 Logout',
    role: 'user',
    route: '/auth/logout',
    style: 'btn-error',
  },
];
