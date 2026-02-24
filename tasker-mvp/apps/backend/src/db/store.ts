import type { UserSettings } from "../types.js";

const settings = new Map<string, UserSettings>();
const auditLogs: Array<{ userId: string; action: string; payload: unknown; at: string }> = [];

export function getSettings(userId: string): UserSettings {
  return settings.get(userId) ?? {
    userId,
    homeBase: process.env.DEFAULT_HOME_BASE || "1 Market St, San Francisco, CA",
    meetingEarlyMinutes: 10,
    dinnerEarlyMinutes: 15,
    domesticFlightMinutes: 90,
    internationalFlightMinutes: 180,
    cushionPercent: 0.1,
    cushionBaseMinutes: 5,
    cushionCapMinutes: 20,
    quietHoursStart: 22,
    quietHoursEnd: 7,
    urgencyThresholdMinutes: 45,
    notificationLeadMinutes: 20,
  };
}

export function saveSettings(userId: string, incoming: Partial<UserSettings>): UserSettings {
  const next = { ...getSettings(userId), ...incoming, userId };
  settings.set(userId, next);
  return next;
}

export function logAction(userId: string, action: string, payload: unknown): void {
  auditLogs.push({ userId, action, payload, at: new Date().toISOString() });
}

export function listAudit(userId: string) {
  return auditLogs.filter((l) => l.userId === userId);
}
