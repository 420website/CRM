import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

const AdminAnalytics = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [isTyping, setIsTyping] = useState(true);
  const [typedText, setTypedText] = useState('');
  const messagesEndRef = useRef(null);
  
  // Excel upload states
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [legacyDataSummary, setLegacyDataSummary] = useState(null);
  const [showUploadSection, setShowUploadSection] = useState(false);
  
  // Handle scroll to top when upload status changes (same pattern as client registration)
  useEffect(() => {
    if (uploadStatus?.type === 'success') {
      window.scrollTo(0, 0);
      document.body.scrollTop = 0;
      document.documentElement.scrollTop = 0;
    }
  }, [uploadStatus]);

  const welcomeMessage = 'Welcome to the Analytics dashboard powered by 420 AI. I can help you analyze enrollment statistics, dispositions, trends, and other data insights about the program\'s performance.';

  // Typewriter effect for welcome message
  useEffect(() => {
    setTypedText('');
    setIsTyping(true);
    
    const typeInterval = setInterval(() => {
      setTypedText(prev => {
        const nextIndex = prev.length;
        if (nextIndex < welcomeMessage.length) {
          return prev + welcomeMessage.charAt(nextIndex);
        } else {
          setIsTyping(false);
          clearInterval(typeInterval);
          // Add the complete message to messages array
          setMessages([{
            role: 'assistant',
            content: welcomeMessage,
            timestamp: new Date().toISOString()
          }]);
          return prev;
        }
      });
    }, 50); // Typing speed: 50ms per character

    return () => clearInterval(typeInterval);
  }, []);

  // Auto-scroll to bottom of messages container only
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ 
        behavior: "smooth",
        block: "nearest" // This prevents scrolling the entire page
      });
    }
  };

  useEffect(() => {
    // Only scroll to bottom when not typing to prevent page jumping
    if (!isTyping) {
      scrollToBottom();
    }
  }, [messages, isTyping]);

  // Check for existing legacy data on load
  useEffect(() => {
    loadLegacyDataSummary();
  }, []);

  const loadLegacyDataSummary = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/legacy-data-summary`);
      if (response.ok) {
        const summary = await response.json();
        setLegacyDataSummary(summary);
      }
    } catch (error) {
      // No legacy data uploaded yet, this is fine
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.name.match(/\.(xlsx|xls|csv)$/i)) {
      setUploadStatus({
        type: 'error',
        message: 'Please upload an Excel (.xlsx, .xls) or CSV (.csv) file'
      });
      return;
    }

    setIsUploading(true);
    setUploadStatus(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/upload-legacy-data`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadStatus({
          type: 'success',
          message: result.message,
          data: result
        });
        
        // Reload summary
        await loadLegacyDataSummary();
        
        // Add message to chat
        const uploadMessage = {
          role: 'assistant',
          content: `📊 Legacy data uploaded successfully! I now have access to ${result.records_count} historical records from ${file.name}. You can ask me questions about trends, dispositions, and patterns in your historical data.`,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, uploadMessage]);
        
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
      }
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: `Upload failed: ${error.message}`
      });
    } finally {
      setIsUploading(false);
      // Clear the file input
      event.target.value = '';
    }
  };

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading || isTyping) return;

    const userMessage = {
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // Ensure we stay at the top of the page
    window.scrollTo({ top: 0, behavior: 'smooth' });

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/claude-chat`, {
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
        timestamp: data.timestamp,
        chart_html: data.chart_html,
        chart_image_url: data.chart_image_url
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
    // Allow Shift+Enter for new lines
  };

  const clearChat = () => {
    setMessages([]);
    setIsTyping(true);
    setTypedText('');
    
    // Restart typewriter effect with improved logic
    const typeInterval = setInterval(() => {
      setTypedText(prev => {
        const nextIndex = prev.length;
        if (nextIndex < welcomeMessage.length) {
          return prev + welcomeMessage.charAt(nextIndex);
        } else {
          setIsTyping(false);
          clearInterval(typeInterval);
          setMessages([{
            role: 'assistant',
            content: welcomeMessage,
            timestamp: new Date().toISOString()
          }]);
          return prev;
        }
      });
    }, 50);
  };

  const goBack = () => {
    navigate('/admin-menu');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">AI Analytics</h1>
          <div className="flex gap-2">
            <button
              onClick={goBack}
              className="inline-flex items-center gap-1 px-3 py-1 bg-black text-white rounded-md hover:bg-gray-800 transition-colors text-xs font-medium"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Admin Menu
            </button>
            <button
              onClick={() => navigate('/')}
              className="inline-flex items-center gap-1 px-3 py-1 bg-white text-black border border-black rounded-md hover:bg-gray-100 transition-colors text-xs font-medium"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Home
            </button>
          </div>
        </div>

        {/* Legacy Data Upload Section */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">📊 Legacy Data</h2>
            <div className="flex gap-3">
              <button
                onClick={clearChat}
                className="text-gray-600 hover:text-gray-800 text-sm flex items-center gap-1"
                title="Clear chat"
              >
                🗑️ Clear
              </button>
              <button
                onClick={() => setShowUploadSection(!showUploadSection)}
                className="text-blue-600 hover:text-blue-800 text-sm"
              >
                {showUploadSection ? 'Hide Upload' : 'Upload Data'}
              </button>
            </div>
          </div>

          {/* Data Summary */}
          {legacyDataSummary && (
            <div className="bg-blue-50 rounded-lg p-4 mb-4">
              <h3 className="font-medium text-blue-900 mb-2">Current Legacy Data:</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-blue-700 font-medium">Records:</span>
                  <div className="text-blue-900">{legacyDataSummary.total_records}</div>
                </div>
                <div>
                  <span className="text-blue-700 font-medium">Date Range:</span>
                  <div className="text-blue-900">
                    {legacyDataSummary.date_range.start ? 
                      `${legacyDataSummary.date_range.start} to ${legacyDataSummary.date_range.end}` : 
                      'No dates found'
                    }
                  </div>
                </div>
                <div>
                  <span className="text-blue-700 font-medium">Top Disposition:</span>
                  <div className="text-blue-900">
                    {legacyDataSummary.top_dispositions[0]?.disposition || 'N/A'}
                  </div>
                </div>
                <div>
                  <span className="text-blue-700 font-medium">File:</span>
                  <div className="text-blue-900 truncate">{legacyDataSummary.upload_info.filename}</div>
                </div>
              </div>
            </div>
          )}

          {/* Upload Section */}
          {showUploadSection && (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
              <div className="text-center">
                <div className="mb-4">
                  <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </div>
                <p className="text-lg font-medium text-gray-900 mb-2">Upload Legacy Patient Data</p>
                <p className="text-sm text-gray-600 mb-4">
                  Upload your Excel file with 2000+ historical records. Supported formats: .xlsx, .xls, .csv
                </p>
                
                <label htmlFor="excel-upload" className="cursor-pointer inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                  {isUploading ? 'Uploading...' : 'Choose Excel File'}
                </label>
                <input
                  id="excel-upload"
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  onChange={handleFileUpload}
                  disabled={isUploading}
                  className="hidden"
                />
              </div>
              
              {/* Upload Status */}
              {uploadStatus && (
                <div className={`mt-4 p-4 rounded-md ${
                  uploadStatus.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
                }`}>
                  <p className="font-medium">{uploadStatus.message}</p>
                  {uploadStatus.data && (
                    <p className="text-sm mt-2">
                      Preview: {uploadStatus.data.preview.length} sample records processed
                    </p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-lg shadow-md p-6">
          {/* Chat Interface */}
          <div className="h-[calc(100vh-250px)] flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto bg-white">
              <div className="space-y-4">
                {/* Show typing effect or messages */}
                {isTyping ? (
                  <div className="flex justify-start">
                    <div className="max-w-[85%] p-3 rounded-lg bg-gray-50 text-gray-800 border">
                      <div className="whitespace-pre-wrap text-sm" style={{ minHeight: '60px' }}>
                        {typedText}
                        <span className="animate-pulse">|</span>
                        {/* Invisible text to reserve space and prevent layout shift */}
                        <span style={{ visibility: 'hidden' }}>{welcomeMessage.substring(typedText.length)}</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[85%] p-3 rounded-lg ${
                          message.role === 'user'
                            ? 'bg-black text-white'
                            : 'bg-gray-50 text-gray-800 border'
                        }`}
                      >
                        <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                        
                        <div className={`text-xs mt-1 ${
                          message.role === 'user' ? 'text-gray-300' : 'text-gray-500'
                        }`}>
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  ))
                )}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-50 text-gray-800 border p-3 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-black"></div>
                        <span className="text-sm">Analyzing data...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div ref={messagesEndRef} />
            </div>

            {/* Input - with matching spacing from messages above */}
            <div className="border-t bg-white pt-4 mt-4">
              <form onSubmit={handleSubmit} className="flex gap-3 items-end">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about registrations..."
                  className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent resize-none overflow-hidden min-h-[40px] max-h-[120px]"
                  disabled={isLoading}
                  rows={1}
                  style={{
                    height: 'auto',
                    minHeight: '40px',
                    maxHeight: '120px'
                  }}
                  onInput={(e) => {
                    e.target.style.height = 'auto';
                    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
                  }}
                />
                <button
                  type="submit"
                  disabled={!inputMessage.trim() || isLoading}
                  className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium text-sm flex-shrink-0"
                  style={{ height: '40px' }}
                >
                  {isLoading ? '...' : 'Send'}
                </button>
              </form>
              
              {/* Action buttons */}
              <div className="mt-3 flex justify-start gap-2 flex-wrap">
                <button
                  onClick={async () => {
                    if (!isLoading && !isTyping) {
                      const query = "Monthly registration summary 2024/2025 and side by side comparison";
                      
                      // Add user message first
                      const userMessage = {
                        role: 'user',
                        content: query,
                        timestamp: new Date().toISOString()
                      };
                      setMessages(prev => [...prev, userMessage]);
                      setIsLoading(true);
                      
                      try {
                        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/claude-chat`, {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                          },
                          body: JSON.stringify({
                            message: query,
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
                          timestamp: data.timestamp,
                          chart_html: data.chart_html,
                          chart_image_url: data.chart_image_url
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
                    }
                  }}
                  disabled={isLoading}
                  className="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors text-xs font-medium"
                >
                  Registrations
                </button>
                
                <button
                  onClick={async () => {
                    if (!isLoading && !isTyping) {
                      const query = "Disposition types for 2024/2025 and comparison";
                      
                      // Add user message first
                      const userMessage = {
                        role: 'user',
                        content: query,
                        timestamp: new Date().toISOString()
                      };
                      setMessages(prev => [...prev, userMessage]);
                      setIsLoading(true);
                      
                      try {
                        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/claude-chat`, {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                          },
                          body: JSON.stringify({
                            message: query,
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
                          timestamp: data.timestamp,
                          chart_html: data.chart_html,
                          chart_image_url: data.chart_image_url
                        };

                        setMessages(prev => [...prev, assistantMessage]);
                      } catch (error) {
                        console.error('Error communicating with AI assistant:', error);
                        const errorMessage = {
                          role: 'assistant',
                          content: 'I apologize, but I\'m having trouble accessing the disposition data right now. Please try again in a moment.',
                          timestamp: new Date().toISOString()
                        };
                        setMessages(prev => [...prev, errorMessage]);
                      } finally {
                        setIsLoading(false);
                      }
                    }
                  }}
                  disabled={isLoading}
                  className="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors text-xs font-medium"
                >
                  Dispositions
                </button>
                
                <button
                  onClick={async () => {
                    if (!isLoading && !isTyping) {
                      const query = "Gender breakdown for 2024/2025";
                      
                      // Add user message first
                      const userMessage = {
                        role: 'user',
                        content: query,
                        timestamp: new Date().toISOString()
                      };
                      setMessages(prev => [...prev, userMessage]);
                      setIsLoading(true);
                      
                      try {
                        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/claude-chat`, {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                          },
                          body: JSON.stringify({
                            message: query,
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
                          timestamp: data.timestamp,
                          chart_html: data.chart_html,
                          chart_image_url: data.chart_image_url
                        };

                        setMessages(prev => [...prev, assistantMessage]);
                      } catch (error) {
                        console.error('Error communicating with AI assistant:', error);
                        const errorMessage = {
                          role: 'assistant',
                          content: 'I apologize, but I\'m having trouble accessing the gender data right now. Please try again in a moment.',
                          timestamp: new Date().toISOString()
                        };
                        setMessages(prev => [...prev, errorMessage]);
                      } finally {
                        setIsLoading(false);
                      }
                    }
                  }}
                  disabled={isLoading}
                  className="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors text-xs font-medium"
                >
                  Gender
                </button>
                
                <button
                  onClick={async () => {
                    if (!isLoading && !isTyping) {
                      const query = "Percentage of clients without a phone";
                      
                      // Add user message first
                      const userMessage = {
                        role: 'user',
                        content: query,
                        timestamp: new Date().toISOString()
                      };
                      setMessages(prev => [...prev, userMessage]);
                      setIsLoading(true);
                      
                      try {
                        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/claude-chat`, {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                          },
                          body: JSON.stringify({
                            message: query,
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
                          timestamp: data.timestamp,
                          chart_html: data.chart_html,
                          chart_image_url: data.chart_image_url
                        };

                        setMessages(prev => [...prev, assistantMessage]);
                      } catch (error) {
                        console.error('Error communicating with AI assistant:', error);
                        const errorMessage = {
                          role: 'assistant',
                          content: 'I apologize, but I\'m having trouble accessing the phone data right now. Please try again in a moment.',
                          timestamp: new Date().toISOString()
                        };
                        setMessages(prev => [...prev, errorMessage]);
                      } finally {
                        setIsLoading(false);
                      }
                    }
                  }}
                  disabled={isLoading}
                  className="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors text-xs font-medium"
                >
                  Phone
                </button>
                
                <button
                  onClick={async () => {
                    if (!isLoading && !isTyping) {
                      const query = "Percentage of clients without a health card";
                      
                      // Add user message first
                      const userMessage = {
                        role: 'user',
                        content: query,
                        timestamp: new Date().toISOString()
                      };
                      setMessages(prev => [...prev, userMessage]);
                      setIsLoading(true);
                      
                      try {
                        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/claude-chat`, {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                          },
                          body: JSON.stringify({
                            message: query,
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
                          timestamp: data.timestamp,
                          chart_html: data.chart_html,
                          chart_image_url: data.chart_image_url
                        };

                        setMessages(prev => [...prev, assistantMessage]);
                      } catch (error) {
                        console.error('Error communicating with AI assistant:', error);
                        const errorMessage = {
                          role: 'assistant',
                          content: 'I apologize, but I\'m having trouble accessing the health card data right now. Please try again in a moment.',
                          timestamp: new Date().toISOString()
                        };
                        setMessages(prev => [...prev, errorMessage]);
                      } finally {
                        setIsLoading(false);
                      }
                    }
                  }}
                  disabled={isLoading}
                  className="bg-gray-100 text-gray-700 px-2 py-2 rounded-lg hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors text-xs font-medium"
                >
                  No health card
                </button>
                
                <button
                  onClick={async () => {
                    if (!isLoading && !isTyping) {
                      const query = "Percentage of clients with invalid health card";
                      
                      // Add user message first
                      const userMessage = {
                        role: 'user',
                        content: query,
                        timestamp: new Date().toISOString()
                      };
                      setMessages(prev => [...prev, userMessage]);
                      setIsLoading(true);
                      
                      try {
                        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/claude-chat`, {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                          },
                          body: JSON.stringify({
                            message: query,
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
                          timestamp: data.timestamp,
                          chart_html: data.chart_html,
                          chart_image_url: data.chart_image_url
                        };

                        setMessages(prev => [...prev, assistantMessage]);
                      } catch (error) {
                        console.error('Error communicating with AI assistant:', error);
                        const errorMessage = {
                          role: 'assistant',
                          content: 'I apologize, but I\'m having trouble accessing the invalid health card data right now. Please try again in a moment.',
                          timestamp: new Date().toISOString()
                        };
                        setMessages(prev => [...prev, errorMessage]);
                      } finally {
                        setIsLoading(false);
                      }
                    }
                  }}
                  disabled={isLoading}
                  className="bg-gray-100 text-gray-700 px-2 py-2 rounded-lg hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors text-xs font-medium"
                >
                  Invalid health card
                </button>
                
                <button
                  onClick={async () => {
                    if (!isLoading && !isTyping) {
                      const query = "Percentage of clients with no address";
                      
                      // Add user message first
                      const userMessage = {
                        role: 'user',
                        content: query,
                        timestamp: new Date().toISOString()
                      };
                      setMessages(prev => [...prev, userMessage]);
                      setIsLoading(true);
                      
                      try {
                        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/claude-chat`, {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                          },
                          body: JSON.stringify({
                            message: query,
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
                          timestamp: data.timestamp,
                          chart_html: data.chart_html,
                          chart_image_url: data.chart_image_url
                        };

                        setMessages(prev => [...prev, assistantMessage]);
                      } catch (error) {
                        console.error('Error communicating with AI assistant:', error);
                        const errorMessage = {
                          role: 'assistant',
                          content: 'I apologize, but I\'m having trouble accessing the housing data right now. Please try again in a moment.',
                          timestamp: new Date().toISOString()
                        };
                        setMessages(prev => [...prev, errorMessage]);
                      } finally {
                        setIsLoading(false);
                      }
                    }
                  }}
                  disabled={isLoading}
                  className="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors text-xs font-medium"
                >
                  Housing
                </button>
                
                <button
                  onClick={async () => {
                    if (!isLoading && !isTyping) {
                      const query = "Total donations for 2024/2025 by month";
                      
                      // Add user message first
                      const userMessage = {
                        role: 'user',
                        content: query,
                        timestamp: new Date().toISOString()
                      };
                      setMessages(prev => [...prev, userMessage]);
                      setIsLoading(true);
                      
                      try {
                        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/claude-chat`, {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                          },
                          body: JSON.stringify({
                            message: query,
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
                          timestamp: data.timestamp,
                          chart_html: data.chart_html,
                          chart_image_url: data.chart_image_url
                        };

                        setMessages(prev => [...prev, assistantMessage]);
                      } catch (error) {
                        console.error('Error communicating with AI assistant:', error);
                        const errorMessage = {
                          role: 'assistant',
                          content: 'I apologize, but I\'m having trouble accessing the rewards data right now. Please try again in a moment.',
                          timestamp: new Date().toISOString()
                        };
                        setMessages(prev => [...prev, errorMessage]);
                      } finally {
                        setIsLoading(false);
                      }
                    }
                  }}
                  disabled={isLoading}
                  className="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors text-xs font-medium"
                >
                  Rewards
                </button>
                
                <button
                  onClick={async () => {
                    if (!isLoading && !isTyping) {
                      const query = "Clients by age range?";
                      
                      // Add user message first
                      const userMessage = {
                        role: 'user',
                        content: query,
                        timestamp: new Date().toISOString()
                      };
                      setMessages(prev => [...prev, userMessage]);
                      setIsLoading(true);
                      
                      try {
                        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/claude-chat`, {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                          },
                          body: JSON.stringify({
                            message: query,
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
                          timestamp: data.timestamp,
                          chart_html: data.chart_html,
                          chart_image_url: data.chart_image_url
                        };

                        setMessages(prev => [...prev, assistantMessage]);
                      } catch (error) {
                        console.error('Error communicating with AI assistant:', error);
                        const errorMessage = {
                          role: 'assistant',
                          content: 'I apologize, but I\'m having trouble accessing the age data right now. Please try again in a moment.',
                          timestamp: new Date().toISOString()
                        };
                        setMessages(prev => [...prev, errorMessage]);
                      } finally {
                        setIsLoading(false);
                      }
                    }
                  }}
                  disabled={isLoading}
                  className="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors text-xs font-medium"
                >
                  Age
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminAnalytics;