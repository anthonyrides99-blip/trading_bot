import { NextResponse } from "next/server";

const BASE = "https://paper-api.alpaca.markets";

function alpacaHeaders() {
  return {
    "APCA-API-KEY-ID": process.env.ALPACA_API_KEY!,
    "APCA-API-SECRET-KEY": process.env.ALPACA_SECRET_KEY!,
  };
}

export async function GET() {
  try {
    const res = await fetch(
      `${BASE}/v2/account/portfolio/history?period=1M&timeframe=1D`,
      { headers: alpacaHeaders(), next: { revalidate: 3600 } }
    );
    if (!res.ok) throw new Error(`${res.status}`);
    const data = await res.json();
    const points = (data.timestamp || []).map((ts: number, i: number) => ({
      date: new Date(ts * 1000).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      }),
      equity: Math.round((data.equity[i] ?? 0) * 100) / 100,
    }));
    return NextResponse.json(points);
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 });
  }
}
