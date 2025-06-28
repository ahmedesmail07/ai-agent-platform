import React, { useState, useEffect } from "react";
import { Plus, Edit, Trash2, MessageSquare } from "lucide-react";
import { Agent, CreateAgentRequest } from "../types/api";
import { apiService } from "../services/api";

interface AgentListProps {
  selectedAgentId: number | null;
  onAgentSelect: (agent: Agent) => void;
  onRefresh: () => void;
}

interface AgentFormData {
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

const defaultFormData: AgentFormData = {
  name: "",
  description: "",
  agent_type: "chatbot",
  is_active: true,
  configuration: {
    model: "gpt-3.5-turbo",
    system_prompt: "You are a helpful assistant.",
    temperature: 0.7,
    max_tokens: 1000,
  },
  capabilities: [],
};

export const AgentList: React.FC<AgentListProps> = ({
  selectedAgentId,
  onAgentSelect,
  onRefresh,
}) => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  const [formData, setFormData] = useState<AgentFormData>(defaultFormData);

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getAgents(1, 100);
      if (response && response.items && Array.isArray(response.items)) {
        setAgents(response.items);
      } else {
        console.warn("Unexpected API response structure:", response);
        setAgents([]);
        setError("Invalid response format from server");
      }
    } catch (err) {
      setError("Failed to load agents");
      console.error("Error loading agents:", err);
      setAgents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAgent = () => {
    setEditingAgent(null);
    setFormData(defaultFormData);
    setShowForm(true);
  };

  const handleEditAgent = (agent: Agent) => {
    setEditingAgent(agent);
    const capabilities = agent.capabilities
      ? Object.entries(agent.capabilities)
          .filter(([_, enabled]) => enabled)
          .map(([capability]) => capability)
      : [];

    setFormData({
      name: agent.name,
      description: agent.description,
      agent_type: agent.agent_type,
      is_active: agent.is_active,
      configuration: agent.configuration,
      capabilities: capabilities,
    });
    setShowForm(true);
  };

  const handleDeleteAgent = async (agentId: number) => {
    if (window.confirm("Are you sure you want to delete this agent?")) {
      try {
        await apiService.deleteAgent(agentId);
        await loadAgents();
        onRefresh();
      } catch (err) {
        setError("Failed to delete agent");
        console.error("Error deleting agent:", err);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const capabilitiesDict: Record<string, boolean> = {};
      const capabilities = Array.isArray(formData.capabilities)
        ? formData.capabilities
        : Object.keys(formData.capabilities || {});

      capabilities.forEach((cap) => {
        capabilitiesDict[cap] = true;
      });

      const payload = {
        ...formData,
        capabilities: capabilitiesDict,
      };

      if (editingAgent) {
        await apiService.updateAgent(editingAgent.id, payload);
      } else {
        await apiService.createAgent(payload as CreateAgentRequest);
      }
      setShowForm(false);
      await loadAgents();
      onRefresh();
    } catch (err) {
      setError("Failed to save agent");
      console.error("Error saving agent:", err);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    if (field.includes(".")) {
      const [parent, child] = field.split(".");
      setFormData((prev) => ({
        ...prev,
        [parent]: {
          ...(prev[parent as keyof AgentFormData] as any),
          [child]: value,
        },
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        [field]: value,
      }));
    }
  };

  if (loading) {
    return (
      <div className="w-80 bg-gray-50 border-r border-gray-200 p-4">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-80 bg-gray-50 border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Agents</h2>
          <button
            onClick={handleCreateAgent}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Plus size={20} />
          </button>
        </div>
      </div>

      {/* Agent List */}
      <div className="flex-1 overflow-y-auto p-4">
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {(agents || []).length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <MessageSquare size={48} className="mx-auto mb-4 text-gray-300" />
            <p>No agents found</p>
            <p className="text-sm">Create your first agent to get started</p>
          </div>
        ) : (
          <div className="space-y-2">
            {(agents || []).map((agent) => (
              <div
                key={agent.id}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  selectedAgentId === agent.id
                    ? "bg-primary-100 border border-primary-200"
                    : "bg-white border border-gray-200 hover:bg-gray-50"
                }`}
              >
                <div
                  className="flex items-center justify-between"
                  onClick={() => onAgentSelect(agent)}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-medium text-gray-900 truncate">
                        {agent.name}
                      </h3>
                      {!agent.is_active && (
                        <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                          Inactive
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 truncate">
                      {agent.description}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {agent.agent_type} • {agent.configuration.model}
                    </p>
                  </div>
                  <div className="flex items-center space-x-1 ml-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditAgent(agent);
                      }}
                      className="p-1 text-gray-400 hover:text-gray-600 rounded"
                    >
                      <Edit size={16} />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteAgent(agent.id);
                      }}
                      className="p-1 text-gray-400 hover:text-red-600 rounded"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Agent Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">
              {editingAgent ? "Edit Agent" : "Create Agent"}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange("name", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) =>
                    handleInputChange("description", e.target.value)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  rows={3}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Agent Type
                </label>
                <select
                  value={formData.agent_type}
                  onChange={(e) =>
                    handleInputChange("agent_type", e.target.value)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="chatbot">Chatbot</option>
                  <option value="assistant">Assistant</option>
                  <option value="specialist">Specialist</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Model
                </label>
                <select
                  value={formData.configuration.model}
                  onChange={(e) =>
                    handleInputChange("configuration.model", e.target.value)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-4-turbo">GPT-4 Turbo</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  System Prompt
                </label>
                <textarea
                  value={formData.configuration.system_prompt}
                  onChange={(e) =>
                    handleInputChange(
                      "configuration.system_prompt",
                      e.target.value
                    )
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  rows={3}
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Temperature
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="2"
                    value={formData.configuration.temperature}
                    onChange={(e) =>
                      handleInputChange(
                        "configuration.temperature",
                        parseFloat(e.target.value)
                      )
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Max Tokens
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="4000"
                    value={formData.configuration.max_tokens}
                    onChange={(e) =>
                      handleInputChange(
                        "configuration.max_tokens",
                        parseInt(e.target.value)
                      )
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) =>
                    handleInputChange("is_active", e.target.checked)
                  }
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label
                  htmlFor="is_active"
                  className="ml-2 block text-sm text-gray-900"
                >
                  Active
                </label>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
                >
                  {editingAgent ? "Update" : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
