/**
 * TypeScript Data Contracts for MIRROR FUTURE.
 * 1:1 reflection of backend Pydantic contracts in backend/app/models/schemas.py
 * Strict typing for EXIF/Vision forensics, RAG Social Twins,
 * NumPy Monte Carlo stochastic simulations, and calendar/messaging actuators.
 */

// ==========================================
// 1. EXIF & Vision Forensics
// ==========================================

export interface ExifGpsCoordinates {
  has_gps: boolean;
  latitude?: number | null;
  longitude?: number | null;
  altitude?: number | null;
  maps_url?: string | null;
}

export interface ExifMetadata {
  has_exif: boolean;
  timestamp?: string | null;
  device_make?: string | null;
  device_model?: string | null;
  lens_model?: string | null;
  software?: string | null;
  iso?: number | null;
  exposure_time?: string | null;
  f_number?: number | null;
  focal_length?: number | null;
  flash_fired?: boolean | null;
  image_width: number;
  image_height: number;
  color_mode: string;
  file_format: string;
  file_size_bytes: number;
  gps: ExifGpsCoordinates;
  security_flags: string[];
}

export interface VisionForensicAnalysis {
  /** Detailed analytical description of the forensic scene */
  scene_description: string;
  /** Identified persons, objects, brands, and materials */
  detected_entities: string[];
  /** Setting type (e.g. party, corporate office, bedroom, library) */
  social_context: string;
  /** Observed intimacy classification (public, casual, intimate, high-risk) */
  intimacy_level: string;
  /** Alcohol, disarray, confidential screens, sensitive documents */
  substances_or_risk_indicators: string[];
  /** Reputational damage risk from 0.0 to 1.0 */
  reputational_risk_score: number;
  /** Privacy leak / geolocation exposure risk from 0.0 to 1.0 */
  privacy_risk_score: number;
  /** Contradictions between EXIF timestamp and lighting/reflections */
  forensic_inconsistencies: string[];
  /** Direct causal recommendation on sharing vs archiving the photo */
  causal_recommendation: string;
}

export interface ImageForensicReport {
  exif: ExifMetadata;
  vision: VisionForensicAnalysis;
  analyzed_at?: string | Date;
}

// ==========================================
// 2. RAG Social Twin & Multiplayer Inference
// ==========================================

export interface ContactLexicalProfile {
  /** Characteristic words and recurring slang */
  frequent_words: string[];
  /** Authentic favorite emojis */
  frequent_emojis: string[];
  /** Median response latency in minutes */
  median_response_minutes: number;
  /** Style: monosyllabic, eloquent, sarcastic, concise */
  syntax_style: string;
  /** Punctuation habits (ellipsis, capitalizations, exclamations) */
  punctuation_traits: string;
  /** Frequent idioms and common linguistic turns */
  frequent_idioms: any[];
  /** Percentage of conversations initiated by the user */
  user_initiates_pct?: number | null;
  total_conversation_sessions?: number;
  user_initiated_sessions?: number;
}

export interface RealContact {
  id: string;
  name: string;
  phone?: string | null;
  /** partner, thesis_advisor, manager, friend, family */
  relationship_type: string;
  closeness_level: number;
  /** User conversation initiation percentage */
  user_initiates_pct?: number | null;
  real_lexical_profile: ContactLexicalProfile;
}

export interface ChatEpisode {
  id: string;
  contact_id: string;
  timestamp?: string | null;
  user_prompt: string;
  contact_response: string;
  similarity_score: number;
  conflict_or_support_tag?: string | null;
}

export interface EvidenceCitation {
  episode_id: string;
  historical_date?: string | null;
  quoted_exchange: string;
  behavioral_pattern_proven: string;
}

export interface SocialTwinPrediction {
  contact_id: string;
  contact_name: string;
  relationship_type: string;
  /** Primary psychological reaction (e.g. Sarcasm, Pride, Skepticism) */
  emotional_reaction: string;
  /** Exact message replicating authentic vocabulary, slang, and emojis */
  predicted_message: string;
  confidence_score: number;
  /** Predicted response latency in minutes */
  estimated_response_minutes: number;
  historical_evidence: EvidenceCitation[];
  causal_rationale: string;
}

export interface MultiTwinSimulationResult {
  action_or_image_tested: string;
  simulated_contacts: SocialTwinPrediction[];
  net_relational_impact_score: number;
  high_risk_alerts: string[];
  strategic_advice: string;
}

// ==========================================
// 3. NumPy Stochastic Monte Carlo Simulation
// ==========================================

export interface DailyScheduleInput {
  day_index: number;
  work_hours: number;
  thesis_hours: number;
  sleep_hours: number;
  social_hours?: number;
  is_weekend?: boolean;
}

export interface MonteCarloSimulationConfig {
  num_trajectories?: number;
  num_days?: number;
  thesis_total_units_required?: number;
  random_seed?: number;
}

export interface TrajectoryPercentilePoint {
  day: number;
  p10: number;
  p50: number;
  p90: number;
}

export interface MonteCarloCurves {
  fatigue: TrajectoryPercentilePoint[];
  thesis_progress: TrajectoryPercentilePoint[];
  burnout_risk: TrajectoryPercentilePoint[];
  relational_capital: TrajectoryPercentilePoint[];
}

export interface InverseEngineeringPrescription {
  optimal_daily_work_cap_hours: number;
  optimal_daily_thesis_hours: number;
  minimum_sleep_target_hours: number;
  thesis_completion_probability_at_day_120: number;
  thesis_completion_probability_at_day_180: number;
  burnout_probability_p90_at_day_180: number;
  strategic_levers: string[];
}

export interface MonteCarloAnalysisOutput {
  curves: MonteCarloCurves;
  final_summary: Record<string, any>;
  llama_causal_diagnosis: string;
  prescription: InverseEngineeringPrescription;
}

// ==========================================
// 4. Actuators & Ingestion Responses
// ==========================================

export interface OptimalTimeBlock {
  title: string;
  description: string;
  category: string;
  start_time: string | Date;
  end_time: string | Date;
  alarm_minutes_before?: number;
  location?: string | null;
}

export interface CalendarIcsResponse {
  ics_raw: string;
  filename: string;
  total_blocks: number;
  generated_at?: string;
}

export interface WhatsAppNotificationRequest {
  recipient_phone: string;
  message_text: string;
  media_url?: string | null;
  media_filename?: string | null;
}

export interface WhatsAppSendResult {
  success: boolean;
  status_code: number;
  message_id?: string | null;
  recipient_phone: string;
  error_message?: string | null;
  timestamp?: string | Date;
}

export interface SocialTwinSimulateRequest {
  action_or_image_claim: string;
  user_id?: string | null;
}

export interface FullPhotoSimulationResponse {
  vision_report: ImageForensicReport;
  social_twin_result: MultiTwinSimulationResult;
  prediction_log_id?: string | null;
}

export interface IngestLexicalProfile {
  top_words: Array<{ word: string; count: number; percentage: number }>;
  top_emojis: Array<{ emoji: string; count: number; percentage: number }>;
  syntax_style?: string;
  tone?: string;
  avg_words_per_message?: number;
  frequent_idioms?: Array<{ idiom: string; count: number; percentage: number }>;
}

export interface IngestContactRecord {
  contact_name?: string;
  relationship_type?: string;
  total_messages_analyzed?: number;
  real_median_reply_minutes?: number;
  user_initiates_pct?: number;
  active_hours_distribution?: Record<string, number>;
  real_lexical_profile: IngestLexicalProfile;
  extracted_psych_summary?: string;
}

export interface IngestBusyMetrics {
  total_events: number;
  busy_events_count: number;
  total_busy_hours: number;
  category_hours: Record<string, number>;
  daily_busy_hours: Record<string, number>;
  hourly_busy_distribution: Record<string, number>;
  average_daily_busy_hours: number;
  days_count: number;
  thesis_hours_total: number;
  work_hours_total: number;
  busiest_day?: string | null;
}

export interface IngestGitHubMetrics {
  total_commits?: number;
  thesis_commits_count?: number;
  nocturnal_commits_count?: number;
  nocturnal_commits_pct?: number;
  languages_detected?: Record<string, number>;
  repositories_active?: string[];
}

export interface IngestWhatsAppResponse {
  success: boolean;
  filename: string;
  contact_id?: string | null;
  user_id?: string;
  contact_record: IngestContactRecord;
  episodes_vectorized: number;
  vector_dimension: number;
  vector_storage_status: string;
  chat_metadata: Record<string, any>;
}

export interface IngestCalendarResponse {
  success: boolean;
  filename: string;
  total_events_parsed: number;
  busy_metrics: IngestBusyMetrics;
  sample_events: any[];
}

export interface IngestGitHubResponse {
  success: boolean;
  username: string;
  events_retrieved: number;
  github_metrics: IngestGitHubMetrics;
}

export interface UserRealProfileTelemetry {
  full_name?: string;
  whatsapp_alias?: string;
  occupation_and_goals?: string;
  real_calendar_busy_hours_week?: number;
  real_avg_sleep_hours?: number;
  real_study_thesis_hours_day?: number;
  github_username?: string;
}

export interface SyncTelemetryResponse {
  success: boolean;
  user_id?: string;
  user_real_profile: UserRealProfileTelemetry;
  correlation_analysis: Record<string, any>;
}

// ==========================================
// 5. Mirror Future Holistic Engine Models
// ==========================================

export interface MacroEconomicContext {
  country_code: string;
  country_name: string;
  annual_inflation_rate: number;
  gdp_growth_rate: number;
  unemployment_rate: number;
  currency: string;
  exchange_rate_to_usd: number;
  is_live_data?: boolean;
  source?: string;
}

export interface DimensionPercentiles {
  p10: number;
  p50: number;
  p90: number;
}

export interface HorizonMetrics {
  financial_net_worth: DimensionPercentiles;
  purchasing_power_score: DimensionPercentiles;
  health_and_vitality_score: DimensionPercentiles;
  burnout_probability: number;
  career_and_goal_completion_pct: DimensionPercentiles;
  social_and_emotional_stability: DimensionPercentiles;
  macro_resilience_score: DimensionPercentiles;
}

export interface HorizonNarrative {
  future_self_portrait: string;
  economic_reality: string;
  health_and_mind_state: string;
  critical_warning: string;
}

export interface HorizonScores5D {
  finances: number;
  health_energy: number;
  career: number;
  relationships: number;
  macro_resilience: number;
}

export interface HorizonSnapshot {
  horizon_name: string;
  horizon_label?: string;
  day_index: number;
  burnout_risk: number;
  scores_5d: HorizonScores5D;
  metrics: HorizonMetrics;
  narrative: HorizonNarrative;
  future_self_image_url?: string | null;
  optimal_comparison_image_url?: string | null;
  visual_scene_caption?: string | null;
  first_person_voice_script?: string | null;
  future_self_video_url?: string | null;
  reference_photo_url?: string | null;
  has_reference_photo?: boolean;
}

export interface GoldenPathAdjustment {
  domain: string;
  lever_title?: string;
  expected_gain?: string;
  current_trajectory_value?: string;
  optimal_dr_jef_value?: string;
  actionable_prescription?: string;
  current_baseline?: string;
  prescribed_target?: string;
  expected_impact_p90?: string;
}

export interface LiveSnippet {
  category: string;
  title: string;
  summary: string;
  url: string;
  source: string;
}

export interface RealJobVacancy {
  job_title: string;
  company_or_entity: string;
  location_and_modality: string;
  offered_salary_range: string;
  gross_salary_monthly: number;
  net_salary_monthly: number;
  required_skills_and_credentials: string[];
  source_url: string;
  exact_match_score_pct: number;
  missing_requirements: string[];
  weeks_to_close_gap: number;
}

export interface LiveWebIntelligenceReport {
  live_snippets: LiveSnippet[];
  city_cost_pressure_index: number;
  career_market_demand_score: number;
  synthesized_real_time_context: string;
  local_salary_range_min: number;
  local_salary_range_max: number;
  remote_salary_range_min: number;
  remote_salary_range_max: number;
  local_companies_found: string[];
  goal_requirements_evidence: string[];
  real_job_openings: RealJobVacancy[];
}

export interface InferredHumanFactors {
  inferred_dependents_burden: number;
  home_emotional_balance: number;
  partner_and_friends_effect: number;
  stress_spending_and_procrastination_risk: number;
  resilience_and_grit_score: number;
  dependents_care_count: number;
  daily_caregiving_hours: number;
  caregiving_details: string;
  human_context_synthesis: string;
}

export interface DiscoveryQuestionsRequest {
  age?: number;
  occupation?: string;
  city?: string;
  lang?: string;
  life_profile_type?: string | null;
}

export interface DiscoveryQuestionsResponse {
  questions: string[];
}

export interface DiscoveryInterviewMessage {
  role: 'assistant' | 'user';
  content: string;
}

export interface DiscoveryInterviewRequest {
  conversation_history: DiscoveryInterviewMessage[];
  lang?: string;
  ingested_files_context?: string | null;
  force_complete?: boolean;
  force_generate?: boolean;
}

export interface DiscoveryInterviewResponse {
  is_complete: boolean;
  completeness_pct: number;
  pillars_covered?: Record<string, boolean>;
  next_question?: string | null;
  full_person_dossier_text?: string | null;
  extracted_parameters?: Record<string, any> | null;
}

export interface SyncDossierRequest {
  dossier_text: string;
  current_parameters?: Record<string, any> | null;
  lang?: string;
}

export interface SyncDossierResponse {
  extracted_parameters: Record<string, any>;
  full_person_dossier_text: string;
  status: string;
}

export interface CareerLifeEvent {
  year: number;
  age_at_event: number;
  event_type: string;
  title_or_role: string;
  monthly_income: number;
  location: string;
  description?: string;
}

export interface LiveWebSource {
  category: string;
  title: string;
  url: string;
}

export interface HolisticLocation {
  country: string;
  city: string;
  [key: string]: any;
}

export interface HolisticFinances {
  monthly_income: number;
  monthly_expenses: number;
  current_savings: number;
  current_debt: number;
  currency: string;
  [key: string]: any;
}

export interface HolisticTimeUse {
  sleep_hours: number;
  work_hours: number;
  study_project_hours: number;
  screen_time_lost_hours: number;
  exercise_hours?: number;
  [key: string]: any;
}

export interface HolisticFutureRequest {
  location: HolisticLocation;
  finances: HolisticFinances;
  time_use: HolisticTimeUse;
  full_person_dossier_text?: string | null;
  past_career_events?: CareerLifeEvent[];
  life_profile_type?: string;
  goal_mode?: boolean;
  lang?: string;
  age?: number;
  country_code?: string;
  city?: string;
  occupation?: string;
  main_goal_1y?: string | null;
  one_year_goal?: string | null;
  medium_term_goals?: string | null;
  long_term_goals?: string | null;
  monthly_income?: number;
  monthly_expenses?: number;
  current_savings?: number;
  current_debt?: number;
  currency?: string;
  sleep_hours?: number;
  work_hours?: number;
  study_or_project_hours?: number;
  screen_time_distraction_hours?: number;
  exercise_days_per_week?: number;
  social_hours?: number;
  person_identifier?: string | null;
  full_name_or_handle?: string | null;
  user_photo_base64?: string | null;
  full_name?: string | null;
  university_or_institution?: string | null;
  current_company_or_org?: string | null;
  daily_income_avg?: number | null;
  work_days_per_week?: number;
  daily_expense_avg?: number | null;
  rural_product?: string | null;
  campaign_income_est?: number | null;
  physical_labor_intensity?: string;
  trade_modality?: string;
  contract_type?: string;
  career_or_degree?: string;
  life_stage?: string;
  months_to_graduation?: number;
  years_of_experience?: number;
  key_skills?: string;
  english_level?: string;
  verified_competence_multiplier?: number;
  daily_caregiving_hours?: number;
  business_type?: string | null;
  monthly_sales_net?: number | null;
  work_modality_target?: string;
  target_monthly_salary_1y?: number;
  housing_situation?: string;
  dependents_count?: number;
  household_climate?: string;
  relationship_status?: string;
  social_circle_influence?: string;
  self_description?: string;
  personality_traits?: string[];
  chat_sentiment_avg?: number | null;
  chat_dominant_tag?: string | null;
  chat_median_reply_min?: number | null;
  chat_extracted_summary?: string | null;
  open_family_and_dependents?: string;
  open_relationships_and_friends?: string;
  open_personality_and_habits?: string;
}

export interface GoalFeasibilityItem {
  horizon_type: string;
  horizon_label: string;
  goal_statement: string;
  feasibility_status: string;
  feasibility_pct: number;
  required_capital: number;
  projected_savings_capital: number;
  capital_gap: number;
  prerequisites_met: string[];
  prerequisites_missing: string[];
  reality_check_verdict: string;
  strategic_bridge: string;
}

export interface GoalsVerificationReport {
  short_term_1y?: GoalFeasibilityItem | null;
  medium_term_3y?: GoalFeasibilityItem | null;
  long_term_5y?: GoalFeasibilityItem | null;
  global_synthesis: string;
}

export interface CareerTransitionNode {
  horizon_key: string;
  horizon: string;
  horizon_label: string;
  months_ahead: number;
  months_from_now: number;
  p10_stagnation_role: string;
  p10_income: number;
  p50_likely_role: string;
  p50_income: number;
  p90_accelerated_role: string;
  p90_income: number;
  transition_probability_pct: number;
  cohort_rank_descriptor: string;
  key_catalysts: string[];
  required_skills_to_unlock: string[];
  blockers: string[];
  key_risk_factor: string;
  market_demand_alignment: string;
}

export interface ActuarialInsertionPlan {
  estimated_weeks_to_first_contract_p10: number;
  estimated_weeks_to_first_contract_p50: number;
  estimated_weeks_to_first_contract_p90: number;
  weeks_to_75pct_probability: number;
  weekly_hiring_probability_curve: number[];
  exact_net_salary_progression: Record<string, any>[];
  cash_flow_monthly_breakdown: Record<string, number>;
}

export interface StrategicRoadmapPhase {
  phase_key: string;
  phase_label: string;
  timeframe: string;
  main_objective: string;
  target_salary_range: string;
  daily_changes_to_implement: string[];
  strategic_actions_milestones: string[];
  critical_trap_to_avoid: string;
}

export interface CareerAutocompletionResult {
  cohort_similarity_percentile: number;
  cohort_archetype: string;
  cohort_rank_descriptor: string;
  predicted_career_transitions: CareerTransitionNode[];
  real_job_openings: RealJobVacancy[];
  strategic_roadmap: StrategicRoadmapPhase[];
  actuarial_insertion?: ActuarialInsertionPlan | null;
  verified_competence_multiplier: number;
  ai_automation_exposure_pct: number;
  ai_leverage_potential_pct: number;
  career_bottlenecks: string[];
  recommended_skill_acquisitions: string[];
  recommended_high_leverage_skills: string[];
  top_target_roles_matching: string[];
  local_market_match_index: number;
  past_events_encoded_count: number;
  trajectory_summary: string;
  trajectory_vector_summary?: string;
}

export interface HolisticFutureResponse {
  request_meta: Record<string, any>;
  macro_context: Record<string, any>;
  live_web_intelligence?: Record<string, any> | null;
  live_web_sources?: LiveWebSource[] | null;
  inferred_human_factors?: InferredHumanFactors | null;
  snapshot_1_month: HorizonSnapshot;
  snapshot_6_months: HorizonSnapshot;
  snapshot_1_year: HorizonSnapshot;
  horizons: {
    one_month: HorizonSnapshot;
    six_months: HorizonSnapshot;
    one_year: HorizonSnapshot;
  };
  root_causes?: Array<{
    rank: number;
    factor?: string;
    description?: string;
    impact?: string;
    category?: string;
    title?: string;
    evidence_quote?: string;
    [key: string]: any;
  }>;
  social_twin_impact?: MultiTwinSimulationResult | null;
  monte_carlo_output?: MonteCarloAnalysisOutput | null;
  golden_path_adjustments: GoldenPathAdjustment[];
  executive_summary: string;
  goals_verification?: GoalsVerificationReport | null;
  career_autocompletion?: CareerAutocompletionResult | null;
}

export type TrajectoryPercentileBranch = 'p10' | 'p50' | 'p90';
