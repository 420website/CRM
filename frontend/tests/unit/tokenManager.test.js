import { describe, it, expect, beforeEach, vitest } from "vitest";
import { tokenManager } from "../../src/tokenManager";

describe("TokenManager", () => {
  beforeEach(() => {
    // Clear token and listeners before each test
    tokenManager.clearAccessToken();
    tokenManager.listeners = [];
  });

  it("initial token is null", () => {
    expect(tokenManager.getAccessToken()).toBeNull();
  });

  it("setAccessToken sets the token", () => {
    tokenManager.setAccessToken("abc123");
    expect(tokenManager.getAccessToken()).toBe("abc123");
  });

  it("clearAccessToken clears the token", () => {
    tokenManager.setAccessToken("token");
    tokenManager.clearAccessToken();
    expect(tokenManager.getAccessToken()).toBeNull();
  });

  it("subscribe adds a listener and returns unsubscribe function", () => {
    const listener = vitest.fn();
    const unsubscribe = tokenManager.subscribe(listener);

    expect(tokenManager.listeners).toContain(listener);

    unsubscribe();
    expect(tokenManager.listeners).not.toContain(listener);
  });

  it("listeners are notified on setAccessToken", () => {
    const listener = vitest.fn();
    tokenManager.subscribe(listener);

    tokenManager.setAccessToken("newtoken");

    expect(listener).toHaveBeenCalledWith("newtoken");
  });

  it("listeners are notified on clearAccessToken", () => {
    const listener = vitest.fn();
    tokenManager.subscribe(listener);

    tokenManager.setAccessToken("token");
    tokenManager.clearAccessToken();

    expect(listener).toHaveBeenCalledWith(null);
  });

  it("multiple listeners are notified", () => {
    const listener1 = vitest.fn();
    const listener2 = vitest.fn();

    tokenManager.subscribe(listener1);
    tokenManager.subscribe(listener2);

    tokenManager.setAccessToken("token123");

    expect(listener1).toHaveBeenCalledWith("token123");
    expect(listener2).toHaveBeenCalledWith("token123");
  });
});
