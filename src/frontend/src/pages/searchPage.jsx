import React, { useState, useEffect } from "react";

const RAGChat = () => {
  const [userId, setUserId] = useState("");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const userIdFromUrl = urlParams.get('user_id');

    if (userIdFromUrl) {
      setUserId(userIdFromUrl);
      console.log('User ID from URL:', userIdFromUrl);

      const newUrl = window.location.pathname;
      window.history.replaceState({}, document.title, newUrl);

      localStorage.setItem('user_id', userIdFromUrl);
    } else {
      const storedUserId = localStorage.getItem('user_id');
      if (storedUserId) {
        setUserId(storedUserId);
        console.log('User ID from localStorage:', storedUserId);
      }
    }
  }, []);

  const sendQuery = async () => {
    if (!input.trim()) return;

    if (!userId) {
      setMessages((prev) => [...prev, {
        role: "assistant",
        text: "Please log in first to use the chat."
      }]);
      return;
    }

    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      console.log('Sending request with userId:', userId);
      const API_URL = import.meta.env.VITE_API_URL;

      const res = await fetch(`${API_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          query: input
        }),
      });

      if (!res.ok) {
        const errorText = await res.text();
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();

      if (!data.answer) {
        throw new Error('No answer received from server');
      }

      setMessages((prev) => [...prev, {
        role: "assistant",
        text: data.answer
      }]);

    } catch (error) {
      console.error('Search error:', error);
      setMessages((prev) => [...prev, {
        role: "assistant",
        text: `Error: ${error.message}.Please try again.`
      }]);
    } finally {
      setIsLoading(false);
      setInput("");
    }
  };

  if (!userId) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p>Loading user session...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4">
      {/* Header with user info */}
      <div className="mb-4 p-2 bg-gray-100 rounded-lg">
        <p className="text-sm text-gray-600">Logged in as: <span className="font-mono">{userId}</span></p>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`p - 3 rounded - lg max - w - xs ${msg.role === "user"
              ? "bg-blue-500 text-white ml-auto"
              : "bg-gray-200 text-gray-900"
              } `}
          >
            {msg.text}
          </div>
        ))}
        {isLoading && (
          <div className="bg-gray-200 text-gray-900 p-3 rounded-lg max-w-xs">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900"></div>
              <span>Thinking...</span>
            </div>
          </div>
        )}
      </div>

      <div className="flex">
        <input
          className="flex-1 border rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Ask me anything..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !isLoading && sendQuery()}
          disabled={isLoading}
        />
        <button
          className={`ml - 2 px - 4 py - 2 rounded - lg text - white ${isLoading
            ? "bg-gray-400 cursor-not-allowed"
            : "bg-blue-500 hover:bg-blue-600"
            } `}
          onClick={sendQuery}
          disabled={isLoading}
        >
          {isLoading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
};

export default RAGChat;
