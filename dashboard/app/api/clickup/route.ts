import { NextResponse } from "next/server";

async function fetchList(listId: string, token: string) {
  const res = await fetch(
    `https://api.clickup.com/api/v2/list/${listId}/task?limit=10`,
    { headers: { Authorization: token }, next: { revalidate: 300 } }
  );
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`List ${listId} → HTTP ${res.status}: ${body.slice(0, 200)}`);
  }
  const data = await res.json();
  return (data.tasks || []).map((t: any) => ({
    id: t.id,
    name: t.name,
    description: (t.description || "").slice(0, 300),
    created: parseInt(t.date_created),
    list: t.list?.name || listId,
  }));
}

export async function GET() {
  const token = process.env.CLICKUP_API_TOKEN;
  const lists = [
    process.env.CLICKUP_LIST_TRADES    || "901416672058",
    process.env.CLICKUP_LIST_DAILY     || "901416672079",
    process.env.CLICKUP_LIST_WEEKLY    || "901416672081",
    process.env.CLICKUP_LIST_PREMARKET || "901416672082",
  ];

  if (!token) {
    return NextResponse.json({ error: "CLICKUP_API_TOKEN not set in Vercel" }, { status: 500 });
  }

  const errors: string[] = [];
  const results = await Promise.all(
    lists.map((id) =>
      fetchList(id, token).catch((e: Error) => {
        errors.push(e.message);
        return [];
      })
    )
  );

  const all = results.flat().sort((a, b) => b.created - a.created);

  if (errors.length > 0 && all.length === 0) {
    return NextResponse.json({ error: "All ClickUp lists failed", details: errors }, { status: 500 });
  }

  return NextResponse.json(all);
}
