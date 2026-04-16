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
    label: 'Batcave',
    icon: Crosshair,
    href: '/dashboard',
    key: 'dashboard',
    section: 'main',
  },
  {
    label: 'New Case',
    icon: Swords,
    href: '/dashboard/new-application',
    key: 'new-application',
    section: 'main',
  },
  {
    label: 'Crime Analysis',
    icon: Radar,
    href: '/dashboard/office-action',
    key: 'office-action',
    section: 'main',
  },
  {
    label: 'Case Files',
    icon: ScrollText,
    href: '/dashboard/history',
    key: 'history',
    section: 'main',
  },
  {
    label: 'Bat Signal',
    icon: Bell,
    href: '/dashboard/notifications',
    key: 'notifications',
    section: 'main',
  },
];

export const bottomNavItems: NavItem[] = [
  {
    label: 'Batcomputer',
    icon: Shield,
    href: '/dashboard/settings',
    key: 'settings',
    section: 'bottom',
  },
  {
    label: 'Alfred',
    icon: HelpCircle,
    href: '/dashboard/help',
    key: 'help',
    section: 'bottom',
  },
];
