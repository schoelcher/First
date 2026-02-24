import "./globals.css";
import Link from "next/link";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main>
          <div className="row" style={{ justifyContent: "space-between", marginBottom: 12 }}>
            <strong>Tasker MVP</strong>
            <div className="row">
              <Link href="/events">Events</Link>
              <Link href="/settings">Settings</Link>
            </div>
          </div>
          {children}
        </main>
      </body>
    </html>
  );
}
