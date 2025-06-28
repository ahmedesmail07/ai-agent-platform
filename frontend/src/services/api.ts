import axios, { AxiosInstance } from 'axios';
import {
    Agent,
    ChatSession,
    Message,
    VoiceResponse,
    CreateAgentRequest,
    CreateMessageRequest,
    PaginatedResponse,
} from '../types/api';

class ApiService {
    private api: AxiosInstance;
    private audioApi: AxiosInstance;

    constructor() {
        this.api = axios.create({
            baseURL: process.env.REACT_APP_API_URL || '/api/v1',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Separate API instance for audio files (without /api/v1 prefix)
        this.audioApi = axios.create({
            baseURL: process.env.REACT_APP_API_URL?.replace('/api/v1', '') || 'http://localhost:8000',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // just a small logging for debugging (for now :"D)
        this.api.interceptors.request.use(
            (config) => {
                console.log('API Request:', config.method?.toUpperCase(), config.url);
                return config;
            },
            (error) => {
                return Promise.reject(error);
            }
        );

        // just a small logging for debugging and error handling
        this.api.interceptors.response.use(
            (response) => {
                return response;
            },
            (error) => {
                console.error('API Error:', error.response?.data || error.message);
                return Promise.reject(error);
            }
        );
    }

    // Agent endpoints
    async getAgents(page: number = 1, size: number = 10): Promise<PaginatedResponse<Agent>> {
        const response = await this.api.get(`/agents/?page=${page}&size=${size}`);
        const agents = response.data;
        return {
            items: agents,
            total: agents.length,
            page: page,
            size: size,
            pages: Math.ceil(agents.length / size)
        };
    }

    async getAgent(id: number): Promise<Agent> {
        const response = await this.api.get(`/agents/${id}`);
        return response.data;
    }

    async createAgent(agent: CreateAgentRequest): Promise<Agent> {
        const response = await this.api.post('/agents/', agent);
        return response.data;
    }

    async updateAgent(id: number, agent: Partial<CreateAgentRequest>): Promise<Agent> {
        const response = await this.api.put(`/agents/${id}`, agent);
        return response.data;
    }

    async deleteAgent(id: number): Promise<void> {
        await this.api.delete(`/agents/${id}`);
    }

    // Session endpoints
    async getSessions(agentId: number, page: number = 1, size: number = 10): Promise<PaginatedResponse<ChatSession>> {
        const response = await this.api.get(`/agents/${agentId}/sessions?page=${page}&size=${size}`);
        const sessions = response.data;
        return {
            items: sessions,
            total: sessions.length,
            page: page,
            size: size,
            pages: Math.ceil(sessions.length / size)
        };
    }

    async createSession(agentId: number): Promise<ChatSession> {
        const response = await this.api.post(`/agents/${agentId}/sessions`);
        return response.data;
    }

    // Message endpoints
    async sendMessage(sessionId: number, message: CreateMessageRequest): Promise<Message> {
        const response = await this.api.post(`/sessions/${sessionId}/messages`, message);
        const agentResponse = response.data;
        return {
            id: Date.now(), // temp id for now, just to make it work (sorry :"D)
            session_id: sessionId,
            content: agentResponse.message,
            role: 'assistant',
            created_at: new Date().toISOString(),
        };
    }

    async getSessionMessages(sessionId: number): Promise<Message[]> {
        const response = await this.api.get(`/sessions/${sessionId}/messages`);
        // map the backend 'sender' to the frontend 'role' (for now)
        return response.data.map((msg: any) => ({
            ...msg,
            role: msg.sender === 'user' ? 'user' : 'assistant',
        }));
    }

    // Voice endpoints
    async sendVoiceMessage(sessionId: number, audioFile: File): Promise<VoiceResponse> {
        const formData = new FormData();
        formData.append('audio_file', audioFile);

        const response = await this.api.post(`/sessions/${sessionId}/voice`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    }

    async getAudioFile(filename: string): Promise<Blob> {
        const response = await this.audioApi.get(`/audio/${filename}`, {
            responseType: 'blob',
        });
        return response.data;
    }

    // Health check
    async healthCheck(): Promise<{ status: string }> {
        const response = await this.api.get('/health');
        return response.data;
    }
}

export const apiService = new ApiService(); 