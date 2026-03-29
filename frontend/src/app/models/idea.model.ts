export interface Analysis {
  id: number;
  problem: string | null;
  failure_type: string | null;
  current_opportunity: string | null;
  pain_score: number | null;
  paying_capacity: number | null;
  mvp_ease: number | null;
  tech_advantage: number | null;
  total_score: number | null;
}

export interface Execution {
  id: number;
  mvp_plan: string | null;
  stack: string | null;
  monetization: string | null;
  estimated_days: number | null;
  status: string;
}

export interface Idea {
  id: number;
  name: string;
  description: string;
  failure_reason: string | null;
  industry: string | null;
  year: number | null;
  source_url: string | null;
  analysis: Analysis | null;
  execution: Execution | null;
}
