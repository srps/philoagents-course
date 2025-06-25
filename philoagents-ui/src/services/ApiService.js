import SessionService from './SessionService.js';

class ApiService {
  constructor() {
    const isHttps = window.location.protocol === 'https:';

    if (isHttps) {
      console.log('Using GitHub Codespaces');
      const currentHostname = window.location.hostname;
      this.apiUrl = `https://${currentHostname.replace('8080', '8000')}`;
    } else {
      this.apiUrl = 'http://localhost:8000';
    }
  }

  async request(endpoint, method, data) {
    const url = `${this.apiUrl}${endpoint}`;
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    };

    const response = await fetch(url, options);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  }

  async sendMessage(philosopher, message) {
    try {
      // Ensure we have a session
      await SessionService.ensureSession();
      const userId = SessionService.getUserId();

      const data = await this.request('/chat', 'POST', {
        message,
        philosopher_id: philosopher.id,
        user_id: userId
      });

      return data.response;
    } catch (error) {
      console.error('Error sending message to API:', error);
      return this.getFallbackResponse(philosopher);
    }
  }

  getFallbackResponse(philosopher) {
    return `I'm sorry, ${philosopher.name || 'the philosopher'} is unavailable at the moment. Please try again later.`;
  }

  async resetMemory() {
    try {
      // Use SessionService to reset user-specific conversations
      return await SessionService.resetUserConversations();
    } catch (error) {
      console.error('Error resetting memory:', error);
      throw error;
    }
  }
}

export default new ApiService(); 