import type { CalendarEvent, EventKind } from "../types.js";

const VIRTUAL_MARKERS = ["zoom", "google meet", "teams", "webex", "http", "https"];
const AIRPORT_MAP: Record<string, string> = {
  SFO: "San Francisco International Airport, CA",
  LAX: "Los Angeles International Airport, CA",
  JFK: "John F. Kennedy International Airport, NY",
};

export function isVirtualEvent(event: CalendarEvent): boolean {
  const location = event.location?.toLowerCase() ?? "";
  return Boolean(event.conferenceData) || VIRTUAL_MARKERS.some((m) => location.includes(m));
}

export function normalizeDestination(location: string): string {
  const trimmed = location.trim();
  return AIRPORT_MAP[trimmed.toUpperCase()] ?? trimmed;
}

export function classifyEventKind(event: CalendarEvent): EventKind {
  const haystack = `${event.title} ${event.description ?? ""}`.toLowerCase();
  if (/flight|airline|terminal|\b[A-Z]{2}\d{1,4}\b/i.test(`${event.title} ${event.description ?? ""}`)) return "flight";
  if (/dinner|restaurant|supper/.test(haystack)) return "dinner";
  if (/meeting|sync|standup|review/.test(haystack)) return "meeting";
  return "other";
}

export function classifyFlightMode(event: CalendarEvent): "domestic" | "international" {
  const haystack = `${event.title} ${event.description ?? ""}`.toLowerCase();
  if (/(international|intl|passport|customs)/.test(haystack)) return "international";
  return "domestic";
}
