import React, { useState, useRef, useEffect } from "react";
import { Send, Mic, Square } from "lucide-react";
import { useVoiceRecorder } from "../hooks/useVoiceRecorder";

interface ChatInputProps {
  onSendMessage: (content: string) => void;
  onSendVoiceMessage: (audioFile: File) => void;
  disabled: boolean;
  loading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  onSendVoiceMessage,
  disabled,
  loading,
}) => {
  const [message, setMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [shouldSendAudio, setShouldSendAudio] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const {
    isRecording: voiceRecording,
    recordingTime,
    startRecording,
    stopRecording,
    audioBlob,
    error: voiceError,
  } = useVoiceRecorder();

  useEffect(() => {
    if (audioBlob && !voiceRecording && shouldSendAudio) {
      // Convert blob to file and send
      const audioFile = new File(
        [audioBlob],
        `voice_message_${Date.now()}.webm`,
        {
          type: "audio/webm",
        }
      );
      onSendVoiceMessage(audioFile);
      setShouldSendAudio(false); // Reset the flag after sending
    }
  }, [audioBlob, voiceRecording, onSendVoiceMessage, shouldSendAudio]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled && !loading) {
      onSendMessage(message.trim());
      setMessage("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    // Auto-resize textarea
    e.target.style.height = "auto";
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  const handleVoiceRecord = async () => {
    if (voiceRecording) {
      stopRecording();
      setIsRecording(false);
      setShouldSendAudio(true); // Set flag to true when stopping recording
    } else {
      try {
        await startRecording();
        setIsRecording(true);
      } catch (err) {
        console.error("Failed to start recording:", err);
      }
    }
  };

  const formatRecordingTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      {voiceError && (
        <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {voiceError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex items-end space-x-3">
        {/* Voice Recording Button */}
        <button
          type="button"
          onClick={handleVoiceRecord}
          disabled={disabled || loading}
          className={`flex-shrink-0 p-3 rounded-lg transition-colors ${
            voiceRecording
              ? "bg-red-500 text-white hover:bg-red-600"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          } ${disabled || loading ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          {voiceRecording ? (
            <div className="flex items-center space-x-2">
              <Square size={20} />
              <span className="text-sm font-medium">
                {formatRecordingTime(recordingTime)}
              </span>
            </div>
          ) : (
            <Mic size={20} />
          )}
        </button>

        {/* Text Input */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleTextareaChange}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={disabled || loading || voiceRecording}
            className={`w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
              disabled || loading || voiceRecording
                ? "opacity-50 cursor-not-allowed"
                : ""
            }`}
            style={{ minHeight: "48px", maxHeight: "120px" }}
            rows={1}
          />

          {/* Recording indicator */}
          {voiceRecording && (
            <div className="absolute top-2 right-2 flex items-center space-x-1">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-red-600 font-medium">
                Recording
              </span>
            </div>
          )}
        </div>

        {/* Send Button */}
        <button
          type="submit"
          disabled={(!message.trim() && !voiceRecording) || disabled || loading}
          className={`flex-shrink-0 p-3 rounded-lg transition-colors ${
            message.trim() || voiceRecording
              ? "bg-primary-600 text-white hover:bg-primary-700"
              : "bg-gray-100 text-gray-400 cursor-not-allowed"
          } ${disabled || loading ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          {loading ? (
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
          ) : (
            <Send size={20} />
          )}
        </button>
      </form>

      {/* Voice recording status */}
      {voiceRecording && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-red-700">
                Recording voice message...
              </span>
            </div>
            <span className="text-sm text-red-600 font-mono">
              {formatRecordingTime(recordingTime)}
            </span>
          </div>
          <p className="text-xs text-red-600 mt-1">
            Click the stop button to finish recording
          </p>
        </div>
      )}
    </div>
  );
};
