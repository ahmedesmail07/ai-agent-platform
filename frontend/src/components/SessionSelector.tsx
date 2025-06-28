import React, { useState, useEffect, useCallback } from "react";
import { Plus, MessageSquare, Clock, ChevronDown } from "lucide-react";
import { ChatSession, Agent } from "../types/api";
import { apiService } from "../services/api";

interface SessionSelectorProps {
  selectedAgent: Agent | null;
  selectedSessionId: number | null;
  onSessionSelect: (session: ChatSession) => void;
  onNewSession: () => void;
}

export const SessionSelector: React.FC<SessionSelectorProps> = ({
  selectedAgent,
  selectedSessionId,
  onSessionSelect,
  onNewSession,
}) => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDropdown, setShowDropdown] = useState(false);

  const loadSessions = useCallback(async () => {
    if (!selectedAgent) return;

    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getSessions(selectedAgent.id, 1, 50);
      if (response && response.items && Array.isArray(response.items)) {
        setSessions(response.items);
      } else {
        console.warn("Unexpected API response structure:", response);
        setSessions([]);
        setError("Invalid response format from server");
      }
    } catch (err) {
      setError("Failed to load sessions");
      console.error("Error loading sessions:", err);
      setSessions([]);
    } finally {
      setLoading(false);
    }
  }, [selectedAgent]);

  useEffect(() => {
    if (selectedAgent) {
      loadSessions();
    } else {
      setSessions([]);
    }
  }, [selectedAgent, loadSessions]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
    } else if (diffInHours < 168) {
      // 7 days
      return date.toLocaleDateString([], { weekday: "short" });
    } else {
      return date.toLocaleDateString([], { month: "short", day: "numeric" });
    }
  };

  const getSelectedSession = () => {
    return sessions.find((session) => session.id === selectedSessionId);
  };

  const handleSessionSelect = (session: ChatSession) => {
    onSessionSelect(session);
    setShowDropdown(false);
  };

  if (!selectedAgent) {
    return (
      <div className="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-center">
        <div className="text-gray-500 text-center">
          <MessageSquare size={20} className="mx-auto mb-1" />
          <p className="text-sm">Select an agent to start chatting</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
            <MessageSquare size={16} className="text-primary-600" />
          </div>
          <div>
            <h2 className="text-sm font-medium text-gray-900">
              {selectedAgent.name}
            </h2>
            <p className="text-xs text-gray-500">{selectedAgent.agent_type}</p>
          </div>
        </div>

        <div className="relative">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-700 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <span>
              {getSelectedSession()
                ? `Session ${getSelectedSession()?.id}`
                : "Select Session"}
            </span>
            <ChevronDown
              size={16}
              className={`transition-transform ${
                showDropdown ? "rotate-180" : ""
              }`}
            />
          </button>

          {showDropdown && (
            <div className="absolute top-full left-0 mt-1 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto">
              <div className="p-2">
                {loading ? (
                  <div className="text-center py-4">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto"></div>
                    <p className="text-sm text-gray-500 mt-2">
                      Loading sessions...
                    </p>
                  </div>
                ) : error ? (
                  <div className="p-3 text-sm text-red-600 bg-red-50 rounded">
                    {error}
                  </div>
                ) : (sessions || []).length === 0 ? (
                  <div className="text-center py-4 text-gray-500">
                    <MessageSquare
                      size={24}
                      className="mx-auto mb-2 text-gray-300"
                    />
                    <p className="text-sm">No sessions yet</p>
                    <p className="text-xs">Start a new conversation</p>
                  </div>
                ) : (
                  <div className="space-y-1">
                    {(sessions || []).map((session) => (
                      <button
                        key={session.id}
                        onClick={() => handleSessionSelect(session)}
                        className={`w-full text-left p-2 rounded text-sm transition-colors ${
                          selectedSessionId === session.id
                            ? "bg-primary-50 text-primary-700"
                            : "hover:bg-gray-50 text-gray-700"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-medium">
                            Session {session.id}
                          </span>
                          <div className="flex items-center space-x-1 text-xs text-gray-500">
                            <Clock size={12} />
                            <span>{formatDate(session.created_at)}</span>
                          </div>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          Status: {session.status}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <button
        onClick={onNewSession}
        className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
      >
        <Plus size={16} />
        <span className="text-sm font-medium">New Session</span>
      </button>

      {/* Click outside to close dropdown */}
      {showDropdown && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setShowDropdown(false)}
        />
      )}
    </div>
  );
};
