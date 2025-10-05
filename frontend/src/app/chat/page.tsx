'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/ProtectedRoute';
import MarkdownRenderer from '@/components/MarkdownRenderer';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';

// TypeScript declarations for Web Speech API
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

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
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [locationInput, setLocationInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCountry, setSelectedCountry] = useState<any>(null);
  const [hasInitialized, setHasInitialized] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isVoiceSupported, setIsVoiceSupported] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [autoReadEnabled, setAutoReadEnabled] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);
  const speechSynthesisRef = useRef<any>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize voice recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        setIsVoiceSupported(true);
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = false;
        recognitionRef.current.lang = 'en-US';

        recognitionRef.current.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setChatInput(transcript);
          setIsRecording(false);
        };

        recognitionRef.current.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          setIsRecording(false);
        };

        recognitionRef.current.onend = () => {
          setIsRecording(false);
        };
      }
    }
  }, []);

  // Initialize chat with country context
  useEffect(() => {
    const initializeChat = async () => {
      if (hasInitialized) return;
      
      try {
        // Get selected country from localStorage (only on client side)
        if (typeof window !== 'undefined') {
          const storedCountry = localStorage.getItem('selectedCountry');
          if (storedCountry) {
            const countryData = JSON.parse(storedCountry);
            setSelectedCountry(countryData);
            setLocationInput(countryData.name);
            
            // Send initial message to backend with country context
            const initialMessage = `I want to visit ${countryData.name}`;
            console.log('DEBUG: Country data from localStorage:', countryData);
            console.log('DEBUG: Initial message:', initialMessage);
            
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
            return;
          }
        }
        
        // No country selected, show default welcome
        const welcomeMessage: ChatMessage = {
          role: 'ai',
          content: "Welcome to Kora! Please select a country from the globe to start planning your sustainable travel adventure."
        };
        setMessages([welcomeMessage]);
        setHasInitialized(true);
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

  const handleLocationSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!locationInput.trim()) return;

    try {
      setIsLoading(true);
      const response: ApiResponse = await apiClient.post('/api/chat/message', {
        message: `I want to visit ${locationInput}`,
        chat_history: messages
      });

      const aiMessage: ChatMessage = {
        role: 'ai',
        content: response.response
      };

      setMessages([aiMessage]);
      
      // Auto-read the AI response if enabled
      if (autoReadEnabled) {
        setTimeout(() => {
          speakText(aiMessage.content);
        }, 500);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'human',
      content: chatInput.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setChatInput('');
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
      
      // Auto-read the AI response if enabled
      if (autoReadEnabled) {
        setTimeout(() => {
          speakText(aiMessage.content);
        }, 500); // Small delay to ensure message is rendered
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  const startVoiceRecording = () => {
    if (recognitionRef.current && !isRecording) {
      setIsRecording(true);
      recognitionRef.current.start();
    }
  };

  const stopVoiceRecording = () => {
    if (recognitionRef.current && isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    }
  };

  const speakText = (text: string) => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      // Stop any current speech
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 0.8;
      
      utterance.onstart = () => {
        setIsSpeaking(true);
      };
      
      utterance.onend = () => {
        setIsSpeaking(false);
      };
      
      utterance.onerror = () => {
        setIsSpeaking(false);
      };
      
      speechSynthesisRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    }
  };

  const stopSpeaking = () => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[linear-gradient(0deg,rgba(246,245,250,1)_0%,rgba(246,245,250,1)_100%)] relative">
        {/* Header with logo and location input */}
        <div className="flex flex-col sm:flex-row items-center justify-between p-4 gap-4">
          {/* Sea turtle logo */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.push('/')}
              className="hover:opacity-80 transition-opacity"
            >
              <img
                className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16"
                alt="Sea turtle logo"
                src="https://c.animaapp.com/xia9nwm7/img/sea-turtle-02-2.svg"
              />
            </button>
          </div>

          {/* Location input form */}
          <form
            onSubmit={handleLocationSubmit}
            className="flex items-center justify-between bg-white rounded-[40px] px-3 py-2 sm:px-4 sm:py-2 md:px-6 md:py-3 border-2 border-solid border-[#d8dfe980] relative w-full sm:w-auto sm:min-w-[250px] md:min-w-[300px]"
          >
            <div className="flex items-center gap-2 relative flex-1">
              <img
                className="w-4 h-4 sm:w-5 sm:h-5"
                alt=""
                src="https://c.animaapp.com/xia9nwm7/img/location-on@2x.png"
                aria-hidden="true"
              />

              <label htmlFor="location-input" className="sr-only">
                Location
              </label>
              <input
                id="location-input"
                type="text"
                value={locationInput}
                onChange={(e) => setLocationInput(e.target.value)}
                className="flex-1 text-sm sm:text-base font-medium text-black placeholder:text-gray-500 focus:outline-none"
                placeholder="Enter location..."
                aria-label="Location input"
              />
            </div>

            <button 
              type="submit" 
              aria-label="Search location"
              className="ml-2 p-1 hover:bg-gray-100 rounded-full transition-colors"
            >
              <img
                className="w-5 h-5 sm:w-6 sm:h-6"
                alt=""
                src="https://c.animaapp.com/xia9nwm7/img/group-4-1@2x.png"
              />
            </button>
          </form>

          {/* Auto-read toggle and User profile button */}
          <div className="flex items-center gap-3">
            {/* Auto-read toggle */}
            <button
              onClick={() => setAutoReadEnabled(!autoReadEnabled)}
              className={`w-10 h-10 sm:w-12 sm:h-12 rounded-full flex items-center justify-center transition-all ${
                autoReadEnabled 
                  ? 'bg-green-100 text-green-600 hover:bg-green-200' 
                  : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
              }`}
              aria-label={autoReadEnabled ? "Disable auto-read" : "Enable auto-read"}
              title={autoReadEnabled ? "Auto-read enabled" : "Auto-read disabled"}
            >
              <svg
                className="w-5 h-5 sm:w-6 sm:h-6"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M3 9V15H7L12 20V4L7 9H3ZM16.5 12C16.5 10.23 15.48 8.71 14 7.97V16.02C15.48 15.29 16.5 13.77 16.5 12ZM14 3.23V5.29C16.89 6.15 19 8.83 19 12S16.89 17.85 14 18.71V20.77C18.01 19.86 21 16.28 21 12S18.01 4.14 14 3.23Z"
                  fill="currentColor"
                />
              </svg>
            </button>

            {/* User profile button */}
            <button
              className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 hover:opacity-80 transition-opacity"
              aria-label="User profile"
              onClick={() => router.push('/profile')}
            >
              <img
                className="w-full h-full"
                alt=""
                src="https://c.animaapp.com/xia9nwm7/img/group-6@2x.png"
              />
            </button>
          </div>
        </div>

        {/* Main content area */}
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
          <div className="bg-[linear-gradient(180deg,rgba(216,223,233,0.25)_0%,rgba(216,223,233,0)_100%),linear-gradient(0deg,rgba(246,245,250,1)_0%,rgba(246,245,250,1)_100%)] rounded-[30px] sm:rounded-[40px] lg:rounded-[50px] border-2 border-solid border-[#d8dfe980] p-4 sm:p-6 lg:p-8 min-h-[200px] sm:min-h-[300px] md:min-h-[400px]">
            
            {/* Chat area with turtle and conversation */}
            <div className="flex gap-4 sm:gap-6 mb-4 sm:mb-6">
              {/* Animated Turtle SVG - 30% width */}
              <div className="w-[30%] flex items-end justify-center">
                <div className="relative w-full h-auto max-w-[160px] sm:max-w-[200px] md:max-w-[240px]">
                  {isLoading ? (
                    <div className="relative w-full h-auto flex items-end justify-center" style={{ minHeight: '160px' }}>
                      {/* First turtle state */}
                      <img
                        className="w-full h-auto"
                        alt="Sea turtle talking state 1"
                        src="/chat/seazine-031.svg"
                        style={{
                          animation: 'turtleTalk 1.2s steps(2, end) infinite',
                          position: 'absolute',
                          bottom: 0,
                          left: '50%',
                          transform: 'translateX(-50%)'
                        }}
                      />
                      {/* Second turtle state */}
                      <img
                        className="w-full h-auto"
                        alt="Sea turtle talking state 2"
                        src="/chat/seazine-032.svg"
                        style={{
                          animation: 'turtleTalk 1.2s steps(2, end) infinite reverse',
                          position: 'absolute',
                          bottom: 0,
                          left: '50%',
                          transform: 'translateX(-50%)'
                        }}
                      />
                    </div>
                  ) : (
                    <img
                      className="w-full h-auto"
                      alt="Sea turtle"
                      src="/chat/seazine-032.svg"
                    />
                  )}
                </div>
              </div>
              
              {/* Chat conversation area - 70% width */}
              <div className="w-[70%] bg-[linear-gradient(180deg,rgba(216,223,233,0)_0%,rgba(218,224,234,0.3)_100%),linear-gradient(0deg,rgba(239,240,164,0)_0%,rgba(239,240,164,0)_100%)] rounded-[20px] sm:rounded-[30px] lg:rounded-[40px] border-2 border-solid border-[#d8dfe9] h-[200px] sm:h-[250px] md:h-[300px] lg:h-[350px] overflow-hidden">
                <div className="h-full overflow-y-auto p-3 sm:p-4 md:p-6 space-y-3 sm:space-y-4 flex flex-col">
                  {messages.length === 0 && (
                    <div className="text-center text-gray-500 mt-6 sm:mt-8">
                      <h3 className="text-lg sm:text-xl font-semibold mb-2">Welcome to Kora!</h3>
                      <p className="text-sm sm:text-base">Start planning your sustainable travel adventure. Tell me where you'd like to go!</p>
                    </div>
                  )}

                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex ${message.role === 'human' ? 'justify-end' : 'justify-start'} chat-message`}
                    >
                      <div
                        className={`max-w-[80%] sm:max-w-sm md:max-w-md lg:max-w-lg px-3 py-2 sm:px-4 sm:py-2 rounded-lg ${
                          message.role === 'human'
                            ? 'bg-blue-600 text-white'
                            : 'bg-white text-gray-800 shadow-sm border border-gray-200'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1">
                            {message.role === 'ai' ? (
                              <MarkdownRenderer 
                                content={message.content} 
                                className="text-sm sm:text-base"
                              />
                            ) : (
                              <p className="text-sm sm:text-base">{message.content}</p>
                            )}
                          </div>
                          {message.role === 'ai' && (
                            <button
                              onClick={() => isSpeaking ? stopSpeaking() : speakText(message.content)}
                              className="flex-shrink-0 w-5 h-5 hover:opacity-80 transition-opacity"
                              aria-label={isSpeaking ? "Stop reading" : "Read message aloud"}
                            >
                              <svg
                                className="w-full h-full"
                                viewBox="0 0 24 24"
                                fill="none"
                                xmlns="http://www.w3.org/2000/svg"
                              >
                                {isSpeaking ? (
                                  // Stop icon
                                  <rect
                                    x="6"
                                    y="6"
                                    width="12"
                                    height="12"
                                    rx="2"
                                    fill="#ef4444"
                                  />
                                ) : (
                                  // Speaker icon
                                  <path
                                    d="M3 9V15H7L12 20V4L7 9H3ZM16.5 12C16.5 10.23 15.48 8.71 14 7.97V16.02C15.48 15.29 16.5 13.77 16.5 12ZM14 3.23V5.29C16.89 6.15 19 8.83 19 12S16.89 17.85 14 18.71V20.77C18.01 19.86 21 16.28 21 12S18.01 4.14 14 3.23Z"
                                    fill="#6b7280"
                                  />
                                )}
                              </svg>
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}

                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-white text-gray-800 shadow-sm border border-gray-200 max-w-[80%] sm:max-w-sm md:max-w-md lg:max-w-lg px-3 py-2 sm:px-4 sm:py-2 rounded-lg">
                        <div className="flex items-center space-x-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                          <p className="text-sm">Thinking...</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {error && (
                    <div className="flex justify-center">
                      <div className="bg-red-50 border border-red-200 rounded-lg p-3 max-w-[90%] sm:max-w-md">
                        <p className="text-red-600 text-sm">Error: {error}</p>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>
              </div>
            </div>

            {/* Chat input form */}
            <form
              onSubmit={handleChatSubmit}
              className="flex items-center gap-3 sm:gap-4 bg-[linear-gradient(180deg,rgba(216,223,233,0.25)_0%,rgba(216,223,233,0)_100%),linear-gradient(0deg,rgba(255,255,255,0.2)_0%,rgba(255,255,255,0.2)_100%)] rounded-[30px] sm:rounded-[40px] lg:rounded-[50px] border-2 border-solid border-[#d8dfe980] p-3 sm:p-4 md:p-6"
            >
              <label htmlFor="chat-input" className="sr-only">
                Ask Kora anything about your travel plans
              </label>
              <input
                id="chat-input"
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask Kora anything about your travel plans"
                className="flex-1 text-sm sm:text-base lg:text-lg font-light text-gray-600 placeholder:text-gray-500 focus:outline-none bg-transparent"
                aria-label="Chat input"
                disabled={isLoading}
              />

              {/* Voice input button */}
              {isVoiceSupported && (
                <button
                  type="button"
                  onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
                  className={`w-6 h-6 sm:w-8 sm:h-8 md:w-10 md:h-10 lg:w-12 lg:h-12 hover:opacity-80 transition-opacity flex items-center justify-center ${
                    isRecording ? 'animate-pulse' : ''
                  }`}
                  aria-label={isRecording ? "Stop voice recording" : "Start voice recording"}
                  disabled={isLoading}
                >
                  <svg
                    className="w-full h-full"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    {isRecording ? (
                      // Stop recording icon (square)
                      <rect
                        x="6"
                        y="6"
                        width="12"
                        height="12"
                        rx="2"
                        fill={isRecording ? "#ef4444" : "#6b7280"}
                      />
                    ) : (
                      // Microphone icon
                      <path
                        d="M12 1C10.34 1 9 2.34 9 4V12C9 13.66 10.34 15 12 15C13.66 15 15 13.66 15 12V4C15 2.34 13.66 1 12 1ZM19 10V12C19 15.87 15.87 19 12 19C8.13 19 5 15.87 5 12V10H7V12C7 14.76 9.24 17 12 17C14.76 17 17 14.76 17 12V10H19ZM11 22H13V24H11V22Z"
                        fill="#6b7280"
                      />
                    )}
                  </svg>
                </button>
              )}

              <button
                type="submit"
                className="w-6 h-6 sm:w-8 sm:h-8 md:w-10 md:h-10 lg:w-12 lg:h-12 hover:opacity-80 transition-opacity disabled:opacity-50"
                aria-label="Send message"
                disabled={!chatInput.trim() || isLoading}
              >
                <img
                  className="w-full h-full"
                  alt=""
                  src="https://c.animaapp.com/xia9nwm7/img/group-4.svg"
                />
              </button>
            </form>
          </div>
        </div>

      </div>
    </ProtectedRoute>
  );
}