import { RideProvider } from "../lib/contracts";
import { env } from "../lib/env";
import { prisma } from "../lib/prisma";

export class UberProvider implements RideProvider {
  detectMode(): "API_BOOKING" | "DEEPLINK_BOOKING" {
    return env.uberApiEnabled ? "API_BOOKING" : "DEEPLINK_BOOKING";
  }

  async estimateRide(): Promise<{ product: string; min: number; max: number; pickupEtaMins: number }> {
    return { product: "UberX", min: 18, max: 24, pickupEtaMins: 6 };
  }

  async confirmBooking(input: { mode: "API_BOOKING" | "DEEPLINK_BOOKING"; approval: boolean; eventId: string }): Promise<{ status: string; deeplink?: string; requestId?: string }> {
    if (!input.approval) throw new Error("Explicit approval required");

    if (input.mode === "API_BOOKING") {
      const requestId = `uber_req_${Date.now()}`;
      await prisma.auditLog.create({ data: { eventId: input.eventId, action: "ride.booked.api", metadata: JSON.stringify({ requestId }) } });
      return { status: "booked", requestId };
    }

    const deeplink = "https://m.uber.com/ul/?action=setPickup";
    await prisma.auditLog.create({ data: { eventId: input.eventId, action: "ride.booked.deeplink", metadata: JSON.stringify({ deeplink }) } });
    return { status: "redirect", deeplink };
  }
}
