export interface Agent {
    id: number;
    name: string;
    description: string;
    agent_type: string;
    is_active: boolean;
    configuration: {
        model: string;
        system_prompt: string;
        temperature: number;
        max_tokens: number;
    };
    capabilities: string[] | Record<string, boolean>;
    created_at: string;
    updated_at: string;
}

export interface ChatSession {
    id: number;
    agent_id: number;
    status: string;
    created_at: string;
    updated_at: string;
    agent?: Agent;
}

export interface Message {
    id: number;
    session_id: number;
    content: string;
    role: 'user' | 'assistant';
    created_at: string;
    audio_metadata?: AudioMetadata;
}

export interface AudioMetadata {
    id: number;
    message_id: number;
    input_audio_path?: string;
    output_audio_path?: string;
    input_audio_format?: string;
    output_audio_format?: string;
    input_audio_duration?: number;
    output_audio_duration?: number;
    transcription_text?: string;
    tts_voice?: string;
    additional_metadata?: Record<string, any>;
    created_at: string;
}

export interface VoiceResponse {
    message: string;
    session_id: number;
    audio_url: string;
    transcription: string;
}

export interface CreateAgentRequest {
    name: string;
    description: string;
    agent_type: string;
    is_active: boolean;
    configuration: {
        model: string;
        system_prompt: string;
        temperature: number;
        max_tokens: number;
    };
    capabilities: string[] | Record<string, boolean>;
}

export interface CreateMessageRequest {
    content: string;
}

export interface ApiResponse<T> {
    data: T;
    message?: string;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    size: number;
    pages: number;
} 