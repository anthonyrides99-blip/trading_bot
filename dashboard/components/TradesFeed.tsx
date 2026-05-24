import { clsx } from "clsx";

interface Order {
  id: string;
  symbol: string;
  side: string;
  qty: number;
  price: number;
  filled_at: string;
}

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const m = Math.floor(diff / 60000);
  const h = Math.floor(m / 60);
  const d = Math.floor(h / 24);
  if (d > 0) return `${d}d ago`;
  if (h > 0) return `${h}h ago`;
  return `${m}m ago`;
}

export default function TradesFeed({ orders }: { orders: Order[] }) {
  return (
    <div className="bg-[#111111] border border-white/[0.06] rounded-xl p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-white/60">Recent Trades</h2>
        <span className="text-xs text-white/25">{orders.length} total</span>
      </div>

      {orders.length === 0 ? (
        <div className="flex items-center justify-center py-10">
          <p className="text-white/20 text-sm">No trades placed yet</p>
        </div>
      ) : (
        <div className="flex flex-col divide-y divide-white/[0.04]">
          {orders.slice(0, 20).map((o) => (
            <div key={o.id} className="flex items-center justify-between py-3.5">
              <div className="flex items-center gap-3">
                <span
                  className={clsx(
                    "text-xs font-bold px-2 py-1 rounded-md border",
                    o.side === "buy"
                      ? "bg-green-500/10 text-green-400 border-green-500/20"
                      : "bg-red-500/10 text-red-400 border-red-500/20"
                  )}
                >
                  {o.side.toUpperCase()}
                </span>
                <div>
                  <span className="text-white text-sm font-semibold">{o.symbol}</span>
                  <span className="text-white/35 text-sm"> · {o.qty} sh</span>
                </div>
              </div>
              <div className="text-right">
                <p className="text-white text-sm font-medium">${o.price.toFixed(2)}</p>
                <p className="text-white/30 text-xs">{timeAgo(o.filled_at)}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
