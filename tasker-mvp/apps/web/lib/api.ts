const base = process.env.API_BASE_URL || "http://localhost:4000";

export async function getEligibleEvents() {
  const res = await fetch(`${base}/events/eligible?userId=demo-user`, { cache: "no-store" });
  return res.json();
}

export async function getRecommendation(eventId: string) {
  const res = await fetch(`${base}/events/${eventId}/recommendation`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ userId: "demo-user" }),
  });
  return res.json();
}

export async function confirmRide(payload: unknown) {
  const res = await fetch(`${base}/rides/confirm`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}
