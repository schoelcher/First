"use client";

import { useState } from "react";

export default function SettingsPage() {
  const [homeBase, setHomeBase] = useState("1 Market St, San Francisco, CA");
  const [meetingEarly, setMeetingEarly] = useState(10);
  const [dinnerEarly, setDinnerEarly] = useState(15);

  return (
    <div>
      <h2>Settings</h2>
      <div className="card">
        <label>Home base address</label>
        <input value={homeBase} onChange={(e) => setHomeBase(e.target.value)} />
        <div style={{ height: 8 }} />
        <label>Meeting early arrival minutes</label>
        <input type="number" value={meetingEarly} onChange={(e) => setMeetingEarly(Number(e.target.value))} />
        <div style={{ height: 8 }} />
        <label>Dinner early arrival minutes</label>
        <input type="number" value={dinnerEarly} onChange={(e) => setDinnerEarly(Number(e.target.value))} />
        <p className="small">Additional fields (flight buffers, cushion, quiet hours, notifications) are exposed via backend settings API.</p>
      </div>
    </div>
  );
}
