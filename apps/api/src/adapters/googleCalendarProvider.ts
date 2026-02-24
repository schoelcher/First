import { CalendarProvider } from "../lib/contracts";
import { prisma } from "../lib/prisma";

export class GoogleCalendarProvider implements CalendarProvider {
  async syncEvents(userId: string, fullResync = false): Promise<void> {
    const user = await prisma.user.findUniqueOrThrow({ where: { id: userId } });
    const mockEvents = [
      {
        providerEventId: "evt_1",
        title: "Team dinner",
        startsAt: new Date(Date.now() + 2 * 60 * 60 * 1000),
        locationName: "123 Main St, San Francisco, CA",
        isVirtual: false
      }
    ];

    if (fullResync) {
      await prisma.event.deleteMany({ where: { userId } });
    }

    for (const e of mockEvents) {
      await prisma.event.upsert({
        where: { userId_providerEventId: { userId, providerEventId: e.providerEventId } },
        update: e,
        create: { ...e, userId }
      });
    }

    await prisma.user.update({ where: { id: userId }, data: { googleSyncToken: `sync_${Date.now()}` } });
    await prisma.auditLog.create({ data: { userId, action: "calendar.sync", metadata: JSON.stringify({ fullResync, bookingMode: user.bookingMode }) } });
  }

  async watchCalendar(userId: string): Promise<void> {
    await prisma.auditLog.create({ data: { userId, action: "calendar.watch.renew", metadata: JSON.stringify({ renewedAt: new Date().toISOString() }) } });
  }
}
