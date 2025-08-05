import React, { useState, useEffect, useRef } from 'react';

const AIAssistant = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize with welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          role: 'assistant',
          content: 'Hello, I am your 420 assistant. What information would you like me to provide about the program\'s performance?',
          timestamp: new Date().toISOString()
        }
      ]);
    }
  }, [isOpen, messages.length]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ai-assistant/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          session_id: sessionId
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from assistant');
      }

      const data = await response.json();
      
      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error communicating with AI assistant:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'I apologize, but I\'m having trouble accessing the registration data right now. Please try again in a moment.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: 'Chat cleared! How can I help you analyze your registration data?',
        timestamp: new Date().toISOString()
      }
    ]);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl h-[80vh] flex flex-col">
        {/* Header */}
        <div className="bg-black text-white px-6 py-4 rounded-t-lg flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold">📊 Registration Data Assistant</h2>
            <p className="text-gray-300 text-sm">Hello, I am your 420 assistant. What information would you like me to provide about the program's performance?</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={clearChat}
              className="text-gray-300 hover:text-white p-1 rounded"
              title="Clear chat"
            >
              🗑️
            </button>
            <button
              onClick={onClose}
              className="text-gray-300 hover:text-white text-xl font-bold p-1 rounded"
            >
              ×
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 p-6 overflow-y-auto bg-gray-50">
          <div className="space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-black text-white'
                      : 'bg-white text-gray-800 shadow-sm border'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  <div className={`text-xs mt-1 ${
                    message.role === 'user' ? 'text-gray-300' : 'text-gray-500'
                  }`}>
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white text-gray-800 shadow-sm border p-3 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-black"></div>
                    <span>Analyzing data...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t bg-white p-4 rounded-b-lg">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about registrations, dispositions, trends, statistics..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || isLoading}
              className="bg-black text-white px-6 py-3 rounded-lg hover:bg-gray-800 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {isLoading ? '...' : 'Send'}
            </button>
          </form>
          
          {/* Quick suggestions */}
          <div className="mt-3 flex flex-wrap gap-2">
            {[
              "Total registrations",
              "Monthly trends", 
              "Disposition breakdown",
              "Completion rate",
              "Today's numbers"
            ].map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => setInputMessage(suggestion)}
                className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-600 px-3 py-1 rounded-full transition-colors"
                disabled={isLoading}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;