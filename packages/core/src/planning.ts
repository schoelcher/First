import { LeaveByInput } from "./types";

export function classifyFlightType(input: LeaveByInput): "domestic" | "international" | "none" {
  const text = `${input.eventTitle} ${input.eventDescription ?? ""}`.toLowerCase();
  if (!input.isAirport) return "none";
  if (input.userFlightOverride) return input.userFlightOverride;
  if (/(international|intl|passport|customs)/.test(text)) return "international";
  return "domestic";
}

export function earlyArrivalMinutes(input: LeaveByInput): number {
  const title = input.eventTitle.toLowerCase();
  if (input.isAirport) {
    const flightType = classifyFlightType(input);
    if (flightType === "international") return input.settings.internationalFlightBufferMins;
    if (flightType === "domestic") return input.settings.domesticFlightBufferMins;
  }
  if (/(dinner|restaurant|reservation)/.test(title)) return input.settings.dinnerEarlyMins;
  return input.settings.meetingEarlyMins;
}

export function uncertaintyCushion(etaMins: number, settings: LeaveByInput["settings"]): number {
  return Math.min(settings.uncertaintyMaxMins, Math.round(etaMins * settings.uncertaintyPct + settings.uncertaintyBaseMins));
}

export function computeLeaveBy(input: LeaveByInput) {
  const early = earlyArrivalMinutes(input);
  const cushion = uncertaintyCushion(input.etaMins, input.settings);
  const arriveBy = new Date(input.eventStart.getTime() - early * 60_000);
  const leaveBy = new Date(arriveBy.getTime() - (input.etaMins + cushion) * 60_000);
  return { leaveBy, arriveBy, earlyArrivalMins: early, uncertaintyMins: cushion };
}

export function requestWindow(now: Date, leaveBy: Date, settings: LeaveByInput["settings"]) {
  const start = new Date(leaveBy.getTime() - settings.requestWindowStartMins * 60_000);
  const end = new Date(leaveBy.getTime() + settings.requestWindowEndMins * 60_000);
  return { start, end, canRequestNow: now >= start && now <= end };
}
