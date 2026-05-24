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
      `${BASE}/v2/orders?status=closed&limit=50&direction=desc`,
      { headers: alpacaHeaders(), next: { revalidate: 60 } }
    );
    if (!res.ok) throw new Error(`${res.status}`);
    const data = await res.json();
    const filled = data.filter((o: any) => o.status === "filled");
    return NextResponse.json(
      filled.map((o: any) => ({
        id: o.id,
        symbol: o.symbol,
        side: o.side,
        qty: parseFloat(o.filled_qty),
        price: parseFloat(o.filled_avg_price),
        filled_at: o.filled_at,
      }))
    );
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 });
  }
}
