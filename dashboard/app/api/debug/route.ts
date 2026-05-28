import { NextResponse } from "next/server";

export async function GET() {
  const token = process.env.CLICKUP_API_TOKEN || "";
  const tokenInfo = {
    length: token.length,
    first6: token.slice(0, 6),
    last4: token.slice(-4),
    startsWithPk: token.startsWith("pk_"),
  };

  const testRes = await fetch(
    "https://api.clickup.com/api/v2/list/901416672082/task?limit=1",
    { headers: { Authorization: token }, cache: "no-store" }
  );

  const body = await testRes.text();

  return NextResponse.json({
    tokenInfo,
    clickupStatus: testRes.status,
    clickupResponse: body.slice(0, 300),
  });
}
