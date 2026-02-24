"use client";
import { useState } from "react";

export function EventCard({ event, apiUrl }: { event: any; apiUrl: string }) {
  const [status, setStatus] = useState("");

  const confirm = async () => {
    const approved = window.confirm("I approve this charge and want to request Uber.");
    if (!approved) return;
    const response = await fetch(`${apiUrl}/events/${event.event.id}/confirm`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ approveCharge: true })
    });
    const body = await response.json();
    if (body.deeplink) window.open(body.deeplink, "_blank");
    setStatus(`Booking flow started: ${body.mode}`);
  };

  return (
    <article className="card">
      <h3>{event.event.title}</h3>
      <p className="meta">Leave by {new Date(event.leaveBy).toLocaleTimeString()}</p>
      <p className="meta">ETA {event.recommendation.route.etaMins}m · {event.recommendation.pricing.product} ${event.recommendation.pricing.min}-${event.recommendation.pricing.max}</p>
      <button className="btn" onClick={confirm}>Confirm & Request Uber</button>
      <button className="btn secondary" style={{ marginTop: 8 }}>Snooze 10m</button>
      <p className="meta">{status}</p>
    </article>
  );
}
