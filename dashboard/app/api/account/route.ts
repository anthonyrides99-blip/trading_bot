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
    const res = await fetch(`${BASE}/v2/account`, {
      headers: alpacaHeaders(),
      next: { revalidate: 60 },
    });
    if (!res.ok) throw new Error(`${res.status}`);
    const d = await res.json();
    const equity = parseFloat(d.equity);
    const lastEquity = parseFloat(d.last_equity);
    return NextResponse.json({
      equity,
      cash: parseFloat(d.cash),
      buying_power: parseFloat(d.buying_power),
      last_equity: lastEquity,
      today_pnl: equity - lastEquity,
      today_pnl_pct: ((equity - lastEquity) / lastEquity) * 100,
    });
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 });
  }
}
