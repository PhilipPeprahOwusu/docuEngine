'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  LayoutDashboard,
  FileText,
  Bot,
  ShieldCheck,
  Settings,
  LogOut,
  Menu,
  X,
  MessageSquare,
  Workflow,
  FileEdit,
  BookOpen
} from 'lucide-react';
import { useState } from 'react';

const navigationGroups = [
  {
    items: [
      { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    ]
  },
  {
    title: 'DOCUMENT MANAGEMENT',
    items: [
      { name: 'Documents', href: '/dashboard/documents', icon: FileText },
      { name: 'Chat', href: '/dashboard/chat', icon: MessageSquare },
    ]
  },
  {
    title: 'AI & INTELLIGENCE',
    items: [
      { name: 'AI Agents', href: '/dashboard/agents', icon: Workflow },
      { name: 'Analysis', href: '/dashboard/analysis', icon: Bot },
      { name: 'Contracts', href: '/dashboard/contracts', icon: FileEdit },
    ]
  },
  {
    title: 'COMPLIANCE & POLICY',
    items: [
      { name: 'Playbooks', href: '/dashboard/playbooks', icon: BookOpen },
      { name: 'Policies', href: '/dashboard/policies', icon: ShieldCheck },
    ]
  },
  {
    items: [
      { name: 'Settings', href: '/dashboard/settings', icon: Settings },
    ]
  },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  const userInitials = user?.name
    ?.split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase() || user?.email?.substring(0, 2).toUpperCase() || 'U';

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 transform bg-white border-r border-slate-200 transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-between px-6 border-b border-slate-200">
            <h1 className="text-xl font-bold text-gray-900">DocuEngine</h1>
            <button
              className="lg:hidden"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="h-6 w-6 text-gray-700" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
            {navigationGroups.map((group, groupIndex) => (
              <div key={groupIndex} className={groupIndex > 0 ? 'mt-6' : ''}>
                {group.title && (
                  <div className="px-3 mb-2">
                    <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      {group.title}
                    </h3>
                  </div>
                )}
                <div className="space-y-1">
                  {group.items.map((item) => (
                    <Link
                      key={item.name}
                      href={item.href}
                      className="flex items-center gap-3 rounded-lg px-3 py-2 text-gray-700 font-medium transition-colors hover:bg-gray-100 hover:text-gray-900"
                      onClick={() => setSidebarOpen(false)}
                    >
                      <item.icon className="h-5 w-5" />
                      <span className="text-sm">{item.name}</span>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </nav>

          {/* User menu */}
          <div className="border-t border-slate-200 p-4">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex w-full items-center gap-3 rounded-lg p-2 hover:bg-gray-100">
                  <Avatar>
                    <AvatarFallback className="bg-gray-800 text-white font-semibold">{userInitials}</AvatarFallback>
                  </Avatar>
                  <div className="flex-1 text-left">
                    <p className="text-sm font-medium text-gray-900">
                      {user?.name || user?.email}
                    </p>
                    <p className="text-xs text-gray-600">{user?.email}</p>
                  </div>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel className="text-gray-900">My Account</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-gray-700">
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                  <LogOut className="mr-2 h-4 w-4" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top bar */}
        <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6 lg:px-8">
          <button
            className="lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6 text-gray-700" />
          </button>
          <div className="flex-1 lg:ml-0">
            <h2 className="text-2xl font-semibold text-gray-900">
              Welcome back, {user?.name?.split(' ')[0] || user?.email?.split('@')[0]}
            </h2>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
