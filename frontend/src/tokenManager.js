// tokenManager.js
class TokenManager {
  constructor() {
    this.accessToken = null;
    this.listeners = [];
  }

  setAccessToken(token) {
    this.accessToken = token;
    this.notifyListeners(token);
  }

  getAccessToken() {
    return this.accessToken;
  }

  clearAccessToken() {
    this.accessToken = null;
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
