"use client";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

interface Point {
  date: string;
  equity: number;
}

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#1c1c1c] border border-white/10 rounded-lg px-3 py-2 shadow-xl">
      <p className="text-white/40 text-xs mb-1">{label}</p>
      <p className="text-white font-semibold text-sm">
        ${payload[0].value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
      </p>
    </div>
  );
}

export default function EquityChart({ data }: { data: Point[] }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-[#111111] border border-white/[0.06] rounded-xl p-5 h-64 flex items-center justify-center">
        <p className="text-white/20 text-sm">No history available yet</p>
      </div>
    );
  }

  const values = data.map((d) => d.equity).filter(Boolean);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const pad = (max - min) * 0.15 || 100;

  return (
    <div className="bg-[#111111] border border-white/[0.06] rounded-xl p-5">
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-sm font-semibold text-white/60">Portfolio Equity</h2>
        <span className="text-xs text-white/25 bg-white/[0.04] px-2 py-0.5 rounded">30 days</span>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data} margin={{ top: 5, right: 5, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#6366f1" stopOpacity={0.25} />
              <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#1a1a1a" strokeDasharray="3 6" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fill: "#444", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            domain={[min - pad, max + pad]}
            tick={{ fill: "#444", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
            width={48}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: "#333", strokeWidth: 1 }} />
          <Area
            type="monotone"
            dataKey="equity"
            stroke="#6366f1"
            strokeWidth={2}
            fill="url(#grad)"
            dot={false}
            activeDot={{ r: 4, fill: "#6366f1", strokeWidth: 0 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
