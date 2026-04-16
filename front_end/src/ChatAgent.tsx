import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import type { Message } from './types';

const ChatAgent: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // メッセージ追加時に自動スクロール
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 1. メッセージ送信、サーバーからの返信受信
  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setIsLoading(true);

    try {
      const INVOKE_URL = import.meta.env.VITE_API_URL;
      const response = await axios.post(INVOKE_URL, {
        query: currentInput,
      });

      const aiResponse: Message = {
        id: response.data.inquiry_id || (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.message,
        category: response.data.category,
        aiCategory: response.data.category,
        isCorrected: false,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiResponse]);
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: "サーバーと通信中に問題が発生しました。",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // 2. カテゴリ修正 (Human-in-the-Loop)
  const handleUpdateCategory = async (messageId: string, newCategory: string) => {
    try {
      const UPDATE_URL = import.meta.env.VITE_UPDATE_URL;
      await axios.patch(UPDATE_URL, {
        inquiry_id: messageId,
        final_category: newCategory,
        is_corrected: true
      });

      setMessages((prev) =>
        prev.map(msg => msg.id === messageId
          ? { ...msg, category: newCategory, isCorrected: true }
          : msg
        )
      );
      setEditingId(null);
    } catch (error) {
      alert("データベースの更新に失敗しました。");
    }
  };

  return (
    // background setting
    <div className="flex flex-col h-screen bg-[#001c58] text-white font-sans overflow-hidden">
      
      {/* Header */}
      <div className="flex justify-center items-center py-8">
        <h1 className="text-4xl font-extrabold tracking-tight">AIチャットボットサービス</h1>
      </div>

      {/* Message List Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 max-w-2xl mx-auto w-full">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-3 ${msg.role === 'user' ? 'flex-row' : 'flex-row-reverse'}`}
          >
            {/* ユーザーおよびAIアバターの設定  */}
            <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl shadow-lg flex-shrink-0 ${
              msg.role === 'user' ? 'bg-yellow-400' : 'bg-cyan-200'
            }`}>
              {msg.role === 'user' ? '🐶' : '🤖'}
            </div>

            {/* 吹き出しおよびカテゴリデザイン */}
            <div className={`flex flex-col max-w-[75%] ${msg.role === 'user' ? 'items-start' : 'items-end'}`}>
              <div className={`px-5 py-3 rounded-2xl text-white font-semibold shadow-md ${
                msg.role === 'user' 
                  ? 'bg-[#007bff] rounded-bl-none' 
                  : 'bg-[#e916dc] rounded-br-none'
              }`}>
                <p className="text-sm">{msg.content}</p>
                
                {/* カテゴリ表示（AI回答時のみ）*/}
                {msg.role === 'assistant' && msg.category && (
                  <div className="mt-2 pt-2 border-t border-white/20">
                    <p className="text-[20px] text-white/90">
                      📍 分類 : {msg.category} {msg.isCorrected && "(修正完了)"}
                    </p>

                    {/* Human-in-the-Loop Button */}
                    {msg.category.includes("確認必要") && (
                      <div className="mt-2">
                        {editingId !== msg.id ? (
                          <button
                            onClick={() => setEditingId(msg.id)}
                            className="w-full py-1 bg-white/20 hover:bg-white/30 rounded text-[30px] transition"
                          >
                            修正
                          </button>
                        ) : (
                          <div className="grid grid-cols-2 gap-1 mt-1">
                            {["技術", "料金", "クレーム", "その他"].map(cat => (
                              <button
                                key={cat}
                                onClick={() => handleUpdateCategory(msg.id, cat)}
                                className="py-1 bg-white text-[#e916dc] rounded text-[9px] font-bold hover:bg-gray-100 transition"
                              >
                                {cat}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-center">
            <div className="text-xs text-blue-300 animate-pulse italic">AIが回答を分析中です…</div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input Area (Bottom Fixed) */}
      <div className="max-w-2xl mx-auto w-full p-4 mb-6 mt-auto">
        <form onSubmit={handleSend} className="flex bg-white rounded-full overflow-hidden shadow-2xl p-1.5">
          <input
            type="text"
            className="flex-1 px-5 py-2.5 outline-none text-gray-800 text-sm"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="お問い合わせ内容を入力してください..."
          />
          <button
            type="submit"
            className="bg-[#007bff] text-white px-6 py-2.5 rounded-full font-bold hover:bg-blue-600 transition shadow-md text-sm"
          >
            伝送
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatAgent;
