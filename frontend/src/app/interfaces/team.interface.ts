export interface ITeamConfiguration {
  name: string;
  api_url: string;
  bearer_token?: string | null;
}

export interface ITeamResponse {
  id: string;
  name: string;
}

export interface ITeam {
  name: string;
  budget: number;
  score: number;
  impressions: number;
  clicks: number;
  conversions: number;
}

export type ITeamsResponse = ITeam[];
