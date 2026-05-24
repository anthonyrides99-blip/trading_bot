"use client";
import { useState, useEffect } from "react";
import useSWR from "swr";
import { Bot, TrendingUp, TrendingDown, DollarSign, Layers, RefreshCw } from "lucide-react";
import MetricCard from "@/components/MetricCard";
import EquityChart from "@/components/EquityChart";
import PositionsTable from "@/components/PositionsTable";
import TradesFeed from "@/components/TradesFeed";
import ActivityFeed from "@/components/ActivityFeed";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

function fmt(n: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(n);
}

export default function Dashboard() {
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const { data: account, isLoading: loadAccount, mutate: refetchAccount } = useSWR(
    "/api/account", fetcher, { refreshInterval: 60_000 }
  );
  const { data: positions = [], isLoading: loadPositions, mutate: refetchPositions } = useSWR(
    "/api/positions", fetcher, { refreshInterval: 60_000 }
  );
  const { data: orders = [], mutate: refetchOrders } = useSWR(
    "/api/orders", fetcher, { refreshInterval: 60_000 }
  );
  const { data: history = [] } = useSWR(
    "/api/history", fetcher, { refreshInterval: 3_600_000 }
  );
  const { data: activity = [], mutate: refetchActivity } = useSWR(
    "/api/clickup", fetcher, { refreshInterval: 300_000 }
  );

  useEffect(() => {
    if (!loadAccount) setLastUpdated(new Date());
  }, [account, loadAccount]);

  function refreshAll() {
    refetchAccount();
    refetchPositions();
    refetchOrders();
    refetchActivity();
    setLastUpdated(new Date());
  }

  const pnlUp = account?.today_pnl >= 0;

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-7">

        {/* ── Header ── */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
              <Bot className="w-5 h-5 text-indigo-400" />
            </div>
            <div>
              <h1 className="text-base font-bold tracking-tight">Trading Bot</h1>
              <p className="text-xs text-white/35">AI-Powered Paper Trading</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              <span className="text-xs text-white/35">Live</span>
            </div>
            <span className="text-xs text-white/25 bg-white/[0.04] border border-white/[0.06] rounded px-2 py-1">
              PAPER
            </span>
            {lastUpdated && (
              <span className="text-xs text-white/25 hidden sm:block">
                {lastUpdated.toLocaleTimeString()}
              </span>
            )}
            <button
              onClick={refreshAll}
              className="p-1.5 rounded-lg border border-white/[0.06] hover:bg-white/[0.04] transition-colors"
              title="Refresh"
            >
              <RefreshCw className="w-3.5 h-3.5 text-white/30" />
            </button>
          </div>
        </div>

        {/* ── Metric cards ── */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
          <MetricCard
            label="Portfolio Value"
            value={loadAccount ? "—" : account?.equity != null ? fmt(account.equity) : "Error"}
            icon={<DollarSign className="w-4 h-4" />}
          />
          <MetricCard
            label="Today's P&L"
            value={loadAccount ? "—" : account?.today_pnl != null ? fmt(account.today_pnl) : "Error"}
            sub={
              account?.today_pnl_pct != null
                ? `${account.today_pnl_pct >= 0 ? "+" : ""}${account.today_pnl_pct.toFixed(2)}%`
                : undefined
            }
            positive={account?.today_pnl > 0}
            negative={account?.today_pnl < 0}
            icon={
              pnlUp ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )
            }
          />
          <MetricCard
            label="Cash"
            value={loadAccount ? "—" : account?.cash != null ? fmt(account.cash) : "Error"}
            icon={<DollarSign className="w-4 h-4" />}
          />
          <MetricCard
            label="Open Positions"
            value={loadPositions ? "—" : String(Array.isArray(positions) ? positions.length : 0)}
            sub={positions.length === 0 ? "flat" : "active"}
            icon={<Layers className="w-4 h-4" />}
          />
        </div>

        {/* ── Equity chart ── */}
        <div className="mb-5">
          <EquityChart data={history} />
        </div>

        {/* ── Positions + Trades ── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-5">
          <PositionsTable positions={Array.isArray(positions) ? positions : []} />
          <TradesFeed orders={Array.isArray(orders) ? orders : []} />
        </div>

        {/* ── Activity feed ── */}
        <ActivityFeed tasks={Array.isArray(activity) ? activity : []} />

        {/* ── Footer ── */}
        <p className="text-center text-white/15 text-xs mt-8">
          Refreshes automatically · Alpaca Paper Account · Claude Opus 4.7
        </p>
      </div>
    </div>
  );
}
