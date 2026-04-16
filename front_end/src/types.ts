// types.ts
export type SenderRole = 'user' | 'assistant';

export interface Message {
  id: string;
  role: SenderRole;
  content: string;
  category?: string;      // 最終カテゴリ（修正時にこの値が変更されます）
  aiCategory?: string;    // AIが最初に分類した値
  isCorrected?: boolean;  // 人が修正したことがあるかどうか
  confidence?: number;    // AIの確信度スコア
  assignedTeam?: string; 
  timestamp: Date;
}
