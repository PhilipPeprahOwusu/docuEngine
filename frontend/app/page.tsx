'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function Home() {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100">
      <div className="max-w-4xl mx-auto px-6 text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-6xl font-bold tracking-tight text-slate-900">
            Document Intelligence Platform
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            AI-powered document analysis with multi-LLM support. Extract insights, assess risks, and manage policies effortlessly.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link href="/register">
            <Button size="lg" className="px-8 py-6 text-lg">
              Get Started Free
            </Button>
          </Link>
          <Link href="/login">
            <Button size="lg" variant="outline" className="px-8 py-6 text-lg">
              Sign In
            </Button>
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
            <h3 className="text-lg font-semibold mb-2">🤖 AI-Powered Analysis</h3>
            <p className="text-slate-600">Extract key information, assess risks, and get instant answers with Anthropic Claude.</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
            <h3 className="text-lg font-semibold mb-2">📊 Policy Management</h3>
            <p className="text-slate-600">Create custom policies and automatically check documents for compliance violations.</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
            <h3 className="text-lg font-semibold mb-2">🔍 Document Comparison</h3>
            <p className="text-slate-600">Compare multiple documents side-by-side and identify key differences instantly.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
