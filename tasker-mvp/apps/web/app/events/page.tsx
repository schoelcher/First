import { EventCard } from "../../components/EventCard";
import { getEligibleEvents } from "../../lib/api";

export default async function EventsPage() {
  const plans = await getEligibleEvents();
  return (
    <div>
      <h2>Upcoming travel events</h2>
      <p className="small">Mobile-first flow: preview recommendation, then explicit charge approval before booking.</p>
      {plans.length === 0 ? <div className="card">No away-location events found.</div> : plans.map((p: any) => <EventCard key={p.eventId} plan={p} />)}
    </div>
  );
}
