// tokenManager.js
class TokenManager {
  constructor() {
    this.accessToken = null;
    this.expiresAt = null;
    this.listeners = [];
  }

  setAccessToken(token) {
    this.accessToken = token;
    this.notifyListeners(token);
  }

  getAccessToken() {
    return this.accessToken;
  }

  setExpiresAt(expiresAt) {
    this.expiresAt = expiresAt;
  }

  getExpiresAt() {
    return this.expiresAt;
  }

  expiresSoon(thresholdMinutes = 5) {
    if (!this.expiresAt) {
      return true; // If no expiry set, assume it needs refresh
    }

    const now = new Date();
    const expiry = new Date(this.expiresAt);
    const minutesUntilExpiry = (expiry - now) / 1000 / 60;

    return minutesUntilExpiry < thresholdMinutes;
  }

  isExpired() {
    if (!this.expiresAt) {
      return true;
    }

    const now = new Date();
    const expiry = new Date(this.expiresAt);

    return now >= expiry;
  }

  clearAccessToken() {
    this.accessToken = null;
    this.expiresAt = null;
    this.notifyListeners(null);
  }

  // For components that want to listen to token changes
  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener);
    };
  }

  notifyListeners(token) {
    this.listeners.forEach((listener) => listener(token));
  }
}

export const tokenManager = new TokenManager();
