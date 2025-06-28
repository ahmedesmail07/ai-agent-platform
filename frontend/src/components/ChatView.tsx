import React, { useRef, useEffect } from "react";
import { User, Bot, Clock, Volume2, MessageSquare } from "lucide-react";
import { Message, Agent } from "../types/api";
import { apiService } from "../services/api";

interface ChatViewProps {
  messages: Message[];
  selectedAgent: Agent | null;
  selectedSessionId: number | null;
  loading: boolean;
}

export const ChatView: React.FC<ChatViewProps> = ({
  messages,
  selectedAgent,
  selectedSessionId,
  loading,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioRefs = useRef<{ [key: number]: HTMLAudioElement | null }>({});

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return "Today";
    } else if (date.toDateString() === yesterday.toDateString()) {
      return "Yesterday";
    } else {
      return date.toLocaleDateString();
    }
  };

  const playAudio = async (messageId: number, audioUrl: string) => {
    try {
      const audioElement = audioRefs.current[messageId];
      if (audioElement) {
        // Extract filename from the audio URL
        const filename = audioUrl.split("/").pop();
        if (filename) {
          // Use the correct base URL for audio files
          const baseUrl =
            process.env.REACT_APP_API_URL?.replace("/api/v1", "") ||
            "http://localhost:8000";
          const directAudioUrl = `${baseUrl}/audio/${filename}`;
          audioElement.src = directAudioUrl;
          await audioElement.play();
        }
      }
    } catch (error) {
      console.error("Error playing audio:", error);
    }
  };

  const renderMessage = (message: Message, index: number) => {
    const isUser = message.role === "user";
    const showDate =
      index === 0 ||
      formatDate(message.created_at) !==
        formatDate(messages[index - 1].created_at);

    return (
      <div key={message.id}>
        {showDate && (
          <div className="flex justify-center my-4">
            <div className="px-3 py-1 bg-gray-100 rounded-full text-xs text-gray-600">
              {formatDate(message.created_at)}
            </div>
          </div>
        )}

        <div
          className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}
        >
          <div
            className={`flex max-w-[70%] ${
              isUser ? "flex-row-reverse" : "flex-row"
            }`}
          >
            {/* Avatar */}
            <div
              className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                isUser ? "ml-3 bg-primary-100" : "mr-3 bg-gray-100"
              }`}
            >
              {isUser ? (
                <User size={16} className="text-primary-600" />
              ) : (
                <Bot size={16} className="text-gray-600" />
              )}
            </div>

            {/* Message Content */}
            <div
              className={`flex flex-col ${
                isUser ? "items-end" : "items-start"
              }`}
            >
              <div
                className={`px-4 py-3 rounded-lg ${
                  isUser
                    ? "bg-primary-600 text-white"
                    : "bg-gray-100 text-gray-900"
                }`}
              >
                <div className="whitespace-pre-wrap break-words">
                  {message.content}
                </div>

                {/* Audio playback for voice messages */}
                {message.audio_metadata?.output_audio_path && (
                  <div className="mt-2">
                    <button
                      onClick={() =>
                        playAudio(
                          message.id,
                          message.audio_metadata!.output_audio_path!
                        )
                      }
                      className={`flex items-center space-x-2 px-2 py-1 rounded text-xs ${
                        isUser
                          ? "bg-primary-700 text-white hover:bg-primary-800"
                          : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                      } transition-colors`}
                    >
                      <Volume2 size={12} />
                      <span>Play Audio</span>
                    </button>
                    <audio
                      ref={(el) => {
                        audioRefs.current[message.id] = el;
                      }}
                      src={`${
                        process.env.REACT_APP_API_URL?.replace("/api/v1", "") ||
                        "http://localhost:8000"
                      }/audio/${message
                        .audio_metadata!.output_audio_path!.split("/")
                        .pop()}`}
                      preload="none"
                    />
                  </div>
                )}

                {/* Transcription for voice messages */}
                {message.audio_metadata?.transcription_text && (
                  <div
                    className={`mt-2 text-xs ${
                      isUser ? "text-primary-200" : "text-gray-500"
                    }`}
                  >
                    <div className="flex items-center space-x-1 mb-1">
                      <Volume2 size={10} />
                      <span>Transcription:</span>
                    </div>
                    <div className="italic">
                      "{message.audio_metadata.transcription_text}"
                    </div>
                  </div>
                )}
              </div>

              {/* Timestamp */}
              <div
                className={`flex items-center space-x-1 mt-1 text-xs text-gray-500 ${
                  isUser ? "flex-row-reverse" : "flex-row"
                }`}
              >
                <Clock size={10} />
                <span>{formatTime(message.created_at)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (!selectedAgent) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center text-gray-500">
          <Bot size={48} className="mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium mb-2">
            Welcome to AI Agent Platform
          </h3>
          <p className="text-sm">
            Select an agent from the sidebar to start chatting
          </p>
        </div>
      </div>
    );
  }

  if (!selectedSessionId) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center text-gray-500">
          <MessageSquare size={48} className="mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium mb-2">No Session Selected</h3>
          <p className="text-sm">
            Create a new session or select an existing one to start chatting
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-gray-50">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500">
              <MessageSquare size={48} className="mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium mb-2">Start a Conversation</h3>
              <p className="text-sm">
                Send a message to begin chatting with {selectedAgent.name}
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            {messages.map((message, index) => renderMessage(message, index))}

            {loading && (
              <div className="flex justify-start mb-4">
                <div className="flex max-w-[70%]">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center mr-3">
                    <Bot size={16} className="text-gray-600" />
                  </div>
                  <div className="px-4 py-3 bg-gray-100 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: "0.1s" }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: "0.2s" }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-500">Typing...</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};
