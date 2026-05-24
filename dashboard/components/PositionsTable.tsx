import { clsx } from "clsx";

interface Position {
  symbol: string;
  qty: number;
  avg_entry_price: number;
  current_price: number;
  market_value: number;
  unrealized_pl: number;
  unrealized_plpc: number;
}

export default function PositionsTable({ positions }: { positions: Position[] }) {
  return (
    <div className="bg-[#111111] border border-white/[0.06] rounded-xl p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-white/60">Open Positions</h2>
        <span className="text-xs text-white/25">{positions.length} active</span>
      </div>

      {positions.length === 0 ? (
        <div className="flex items-center justify-center py-10">
          <p className="text-white/20 text-sm">Flat — no open positions</p>
        </div>
      ) : (
        <div className="flex flex-col divide-y divide-white/[0.04]">
          {positions.map((p) => (
            <div key={p.symbol} className="flex items-center justify-between py-3.5">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-indigo-500/10 border border-indigo-500/15 flex items-center justify-center shrink-0">
                  <span className="text-indigo-400 text-xs font-bold">{p.symbol.slice(0, 2)}</span>
                </div>
                <div>
                  <p className="text-white text-sm font-semibold">{p.symbol}</p>
                  <p className="text-white/35 text-xs">
                    {p.qty} shares · avg ${p.avg_entry_price.toFixed(2)}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-white text-sm font-medium">${p.current_price.toFixed(2)}</p>
                <p
                  className={clsx("text-xs font-medium", {
                    "text-green-400": p.unrealized_pl >= 0,
                    "text-red-400": p.unrealized_pl < 0,
                  })}
                >
                  {p.unrealized_pl >= 0 ? "+" : ""}${p.unrealized_pl.toFixed(2)} (
                  {p.unrealized_plpc >= 0 ? "+" : ""}
                  {p.unrealized_plpc.toFixed(2)}%)
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
