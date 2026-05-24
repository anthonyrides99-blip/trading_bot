interface Task {
  id: string;
  name: string;
  description: string;
  created: number;
  list: string;
}

function timeAgo(ms: number) {
  const diff = Date.now() - ms;
  const m = Math.floor(diff / 60000);
  const h = Math.floor(m / 60);
  const d = Math.floor(h / 24);
  if (d > 0) return `${d}d ago`;
  if (h > 0) return `${h}h ago`;
  return `${m}m ago`;
}

function badgeStyle(listName: string) {
  if (listName.toLowerCase().includes("trade"))
    return "text-green-400 bg-green-500/10 border-green-500/20";
  if (listName.toLowerCase().includes("daily") || listName.toLowerCase().includes("post"))
    return "text-blue-400 bg-blue-500/10 border-blue-500/20";
  if (listName.toLowerCase().includes("weekly"))
    return "text-purple-400 bg-purple-500/10 border-purple-500/20";
  if (listName.toLowerCase().includes("pre") || listName.toLowerCase().includes("market"))
    return "text-yellow-400 bg-yellow-500/10 border-yellow-500/20";
  return "text-white/40 bg-white/5 border-white/10";
}

function shortListName(name: string) {
  if (name.toLowerCase().includes("trade")) return "TRADE";
  if (name.toLowerCase().includes("daily")) return "DAILY";
  if (name.toLowerCase().includes("weekly")) return "WEEKLY";
  if (name.toLowerCase().includes("pre")) return "PRE-MKT";
  return name.slice(0, 8).toUpperCase();
}

export default function ActivityFeed({ tasks }: { tasks: Task[] }) {
  return (
    <div className="bg-[#111111] border border-white/[0.06] rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-white/60">Bot Activity</h2>
        <span className="text-xs text-white/25">All lists · last 10 per list</span>
      </div>

      {tasks.length === 0 ? (
        <div className="flex items-center justify-center py-10">
          <p className="text-white/20 text-sm">No activity logged yet</p>
        </div>
      ) : (
        <div className="flex flex-col divide-y divide-white/[0.04]">
          {tasks.slice(0, 20).map((t) => (
            <div key={t.id} className="flex items-start gap-3 py-3.5">
              <span
                className={`shrink-0 mt-0.5 text-xs font-bold px-2 py-0.5 rounded border ${badgeStyle(t.list)}`}
              >
                {shortListName(t.list)}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-white/80 text-sm truncate">{t.name}</p>
                {t.description && (
                  <p className="text-white/25 text-xs mt-0.5 line-clamp-1">{t.description}</p>
                )}
              </div>
              <span className="shrink-0 text-white/25 text-xs">{timeAgo(t.created)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
