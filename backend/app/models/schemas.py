"""
Pydantic Data Contracts for MIRROR FUTURE.
Strict typed schemas for EXIF/Vision forensics, RAG Social Twins,
NumPy Monte Carlo stochastic simulations, and calendar/messaging actuators.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


# ==========================================
# 1. EXIF & Vision Forensics
# ==========================================

class ExifGpsCoordinates(BaseModel):
    has_gps: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    maps_url: Optional[str] = None


class ExifMetadata(BaseModel):
    has_exif: bool = False
    timestamp: Optional[str] = None
    device_make: Optional[str] = None
    device_model: Optional[str] = None
    lens_model: Optional[str] = None
    software: Optional[str] = None
    iso: Optional[int] = None
    exposure_time: Optional[str] = None
    f_number: Optional[float] = None
    focal_length: Optional[float] = None
    flash_fired: Optional[bool] = None
    image_width: int
    image_height: int
    color_mode: str
    file_format: str
    file_size_bytes: int
    gps: ExifGpsCoordinates = Field(default_factory=ExifGpsCoordinates)
    security_flags: List[str] = Field(default_factory=list)


class VisionForensicAnalysis(BaseModel):
    scene_description: str = Field(..., description="Detailed analytical description of framing, lighting, and subjects")
    detected_entities: List[str] = Field(default_factory=list, description="Identified persons, objects, brands, and materials")
    social_context: str = Field(..., description="Setting type (e.g. party, corporate office, bedroom, library)")
    intimacy_level: str = Field(..., description="Observed intimacy classification (public, casual, intimate, high-risk)")
    substances_or_risk_indicators: List[str] = Field(default_factory=list, description="Alcohol, disarray, confidential screens, sensitive documents")
    reputational_risk_score: float = Field(..., ge=0.0, le=1.0, description="Reputational damage risk from 0.0 to 1.0")
    privacy_risk_score: float = Field(..., ge=0.0, le=1.0, description="Privacy leak / geolocation exposure risk from 0.0 to 1.0")
    forensic_inconsistencies: List[str] = Field(default_factory=list, description="Contradictions between EXIF timestamp and lighting/reflections")
    causal_recommendation: str = Field(..., description="Direct causal recommendation on sharing vs archiving the photo")


class ImageForensicReport(BaseModel):
    exif: ExifMetadata
    vision: VisionForensicAnalysis
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


# ==========================================
# 2. RAG Social Twin & Multiplayer Inference
# ==========================================

class ContactLexicalProfile(BaseModel):
    frequent_words: List[str] = Field(default_factory=list, description="Characteristic words and recurring slang")
    frequent_emojis: List[str] = Field(default_factory=list, description="Authentic favorite emojis")
    median_response_minutes: float = Field(default=15.0, description="Median response latency in minutes")
    syntax_style: str = Field(default="informal", description="Style: monosyllabic, eloquent, sarcastic, concise")
    punctuation_traits: str = Field(default="", description="Punctuation habits (ellipsis, capitalizations, exclamations)")
    frequent_idioms: List[Any] = Field(default_factory=list, description="Frequent idioms and common linguistic turns")
    user_initiates_pct: Optional[float] = Field(default=None, description="Percentage of conversations initiated by the user")


class RealContact(BaseModel):
    id: str
    name: str
    phone: Optional[str] = None
    relationship_type: str = Field(..., description="partner, thesis_advisor, manager, friend, family")
    closeness_level: float = Field(default=0.8, ge=0.0, le=1.0)
    user_initiates_pct: Optional[float] = Field(default=None, description="User conversation initiation percentage")
    real_lexical_profile: ContactLexicalProfile


class ChatEpisode(BaseModel):
    id: str
    contact_id: str
    timestamp: Optional[str] = None
    user_prompt: str
    contact_response: str
    similarity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    conflict_or_support_tag: Optional[str] = None


class EvidenceCitation(BaseModel):
    episode_id: str
    historical_date: Optional[str] = None
    quoted_exchange: str
    behavioral_pattern_proven: str


class SocialTwinPrediction(BaseModel):
    contact_id: str
    contact_name: str
    relationship_type: str
    emotional_reaction: str = Field(..., description="Primary psychological reaction (e.g. Sarcasm, Pride, Skepticism)")
    predicted_message: str = Field(..., description="Exact message replicating authentic vocabulary, slang, and emojis")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    estimated_response_minutes: float = Field(..., description="Predicted response latency in minutes")
    historical_evidence: List[EvidenceCitation] = Field(default_factory=list)
    causal_rationale: str = Field(..., description="Behavioral justification grounded in authentic past chats")


class MultiTwinSimulationResult(BaseModel):
    action_or_image_tested: str
    simulated_contacts: List[SocialTwinPrediction]
    net_relational_impact_score: float = Field(..., ge=-1.0, le=1.0, description="Net relational balance (-1.0 destructive to +1.0 synergic)")
    high_risk_alerts: List[str] = Field(default_factory=list)
    strategic_advice: str


# ==========================================
# 3. NumPy Stochastic Monte Carlo Simulation
# ==========================================

class DailyScheduleInput(BaseModel):
    day_index: int
    work_hours: float
    thesis_hours: float
    sleep_hours: float
    social_hours: float = 1.0
    is_weekend: bool = False


class MonteCarloSimulationConfig(BaseModel):
    num_trajectories: int = Field(default=1000, description="Number of stochastic Monte Carlo sample paths")
    num_days: int = Field(default=180, description="Simulation time horizon in days")
    thesis_total_units_required: float = Field(default=350.0, description="Net units required to complete objectives")
    random_seed: Optional[int] = 42


class TrajectoryPercentilePoint(BaseModel):
    day: int
    p10: float
    p50: float
    p90: float


class MonteCarloCurves(BaseModel):
    fatigue: List[TrajectoryPercentilePoint]
    thesis_progress: List[TrajectoryPercentilePoint]
    burnout_risk: List[TrajectoryPercentilePoint]
    relational_capital: List[TrajectoryPercentilePoint]


class InverseEngineeringPrescription(BaseModel):
    optimal_daily_work_cap_hours: float
    optimal_daily_thesis_hours: float
    minimum_sleep_target_hours: float
    thesis_completion_probability_at_day_120: float
    thesis_completion_probability_at_day_180: float
    burnout_probability_p90_at_day_180: float
    strategic_levers: List[str]


class MonteCarloAnalysisOutput(BaseModel):
    curves: MonteCarloCurves
    final_summary: Dict[str, Any]
    llama_causal_diagnosis: str
    prescription: InverseEngineeringPrescription


# ==========================================
# 4. Actuators (Calendar & Messaging)
# ==========================================

class OptimalTimeBlock(BaseModel):
    title: str
    description: str
    category: str = Field(default="DEEP_WORK", description="DEEP_WORK, THESIS, SLEEP, RELATIONAL_BUFFER, REST")
    start_time: datetime
    end_time: datetime
    alarm_minutes_before: int = 15
    location: Optional[str] = None


class CalendarIcsResponse(BaseModel):
    ics_raw: str
    filename: str
    total_blocks: int
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class WhatsAppNotificationRequest(BaseModel):
    recipient_phone: str = Field(..., description="Phone number with country code in E.164 format (e.g. +573001234567)")
    message_text: str
    media_url: Optional[str] = None
    media_filename: Optional[str] = None


class WhatsAppSendResult(BaseModel):
    success: bool
    status_code: int
    message_id: Optional[str] = None
    recipient_phone: str
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SocialTwinSimulateRequest(BaseModel):
    action_or_image_claim: str
    user_id: Optional[str] = None


class FullPhotoSimulationResponse(BaseModel):
    vision_report: ImageForensicReport
    social_twin_result: MultiTwinSimulationResult
    prediction_log_id: Optional[str] = None


# ==========================================
# 5. Mirror Future Holistic Engine Contracts
# ==========================================

class MacroEconomicContext(BaseModel):
    country_code: str = Field(..., description="ISO country code (PE, CO, MX, US, ES, etc.)")
    country_name: str = Field(..., description="Full country name")
    annual_inflation_rate: float = Field(..., description="Annual inflation rate (%)")
    gdp_growth_rate: float = Field(..., description="Real annual GDP growth (%)")
    unemployment_rate: float = Field(..., description="National unemployment rate (%)")
    currency: str = Field(..., description="ISO currency code (PEN, COP, MXN, USD, EUR)")
    exchange_rate_to_usd: float = Field(..., description="Local currency units per 1 USD")
    is_live_data: bool = Field(default=True, description="True if sourced from active live APIs")
    source: str = Field(default="World Bank API & ExchangeRate API")


class DimensionPercentiles(BaseModel):
    p10: float
    p50: float
    p90: float


class HorizonMetrics(BaseModel):
    financial_net_worth: DimensionPercentiles
    purchasing_power_score: DimensionPercentiles
    health_and_vitality_score: DimensionPercentiles
    burnout_probability: float
    career_and_goal_completion_pct: DimensionPercentiles
    social_and_emotional_stability: DimensionPercentiles
    macro_resilience_score: DimensionPercentiles


class HorizonNarrative(BaseModel):
    future_self_portrait: str = ""
    economic_reality: str = ""
    health_and_mind_state: str = ""
    critical_warning: str = ""


class HorizonSnapshot(BaseModel):
    horizon_name: str
    day_index: int
    metrics: HorizonMetrics
    narrative: HorizonNarrative
    future_self_image_url: Optional[str] = None
    optimal_comparison_image_url: Optional[str] = None
    visual_scene_caption: Optional[str] = None
    first_person_voice_script: Optional[str] = None
    future_self_video_url: Optional[str] = None
    reference_photo_url: Optional[str] = None
    has_reference_photo: bool = False


class GoldenPathAdjustment(BaseModel):
    domain: str
    current_baseline: str
    prescribed_target: str
    expected_impact_p90: str


class LiveSnippet(BaseModel):
    category: str = Field(..., description="'CITY_AND_ECONOMY' | 'LABOR_MARKET' | 'GOAL_FEASIBILITY' | 'PROFESSIONAL_FOOTPRINT'")
    title: str
    summary: str
    url: str
    source: str


class RealJobVacancy(BaseModel):
    job_title: str = Field(description="Exact job title from active recruitment listing")
    company_or_entity: str = Field(description="Company, public agency, or hiring entity")
    location_and_modality: str = Field(description="Location and modality (e.g. On-site, Hybrid, Remote LATAM/Global)")
    offered_salary_range: str = Field(description="Published or estimated salary range in local currency")
    gross_salary_monthly: float = Field(default=0.0, description="Gross monthly salary in local currency")
    net_salary_monthly: float = Field(default=0.0, description="Take-home net salary after statutory deductions")
    required_skills_and_credentials: List[str] = Field(default_factory=list, description="Required credentials and technical skills")
    source_url: str = Field(default="", description="URL link to job opening or portal")
    exact_match_score_pct: float = Field(default=0.0, description="Semantic 384d match penalized by strict exclusion filters (0 to 100%)")
    missing_requirements: List[str] = Field(default_factory=list, description="Mandatory requirements currently missing")
    weeks_to_close_gap: int = Field(default=0, description="Estimated real weeks to bridge missing credentials")


class LiveWebIntelligenceReport(BaseModel):
    live_snippets: List[LiveSnippet] = Field(default_factory=list)
    city_cost_pressure_index: float = Field(default=1.0, ge=0.7, le=1.5, description="Cost of living pressure index (0.7 to 1.5)")
    career_market_demand_score: float = Field(default=75.0, ge=0.0, le=100.0, description="Market demand score for occupation (0 to 100)")
    synthesized_real_time_context: str = Field(default="", description="Synthesized summary of live web intelligence")
    local_salary_range_min: float = Field(default=0.0, description="Local minimum salary in target city")
    local_salary_range_max: float = Field(default=0.0, description="Local maximum salary in target city")
    remote_salary_range_min: float = Field(default=0.0, description="Remote / national minimum salary")
    remote_salary_range_max: float = Field(default=0.0, description="Remote / national maximum salary")
    local_companies_found: List[str] = Field(default_factory=list, description="Identified companies operating in region")
    goal_requirements_evidence: List[str] = Field(default_factory=list, description="Market requirements verified for primary goal")
    real_job_openings: List[RealJobVacancy] = Field(default_factory=list, description="Active vacancies and public tenders analyzed")


class InferredHumanFactors(BaseModel):
    inferred_dependents_burden: float = Field(default=0.0, ge=0.0, le=1.0, description="Financial and caregiving load index (0.0 to 1.0)")
    home_emotional_balance: float = Field(default=0.5, ge=-1.0, le=1.0, description="Home emotional climate (-1.0 conflict to +1.0 supportive)")
    partner_and_friends_effect: float = Field(default=0.4, ge=-1.0, le=1.0, description="Social circle leverage (-1.0 draining to +1.0 uplifting)")
    stress_spending_and_procrastination_risk: float = Field(default=0.3, ge=0.0, le=1.0, description="Anxiety / impulsive spending risk (0.0 to 1.0)")
    resilience_and_grit_score: float = Field(default=0.7, ge=0.0, le=1.0, description="Discipline and grit index (0.0 to 1.0)")
    dependents_care_count: int = Field(default=0, ge=0, description="Number of family dependents requiring active care")
    daily_caregiving_hours: float = Field(default=0.0, ge=0.0, description="Daily hours committed to family caregiving")
    caregiving_details: str = Field(default="", description="Caregiving details extracted from open questions")
    human_context_synthesis: str = Field(default="", description="Psychological and contextual synthesis of personal responses")


class DiscoveryQuestionsRequest(BaseModel):
    age: int = 25
    occupation: str = "General"
    city: str = "General"
    lang: str = "EN"
    life_profile_type: Optional[str] = None


class DiscoveryQuestionsResponse(BaseModel):
    questions: List[str]


class DiscoveryInterviewMessage(BaseModel):
    role: str = Field(description="'assistant' | 'user'")
    content: str


class DiscoveryInterviewRequest(BaseModel):
    conversation_history: List[DiscoveryInterviewMessage] = Field(default_factory=list)
    lang: str = "EN"
    ingested_files_context: Optional[str] = None
    force_complete: bool = False
    force_generate: bool = False


class DiscoveryInterviewResponse(BaseModel):
    is_complete: bool
    completeness_pct: int
    next_question: Optional[str] = None
    full_person_dossier_text: Optional[str] = None
    extracted_parameters: Optional[Dict[str, Any]] = None


class SyncDossierRequest(BaseModel):
    dossier_text: str
    current_parameters: Optional[Dict[str, Any]] = None
    lang: str = "EN"


class SyncDossierResponse(BaseModel):
    extracted_parameters: Dict[str, Any]
    full_person_dossier_text: str
    status: str = "synced"


class CareerLifeEvent(BaseModel):
    year: int = Field(description="Event calendar year (e.g. 2022, 2024, 2026)")
    age_at_event: int = Field(description="Age of person at event")
    event_type: str = Field(
        description="'EDUCATION' | 'FIRST_JOB' | 'ROLE_CHANGE' | 'SKILL_ACQUISITION' | 'UNEMPLOYMENT_GAP' | 'FREELANCE_OR_BUSINESS' | 'CURRENT_STATE'"
    )
    title_or_role: str = Field(description="Title of role, study, or professional milestone")
    monthly_income: float = Field(default=0.0, description="Monthly income at that career milestone")
    location: str = Field(default="", description="City or country where event occurred")
    description: Optional[str] = Field(default="", description="Supplementary milestone details")


class HolisticFutureRequest(BaseModel):
    # 0. Reality Profile and Mirror Mode
    full_person_dossier_text: Optional[str] = Field(default="", description="Complete biographical summary and reality dossier")
    past_career_events: List[CareerLifeEvent] = Field(default_factory=list, description="Chronological sequence of life and career events (Life2Vec sequence)")
    life_profile_type: str = Field(
        default="DAY_TO_DAY_WORKER",
        description="'DAY_TO_DAY_WORKER' | 'RURAL_FIELD_PRODUCER' | 'SKILLED_TRADE' | 'TITLED_PROFESSIONAL' | 'UNIVERSITY_OR_TECH_STUDENT' | 'BUSINESS_OWNER'"
    )
    goal_mode: bool = Field(default=False, description="True if evaluating a specific target goal, False for pure Mirror mode")
    lang: str = Field(default="EN", description="'EN' | 'ES'")

    # Base demographic parameters
    age: int = 24
    country_code: str = "PE"
    city: str = ""
    occupation: str = ""
    main_goal_1y: Optional[str] = ""
    one_year_goal: Optional[str] = ""
    medium_term_goals: Optional[str] = Field(default="", description="Medium-term goals (2-3 years): e.g. savings buffer, certification, relocation")
    long_term_goals: Optional[str] = Field(default="", description="Long-term aspirational goals (5+ years): e.g. global remote work, financial independence")
    monthly_income: float = 0.0
    monthly_expenses: float = 0.0
    current_savings: float = 0.0
    current_debt: float = 0.0
    currency: str = "PEN"
    sleep_hours: float = 7.0
    work_hours: float = 0.0
    study_or_project_hours: float = 0.0
    screen_time_distraction_hours: float = 0.0
    exercise_days_per_week: float = 0.0
    social_hours: float = 0.0
    person_identifier: Optional[str] = None
    full_name_or_handle: Optional[str] = None
    user_photo_base64: Optional[str] = None

    # 1. Identity for Live Grounding (Optional)
    full_name: Optional[str] = None
    university_or_institution: Optional[str] = None
    current_company_or_org: Optional[str] = None

    # 2. Profile-specific variables
    # Day-to-day
    daily_income_avg: Optional[float] = None
    work_days_per_week: float = 0.0
    daily_expense_avg: Optional[float] = None

    # Rural / Agricultural
    rural_product: Optional[str] = None
    campaign_income_est: Optional[float] = None
    physical_labor_intensity: str = Field(default="MEDIUM", description="'HIGH' | 'MEDIUM' | 'LOW'")

    # Skilled Trade
    trade_modality: str = Field(default="INDEPENDENT", description="'INDEPENDENT' | 'EMPLOYED'")

    # Professional
    contract_type: str = Field(default="PERMANENT", description="'PERMANENT' | 'TEMPORARY'")
    career_or_degree: str = ""
    life_stage: str = Field(
        default="ACTIVE_PROFESSIONAL",
        description="'FINISHING_UNIVERSITY' | 'WORKING_AND_FINISHING_UNI' | 'RECENT_GRADUATE' | 'ACTIVE_PROFESSIONAL' | 'STUDENT_MID_CAREER'"
    )
    months_to_graduation: int = Field(default=0, ge=0, le=72, description="Months remaining to university completion")
    years_of_experience: float = Field(default=1.0, ge=0.0, le=50.0, description="Years of professional or practical experience")
    key_skills: str = Field(default="", description="Core technical competencies and software mastery")
    english_level: str = Field(default="A1_A2", description="'A1_A2' | 'B1_B2' | 'C1_C2'")
    verified_competence_multiplier: float = Field(default=1.0, ge=0.5, le=1.5, description="Audited practical competence multiplier (0.6 to 1.3)")
    daily_caregiving_hours: float = Field(default=0.0, ge=0.0, le=24.0, description="Daily hours dedicated to family or dependent care")

    # Business / Enterprise
    business_type: Optional[str] = None
    monthly_sales_net: Optional[float] = None

    # 3. Target market and local economic context
    work_modality_target: str = Field(default="LOCAL_CITY", description="'LOCAL_CITY' | 'HYBRID_NATIONAL' | 'REMOTE_GLOBAL'")
    target_monthly_salary_1y: float = Field(default=3500.0, ge=0.0, description="1-year target monthly salary in local currency")
    housing_situation: str = Field(default="FAMILY_HOME", description="'FAMILY_HOME' | 'RENTING_INDEPENDENT'")

    # 4. Family and environment
    dependents_count: int = Field(default=0, ge=0, description="Number of financial dependents")
    household_climate: str = Field(default="SUPPORTIVE", description="'SUPPORTIVE' | 'NEUTRAL' | 'STRESSFUL_CONFLICT'")
    relationship_status: str = Field(default="SINGLE_PEACEFUL", description="'SINGLE_PEACEFUL' | 'SUPPORTIVE_PARTNER' | 'UNSTABLE_DRAINING'")
    social_circle_influence: str = Field(default="GROWTH", description="'GROWTH' | 'NEUTRAL' | 'DRAINING_PARTY'")

    # 5. Personality and behavioral habits
    self_description: str = Field(default="", description="Personal narrative describing habits, virtues, and concerns")
    personality_traits: List[str] = Field(default_factory=list, description="Selected traits: 'RESILIENT', 'PROCRASTINATOR', 'ANXIOUS_OVERTHINKER', 'DISCIPLINED', 'IMPULSIVE_SPENDER', 'INTROVERT', 'AMBITIOUS'")

    # 6. Real chat signals extracted from ingested WhatsApp
    chat_sentiment_avg: Optional[float] = Field(default=None, description="Average sentiment score extracted from authentic chats")
    chat_dominant_tag: Optional[str] = Field(default=None, description="'support', 'conflict', 'affection', 'thesis_pressure', 'neutral'")
    chat_median_reply_min: Optional[float] = Field(default=None, description="Median response latency in minutes")
    chat_extracted_summary: Optional[str] = Field(default=None, description="Summary extracted by relational profiler")

    # 7. Situational open questions
    open_family_and_dependents: str = Field(
        default="",
        description="Who do you live with, who depends on you, and how is the home environment?"
    )
    open_relationships_and_friends: str = Field(
        default="",
        description="What is your current relationship status and how do close friends influence your time and finances?"
    )
    open_personality_and_habits: str = Field(
        default="",
        description="How do you describe your character, how do you handle financial stress, and what habit is hardest to control?"
    )

    @model_validator(mode="before")
    @classmethod
    def sync_legacy_and_transition_fields(cls, values: Any) -> Any:
        if isinstance(values, dict):
            fam = values.get("family_and_environment")
            if isinstance(fam, dict):
                values.setdefault("dependents_count", fam.get("dependents_count", 0))
                values.setdefault("household_climate", fam.get("household_climate", "SUPPORTIVE"))
                values.setdefault("relationship_status", fam.get("relationship_status", "SINGLE_PEACEFUL"))
                values.setdefault("social_circle_influence", fam.get("social_circle_influence", "GROWTH"))

            pers = values.get("personality_profile")
            if isinstance(pers, dict):
                values.setdefault("self_description", pers.get("self_description", ""))
                values.setdefault("personality_traits", pers.get("personality_traits", []))

            chat_sig = values.get("ingested_chat_signals")
            if isinstance(chat_sig, dict):
                values.setdefault("chat_sentiment_avg", chat_sig.get("chat_sentiment_avg"))
                values.setdefault("chat_dominant_tag", chat_sig.get("chat_dominant_tag"))
                values.setdefault("chat_median_reply_min", chat_sig.get("chat_median_reply_min"))
                values.setdefault("chat_extracted_summary", chat_sig.get("chat_extracted_summary"))

            profile = values.get("life_profile_type") or "DAY_TO_DAY_WORKER"

            # 1. Monthly income/expense conversions
            if profile == "DAY_TO_DAY_WORKER":
                d_inc = values.get("daily_income_avg")
                w_days = float(values.get("work_days_per_week") or 6.0)
                d_exp = values.get("daily_expense_avg")
                if d_inc is not None and float(d_inc) > 0:
                    values["monthly_income"] = round(float(d_inc) * w_days * 4.333, 2)
                if d_exp is not None and float(d_exp) > 0:
                    values["monthly_expenses"] = round(float(d_exp) * 30.417, 2)

            elif profile == "RURAL_FIELD_PRODUCER":
                c_inc = values.get("campaign_income_est")
                if c_inc is not None and float(c_inc) > 0:
                    values["monthly_income"] = round(float(c_inc) / 5.0, 2)
                prod = values.get("rural_product")
                if prod:
                    values.setdefault("occupation", f"Producer of {prod}")
                    values.setdefault("career_or_degree", f"Producer of {prod}")

            elif profile == "BUSINESS_OWNER":
                sales = values.get("monthly_sales_net")
                if sales is not None and float(sales) > 0:
                    values["monthly_income"] = round(float(sales), 2)
                b_type = values.get("business_type")
                if b_type:
                    values.setdefault("occupation", f"Business owner: {b_type}")
                    values.setdefault("career_or_degree", f"Business owner: {b_type}")

            # 2. Synchronize occupation and degree
            c_degree = values.get("career_or_degree")
            occ = values.get("occupation")
            if c_degree and not occ:
                values["occupation"] = c_degree
            elif occ and not c_degree:
                values["career_or_degree"] = occ

            # 3. Synchronize goal mode
            g_mode = values.get("goal_mode", False)
            goal_1y = values.get("one_year_goal") or values.get("main_goal_1y")
            if not g_mode or not goal_1y or str(goal_1y).strip() == "":
                values["main_goal_1y"] = ""
                values["one_year_goal"] = ""
                values["goal_mode"] = False
            else:
                values["main_goal_1y"] = str(goal_1y).strip()
                values["one_year_goal"] = str(goal_1y).strip()
                values["goal_mode"] = True

            # 4. Synchronize identity
            f_name = values.get("full_name")
            f_handle = values.get("full_name_or_handle")
            p_ident = values.get("person_identifier")
            resolved_name = f_name or f_handle or p_ident
            if resolved_name:
                values.setdefault("full_name", resolved_name)
                values.setdefault("full_name_or_handle", resolved_name)
                values.setdefault("person_identifier", resolved_name)

        return values

    @model_validator(mode="after")
    def sync_after(self) -> "HolisticFutureRequest":
        if self.career_or_degree and not self.occupation:
            self.occupation = self.career_or_degree
        elif self.occupation and not self.career_or_degree:
            self.career_or_degree = self.occupation
        resolved = self.full_name or self.full_name_or_handle or self.person_identifier
        if resolved:
            self.full_name = resolved
            self.full_name_or_handle = resolved
            self.person_identifier = resolved
        return self


class GoalFeasibilityItem(BaseModel):
    horizon_type: str = Field(description="'SHORT_1Y' | 'MEDIUM_3Y' | 'LONG_5Y_IDEAL'")
    horizon_label: str = Field(description="Temporal horizon label")
    goal_statement: str = Field(description="Goal or aspirational milestone statement")
    feasibility_status: str = Field(description="'VIABLE_ON_TRACK' | 'AT_RISK_GAPS' | 'NOT_FEASIBLE_INSUFFICIENT_RESOURCES'")
    feasibility_pct: float = Field(description="Feasibility likelihood from 0.0 to 100.0%")
    required_capital: float = Field(default=0.0, description="Minimum estimated capital in local currency")
    projected_savings_capital: float = Field(default=0.0, description="Projected savings capital from stochastic simulation")
    capital_gap: float = Field(default=0.0, description="Financial capital deficit or surplus")
    prerequisites_met: List[str] = Field(default_factory=list, description="Conditions and credentials already fulfilled")
    prerequisites_missing: List[str] = Field(default_factory=list, description="Missing prerequisites or gatekeeper criteria")
    reality_check_verdict: str = Field(description="Objective, unembellished assessment of feasibility")
    strategic_bridge: str = Field(description="Concrete strategic leverage point to convert goal into reality")


class GoalsVerificationReport(BaseModel):
    short_term_1y: Optional[GoalFeasibilityItem] = None
    medium_term_3y: Optional[GoalFeasibilityItem] = None
    long_term_5y: Optional[GoalFeasibilityItem] = None
    global_synthesis: str = Field(default="", description="Causal synthesis of goals against empirical resources")


class CareerTransitionNode(BaseModel):
    horizon_key: str = Field(description="'1_MONTH' | '6_MONTHS' | '1_YEAR' | '3_YEARS' | '5_YEARS'")
    horizon: str = Field(default="", description="Frontend alias")
    horizon_label: str = Field(description="Horizon label (e.g. 1 Month, 6 Months, 1 Year, 3 Years, 5 Years)")
    months_ahead: int = Field(description="Future timeline distance in months (1, 6, 12, 36, 60)")
    months_from_now: int = Field(default=0, description="Frontend alias")
    p10_stagnation_role: str = Field(description="Role in stagnant / friction scenario (Percentile 10)")
    p10_income: float = Field(description="Monthly income in Percentile 10")
    p50_likely_role: str = Field(description="Most probable cohort role (Percentile 50)")
    p50_income: float = Field(description="Monthly income in Percentile 50")
    p90_accelerated_role: str = Field(description="Accelerated / optimal scenario role (Percentile 90)")
    p90_income: float = Field(description="Monthly income in Percentile 90")
    transition_probability_pct: float = Field(description="Statistical transition probability (0.0 to 100.0%)")
    cohort_rank_descriptor: str = Field(default="", description="Relative competitive cohort positioning")
    key_catalysts: List[str] = Field(default_factory=list, description="Catalyst milestones accelerating advancement")
    required_skills_to_unlock: List[str] = Field(default_factory=list, description="Skills required to unlock progression")
    blockers: List[str] = Field(default_factory=list, description="Frictional blockers locking user into P10")
    key_risk_factor: str = Field(default="", description="Primary risk factor")
    market_demand_alignment: str = Field(default="High", description="Labor market demand alignment")


class ActuarialInsertionPlan(BaseModel):
    estimated_weeks_to_first_contract_p10: int = Field(default=28, description="Weeks to contract in friction scenario (P10)")
    estimated_weeks_to_first_contract_p50: int = Field(default=14, description="Median estimated weeks to contract (P50)")
    estimated_weeks_to_first_contract_p90: int = Field(default=6, description="Weeks to contract in optimal scenario (P90)")
    weeks_to_75pct_probability: int = Field(default=16, description="Week where cumulative survival crosses 75%")
    weekly_hiring_probability_curve: List[float] = Field(default_factory=list, description="52-week cumulative survival curve (Weibull/Cox)")
    exact_net_salary_progression: List[Dict[str, Any]] = Field(default_factory=list, description="Monthly evolution of gross vs net take-home salary")
    cash_flow_monthly_breakdown: Dict[str, float] = Field(default_factory=dict, description="Accounting breakdown: gross, deductions, transport, net disposable")


class StrategicRoadmapPhase(BaseModel):
    phase_key: str = Field(description="Phase identifier: MONTH_1, MONTHS_2_6, YEAR_1, YEARS_3_5")
    phase_label: str = Field(description="Human-readable phase title")
    timeframe: str = Field(description="Exact temporal window (e.g. Days 1 to 30)")
    main_objective: str = Field(description="Primary objective for this roadmap phase")
    target_salary_range: str = Field(description="Target net take-home salary band")
    daily_changes_to_implement: List[str] = Field(default_factory=list, description="Exact daily routine and habit changes")
    strategic_actions_milestones: List[str] = Field(default_factory=list, description="Concrete milestone actions to execute")
    critical_trap_to_avoid: str = Field(description="Critical behavioral trap that causes regression")


class CareerAutocompletionResult(BaseModel):
    cohort_similarity_percentile: float = Field(description="Competitiveness percentile (0 to 100) vs peer cohort")
    cohort_archetype: str = Field(description="Identified cohort archetype")
    cohort_rank_descriptor: str = Field(default="Accelerated / High Performance", description="Human-readable cohort descriptor")
    predicted_career_transitions: List[CareerTransitionNode] = Field(default_factory=list, description="Projected transitions across 1M, 6M, 1Y, 3Y, and 5Y")
    real_job_openings: List[RealJobVacancy] = Field(default_factory=list, description="Real job openings and public tenders with 384d match")
    strategic_roadmap: List[StrategicRoadmapPhase] = Field(default_factory=list, description="Step-by-step roadmap of habits and milestones")
    actuarial_insertion: Optional[ActuarialInsertionPlan] = Field(default=None, description="Weibull/Cox survival model of week-by-week hiring")
    verified_competence_multiplier: float = Field(default=1.0, description="Audited technical competence multiplier (0.6 to 1.3)")
    ai_automation_exposure_pct: float = Field(description="Percentage risk of task automation by AI")
    ai_leverage_potential_pct: float = Field(description="Potential to multiply income by leveraging AI tooling")
    career_bottlenecks: List[str] = Field(default_factory=list, description="Identified bottleneck restricting advancement")
    recommended_skill_acquisitions: List[str] = Field(default_factory=list, description="High-leverage skills to acquire")
    recommended_high_leverage_skills: List[str] = Field(default_factory=list, description="Key accelerator skills")
    top_target_roles_matching: List[str] = Field(default_factory=list, description="Top matching high-demand roles")
    local_market_match_index: float = Field(default=75.0, description="Percentage alignment with target labor market")
    past_events_encoded_count: int = Field(default=0, description="Number of historical events encoded in sequence")
    trajectory_summary: str = Field(default="", description="Descriptive summary of Life2Vec career trajectory")
    trajectory_vector_summary: Optional[str] = Field(default="", description="Latent trajectory vector description")


class HolisticFutureResponse(BaseModel):
    request_meta: Dict[str, Any]
    macro_context: Dict[str, Any]
    live_web_intelligence: Optional[Dict[str, Any]] = None
    live_web_sources: Optional[List[Dict[str, Any]]] = None
    inferred_human_factors: Optional[InferredHumanFactors] = None
    snapshot_1_month: HorizonSnapshot
    snapshot_6_months: HorizonSnapshot
    snapshot_1_year: HorizonSnapshot
    golden_path_adjustments: List[GoldenPathAdjustment]
    executive_summary: str
    goals_verification: Optional[GoalsVerificationReport] = None
    career_autocompletion: Optional[CareerAutocompletionResult] = None
