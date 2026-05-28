import { NextResponse } from "next/server";

async function fetchList(listId: string, token: string) {
  try {
    const res = await fetch(
      `https://api.clickup.com/api/v2/list/${listId}/task?order_by=date_created&reverse=true&limit=10`,
      { headers: { Authorization: token }, next: { revalidate: 300 } }
    );
    if (!res.ok) return [];
    const data = await res.json();
    return (data.tasks || []).map((t: any) => ({
      id: t.id,
      name: t.name,
      description: (t.description || "").slice(0, 300),
      created: parseInt(t.date_created),
      list: t.list?.name || listId,
    }));
  } catch {
    return [];
  }
}

export async function GET() {
  const token = process.env.CLICKUP_API_TOKEN!;
  const lists = [
    process.env.CLICKUP_LIST_TRADES    || "901416672058",
    process.env.CLICKUP_LIST_DAILY     || "901416672079",
    process.env.CLICKUP_LIST_WEEKLY    || "901416672081",
    process.env.CLICKUP_LIST_PREMARKET || "901416672082",
  ];

  if (!token) {
    return NextResponse.json({ error: "CLICKUP_API_TOKEN not set" }, { status: 500 });
  }

  try {
    const results = await Promise.all(lists.map((id) => fetchList(id, token)));
    const all = results.flat().sort((a, b) => b.created - a.created);
    return NextResponse.json(all);
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 });
  }
}
