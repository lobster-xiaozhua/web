export interface Novel {
  id: string;
  title: string;
  author: string;
  cover: string;
  description: string;
  tags: string[];
  rating: number;
  viewCount: number;
  chapterCount: number;
  status: "ongoing" | "completed";
  updatedAt: string;
}

export interface Chapter {
  id: string;
  novelId: string;
  title: string;
  content: string;
  order: number;
  wordCount: number;
  publishedAt: string;
}

export interface User {
  id: string;
  username: string;
  avatar: string;
  email: string;
  favorites: string[];
  history: ReadingHistory[];
  createdAt: string;
}

export interface ReadingHistory {
  novelId: string;
  chapterId: string;
  progress: number;
  lastReadAt: string;
}

export interface ReadingProgress {
  chapterId: string;
  novelId: string;
  progress: number;
  fontSize: number;
  theme: "light" | "dark" | "sepia";
}

export interface Comment {
  id: string;
  userId: string;
  username: string;
  avatar: string;
  content: string;
  createdAt: string;
  likes: number;
}

export interface RankingItem {
  rank: number;
  novel: Novel;
  score: number;
}

export interface SearchResult {
  novels: Novel[];
  total: number;
  page: number;
  pageSize: number;
}

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}
