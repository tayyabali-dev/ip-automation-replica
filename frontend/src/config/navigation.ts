import {
  Home,
  FilePlus,
  FileSearch,
  Clock,
  Settings,
  HelpCircle,
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
    label: 'Dashboard',
    icon: Home,
    href: '/dashboard',
    key: 'dashboard',
    section: 'main',
  },
  {
    label: 'New Application',
    icon: FilePlus,
    href: '/dashboard/new-application',
    key: 'new-application',
    section: 'main',
  },
  {
    label: 'Office Actions',
    icon: FileSearch,
    href: '/dashboard/office-action',
    key: 'office-action',
    section: 'main',
  },
  {
    label: 'History',
    icon: Clock,
    href: '/dashboard/history',
    key: 'history',
    section: 'main',
  },
];

export const bottomNavItems: NavItem[] = [
  {
    label: 'Settings',
    icon: Settings,
    href: '/dashboard/settings',
    key: 'settings',
    section: 'bottom',
  },
  {
    label: 'Help',
    icon: HelpCircle,
    href: '/dashboard/help',
    key: 'help',
    section: 'bottom',
  },
];
