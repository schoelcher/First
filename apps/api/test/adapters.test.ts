import { describe, expect, it } from "vitest";
import { UberProvider } from "../src/adapters/uberProvider";
import { GoogleMapsProvider } from "../src/adapters/googleMapsProvider";

describe("provider adapters", () => {
  it("uber detects a booking mode", () => {
    const uber = new UberProvider();
    expect(["API_BOOKING", "DEEPLINK_BOOKING"]).toContain(uber.detectMode());
  });

  it("maps geocodes", async () => {
    const maps = new GoogleMapsProvider();
    const [result] = await maps.geocode("SFO");
    expect(result.lat).toBeTypeOf("number");
  });
});
