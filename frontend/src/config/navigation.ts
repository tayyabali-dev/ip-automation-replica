import {
  Crosshair,
  Swords,
  Radar,
  ScrollText,
  Shield,
  HelpCircle,
  Bell,
  type LucideIcon
} from 'lucide-react';

export interface NavItem {
  label: string;
  icon: LucideIcon;
  href: string;
  key: string;
  section?: 'main' | 'bottom';
}

export const navigationItems: NavItem[] = [
  {
    label: 'Fortress',
    icon: Crosshair,
    href: '/dashboard',
    key: 'dashboard',
    section: 'main',
  },
  {
    label: 'New Mission',
    icon: Swords,
    href: '/dashboard/new-application',
    key: 'new-application',
    section: 'main',
  },
  {
    label: 'Threat Scan',
    icon: Radar,
    href: '/dashboard/office-action',
    key: 'office-action',
    section: 'main',
  },
  {
    label: 'Archives',
    icon: ScrollText,
    href: '/dashboard/history',
    key: 'history',
    section: 'main',
  },
  {
    label: 'Distress Calls',
    icon: Bell,
    href: '/dashboard/notifications',
    key: 'notifications',
    section: 'main',
  },
];

export const bottomNavItems: NavItem[] = [
  {
    label: 'Systems',
    icon: Shield,
    href: '/dashboard/settings',
    key: 'settings',
    section: 'bottom',
  },
  {
    label: 'Jor-El',
    icon: HelpCircle,
    href: '/dashboard/help',
    key: 'help',
    section: 'bottom',
  },
];
