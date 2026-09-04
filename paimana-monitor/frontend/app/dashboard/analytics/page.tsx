"use client";

import { useEffect, useState } from "react";
import { getPortfolioSummary, type PortfolioSummary } from "@/lib/api";
import { formatCurrency, formatProgress } from "@/lib/formatters";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend, LineChart, Line
} from "recharts";

// Mock historic data for analytics charts since we don't have a time-series portfolio endpoint yet
const generateTrendData = () => {
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"];
  return months.map((month, i) => ({
    month,
    projects: 1500 + i * 15,
    expenditure: 800000 + i * 45000,
    cost: 1200000 + i * 25000,
    highRisk: 120 - i * 5,
    criticalRisk: 40 - i * 2,
    alerts: 300 - i * 12,
  }));
};

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [trendData] = useState(generateTrendData());
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getPortfolioSummary()
      .then(setSummary)
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="skeleton h-8 w-64 rounded" />
        <div className="grid grid-cols-2 gap-4">
          <div className="skeleton h-80 rounded-xl" />
          <div className="skeleton h-80 rounded-xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-100">Advanced Analytics</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Portfolio-level trends, forecasting, and risk aggregation
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cost vs Expenditure Trend */}
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Financial Trajectory (YTD)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={trendData}>
              <defs>
                <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorExp" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="month" tick={{ fill: "#64748b", fontSize: 11 }} />
              <YAxis tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={(val) => `₹${val/1000}k Cr`} />
              <Tooltip
                contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
                itemStyle={{ color: "#f1f5f9" }}
              />
              <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
              <Area type="monotone" dataKey="cost" name="Revised Cost" stroke="#f59e0b" fillOpacity={1} fill="url(#colorCost)" />
              <Area type="monotone" dataKey="expenditure" name="Expenditure" stroke="#10b981" fillOpacity={1} fill="url(#colorExp)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Risk Trend */}
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Risk Profile Evolution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="month" tick={{ fill: "#64748b", fontSize: 11 }} />
              <YAxis tick={{ fill: "#64748b", fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
                itemStyle={{ color: "#f1f5f9" }}
              />
              <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
              <Line type="monotone" dataKey="highRisk" name="High Risk Projects" stroke="#ef4444" strokeWidth={2} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="criticalRisk" name="Critical Risk Projects" stroke="#a855f7" strokeWidth={2} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="alerts" name="Active Alerts" stroke="#3b82f6" strokeWidth={2} strokeDasharray="4 4" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
