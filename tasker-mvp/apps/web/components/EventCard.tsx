"use client";

import { useState } from "react";
import { confirmRide, getRecommendation } from "../lib/api";

export function EventCard({ plan }: { plan: any }) {
  const [rec, setRec] = useState<any>(null);
  const [busy, setBusy] = useState(false);

  async function preview() {
    setBusy(true);
    const r = await getRecommendation(plan.eventId);
    setRec(r);
    setBusy(false);
  }

  async function approveAndRequest() {
    const approvedCharge = window.confirm("I approve this charge and want to request this Uber.");
    if (!approvedCharge) return;
    const result = await confirmRide({
      userId: "demo-user",
      approvedCharge: true,
      productId: rec.recommended.productId,
      origin: rec.plan.origin,
      destination: rec.plan.destination,
      latestArrivalIso: rec.plan.arriveBy,
    });
    alert(`Ride requested: ${result.rideId}`);
  }

  return (
    <div className="card">
      <div><strong>{plan.eventKind.toUpperCase()}</strong> • leave by {new Date(plan.leaveBy).toLocaleTimeString()}</div>
      <div className="small">{plan.origin} → {plan.destination}</div>
      <div className="row" style={{ marginTop: 10 }}>
        <button className="btn btn-primary" onClick={preview} disabled={busy}>{busy ? "Loading..." : "Request Uber"}</button>
        {plan.urgent ? <span className="small">Urgent: leave within {45} min</span> : null}
      </div>
      {rec ? (
        <div className="card" style={{ marginTop: 10 }}>
          <div>Recommended: {rec.recommended.displayName} (${rec.recommended.lowEstimate}-${rec.recommended.highEstimate})</div>
          <div className="small">Pickup ETA {rec.recommended.pickupEtaMinutes}m • confidence {rec.plan.confidence}</div>
          <button className="btn btn-primary" onClick={approveAndRequest} style={{ marginTop: 8 }}>Confirm & Request Uber</button>
        </div>
      ) : null}
    </div>
  );
}
