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
    label: 'Pokemon Center',
    icon: Crosshair,
    href: '/dashboard',
    key: 'dashboard',
    section: 'main',
  },
  {
    label: 'New Patent',
    icon: Swords,
    href: '/dashboard/new-application',
    key: 'new-application',
    section: 'main',
  },
  {
    label: 'Office Scan',
    icon: Radar,
    href: '/dashboard/office-action',
    key: 'office-action',
    section: 'main',
  },
  {
    label: 'Patent Archives',
    icon: ScrollText,
    href: '/dashboard/history',
    key: 'history',
    section: 'main',
  },
  {
    label: 'Poke Center Alerts',
    icon: Bell,
    href: '/dashboard/notifications',
    key: 'notifications',
    section: 'main',
  },
];

export const bottomNavItems: NavItem[] = [
  {
    label: 'Trainer Settings',
    icon: Shield,
    href: '/dashboard/settings',
    key: 'settings',
    section: 'bottom',
  },
  {
    label: 'Professor Oak',
    icon: HelpCircle,
    href: '/dashboard/help',
    key: 'help',
    section: 'bottom',
  },
];
