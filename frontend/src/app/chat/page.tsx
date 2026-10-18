"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";

interface Message {
  id: string;
  sender: "child" | "bot";
  text: string;
  mode?: string;
  level?: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      sender: "bot",
      text: "Hello friend! Let's learn and talk together! 🌟",
      mode: "learning",
      level: "L1",
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [currentLevel, setCurrentLevel] = useState("L1");
  const [currentMode, setCurrentMode] = useState("learning");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState("mock_sess_001");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    async function initSession() {
      try {
        const childRes = await fetch("http://localhost:8000/api/v1/children", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "guardian-id": "guardian_demo_1",
          },
          body: JSON.stringify({
            pseudonym: "Leo",
            birth_month_year: "2020-01",
          }),
        });
        if (childRes.ok) {
          const childData = await childRes.json();
          const sessRes = await fetch("http://localhost:8000/api/v1/sessions", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "guardian-id": "guardian_demo_1",
            },
            body: JSON.stringify({
              child_id: childData.id,
            }),
          });
          if (sessRes.ok) {
            const sessData = await sessRes.json();
            setSessionId(sessData.id);
            if (sessData.active_mode) setCurrentMode(sessData.active_mode);
          }
        }
      } catch {
        // Keeps mock_sess_001 if backend is temporarily unreachable
      }
    }
    initSession();
  }, []);

  const sendMessage = async (customText?: string) => {
    const textToSend = (customText || inputMessage).trim();
    if (!textToSend || isLoading) return;

    const childMsgId = `child_${Date.now()}`;
    const newMsg: Message = {
      id: childMsgId,
      sender: "child",
      text: textToSend,
    };

    setMessages((prev) => [...prev, newMsg]);
    if (!customText) setInputMessage("");
    setIsLoading(true);
    setErrorMessage(null);

    const idempotencyKey = `turn_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;

    try {
      const response = await fetch("http://localhost:8000/api/v1/chat/turn", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "guardian-id": "guardian_demo_1",
        },
        body: JSON.stringify({
          session_id: sessionId,
          child_message: textToSend,
          idempotency_key: idempotencyKey,
        }),
      });

      if (!response.ok) {
        throw new Error("Could not reach companion");
      }

      const data = await response.json();
      setCurrentLevel(data.level || "L1");
      setCurrentMode(data.mode || "learning");

      setMessages((prev) => [
        ...prev,
        {
          id: data.turn_id || `bot_${Date.now()}`,
          sender: "bot",
          text: data.response_text || "You are doing great!",
          mode: data.mode,
          level: data.level,
        },
      ]);
    } catch {
      // Deterministic offline client fallback when backend is offline
      let fallbackText = "Hello! Let us learn together! 🌟";
      let fallbackMode = "learning";

      const lower = textToSend.toLowerCase();
      if (lower.includes("stop") || lower.includes("break") || lower.includes("bye")) {
        fallbackText = "It is okay to take a break! You did great today! 🌟";
        fallbackMode = "support";
      } else if (lower.includes("game") || lower.includes("play")) {
        fallbackText = "Let's play an animal game! What does a cat say?";
        fallbackMode = "engagement";
      } else if (lower.includes("cat") || lower.includes("dog") || lower.includes("like")) {
        fallbackText = "I like friendly animals too! Tell me more!";
        fallbackMode = "conversation";
      }

      setCurrentMode(fallbackMode);
      setMessages((prev) => [
        ...prev,
        {
          id: `bot_fallback_${Date.now()}`,
          sender: "bot",
          text: fallbackText,
          mode: fallbackMode,
          level: currentLevel,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickWords = ["Blue", "Red", "Cat", "Dog", "Apple", "Yes"];

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto bg-white shadow-lg border-x border-slate-100">
      {/* Header */}
      <header className="flex items-center justify-between p-4 bg-blue-600 text-white rounded-b-2xl shadow-sm">
        <div className="flex items-center gap-3">
          <Link href="/" className="p-1 hover:bg-blue-700 rounded-lg text-sm" aria-label="Home">
            🏠
          </Link>
          <div>
            <h1 className="text-lg font-bold">English Buddy 🌟</h1>
            <div className="flex items-center gap-2 text-xs">
              <span className="bg-blue-700 px-2 py-0.5 rounded-full font-semibold">
                Level {currentLevel}
              </span>
              <span className="bg-blue-500 px-2 py-0.5 rounded-full capitalize">
                Mode: {currentMode}
              </span>
            </div>
          </div>
        </div>

        <button
          onClick={() => sendMessage("Stop! I want a break.")}
          className="px-3 py-1 bg-blue-700 hover:bg-blue-800 rounded-xl text-xs font-semibold text-white transition"
          aria-label="Take a break"
        >
          Take a Break 🛑
        </button>
      </header>

      {/* Message List */}
      <main className="flex-1 overflow-y-auto p-4 space-y-4" role="log" aria-live="polite">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === "child" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl p-4 text-base leading-relaxed ${
                msg.sender === "child"
                  ? "bg-blue-600 text-white rounded-br-none"
                  : "bg-slate-100 text-slate-800 rounded-bl-none border border-slate-200"
              }`}
            >
              <p className="font-medium">{msg.text}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-100 rounded-2xl p-4 rounded-bl-none flex items-center gap-2">
              <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></span>
              <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-100"></span>
              <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-200"></span>
            </div>
          </div>
        )}

        {errorMessage && (
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-amber-800 text-sm flex justify-between items-center">
            <span>{errorMessage}</span>
            <button
              onClick={() => sendMessage()}
              className="text-xs bg-amber-200 hover:bg-amber-300 px-2 py-1 rounded"
            >
              Retry
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </main>

      {/* Quick Word Helpers for under 7s */}
      <div className="px-4 py-2 bg-slate-50 border-t border-slate-100 flex gap-2 overflow-x-auto">
        {quickWords.map((word) => (
          <button
            key={word}
            onClick={() => sendMessage(word)}
            disabled={isLoading}
            className="px-3 py-1 bg-white hover:bg-blue-50 text-slate-700 hover:text-blue-600 border border-slate-200 rounded-full text-xs font-semibold whitespace-nowrap transition"
          >
            {word}
          </button>
        ))}
      </div>

      {/* Input Bar */}
      <footer className="p-4 bg-white border-t border-slate-100 flex gap-2">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a word or message..."
          disabled={isLoading}
          className="flex-1 px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm text-slate-800"
          aria-label="Message input"
        />
        <button
          onClick={() => sendMessage()}
          disabled={isLoading || !inputMessage.trim()}
          className="px-5 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white font-semibold rounded-2xl text-sm transition"
          aria-label="Send message"
        >
          Send 🚀
        </button>
      </footer>
    </div>
  );
}
