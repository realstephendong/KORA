
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiClient {
  private baseUrl: string;
  private getToken: (() => string | null) | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  setTokenProvider(getToken: () => string | null) {
    this.getToken = getToken;
  }

  private getAuthHeaders(): HeadersInit {
    const token = this.getToken ? this.getToken() : null;
    return {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    };
  }

  async get(endpoint: string): Promise<any> {
    const headers = this.getAuthHeaders();
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async post(endpoint: string, data: any): Promise<any> {
    const headers = this.getAuthHeaders();
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async put(endpoint: string, data: any): Promise<any> {
    const headers = this.getAuthHeaders();
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async delete(endpoint: string): Promise<any> {
    const headers = this.getAuthHeaders();
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

// Create a singleton instance
export const apiClient = new ApiClient();

// Function to set up the API client with auth context
export function setupApiClient(getToken: () => string | null) {
  apiClient.setTokenProvider(getToken);
}

// Debug API methods
export const debugApi = {
  // Test authentication
  async testAuth(): Promise<any> {
    return apiClient.get('/api/debug/auth');
  }
};

// Itinerary-related API methods
export const itineraryApi = {
  // Get all itineraries for the current user
  async getAllItineraries(): Promise<any> {
    return apiClient.get('/api/itineraries');
  },

  // Get a specific itinerary by ID
  async getItinerary(itineraryId: number): Promise<any> {
    return apiClient.get(`/api/itineraries/${itineraryId}`);
  },

  // Export itinerary as structured JSON for visualization
  async exportItinerary(itineraryId: number): Promise<any> {
    return apiClient.get(`/api/itineraries/${itineraryId}/export`);
  }
};
