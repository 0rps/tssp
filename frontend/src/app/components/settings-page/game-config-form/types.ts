export interface IGameConfiguration {
  ads_txt_enabled: boolean,
  auction_type: 1 | 2,
  budget: number,
  click_revenue: number,
  conversion_revenue: number,
  frequency_capping: number,
  frequency_capping_enabled: boolean,
  game_goal: 'revenue' | 'cpc',
  impression_revenue: number,
  impressions_total: number,
  mode: 'free' | 'script',
  blocked_categories_enabled: boolean
}
