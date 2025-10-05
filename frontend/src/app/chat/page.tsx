'use client';

import { useState, useRef, useEffect } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';

interface ChatMessage {
  role: 'human' | 'ai';
  content: string;
}

interface ApiResponse {
  response: string;
  intermediate_steps: any[];
  success: boolean;
  timestamp: string;
  error?: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCountry, setSelectedCountry] = useState<any>(null);
  const [hasInitialized, setHasInitialized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize chat with country context
  useEffect(() => {
    const initializeChat = async () => {
      if (hasInitialized) return;
      
      try {
        // Get selected country from localStorage
        const storedCountry = localStorage.getItem('selectedCountry');
        if (storedCountry) {
          const countryData = JSON.parse(storedCountry);
          setSelectedCountry(countryData);
          
          // Send initial message to backend with country context
          const initialMessage = `I want to visit ${countryData.name}`;
          
          setIsLoading(true);
          const response: ApiResponse = await apiClient.post('/api/chat/message', {
            message: initialMessage,
            chat_history: [],
            country_context: countryData
          });

          const aiMessage: ChatMessage = {
            role: 'ai',
            content: response.response
          };

          setMessages([aiMessage]);
          setHasInitialized(true);
          
          // Clear the stored country after using it
          localStorage.removeItem('selectedCountry');
        } else {
          // No country selected, show default welcome
          const welcomeMessage: ChatMessage = {
            role: 'ai',
            content: "Welcome to Kora! Please select a country from the globe to start planning your sustainable travel adventure."
          };
          setMessages([welcomeMessage]);
          setHasInitialized(true);
        }
      } catch (err) {
        console.error('Error initializing chat:', err);
        const errorMessage: ChatMessage = {
          role: 'ai',
          content: "Welcome to Kora! I'm here to help you plan your sustainable travel adventure. How can I assist you today?"
        };
        setMessages([errorMessage]);
        setHasInitialized(true);
      } finally {
        setIsLoading(false);
      }
    };

    initializeChat();
  }, [hasInitialized]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'human',
      content: inputMessage.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const response: ApiResponse = await apiClient.post('/api/chat/message', {
        message: userMessage.content,
        chat_history: messages
      });

      const aiMessage: ChatMessage = {
        role: 'ai',
        content: response.response
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="max-w-4xl mx-auto h-screen flex flex-col">
          {/* Header */}
          <div className="bg-white shadow-sm border-b border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Travel Planning Assistant</h1>
                {selectedCountry && (
                  <p className="text-sm text-gray-600 mt-1">
                    Planning your trip to <span className="font-semibold text-blue-600">{selectedCountry.name}</span>
                  </p>
                )}
              </div>
              <div className="flex gap-2">
                <a 
                  href="/itineraries" 
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                >
                  My Trips
                </a>
                <a 
                  href="/profile" 
                  className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Profile
                </a>
                <a 
                  href="/globe" 
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Globe
                </a>
                <a 
                  href="/api/auth/logout" 
                  className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
                >
                  Logout
                </a>
              </div>
            </div>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 mt-8">
                <h3 className="text-xl font-semibold mb-2">Welcome to Kora!</h3>
                <p>Start planning your sustainable travel adventure. Tell me where you'd like to go!</p>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'human' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.role === 'human'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-800 shadow-sm border border-gray-200'
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white text-gray-800 shadow-sm border border-gray-200 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    <p className="text-sm">Thinking...</p>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="flex justify-center">
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 max-w-md">
                  <p className="text-red-600 text-sm">Error: {error}</p>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <div className="bg-white border-t border-gray-200 p-4">
            <form onSubmit={handleSendMessage} className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Tell me about your travel plans..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || isLoading}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Sending...' : 'Send'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
