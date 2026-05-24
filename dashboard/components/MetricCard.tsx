import { clsx } from "clsx";

interface Props {
  label: string;
  value: string;
  sub?: string;
  positive?: boolean;
  negative?: boolean;
  icon?: React.ReactNode;
}

export default function MetricCard({ label, value, sub, positive, negative, icon }: Props) {
  return (
    <div className="bg-[#111111] border border-white/[0.06] rounded-xl p-5 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-white/40 uppercase tracking-widest">{label}</span>
        {icon && <span className="text-white/20">{icon}</span>}
      </div>
      <div className="flex items-end gap-2">
        <span
          className={clsx("text-2xl font-bold tracking-tight", {
            "text-green-400": positive,
            "text-red-400": negative,
            "text-white": !positive && !negative,
          })}
        >
          {value}
        </span>
        {sub && (
          <span
            className={clsx("text-sm mb-0.5 font-medium", {
              "text-green-400": positive,
              "text-red-400": negative,
              "text-white/40": !positive && !negative,
            })}
          >
            {sub}
          </span>
        )}
      </div>
    </div>
  );
}
