export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
}

export interface Analysis {
  id: string;
  project_id: string;
  file_type: string;
  file_name: string;
  status: string;
  created_at: string;
}

export interface Finding {
  id: string;
  analysis_id: string;
  title: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  description: string;
  recommendation: string | null;
  source: string | null;
}

export interface Report {
  id: string;
  analysis_id: string;
  summary: string;
  ai_explanation: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
