class SessionService {
  constructor() {
    this.apiUrl = this.determineApiUrl();
    this.sessionKey = 'philoagents_session';
    this.currentSession = null;
    this.initializeSession();
  }

  determineApiUrl() {
    const isHttps = window.location.protocol === 'https:';
    
    if (isHttps) {
      console.log('Using GitHub Codespaces');
      const currentHostname = window.location.hostname;
      return `https://${currentHostname.replace('8080', '8000')}`;
    }
    
    return 'http://localhost:8000';
  }

  async initializeSession() {
    // Try to load existing session from localStorage
    const storedSession = this.loadSessionFromStorage();
    
    if (storedSession && this.isSessionValid(storedSession)) {
      this.currentSession = storedSession;
      console.log('Loaded existing session:', this.currentSession.user_id);
    } else {
      // Create new session
      await this.createNewSession();
    }
  }

  loadSessionFromStorage() {
    try {
      const sessionData = localStorage.getItem(this.sessionKey);
      return sessionData ? JSON.parse(sessionData) : null;
    } catch (error) {
      console.error('Error loading session from storage:', error);
      return null;
    }
  }

  isSessionValid(session) {
    if (!session || !session.user_id || !session.created_at) {
      return false;
    }

    // Check if session is not older than 24 hours
    const createdAt = new Date(session.created_at);
    const now = new Date();
    const hoursDiff = (now - createdAt) / (1000 * 60 * 60);
    
    return hoursDiff < 24;
  }

  async createNewSession() {
    try {
      const response = await fetch(`${this.apiUrl}/session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to create session: ${response.status}`);
      }

      const sessionData = await response.json();
      this.currentSession = sessionData;
      
      // Store session in localStorage
      localStorage.setItem(this.sessionKey, JSON.stringify(sessionData));
      
      console.log('Created new session:', this.currentSession.user_id);
      return this.currentSession;
    } catch (error) {
      console.error('Error creating session:', error);
      
      // Fallback: create a temporary session with UUID
      this.currentSession = {
        user_id: crypto.randomUUID(),
        created_at: new Date().toISOString(),
        message: 'Fallback session created'
      };
      
      localStorage.setItem(this.sessionKey, JSON.stringify(this.currentSession));
      return this.currentSession;
    }
  }

  getUserId() {
    return this.currentSession ? this.currentSession.user_id : null;
  }

  getSession() {
    return this.currentSession;
  }

  async refreshSession() {
    await this.createNewSession();
    return this.currentSession;
  }

  clearSession() {
    this.currentSession = null;
    localStorage.removeItem(this.sessionKey);
    console.log('Session cleared');
  }

  async resetUserConversations() {
    if (!this.currentSession) {
      throw new Error('No active session');
    }

    try {
      const response = await fetch(`${this.apiUrl}/reset-memory`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: this.currentSession.user_id })
      });

      if (!response.ok) {
        throw new Error(`Failed to reset conversations: ${response.status}`);
      }

      const result = await response.json();
      console.log('User conversations reset:', result);
      return result;
    } catch (error) {
      console.error('Error resetting user conversations:', error);
      throw error;
    }
  }

  // Event system for session changes
  onSessionChange(callback) {
    if (!this._sessionChangeCallbacks) {
      this._sessionChangeCallbacks = [];
    }
    this._sessionChangeCallbacks.push(callback);
  }

  _notifySessionChange() {
    if (this._sessionChangeCallbacks) {
      this._sessionChangeCallbacks.forEach(callback => {
        try {
          callback(this.currentSession);
        } catch (error) {
          console.error('Error in session change callback:', error);
        }
      });
    }
  }

  // Ensure session is ready before use
  async ensureSession() {
    if (!this.currentSession) {
      await this.createNewSession();
    }
    return this.currentSession;
  }
}

export default new SessionService();
