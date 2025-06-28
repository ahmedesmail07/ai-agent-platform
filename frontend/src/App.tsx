import React, { useState, useEffect } from "react";
import { AgentList } from "./components/AgentList";
import { SessionSelector } from "./components/SessionSelector";
import { ChatView } from "./components/ChatView";
import { ChatInput } from "./components/ChatInput";
import { Agent, ChatSession, Message } from "./types/api";
import { apiService } from "./services/api";

function App() {
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(
    null
  );
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load messages when session changes
  useEffect(() => {
    if (selectedSessionId) {
      loadMessages();
    } else {
      setMessages([]);
    }
  }, [selectedSessionId]);

  const loadMessages = async () => {
    if (!selectedSessionId) return;
    try {
      setLoading(true);
      setError(null);
      const msgs = await apiService.getSessionMessages(selectedSessionId);
      setMessages(msgs);
    } catch (err) {
      setError("Failed to load messages");
      console.error("Error loading messages:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAgentSelect = (agent: Agent) => {
    setSelectedAgent(agent);
    setSelectedSessionId(null);
    setMessages([]);
  };

  const handleSessionSelect = (session: ChatSession) => {
    setSelectedSessionId(session.id);
  };

  const handleNewSession = async () => {
    if (!selectedAgent) return;

    try {
      setLoading(true);
      const newSession = await apiService.createSession(selectedAgent.id);
      setSelectedSessionId(newSession.id);
      setMessages([]);
    } catch (err) {
      setError("Failed to create new session");
      console.error("Error creating session:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!selectedSessionId) return;
    const tempId = Date.now();
    const userMessage: Message = {
      id: tempId,
      session_id: selectedSessionId,
      content,
      role: "user",
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.sendMessage(selectedSessionId, {
        content,
      });
      setMessages((prev) => [...prev, response]);
    } catch (err) {
      setError("Failed to send message");
      setMessages((prev) => prev.filter((msg) => msg.id !== tempId));
    } finally {
      setLoading(false);
    }
  };

  const handleSendVoiceMessage = async (audioFile: File) => {
    if (!selectedSessionId) return;
    const tempId = Date.now();
    const userMessage: Message = {
      id: tempId,
      session_id: selectedSessionId,
      content: "🎤 Voice message...",
      role: "user",
      created_at: new Date().toISOString(),
      audio_metadata: {
        id: tempId,
        message_id: tempId,
        input_audio_path: audioFile.name,
        input_audio_format: "webm",
        created_at: new Date().toISOString(),
      },
    };
    setMessages((prev) => [...prev, userMessage]);
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.sendVoiceMessage(
        selectedSessionId,
        audioFile
      );
      let userTranscribedMessage: Message | null = null;
      if (response.transcription) {
        userTranscribedMessage = {
          id: tempId + 1,
          session_id: selectedSessionId,
          content: response.transcription,
          role: "user",
          created_at: new Date().toISOString(),
        };
      }
      const assistantMessage: Message = {
        id: tempId + 2,
        session_id: selectedSessionId,
        content: response.message,
        role: "assistant",
        created_at: new Date().toISOString(),
        audio_metadata: {
          id: tempId + 2,
          message_id: tempId + 2,
          output_audio_path: response.audio_url,
          output_audio_format: "mp3",
          transcription_text: response.transcription,
          created_at: new Date().toISOString(),
        },
      };
      setMessages((prev) => {
        let newMessages = [...prev];
        if (userTranscribedMessage) newMessages.push(userTranscribedMessage);
        newMessages.push(assistantMessage);
        return newMessages;
      });
    } catch (err) {
      setError("Failed to send voice message");
      setMessages((prev) => prev.filter((msg) => msg.id !== tempId));
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    // TODO: Implement refresh logic (for now just a log) :"D
    console.log("Refreshing...");
  };

  return (
    <div className="h-screen flex bg-gray-50">
      {/* Left Sidebar - Agent List */}
      <AgentList
        selectedAgentId={selectedAgent?.id || null}
        onAgentSelect={handleAgentSelect}
        onRefresh={handleRefresh}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Section - Session Selector */}
        <SessionSelector
          selectedAgent={selectedAgent}
          selectedSessionId={selectedSessionId}
          onSessionSelect={handleSessionSelect}
          onNewSession={handleNewSession}
        />

        {/* Center - Chat View */}
        <ChatView
          messages={messages}
          selectedAgent={selectedAgent}
          selectedSessionId={selectedSessionId}
          loading={loading}
        />

        {/* Bottom - Chat Input */}
        {selectedAgent && selectedSessionId && (
          <ChatInput
            onSendMessage={handleSendMessage}
            onSendVoiceMessage={handleSendVoiceMessage}
            disabled={!selectedAgent.is_active}
            loading={loading}
          />
        )}

        {/* Error Display */}
        {error && (
          <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg max-w-sm">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <div className="w-5 h-5 bg-red-400 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs font-bold">!</span>
                </div>
              </div>
              <div className="flex-1">
                <p className="text-sm text-red-800">{error}</p>
                <button
                  onClick={() => setError(null)}
                  className="mt-2 text-xs text-red-600 hover:text-red-800 underline"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
