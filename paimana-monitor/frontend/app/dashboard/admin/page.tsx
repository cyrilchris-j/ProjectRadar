"use client";

import { useAuth } from "@/lib/auth";

export default function AdminPage() {
  const { user } = useAuth();

  if (user?.role !== "admin") {
    return (
      <div className="card p-12 text-center text-red-400">
        <h2 className="text-xl font-bold mb-2">Access Denied</h2>
        <p className="text-sm">You do not have administrative privileges to view this page.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-100">System Administration</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Manage platform users, roles, and global configurations.
        </p>
      </div>

      <div className="card p-6">
        <h2 className="text-sm font-semibold text-slate-200 mb-4">User Management (Stub)</h2>
        <div className="text-sm text-slate-400 py-8 text-center border border-dashed border-slate-700 rounded-lg">
          This section is a placeholder for Phase 4 implementation.
        </div>
      </div>
    </div>
  );
}
