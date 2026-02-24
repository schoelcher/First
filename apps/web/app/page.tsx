import { EventCard } from "../components/EventCard";

const apiUrl = process.env.API_URL ?? "http://localhost:4000";

async function getEvents() {
  const res = await fetch(`${apiUrl}/events/demo-user`, { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
}

export default async function Home() {
  const events = await getEvents();
  return (
    <main className="container">
      <h1>Leave-by Uber Assistant</h1>
      <p className="meta">Mobile-first PWA for calendar travel planning with explicit charge confirmation.</p>
      {events.length === 0 ? <p className="card">Connect calendar to begin.</p> : events.map((e: any) => <EventCard key={e.event.id} event={e} apiUrl={apiUrl} />)}
    </main>
  );
}
