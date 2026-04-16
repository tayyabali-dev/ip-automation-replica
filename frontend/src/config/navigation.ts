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
    label: 'Plumber HQ',
    icon: Crosshair,
    href: '/dashboard',
    key: 'dashboard',
    section: 'main',
  },
  {
    label: 'New Transform',
    icon: Swords,
    href: '/dashboard/new-application',
    key: 'new-application',
    section: 'main',
  },
  {
    label: 'Alien Scan',
    icon: Radar,
    href: '/dashboard/office-action',
    key: 'office-action',
    section: 'main',
  },
  {
    label: 'Alien Database',
    icon: ScrollText,
    href: '/dashboard/history',
    key: 'history',
    section: 'main',
  },
  {
    label: 'Omnitrix Alert',
    icon: Bell,
    href: '/dashboard/notifications',
    key: 'notifications',
    section: 'main',
  },
];

export const bottomNavItems: NavItem[] = [
  {
    label: 'Plumber Tech',
    icon: Shield,
    href: '/dashboard/settings',
    key: 'settings',
    section: 'bottom',
  },
  {
    label: 'Grandpa Max',
    icon: HelpCircle,
    href: '/dashboard/help',
    key: 'help',
    section: 'bottom',
  },
];
