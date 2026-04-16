// types.ts
export type SenderRole = 'user' | 'assistant';

export interface Message {
  id: string;
  role: SenderRole;
  content: string;
  category?: string;      // 최종 카테고리 (수정 시 이 값이 바뀜)
  aiCategory?: string;    // AI가 최초에 분류했던 값 (로그용)
  isCorrected?: boolean;  // 사람이 수정한 적이 있는지 여부
  confidence?: number;    // AI의 확신도 점수 (2번 과제 연동)
  assignedTeam?: string; 
  timestamp: Date;
}