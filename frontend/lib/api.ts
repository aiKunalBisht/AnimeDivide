import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface TopDivide {
  topic: string;
  jp_score: number;
  en_score: number;
  divide: number;
}

export interface Show {
  slug: string;
  title_en: string;
  title_jp: string;
  year: number;
  top_divide: TopDivide | null;
}

export interface TopicData {
  topic: string;
  jp_score: number;
  en_score: number;
  divide: number;
  post_count_jp: number;
  post_count_en: number;
}

export interface ShowDetail {
  slug: string;
  title_en: string;
  title_jp: string;
  mal_id: number;
  year: number;
  post_count: {
    en: number;
    jp: number;
  };
  topics: TopicData[];
}

export const getShows = async (): Promise<Show[]> => {
  const response = await axios.get(`${API_URL}/shows`);
  return response.data;
};

export const getShow = async (slug: string): Promise<ShowDetail> => {
  const response = await axios.get(`${API_URL}/shows/${slug}`);
  return response.data;
};

export const getNarrative = async (slug: string): Promise<string> => {
  const response = await axios.get(`${API_URL}/shows/${slug}/narrative`);
  return response.data.narrative;
};
