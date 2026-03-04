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
    label: 'Command Center',
    icon: Crosshair,
    href: '/dashboard',
    key: 'dashboard',
    section: 'main',
  },
  {
    label: 'New Transmission',
    icon: Swords,
    href: '/dashboard/new-application',
    key: 'new-application',
    section: 'main',
  },
  {
    label: 'Scan Intel',
    icon: Radar,
    href: '/dashboard/office-action',
    key: 'office-action',
    section: 'main',
  },
  {
    label: 'Holocron Archives',
    icon: ScrollText,
    href: '/dashboard/history',
    key: 'history',
    section: 'main',
  },
  {
    label: 'Holonet',
    icon: Bell,
    href: '/dashboard/notifications',
    key: 'notifications',
    section: 'main',
  },
];

export const bottomNavItems: NavItem[] = [
  {
    label: 'Ship Systems',
    icon: Shield,
    href: '/dashboard/settings',
    key: 'settings',
    section: 'bottom',
  },
  {
    label: 'Jedi Council',
    icon: HelpCircle,
    href: '/dashboard/help',
    key: 'help',
    section: 'bottom',
  },
];
