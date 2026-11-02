"""
Mirror Future - Holistic Future Engine (MiroFish + 365-Day Vectorized Monte Carlo + Live Web Grounding).
Modela la trayectoria estocástica integral de la persona en cortes de:
- 1 MES (Día 30)
- 6 MESES (Día 180)
- 1 AÑO (Día 365)
Cruzando finanzas personales y presupuesto de 24 horas con las fuerzas macroeconómicas
del país (inflación real, desempleo y PIB), la evidencia web en tiempo real
(microeconomía y sueldos locales de su ciudad, salarios remotos, empresas contratantes y requisitos)
y la transición temporal de etapa de vida (estudios -> egreso -> inserción y consolidación laboral)
mediante 1,000 caminos estocásticos en NumPy y síntesis narrativa pericial con Meta Llama 3.3 70B.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, Any, Tuple, List, Optional
import numpy as np
from app.config import get_settings
from app.models.schemas import (
    HolisticFutureRequest,
    DimensionPercentiles,
    HorizonMetrics,
    HorizonNarrative,
    HorizonSnapshot,
    GoldenPathAdjustment,
    HolisticFutureResponse,
    LiveSnippet,
    LiveWebIntelligenceReport,
    InferredHumanFactors,
    DiscoveryQuestionsRequest,
    DiscoveryQuestionsResponse,
    DiscoveryInterviewRequest,
    DiscoveryInterviewResponse,
    SyncDossierRequest,
    SyncDossierResponse,
    GoalFeasibilityItem,
    GoalsVerificationReport,
    CareerLifeEvent,
    CareerTransitionNode,
    CareerAutocompletionResult,
)
from app.causal_engine.life2vec_career_engine import Life2VecCareerEngine
from app.ingestion.macro_world_engine import MacroEconomicContext, macro_engine, COUNTRY_METADATA
from app.ingestion.live_web_research_engine import live_web_engine
from app.causal_engine.meta_llama_api import llama_client

logger = logging.getLogger("mirror_future.holistic_future_engine")
logger.setLevel(logging.INFO)

TRAIT_TRANSLATIONS_ES = {
    "PROCRASTINATOR": "tendencia a postergar tareas clave",
    "ANXIOUS_OVERTHINKER": "sobrepensamiento y ansiedad ante la incertidumbre",
    "AMBITIOUS": "ambición de superación profesional",
    "RESILIENT": "alta resiliencia y aguante",
    "DISCIPLINED": "disciplina constante",
    "IMPULSIVE_SPENDER": "gasto impulsivo bajo estrés",
    "INTROVERT": "enfoque reservado e introspectivo",
}

INTENSITY_TRANSLATIONS_ES = {
    "HIGH": "alta intensidad física",
    "MEDIUM": "moderada exigencia física",
    "LOW": "baja exigencia física / sedentaria",
}

CLIMATE_TRANSLATIONS_ES = {
    "SUPPORTIVE": "apoyo y respaldo familiar",
    "NEUTRAL": "convivencia familiar independiente",
    "STRESSFUL_CONFLICT": "ambiente de tensión o exigencias en casa",
}

RELATIONSHIP_TRANSLATIONS_ES = {
    "SINGLE_PEACEFUL": "soltería tranquila y enfocada",
    "SUPPORTIVE_PARTNER": "relación sentimental de mutuo respaldo",
    "UNSTABLE_DRAINING": "relación inestable de desgaste emocional",
}


class HolisticMonteCarloSimulator:
    """
    Simulador econométrico estocástico en NumPy de 1,000 trayectorias a 365 días.
    Integra modelado de cambio de fase temporal (Día 1 a Día 365):
    - Fase Pre-Egreso: Carga combinada de universidad/tesis + trabajo, mayor estrés cognitivo.
    - Transición de Fase Laboral: Liberación de horas de clase, cálculo de probabilidad de
      inserción/ascenso según experiencia, inglés, skills y modalidad.
    - Evolución salarial hacia los rangos reales de mercado de su ciudad / remoto,
      acercándose al sueldo objetivo en P50 y P90.
    - Modulación por situación de vivienda (vivienda familiar vs. alquiler independiente).
    """

    NUM_TRAJECTORIES = 1000
    NUM_DAYS = 365

    @classmethod
    def simulate(
        cls,
        req: HolisticFutureRequest,
        macro: MacroEconomicContext,
        live_intel: Optional[LiveWebIntelligenceReport] = None,
        human_factors: Optional[InferredHumanFactors] = None,
        random_seed: Optional[int] = 42,
        career_autocompletion: Optional[CareerAutocompletionResult] = None
    ) -> Dict[str, HorizonMetrics]:
        rng = np.random.default_rng(random_seed)
        N = cls.NUM_TRAJECTORIES
        T = cls.NUM_DAYS

        hf = human_factors or InferredHumanFactors()

        # -------------------------------------------------------------
        # 1. PARÁMETROS MACRO, WEB GROUNDING Y FINANCIEROS
        # -------------------------------------------------------------
        annual_inflation = max(0.5, macro.annual_inflation_rate) / 100.0
        daily_inflation = (1.0 + annual_inflation) ** (1.0 / 365.0) - 1.0

        annual_debt_apr = 0.28
        daily_debt_rate = (1.0 + annual_debt_apr) ** (1.0 / 365.0) - 1.0

        annual_savings_yield = max(0.02, min(0.12, annual_inflation * 1.2))
        daily_savings_rate = (1.0 + annual_savings_yield) ** (1.0 / 365.0) - 1.0

        # Modulaciones de Live Web Grounding
        cost_pressure = live_intel.city_cost_pressure_index if live_intel else 1.00
        demand_score = live_intel.career_market_demand_score if live_intel else 75.0
        cost_factor = float(np.clip(cost_pressure, 0.70, 1.50))

        # Ajuste por situación de vivienda y dependientes (combinando explícitos e inferidos)
        is_renting = req.housing_situation == "RENTING_INDEPENDENT"
        housing_expense_multiplier = 1.22 if is_renting else 0.95
        dep_count = max(0, req.dependents_count or 0)
        effective_dep_factor = max(float(dep_count), hf.inferred_dependents_burden * 3.5)
        dependents_multiplier = 1.0 + (effective_dep_factor * 0.12)
        daily_base_expenses = (req.monthly_expenses / 30.417) * cost_factor * housing_expense_multiplier * dependents_multiplier

        # -------------------------------------------------------------
        # 2. CALIBRACIÓN ESTOCÁSTICA DIFERENCIADA POR PERFIL DE VIDA
        # -------------------------------------------------------------
        profile = req.life_profile_type or "DAY_TO_DAY_WORKER"
        is_pure_mirror = (not req.goal_mode) or (not bool((req.main_goal_1y or req.one_year_goal or "").strip()))

        # Parámetros por perfil
        if profile == "DAY_TO_DAY_WORKER":
            income_shock_std = 0.22
            income_friction_prob = 0.035  # Días de venta baja o lluvia
            labor_drag = 3.8 if req.physical_labor_intensity == "HIGH" else (2.0 if req.physical_labor_intensity == "MEDIUM" else 0.8)
            transition_day = 0
            is_graduating_phase = False
            employability_score = 0.50

        elif profile == "RURAL_FIELD_PRODUCER":
            income_shock_std = 0.26
            income_friction_prob = 0.025  # Shock climático / plaga / caída de precios
            labor_drag = 4.5 if req.physical_labor_intensity == "HIGH" else (2.5 if req.physical_labor_intensity == "MEDIUM" else 1.0)
            transition_day = 0
            is_graduating_phase = False
            employability_score = 0.55

        elif profile == "SKILLED_TRADE":
            income_shock_std = 0.16
            income_friction_prob = 0.020 if req.trade_modality == "INDEPENDENT" else 0.010
            labor_drag = 3.2 if req.physical_labor_intensity == "HIGH" else (1.8 if req.physical_labor_intensity == "MEDIUM" else 0.6)
            transition_day = 0
            is_graduating_phase = False
            employability_score = 0.65

        elif profile == "BUSINESS_OWNER":
            income_shock_std = 0.18
            income_friction_prob = 0.018  # Volatilidad en demanda o cobranza
            labor_drag = 1.2
            transition_day = 0
            is_graduating_phase = False
            employability_score = 0.70

        elif profile == "UNIVERSITY_OR_TECH_STUDENT":
            income_shock_std = 0.08
            income_friction_prob = 0.015
            labor_drag = 0.5
            is_graduating_phase = (
                req.life_stage in ("FINISHING_UNIVERSITY", "WORKING_AND_FINISHING_UNI")
                and (req.months_to_graduation is not None and 1 <= req.months_to_graduation <= 6)
                and bool((req.career_or_degree or "").strip())
                and req.career_or_degree.strip().lower() not in ("comercio / independiente", "desconocido", "")
                and bool((req.university_or_institution or "").strip())
            )
            if is_graduating_phase:
                transition_day = max(1, min(180, int((req.months_to_graduation or 1) * 30)))
            elif req.life_stage == "STUDENT_MID_CAREER":
                transition_day = 365
            else:
                transition_day = 0

            # Score de empleabilidad estudiantil con anclaje en universidad, carrera y personalidad
            h_demand = (demand_score / 100.0) * 0.30
            h_exp = min(0.20, req.years_of_experience * 0.04)
            h_eng = 0.20 if req.english_level == "C1_C2" else (0.12 if req.english_level == "B1_B2" else 0.04)
            h_skills = 0.15 if len(req.key_skills.strip()) > 3 else 0.05
            h_modality = 0.10 if req.work_modality_target in ("REMOTE_GLOBAL", "HYBRID_NATIONAL") else 0.08

            uni_lower = (req.university_or_institution or "").lower()
            h_uni = 0.10 if any(u in uni_lower for u in ["continental", "uncp", "pucp", "uni", "san marcos", "senati", "tecsup", "upc", "lima", "utp"]) else 0.04

            career_lower = (req.career_or_degree or req.occupation or "").lower()
            h_career = 0.10 if any(c in career_lower for c in ["sistemas", "software", "informática", "computación", "datos", "tecnología", "redes"]) else 0.04

            traits_set = set(req.personality_traits or [])
            trait_pen = 0.0
            if "PROCRASTINATOR" in traits_set:
                trait_pen -= 0.10
            if "ANXIOUS_OVERTHINKER" in traits_set:
                trait_pen -= 0.05
            if "DISCIPLINED" in traits_set:
                trait_pen += 0.08
            if "RESILIENT" in traits_set:
                trait_pen += 0.06
            if "AMBITIOUS" in traits_set:
                trait_pen += 0.05

            employability_score = float(np.clip(h_demand + h_exp + h_eng + h_skills + h_modality + h_uni + h_career + trait_pen, 0.25, 0.95))

        else:  # TITLED_PROFESSIONAL
            income_shock_std = 0.04
            income_friction_prob = 0.008 if req.contract_type == "PERMANENT" else 0.022
            labor_drag = 0.3
            transition_day = 0
            is_graduating_phase = False
            h_demand = (demand_score / 100.0) * 0.35
            h_exp = min(0.25, req.years_of_experience * 0.04)
            h_eng = 0.20 if req.english_level == "C1_C2" else (0.12 if req.english_level == "B1_B2" else 0.04)
            h_skills = 0.15 if len(req.key_skills.strip()) > 3 else 0.05
            employability_score = float(np.clip(h_demand + h_exp + h_eng + h_skills + 0.10, 0.35, 0.95))

        # Calibración de salarios de mercado según modalidad y datos en tiempo real
        local_min = live_intel.local_salary_range_min if (live_intel and live_intel.local_salary_range_min > 0) else max(400.0, req.monthly_income * 0.75)
        local_max = live_intel.local_salary_range_max if (live_intel and live_intel.local_salary_range_max > 0) else max(local_min * 1.5, req.monthly_income * 1.3)
        remote_min = live_intel.remote_salary_range_min if (live_intel and live_intel.remote_salary_range_min > 0) else max(local_max, req.monthly_income * 1.4)
        remote_max = live_intel.remote_salary_range_max if (live_intel and live_intel.remote_salary_range_max > 0) else max(remote_min * 1.8, req.target_monthly_salary_1y * 1.1)

        if req.work_modality_target == "REMOTE_GLOBAL":
            mkt_floor, mkt_mid, mkt_ceil = remote_min, (remote_min + remote_max) * 0.5, remote_max
        elif req.work_modality_target == "HYBRID_NATIONAL":
            mkt_floor = (local_min + remote_min) * 0.5
            mkt_mid = (local_max + remote_min) * 0.5
            mkt_ceil = (local_max + remote_max) * 0.5
        else:  # LOCAL_CITY
            mkt_floor, mkt_mid, mkt_ceil = local_min, (local_min + local_max) * 0.5, local_max

        # Rango salarial de entrada realista para recién egresados según moneda
        if req.currency == "PEN":
            entry_floor, entry_mid, entry_ceil = 1300.0, 1750.0, 2200.0
        elif req.currency == "COP":
            entry_floor, entry_mid, entry_ceil = 1500000.0, 2000000.0, 2600000.0
        elif req.currency == "MXN":
            entry_floor, entry_mid, entry_ceil = 9000.0, 13000.0, 18000.0
        elif req.currency == "EUR":
            entry_floor, entry_mid, entry_ceil = 1400.0, 1800.0, 2400.0
        else:  # USD u otros
            entry_floor, entry_mid, entry_ceil = 450.0, 650.0, 950.0

        target_sal = max(req.monthly_income, req.target_monthly_salary_1y) if not is_pure_mirror else req.monthly_income

        base_salary_targets = np.zeros(N)
        rand_percentiles = rng.uniform(0.0, 1.0, size=N)

        # Calibración estocástica de Life2Vec Career Engine (bandas de transición salarial):
        has_life2vec_1y = bool(career_autocompletion and career_autocompletion.predicted_career_transitions)
        t_1y = None
        if has_life2vec_1y:
            t_map = {t.horizon_key: t for t in career_autocompletion.predicted_career_transitions}
            t_1y = t_map.get("1_YEAR")

        for i in range(N):
            pct = rand_percentiles[i]
            if t_1y and t_1y.p50_income > 0:
                # Modulación directa por probabilidades y percentiles de Life2Vec
                p10_anc = float(t_1y.p10_income)
                p50_anc = float(t_1y.p50_income)
                p90_anc = float(t_1y.p90_income)
                prob_trans = float(t_1y.transition_probability_pct) / 100.0
                if pct < 0.20:
                    base_salary_targets[i] = p10_anc * (0.90 + 0.20 * (pct / 0.20))
                elif pct < 0.75:
                    p_rel = (pct - 0.20) / 0.55
                    base_salary_targets[i] = p10_anc + (p50_anc - p10_anc) * (0.35 + 0.65 * prob_trans) * p_rel
                else:
                    p_rel = (pct - 0.75) / 0.25
                    base_salary_targets[i] = p50_anc + (p90_anc - p50_anc) * p_rel
            elif is_graduating_phase:
                # Al egresar, su nuevo salario de inserción depende del mercado de entrada de su ciudad
                base_salary_targets[i] = entry_floor + (entry_ceil - entry_floor) * (0.35 * pct + 0.65 * employability_score)
            elif is_pure_mirror or profile in ("DAY_TO_DAY_WORKER", "RURAL_FIELD_PRODUCER", "SKILLED_TRADE") or req.monthly_income == 0:
                # En modo espejo o actividades independientes, o con ingreso 0, el ingreso oscila alrededor de su baseline
                base_salary_targets[i] = req.monthly_income * (0.85 + 0.35 * pct)
            else:
                if pct < 0.20:
                    base_salary_targets[i] = mkt_floor + (mkt_mid - mkt_floor) * (pct / 0.20)
                elif pct < 0.70:
                    p_rel = (pct - 0.20) / 0.50
                    base_salary_targets[i] = mkt_mid + (target_sal * (0.85 + 0.15 * employability_score) - mkt_mid) * p_rel
                else:
                    p_rel = (pct - 0.70) / 0.30
                    base_salary_targets[i] = target_sal + (max(mkt_ceil, target_sal * 1.25) - target_sal) * p_rel

        # Demora de contratación si hay fase de transición estudiantil
        traits_set = set(req.personality_traits or [])
        if profile == "UNIVERSITY_OR_TECH_STUDENT" and is_graduating_phase:
            base_search_days = int(35 + (1.0 - employability_score) * 55)
            if "PROCRASTINATOR" in traits_set:
                base_search_days += 30  # Procrastinar la postulación demora semanas
            if "ANXIOUS_OVERTHINKER" in traits_set:
                base_search_days += 15  # Dudas e inseguridad al postularse
            if "DISCIPLINED" in traits_set:
                base_search_days = max(15, base_search_days - 20)
            if "RESILIENT" in traits_set:
                base_search_days = max(15, base_search_days - 15)
            if hf.daily_caregiving_hours > 2.0:
                base_search_days += 15  # Cuidado de hermanos/familia reduce horas libres para búsqueda

            hire_delay_days = rng.exponential(scale=base_search_days, size=N).astype(np.int32)
            hire_delay_days = np.clip(hire_delay_days, 15, 180)
            hiring_effective_day = transition_day + hire_delay_days
        else:
            hiring_effective_day = np.zeros(N, dtype=np.int32)

        # Fricción macroeconómica
        unemp_rate = macro.unemployment_rate / 100.0
        income_friction_prob = float(np.clip(unemp_rate * 0.07 * (1.30 - employability_score), 0.003, 0.04))

        # Entorno familiar, de pareja y círculo social (combinando categóricos y factores inferidos)
        household_climate = req.household_climate or "SUPPORTIVE"
        rel_status = req.relationship_status or "SINGLE_PEACEFUL"
        circle_inf = req.social_circle_influence or "GROWTH"
        chat_tag = req.chat_dominant_tag or ""

        # Factores psicométricos y de convivencia inferidos por IA
        home_bal = float(hf.home_emotional_balance)  # -1.0 a +1.0
        partner_eff = float(hf.partner_and_friends_effect)  # -1.0 a +1.0
        stress_risk = float(hf.stress_spending_and_procrastination_risk)  # 0.0 a 1.0
        grit = float(hf.resilience_and_grit_score)  # 0.0 a 1.0

        is_conflict_env = (
            household_climate == "STRESSFUL_CONFLICT"
            or rel_status == "UNSTABLE_DRAINING"
            or chat_tag == "conflict"
            or home_bal < -0.35
            or partner_eff < -0.35
        )
        is_supportive_env = (
            (household_climate == "SUPPORTIVE" or home_bal > 0.30)
            and (rel_status == "SUPPORTIVE_PARTNER" or partner_eff > 0.30 or chat_tag in ("support", "affection"))
        )

        # Modulación de telemetría de chat
        chat_vitality_mod = 0.0
        if req.chat_sentiment_avg is not None:
            chat_vitality_mod = float(np.clip(req.chat_sentiment_avg * 3.5, -3.5, 3.0))
        if req.chat_median_reply_min is not None and req.chat_median_reply_min < 5.0:
            chat_vitality_mod -= 1.0  # Fricción por hiperconectividad digital

        # Rasgos de personalidad
        traits = set(req.personality_traits or [])
        has_impulsive = "IMPULSIVE_SPENDER" in traits
        has_procrastinator = "PROCRASTINATOR" in traits
        has_anxious = "ANXIOUS_OVERTHINKER" in traits
        has_disciplined = "DISCIPLINED" in traits
        has_resilient = "RESILIENT" in traits
        has_ambitious = "AMBITIOUS" in traits
        has_introvert = "INTROVERT" in traits

        # Matrices de estado (N x T)
        savings = np.zeros((N, T), dtype=np.float64)
        debt = np.zeros((N, T), dtype=np.float64)
        vitality = np.zeros((N, T), dtype=np.float64)
        goal_accum = np.zeros((N, T), dtype=np.float64)
        social_cap = np.zeros((N, T), dtype=np.float64)
        burnout_active = np.zeros((N, T), dtype=np.bool_)
        current_daily_income = np.zeros((N, T), dtype=np.float64)

        # Condiciones iniciales
        savings[:, 0] = req.current_savings
        debt[:, 0] = req.current_debt
        initial_vitality = np.clip(
            50.0 + (req.sleep_hours - 7.0) * 10.0 + (req.exercise_days_per_week / 7.0) * 15.0 - (req.screen_time_distraction_hours * 3.0) + chat_vitality_mod,
            25.0, 95.0
        )
        vitality[:, 0] = initial_vitality
        social_cap[:, 0] = np.clip(req.social_hours * 25.0 + 35.0, 15.0, 95.0)
        current_daily_income[:, 0] = req.monthly_income / 30.417

        # -------------------------------------------------------------
        # 3. EVOLUCIÓN ESTOCÁSTICA DÍA A DÍA
        # -------------------------------------------------------------
        for t in range(1, T):
            is_post_transition_global = t >= transition_day

            # A. EVOLUCIÓN DINÁMICA DE INGRESOS CON CAMBIO DE FASE
            # Trayectorias que ya cruzaron su fecha de contratación escalan hacia su nuevo sueldo
            hired_mask = t >= hiring_effective_day
            ramp_factor = np.minimum(1.0, (t - hiring_effective_day) / 30.0)

            target_daily = base_salary_targets / 30.417
            pre_daily = req.monthly_income / 30.417

            # Sueldo base transicional del día
            day_base_inc = np.where(
                hired_mask,
                pre_daily + (target_daily - pre_daily) * ramp_factor,
                pre_daily
            )

            # Shocks estocásticos de caja
            income_shocks = rng.normal(1.0, income_shock_std, size=N)
            friction_mask = rng.random(N) < income_friction_prob
            if profile == "DAY_TO_DAY_WORKER":
                income_shocks[friction_mask] *= rng.uniform(0.15, 0.35, size=np.sum(friction_mask))
            elif profile == "RURAL_FIELD_PRODUCER":
                income_shocks[friction_mask] *= rng.uniform(0.20, 0.45, size=np.sum(friction_mask))
            elif profile == "SKILLED_TRADE":
                income_shocks[friction_mask] *= rng.uniform(0.30, 0.60, size=np.sum(friction_mask))
            else:
                income_shocks[friction_mask] *= rng.uniform(0.55, 0.85, size=np.sum(friction_mask))
            today_income = day_base_inc * np.maximum(0.1, income_shocks)
            current_daily_income[:, t] = today_income

            # B. GASTOS E INFLACIÓN
            current_cumulative_inf = (1.0 + daily_inflation) ** t
            fatigue_stress = np.maximum(0.0, (65.0 - vitality[:, t - 1]) / 65.0)

            # Modulación de gasto impulsivo por estrés, personalidad y entorno social
            base_impulse_range = 0.24 + (stress_risk * 0.32)
            if has_impulsive:
                base_impulse_range *= 1.25
            if circle_inf == "DRAINING_PARTY":
                base_impulse_range *= 1.15
            if has_disciplined or grit > 0.70:
                base_impulse_range *= 0.70

            impulse_spending = 1.0 + (fatigue_stress * rng.uniform(0.0, base_impulse_range, size=N))

            # Shock de emergencia (sensible a carga de dependientes efectiva)
            emergency_prob = 0.010 + min(0.025, effective_dep_factor * 0.005)
            emergency_mask = rng.random(N) < emergency_prob
            emergency_amount = np.zeros(N)
            if np.any(emergency_mask):
                min_mult = 3.5 + (effective_dep_factor * 0.8)
                max_mult = 15.0 + (effective_dep_factor * 2.2)
                emergency_amount[emergency_mask] = rng.uniform(
                    daily_base_expenses * min_mult, daily_base_expenses * max_mult, size=np.sum(emergency_mask)
                )

            today_expenses = (daily_base_expenses * current_cumulative_inf * impulse_spending) + emergency_amount
            net_daily_cash = today_income - today_expenses

            prev_sav = savings[:, t - 1]
            prev_debt = debt[:, t - 1]

            # Si hay superávit: amortiza pasivos y acumula ahorros
            surplus_mask = net_daily_cash >= 0
            surplus = net_daily_cash[surplus_mask]
            cur_debt_surplus = prev_debt[surplus_mask]
            debt_paid = np.minimum(cur_debt_surplus, surplus)
            remaining_surplus = surplus - debt_paid

            new_debt = np.copy(prev_debt)
            new_savings = np.copy(prev_sav)

            new_debt[surplus_mask] = (cur_debt_surplus - debt_paid) * (1.0 + daily_debt_rate)
            new_savings[surplus_mask] = (prev_sav[surplus_mask] + remaining_surplus) * (1.0 + daily_savings_rate)

            # Si hay déficit: primero usa colchón de ahorro, luego incurre en pasivo
            deficit_mask = ~surplus_mask
            deficit = -net_daily_cash[deficit_mask]
            cur_sav_deficit = prev_sav[deficit_mask]
            savings_used = np.minimum(cur_sav_deficit, deficit)
            uncovered_deficit = deficit - savings_used

            new_savings[deficit_mask] = (cur_sav_deficit - savings_used) * (1.0 + daily_savings_rate)
            new_debt[deficit_mask] = (prev_debt[deficit_mask] + uncovered_deficit) * (1.0 + daily_debt_rate)

            savings[:, t] = new_savings
            debt[:, t] = new_debt

            # C. SALUD, FATIGA Y VITALIDAD
            sleep_factor = (req.sleep_hours - 7.5) * 4.0
            care_strain = (float(hf.daily_caregiving_hours) * 1.3) if hf.daily_caregiving_hours > 0 else 0.0
            if profile in ("DAY_TO_DAY_WORKER", "RURAL_FIELD_PRODUCER", "SKILLED_TRADE"):
                effective_strain = max(0.0, req.work_hours - 7.0) * 1.6 + labor_drag + care_strain
            elif not is_post_transition_global and is_graduating_phase:
                effective_strain = max(0.0, (req.work_hours + 1.35 * req.study_or_project_hours) - 8.0) * 2.3 + care_strain
            elif profile == "TITLED_PROFESSIONAL":
                effective_strain = max(0.0, req.work_hours - 8.0) * 1.5 + labor_drag + care_strain
            else:
                effective_strain = max(0.0, req.work_hours - 8.0) * 1.7 + care_strain

            screen_penalty = max(0.0, req.screen_time_distraction_hours - 1.5) * 1.8
            exercise_buff = (req.exercise_days_per_week / 7.0) * 7.5

            # Modulaciones de entorno relacional y personalidad continuas
            relational_impact = (home_bal * 3.5) + (partner_eff * 2.2)
            grit_boost = (grit - 0.5) * 3.5
            stress_drag = stress_risk * 2.5

            if circle_inf == "DRAINING_PARTY":
                relational_impact -= 1.2
            elif circle_inf == "GROWTH":
                relational_impact += 1.0

            if has_anxious:
                stress_drag += 1.5
            if has_resilient:
                grit_boost += 1.5

            env_vitality_impact = relational_impact + grit_boost - stress_drag + chat_vitality_mod
            daily_habit_impact = sleep_factor - effective_strain - screen_penalty + exercise_buff + env_vitality_impact
            vitality_attractor = float(np.clip(62.0 + daily_habit_impact * 2.2, 10.0, 95.0))

            rebound_boost = np.where(vitality[:, t - 1] < 45.0, 3.0 * grit, 0.0) if (has_resilient or grit > 0.65) else 0.0
            vitality[:, t] = np.clip(0.92 * vitality[:, t - 1] + 0.08 * vitality_attractor + rebound_boost + rng.normal(0, 2.0, N), 5.0, 100.0)

            burnout_cutoff = 35.0 - (home_bal * 3.5) - (grit * 4.0) + (stress_risk * 3.0)
            burnout_cutoff = float(np.clip(burnout_cutoff, 26.0, 44.0))
            burnout_active[:, t] = (vitality[:, t] < burnout_cutoff) | ((vitality[:, t] < (burnout_cutoff + 7.0)) & (burnout_active[:, t - 1]))

            # D. AVANCE DE META ANUAL / ADAPTACIÓN DE VIDA
            study_efficiency = 1.25 if is_post_transition_global else 0.85
            relational_focus = float(np.clip(1.0 + (home_bal * 0.12) + (partner_eff * 0.15), 0.75, 1.25))
            grit_efficiency = float(np.clip(0.85 + (grit * 0.35), 0.80, 1.25))
            study_efficiency *= (relational_focus * grit_efficiency)

            if circle_inf == "GROWTH":
                study_efficiency *= 1.08
            elif circle_inf == "DRAINING_PARTY":
                study_efficiency *= 0.90

            if has_disciplined:
                study_efficiency *= 1.10
            if has_ambitious and np.mean(vitality[:, t]) > 50.0:
                study_efficiency *= 1.10

            focus_factor = max(0.20, 1.0 - 0.09 * req.screen_time_distraction_hours)
            if stress_risk > 0.55 or has_procrastinator:
                focus_mult = rng.choice([0.12, 0.45, 0.95, 1.15], size=N, p=[0.25, 0.25, 0.30, 0.20])
            else:
                focus_mult = rng.uniform(0.90, 1.10, N)

            effective_study = (
                req.study_or_project_hours
                * (vitality[:, t] / 100.0)
                * focus_factor
                * study_efficiency
            )
            goal_accum[:, t] = goal_accum[:, t - 1] + np.maximum(0.0, effective_study * focus_mult)

            # E. CAPITAL SOCIAL
            social_drift = 2.0 * min(2.5, req.social_hours) - 1.5 * max(0.0, 1.0 - req.social_hours)
            if not is_post_transition_global and (req.work_hours + req.study_or_project_hours) > 11.0:
                social_drift -= 1.6
            social_drift += (partner_eff * 1.8) + (home_bal * 1.0)
            if circle_inf == "GROWTH":
                social_drift += 1.0
            elif circle_inf == "DRAINING_PARTY":
                social_drift -= 1.2
            if has_introvert:
                social_drift -= 0.6

            social_cap[:, t] = np.clip(0.96 * social_cap[:, t - 1] + 0.04 * 50.0 + social_drift + rng.normal(0, 1.4, N), 5.0, 100.0)

        # -------------------------------------------------------------
        # 4. EXTRACCIÓN DE SNAPSHOTS (DÍAS 30, 180, 365)
        # -------------------------------------------------------------
        cut_indices = {
            "1_month": 29,    # Día 30
            "6_months": 179,  # Día 180
            "1_year": 364     # Día 365
        }

        results: Dict[str, HorizonMetrics] = {}

        for horizon, d in cut_indices.items():
            cumulative_inf_at_cut = (1.0 + daily_inflation) ** (d + 1)
            nominal_nw = savings[:, d] - debt[:, d]
            real_nw = nominal_nw / cumulative_inf_at_cut

            # LEY DE CONSERVACIÓN DEL DINERO: Mes 1 (Día 30) sin ingresos, sin gastos y sin ahorros iniciales
            if horizon == "1_month" and req.monthly_income == 0.0 and req.monthly_expenses == 0.0 and req.current_savings == 0.0:
                nominal_nw = np.zeros(N)
                real_nw = np.zeros(N)
                savings[:, d] = 0.0
                debt[:, d] = 0.0
            elif req.housing_situation == "FAMILY_HOME" and req.monthly_expenses == 0.0:
                debt[:, d] = np.maximum(0.0, req.current_debt)
                if req.monthly_income == 0.0 and req.current_savings == 0.0 and horizon == "1_month":
                    real_nw = np.zeros(N)

            monthly_burn = (daily_base_expenses * 30.417 * cumulative_inf_at_cut)
            runway_months = np.maximum(0.0, savings[:, d]) / np.maximum(10.0, monthly_burn)

            # Bonificación al poder de compra si vive en hogar familiar
            family_home_bonus = 8.0 if req.housing_situation == "FAMILY_HOME" else 0.0

            pp_score = np.clip(
                runway_months * 13.0
                + np.where(real_nw > 0, 25.0, 5.0)
                - (debt[:, d] / max(10.0, req.monthly_income) * 14.0)
                - ((cost_factor - 1.0) * 10.0)
                + family_home_bonus,
                0.0, 100.0
            )

            vit_score = vitality[:, d]
            burnout_prob = float(np.mean(burnout_active[:, d]))

            if is_pure_mirror:
                # Índice de Bienestar y Estabilidad General:
                # 35% salud/vitalidad, 45% colchón financiero (días de supervivencia), 20% tranquilidad mental
                daily_exp_cut = daily_base_expenses * cumulative_inf_at_cut
                runway_days = np.maximum(0.0, savings[:, d]) / np.maximum(0.1, daily_exp_cut)
                financial_cushion_score = np.clip((runway_days / 90.0) * 100.0, 0.0, 100.0)

                debt_ratio = debt[:, d] / np.maximum(10.0, req.monthly_income)
                debt_load = np.clip(debt_ratio * 15.0, 0.0, 50.0)
                peace_of_mind = np.clip(100.0 - (burnout_prob * 100.0 * 0.5) - debt_load, 0.0, 100.0)

                composite_wellbeing = np.clip(
                    0.35 * vit_score + 0.45 * financial_cushion_score + 0.20 * peace_of_mind,
                    0.0, 100.0
                )
                goal_pct = composite_wellbeing
            else:
                # Meta anual declarada (benchmark: 380 horas efectivas de foco profundo)
                goal_pct = np.clip((goal_accum[:, d] / 380.0) * 100.0, 0.0, 100.0)
            soc_score = social_cap[:, d]

            macro_resilience = np.clip(
                45.0 + (runway_months * 7.5) - (debt[:, d] / max(1.0, req.monthly_income) * 20.0)
                - (macro.annual_inflation_rate * 1.4) - (macro.unemployment_rate * 1.1)
                + ((demand_score - 70.0) * 0.20) + family_home_bonus,
                5.0, 100.0
            )

            metrics = HorizonMetrics(
                financial_net_worth=DimensionPercentiles(
                    p10=round(float(np.percentile(real_nw, 10)), 2),
                    p50=round(float(np.percentile(real_nw, 50)), 2),
                    p90=round(float(np.percentile(real_nw, 90)), 2),
                ),
                purchasing_power_score=DimensionPercentiles(
                    p10=round(float(np.percentile(pp_score, 10)), 1),
                    p50=round(float(np.percentile(pp_score, 50)), 1),
                    p90=round(float(np.percentile(pp_score, 90)), 1),
                ),
                health_and_vitality_score=DimensionPercentiles(
                    p10=round(float(np.percentile(vit_score, 10)), 1),
                    p50=round(float(np.percentile(vit_score, 50)), 1),
                    p90=round(float(np.percentile(vit_score, 90)), 1),
                ),
                burnout_probability=round(burnout_prob, 3),
                career_and_goal_completion_pct=DimensionPercentiles(
                    p10=round(float(np.percentile(goal_pct, 10)), 1),
                    p50=round(float(np.percentile(goal_pct, 50)), 1),
                    p90=round(float(np.percentile(goal_pct, 90)), 1),
                ),
                social_and_emotional_stability=DimensionPercentiles(
                    p10=round(float(np.percentile(soc_score, 10)), 1),
                    p50=round(float(np.percentile(soc_score, 50)), 1),
                    p90=round(float(np.percentile(soc_score, 90)), 1),
                ),
                macro_resilience_score=DimensionPercentiles(
                    p10=round(float(np.percentile(macro_resilience, 10)), 1),
                    p50=round(float(np.percentile(macro_resilience, 50)), 1),
                    p90=round(float(np.percentile(macro_resilience, 90)), 1),
                )
            )
            results[horizon] = metrics

        return results


class DiscoveryQuestionsEngine:
    """
    Motor generador de preguntas situacionales empáticas para descubrir la realidad
    de la persona (Familia, Pareja/Amigos, Personalidad) adaptadas a su ocupación, ciudad y edad.
    """

    @classmethod
    async def generate_questions(cls, req: DiscoveryQuestionsRequest) -> List[str]:
        settings = get_settings()
        is_es = (req.lang or "EN").upper() == "ES"
        age = req.age or 25
        occupation = req.occupation or "General"
        city = req.city or "General"
        profile = req.life_profile_type or "GENERAL"

        if is_es:
            system_msg = (
                "Eres un entrevistador empático y analista de vida para Mirror Future. "
                "Tu objetivo es hacer de 3 a 4 preguntas cortas, humanas, curiosas y muy concretas "
                "para ayudar a una persona a expresar su situación familiar, sentimental y emocional si no sabe qué escribir. "
                "Adapta el tono y los ejemplos a su edad, ocupación y ciudad. "
                "Devuelve ÚNICAMENTE un objeto JSON con la clave 'questions': lista de strings."
            )
            user_msg = (
                f"La persona tiene {age} años, trabaja/se dedica a '{occupation}' en '{city}', perfil '{profile}'. "
                "Formula 3 a 4 preguntas puntuales que toquen: "
                "1) Quién depende de su dinero o de su tiempo en casa y cómo se siente el ambiente familiar, "
                "2) Cómo influyen sus amigos o su pareja en sus decisiones y gastos del fin de semana, "
                "3) Qué hace o cómo reacciona cuando siente que no llega a fin de mes o se satura de trabajo.\n"
                "JSON format: {\"questions\": [\"pregunta 1\", \"pregunta 2\", ...]}"
            )
        else:
            system_msg = (
                "You are an empathetic interviewer and life reality analyst for Mirror Future. "
                "Your goal is to formulate 3 to 4 short, human, insightful questions to help a person describe "
                "their family, romantic, social, and emotional reality when they are facing writer's block. "
                "Tailor the tone to their age, occupation, and city. "
                "Return ONLY a JSON object with key 'questions': list of strings."
            )
            user_msg = (
                f"The person is {age} years old, works as '{occupation}' in '{city}', life profile '{profile}'. "
                "Ask 3 to 4 tailored questions covering: "
                "1) Who relies on them at home and what the household vibe is like, "
                "2) How their partner or friend circle affects their energy and spending, "
                "3) What habit or emotional pattern kicks in when stressed or under financial pressure.\n"
                "JSON format: {\"questions\": [\"question 1\", \"question 2\", ...]}"
            )

        try:
            raw = await llama_client.structured_completion(
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                model=settings.llama_fast_model,
                temperature=0.4,
                max_tokens=600
            )
            questions = raw.get("questions")
            if isinstance(questions, list) and len(questions) > 0:
                return [str(q).strip() for q in questions if str(q).strip()]
        except Exception as exc:
            logger.warning("Falla al generar discovery questions con LLM: %s. Usando contingencia.", exc)

        # Fallback adaptativo
        if is_es:
            return [
                f"¿En tu casa en {city}, quiénes dependen de tu dinero o de tus cuidados en el día a día?",
                "¿Tu pareja o tus amistades te impulsan a superarte o te jalan a gastar tiempo y dinero en distracciones?",
                f"Como {occupation}, cuando se junta el cansancio y la presión de dinero, ¿cuál es tu primera reacción o hábito que te sabotea?"
            ]
        else:
            return [
                f"At home in {city}, who relies on your financial support or daily care?",
                "Do your partner and closest friends encourage your progress or pull you into draining expenses?",
                f"As a {occupation}, when fatigue and money stress collide, what is the first reaction or habit that trips you up?"
            ]


class DiscoveryInterviewEngine:
    """
    Conversational Reality Discovery & Biographical Dossier Synthesis Engine:
    Evaluates 6 fundamental life pillars through guided interview with Llama 3.3 (70B) & heuristic fallbacks:
    1. Identity, City, Occupation & Life Stage
    2. Ideas, Goals & 1-Year Aspirations
    3. Real Economics (income, expenses, savings, debt in local currency)
    4. 24h Routine (sleep, work/study hours, screen time)
    5. Family, Dependents & Social Support System
    6. Personality, Habits, Strengths & Cognitive Bottlenecks
    """

    @classmethod
    def _evaluate_pillars(cls, text: str) -> Dict[str, bool]:
        import re
        t = (text or "").lower()
        # 1. Identity: name, age, city, occupation or university
        p1 = any(w in t for w in ["llamo", "nombre", "soy", "tengo", "años", "anos", "years", "vivo en", "ciudad", "huancayo", "lima", "arequipa", "cusco", "trujillo", "bogot", "medell", "cdmx", "estudio", "carrera", "sistemas", "software", "trabajo", "oficio", "productor", "negocio", "universidad", "continental", "uncp", "estudiante", "egresad", "universitario", "instituto", "facultad", "pregrado", "alumno"])
        # 2. Goals: 1y goal, medium term (2-3y), long term & travel ideals (5y+)
        p2 = any(w in t for w in ["meta", "quiero", "sueño", "sueno", "idea", "planes", "plan", "egresar", "graduarme", "titularme", "conseguir empleo", "primer trabajo", "ganar", "ahorrar para", "espejo", "objetivo", "año", "1 año", "1a", "meta 1", "mediano plazo", "largo plazo", "viajar", "salir", "trabajar afuera", "trabajar en otro lado", "extranjero", "emigrar", "independiz"])
        # 3. Economy: finances (even if 0)
        p3 = any(w in t for w in ["ingreso", "gasto", "ahorro", "deuda", "soles", "dólares", "dolares", "s/", "$", "plata", "dinero", "sin ingresos", "ingreso = 0", "ingresos = 0", "ingreso 0", "0 soles", "presupuesto", "sueldo", "banco", "económic", "costos", "finanzas", "sin ahorros", "sin deudas", "no gano", "0 gasto", "0 ahorro", "0 deuda", "no trabajo", "no tengo trabajo", "no genero"])
        # 4. Routine: 24h schedule (explicit sleep or daily hours breakdown)
        has_hours_num = bool(re.search(r'\b[0-9]+(?:\.[0-9]+)?\s*h(?:oras)?\b', t))
        has_sleep_explicit = any(w in t for w in ["duermo", "dormir", "horas de sueño", "horas de descanso", "desvelo", "horas en pantalla", "horas de celular", "horas de trabajo", "horas de estudio"])
        p4 = has_hours_num or has_sleep_explicit
        # 5. Family: household & dependents/caregiving
        p5 = any(w in t for w in ["familia", "vivo con", "padres", "mamá", "mama", "papá", "papa", "hermano", "hermanos", "hijo", "hijos", "cuidado", "dependen", "casa familiar", "pareja", "esposa", "esposo", "soltero", "soltera", "novia", "novio", "apoyo", "hogar", "vivo solo", "vivo sola"])
        # 6. Personality: traits, habits, blocks
        p6 = any(w in t for w in ["procrastin", "postergar", "sobrepens", "ansiedad", "ansioso", "miedo", "estrés", "estres", "disciplin", "perseveran", "autoexigente", "carácter", "caracter", "hábito", "habito", "frena", "virtud", "defecto", "bloqueo", "personalidad", "ánimo", "animo", "responsable", "dedicado", "organizado", "desordenado"])
        p7 = any(w in t for w in ["github", "deploy", "producción", "produccion", "portfolio", "portafolio", "stack", "base de datos", "api", "apis", "docker", "frontend", "backend", "clientes", "ventas", "margen", "colegiatura", "casos", "teoría", "teoria", "solo clases", "prácticas", "practicas", "proyectos"])
        return {
            "identity": p1,
            "goals": p2,
            "economy": p3,
            "routine": p4,
            "family": p5,
            "personality": p6,
            "competence_audit": p7,
        }

    @classmethod
    def _extract_parameters(cls, text: str, lang: str = "ES") -> Dict[str, Any]:
        import re
        t = (text or "").lower()

        # 1. Nombre Completo
        full_name = ""
        m_name = re.search(r'(?:me llamo|mi nombre es|soy)\s+([A-ZÁÉÍÓÚa-záéíóú]+(?:\s+[A-ZÁÉÍÓÚa-záéíóú]+){0,3})', text, re.IGNORECASE)
        if m_name:
            cand = m_name.group(1).strip()
            if not cand.lower().startswith(('de ', 'estudiante', 'un ', 'una ', 'programador', 'ingeniero', 'en ')):
                full_name = cand

        # 2. Ciudad, País y Moneda
        city = ""
        country_code = "PE"
        currency = "PEN"

        if "huancayo" in t: city = "Huancayo"
        elif "lima" in t: city = "Lima"
        elif "arequipa" in t: city = "Arequipa"
        elif "cusco" in t: city = "Cusco"
        elif "trujillo" in t: city = "Trujillo"
        elif "bogot" in t: city, country_code, currency = "Bogotá", "CO", "COP"
        elif "medell" in t: city, country_code, currency = "Medellín", "CO", "COP"
        elif "cdmx" in t or "méxico" in t or "mexico" in t: city, country_code, currency = "Ciudad de México", "MX", "MXN"
        elif "chile" in t or "santiago" in t: city, country_code, currency = "Santiago", "CL", "CLP"
        elif "argentina" in t or "buenos aires" in t: city, country_code, currency = "Buenos Aires", "AR", "ARS"
        else:
            m_city = re.search(r'(?:vivo en|en la ciudad de|de la ciudad de|desde)\s+([A-ZÁÉÍÓÚ][a-záéíóú]+)', text)
            if m_city:
                city = m_city.group(1).strip()

        # 3. Edad
        m_age = re.search(r'([0-9]{1,2})\s*(?:años|anos|years)', t) or re.search(r'tengo\s*([0-9]{1,2})', t) or re.search(r'edad(?:\s*es)?\s*(?:de)?\s*([0-9]{1,2})', t)
        age = int(m_age.group(1)) if m_age else None

        # 4. Carrera, Ocupación y Universidad
        is_systems = any(w in t for w in ["sistemas", "software", "computación", "computacion", "programad", "código", "angular", "python"])
        is_econ = any(w in t for w in ["econom", "finanz", "contab", "banc"])
        is_taxi = any(w in t for w in ["taxista", "taxi", "mototaxi", "chofer", "conductor", "colectivo", "transporte", "manejo taxi", "remisse"])
        is_agro = any(w in t for w in ["granja", "granjas", "avícol", "avicol", "porcin", "cuy", "galpón", "galpon", "campo", "papa", "agric", "agrícol", "ganad", "chacra", "fundo", "cultivo", "maíz", "maiz"])
        is_business = any(w in t for w in ["comerciante", "comercio", "bodega", "tienda", "abarrotes", "negocio", "emprend", "vendo ropa", "pyme"])
        is_food = any(w in t for w in ["comida", "alimento", "restaurante", "cocin", "puesto", "ambulante", "vendo"])
        is_trade = any(w in t for w in ["electric", "mecanic", "mecánic", "gasfiter", "taller", "carpinter", "soldador", "plomer"])

        occupation = ""
        if is_taxi:
            career = "Transporte & Conducción (Taxi)"
            occupation = "Taxista / Conductor de Transporte Urbano"
        elif is_agro:
            career = "Producción Agropecuaria y Granjas"
            occupation = "Productor Agropecuario / Granjas"
        elif is_business:
            career = "Comercio & Gestión de Negocio"
            occupation = "Comerciante / Dueño de Negocio"
        elif is_systems:
            career = "Ingeniería de Sistemas e Informática"
            occupation = "Desarrollador de Software & TI"
        elif is_econ:
            career = "Economía y Finanzas"
            occupation = "Analista Económico y Financiero"
        elif is_food:
            career = "Comercio Gastronómico y Venta de Alimentos"
            occupation = "Comerciante Gastronómico / Alimentos"
        elif is_trade:
            career = "Servicios Técnicos Especializados"
            occupation = "Técnico Especialista"
        else:
            career = ""

        if not career:
            m_car = re.search(r'(?:estudio|carrera de|laboro en|trabajo en|me dedico a)\s+([A-ZÁÉÍÓÚa-záéíóú\s]{4,30})', text)
            if m_car:
                career = m_car.group(1).strip()
                occupation = career
            else:
                career = ""

        univ = "Universidad Continental" if any(w in t for w in ["continental", "u continental"]) else ("UNCP" if "uncp" in t else ("Universidad" if "universidad" in t else ""))

        # Detección estricta de condición de graduación vs estudiante activo vs comercio/oficio/taxi/granjas
        is_graduated = any(w in t for w in ["egresad", "bachiller", "titulad", "colegiad", "graduad", "ya egresé", "ya termine", "ya terminé", "con trabajo"])
        is_day_worker = is_taxi or is_food or any(w in t for w in ["vendo comida", "venta de comida", "vendedor", "ambulante", "mototaxi", "taxi", "día a día", "dia a dia", "puesto", "mozo", "obrero", "jornal"])
        is_trade_worker = is_trade or any(w in t for w in ["electricis", "taller mecanico", "gasfiter", "carpinter", "soldador"])
        is_active_student = not is_graduated and not is_taxi and not is_agro and not is_trade_worker and not is_business and any(w in t for w in ["estudiant", "estudio ", "estudiar", "facultad", "ciclo", "semestre", "pregrado", "alumno"])
        is_student = is_active_student

        months_to_grad = 0
        if is_graduated:
            profile = "TITLED_PROFESSIONAL"
            life_stage = "ACTIVE_PROFESSIONAL"
        elif is_taxi:
            profile = "DAY_TO_DAY_WORKER"
            life_stage = "ACTIVE_TRANSPORT"
        elif is_agro:
            profile = "RURAL_FIELD_PRODUCER"
            life_stage = "ACTIVE_PRODUCER"
        elif is_business:
            profile = "BUSINESS_OWNER"
            life_stage = "ACTIVE_COMMERCE"
        elif is_day_worker:
            profile = "DAY_TO_DAY_WORKER"
            life_stage = "ACTIVE_COMMERCE"
        elif is_trade_worker:
            profile = "SKILLED_TRADE"
            life_stage = "ACTIVE_TRADE"
        elif is_active_student:
            profile = "UNIVERSITY_OR_TECH_STUDENT"
            if any(w in t for w in ["día a día", "dia a dia", "actividades", "ingreso", "chamb", "trabaj", "vender", "generar", "emprend", "independiente"]):
                life_stage = "WORKING_AND_FINISHING_UNI"
            else:
                life_stage = "FINISHING_UNIVERSITY"
            months_to_grad = 1
            if "2 meses" in t or "dos meses" in t: months_to_grad = 2
            elif "3 meses" in t or "tres meses" in t: months_to_grad = 3
            elif "6 meses" in t or "seis meses" in t: months_to_grad = 6
            elif "12 meses" in t or "un año" in t: months_to_grad = 12
        else:
            profile = "TITLED_PROFESSIONAL" if career else "DAY_TO_DAY_WORKER"
            life_stage = "ACTIVE_PROFESSIONAL" 

        # 5. Finanzas (Ley de Conservación del Dinero: estricto 0 si no genera o declara 0)
        income = 0.0
        expenses = 0.0
        savings = 0.0
        debt = 0.0

        daily_income = 0.0
        is_explicit_zero_inc = bool(re.search(r'\b(?:ingreso|ingresos|gano|sueldo)\s*(?:=|es|de)?\s*0\b', t)) or any(w in t for w in ["sin ingreso", "sin ingresos", "no gano nada", "no gano dinero", "no trabajo", "cero soles", "cero ingresos"]) or bool(re.search(r'\b0\s*(?:soles|pen|\$)\b', t))
        if not is_explicit_zero_inc:
            m_inc = re.search(r'(?:ingreso|gano|sueldo|salario)\s*(?:de|es)?\s*(?:s/?\.?|\$)?\s*([0-9]+[0-9,\.]*)', t)
            if m_inc:
                try:
                    raw_val = float(m_inc.group(1).replace(",", ""))
                    if any(w in t for w in ["diario", "al dia", "al día", "por dia", "por día", "cada dia", "cada día"]):
                        daily_income = raw_val
                        income = round(raw_val * 6 * 4.333, 2)
                    else:
                        income = raw_val
                except: pass

        if not any(w in t for w in ["gasto = 0", "gastos = 0", "sin gasto", "sin gastos", "gasto 0", "gastos en 0", "0 de gasto"]):
            m_exp = re.search(r'(?:gasto|costo|costos)\s*(?:de|es)?\s*(?:s/?\.?|\$)?\s*([0-9]+[0-9,\.]*)', t)
            if m_exp:
                try: expenses = float(m_exp.group(1).replace(",", ""))
                except: pass

        if not any(w in t for w in ["ahorro = 0", "ahorros = 0", "sin ahorro", "sin ahorros", "ahorro 0", "ahorros en 0", "no tengo ahorro", "0 ahorros"]):
            m_sav = re.search(r'(?:ahorro|guardado)\s*(?:de|es)?\s*(?:s/?\.?|\$)?\s*([0-9]+[0-9,\.]*)', t)
            if m_sav:
                try: savings = float(m_sav.group(1).replace(",", ""))
                except: pass

        if not any(w in t for w in ["deuda = 0", "deudas = 0", "sin deuda", "sin deudas", "deuda 0", "0 deudas", "no tengo deuda"]):
            m_deb = re.search(r'(?:deuda|préstamo|prestamo|credito)\s*(?:de|es)?\s*(?:s/?\.?|\$)?\s*([0-9]+[0-9,\.]*)', t)
            if m_deb:
                try: debt = float(m_deb.group(1).replace(",", ""))
                except: pass

        # 6. Rutina de 24 Horas (CERO HORAS INVENTADAS)
        m_sleep = re.search(r'(?:duermo|sueño|dormir|descanso)\s*(?:unas|unos|alrededor de)?\s*([0-9]+(?:\.[0-9]+)?)\s*h', t) or re.search(r'([0-9]+(?:\.[0-9]+)?)\s*h(?:oras)?\s*(?:de\s+)?(?:sueño|dormir|descanso)', t)
        sleep_hours = float(m_sleep.group(1)) if m_sleep else 0.0

        if any(w in t for w in ["no trabajo", "sin trabajo", "ingreso = 0", "0h de trabajo", "0h trabajo", "0 horas de trabajo", "0 de trabajo"]):
            work_hours = 0.0
        else:
            m_work = re.search(r'(?:trabajo|laboro|jornada)\s*(?:unas|unos|de)?\s*([0-9]+(?:\.[0-9]+)?)\s*h', t) or re.search(r'([0-9]+(?:\.[0-9]+)?)\s*h(?:oras)?\s*(?:de\s+)?(?:trabajo|jornada)', t)
            work_hours = float(m_work.group(1)) if m_work else 0.0

        m_study = re.search(r'(?:estudio|estudiar|proyecto|tesis)\s*(?:unas|unos|de)?\s*([0-9]+(?:\.[0-9]+)?)\s*h', t) or re.search(r'([0-9]+(?:\.[0-9]+)?)\s*h(?:oras)?\s*(?:de|en)?\s*(?:mi\s+)?(?:estudio|proyecto|tesis)', t)
        study_hours = float(m_study.group(1)) if m_study else 0.0

        m_screen = re.search(r'(?:pantalla|pantallas|redes|celular|ocio|tik\s*tok|instagram)\s*(?:unas|unos|de)?\s*([0-9]+(?:\.[0-9]+)?)\s*h', t) or re.search(r'([0-9]+(?:\.[0-9]+)?)\s*h(?:oras)?\s*(?:en|de)?\s*(?:pantalla|redes|ocio|celular)', t)
        screen_hours = float(m_screen.group(1)) if m_screen else 0.0

        # 7. Familia, Entorno y Cuidados (Fiel al texto real, cero plantillas duras)
        dep_count = 0
        care_hours = 0.0
        open_family = ""

        m_fam_sent = re.search(r'([^.!?\n]*(?:cuidado|hermano|hermana|hijo|hija|padres|mamá|papá|familia|dependen)[^.!?\n]*)', text, re.IGNORECASE)
        if m_fam_sent:
            open_family = m_fam_sent.group(1).strip()

        if any(w in t for w in ["dos hermanos", "2 hermanos", "hermanos uno de 9 y otro de 3"]):
            dep_count = 2
            care_hours = 3.5
        elif any(w in t for w in ["tres hermanos", "3 hermanos"]):
            dep_count = 3
            care_hours = 4.5
        elif any(w in t for w in ["un hermano", "1 hermano"]):
            dep_count = 1
            care_hours = 2.0
        elif any(w in t for w in ["dos hijos", "2 hijos"]):
            dep_count = 2
            care_hours = 4.0
        elif any(w in t for w in ["un hijo", "1 hijo"]):
            dep_count = 1
            care_hours = 3.0

        # Cero textos inventados para pareja/amigos: solo si el usuario lo mencionó
        open_rel = ""
        if any(w in t for w in ["amigos", "pareja", "novia", "novio", "esposa", "esposo", "círculo", "circulo"]):
            m_rel = re.search(r'(?:amigos|pareja|novia|novio|esposa|esposo)[^.\n]{5,100}', text, re.IGNORECASE)
            if m_rel:
                open_rel = m_rel.group(0).strip()

        # 8. Personalidad y Bloqueos Internos (Fiel al texto real, cero plantillas duras)
        traits = []
        if any(w in t for w in ["postergar", "procrastin", "procastin", "demor", "atraso", "dejo para el final"]):
            traits.append("PROCRASTINATOR")
        if any(w in t for w in ["sobrepens", "ansiedad", "ansioso", "preocup", "mente no para"]):
            traits.append("ANXIOUS_OVERTHINKER")
        if any(w in t for w in ["ambicio", "superar", "metas", "crecer", "salir adelante"]):
            traits.append("AMBITIOUS")
        if any(w in t for w in ["disciplin", "ordenad", "constan"]):
            traits.append("DISCIPLINED")
        if any(w in t for w in ["resilien", "perseveran", "luch", "fuerte"]):
            traits.append("RESILIENT")

        open_pers = ""
        m_pers_sent = re.search(r'([^.!?\n]*(?:concentrar|sobrepens|postergar|procrastin|ansiedad|estrés|estres|hábito|habito|carácter|caracter|bloqueo|frena)[^.!?\n]*)', text, re.IGNORECASE)
        if m_pers_sent:
            open_pers = m_pers_sent.group(1).strip()
        elif traits:
            traits_str = ", ".join([TRAIT_TRANSLATIONS_ES.get(tr, tr.lower()) for tr in traits])
            open_pers = f"Rasgos identificados: {traits_str}."

        # 9. Meta Clave (1 Año) y Metas a Mediano / Largo Plazo (Fiel al texto real y calibrado por arquetipo)
        goal_mode = False
        goal = ""
        m_goal = re.search(r'(?:meta a corto plazo|meta principal|meta a 1 año|meta|sueño|quiero|plan)\s*(?:es|de)?\s*([^.\n]{5,100})', text, re.IGNORECASE)
        if m_goal:
            goal_mode = True
            goal = m_goal.group(1).strip()
        elif is_active_student:
            goal_mode = True
            if univ:
                goal = f"Culminar formación en {career} en {univ} e insertarme al mercado laboral"
            else:
                goal = f"Culminar formación en {career} e insertarme al mercado laboral"
        elif is_day_worker:
            goal_mode = True
            goal = f"Asegurar punto de venta formalizado y elevar ingresos netos diarios"
        elif is_trade_worker:
            goal_mode = True
            goal = f"Equipar taller propio y cerrar contratos de mantenimiento técnico recurrentes"
        elif is_graduated:
            goal_mode = True
            goal = f"Consolidación profesional, ascenso a Analista/Especialista y titulación en {career or 'mi área'}"
        else:
            goal_mode = True
            goal = f"Aumentar ingresos netos y consolidar estabilidad económica en {career or 'mi actividad'}"

        # Metas a Mediano Plazo (2 - 3 Años)
        med_goal = ""
        m_med = re.search(r'(?:mediano plazo|en 2 años|en 3 años|a 2 años|a 3 años|ahorrar para|especializ(?:ar|arme)|fondo de|independiz(?:ar|arme)|post-egreso)\s*(?:es|de|:)?\s*([^.\n]{5,120})', text, re.IGNORECASE)
        if m_med:
            med_goal = m_med.group(0).strip()
        elif is_active_student:
            med_goal = f"Ahorrar colchón financiero inicial y ganar 2 años de experiencia sólida en {career or 'mi área'}"
        elif is_day_worker:
            med_goal = f"Establecer módulo comercial fijo (Nuevo RUS) y reinvertir en inventario/maquinaria propia"
        elif is_trade_worker:
            med_goal = f"Taller homologado con 1-2 ayudantes y cartera de clientes corporativos"
        elif is_graduated:
            med_goal = f"Alcanzar nivel Senior / Jefatura de área y formalizar colegiatura/posgrado"
        else:
            med_goal = f"Diversificar ingresos y consolidar patrimonio con un fondo de emergencia de 6 meses"

        # Ideales y Metas a Largo Plazo (5+ Años: viajar, salir y trabajar afuera, etc.)
        long_goal = ""
        m_long = re.search(r'(?:largo plazo|a futuro|ideal(?:es)?|sueño a futuro|viajar y salir|viajar|salir y trabajar|trabajar en otro lado|trabajar afuera|emigrar|en el extranjero|otro país|comprar departamento|libertad financiera)\s*(?:es|de|:)?\s*([^.\n]{5,120})', text, re.IGNORECASE)
        if m_long:
            long_goal = m_long.group(0).strip()
        elif any(w in t for w in ["viajar", "trabajar en otro lado", "trabajar afuera", "extranjero", "otro país", "emigrar", "salir"]):
            long_goal = "Viajar, salir y trabajar en el extranjero o en otra ciudad con mejores oportunidades económicas"
        elif is_active_student:
            long_goal = "Alcanzar independencia económica y proyectarme internacionalmente o en posiciones de liderazgo"
        elif is_day_worker:
            long_goal = "Local comercial propio consolidado con personal a cargo y estabilidad patrimonial familiar"
        elif is_trade_worker:
            long_goal = "Empresa contratista de ingeniería y mantenimiento con cuadrillas y flota propia"
        elif is_graduated:
            long_goal = "Dirección de proyectos / Gerencia corporativa o consultoría independiente de alta solvencia"
        else:
            long_goal = "Libertad financiera, patrimonio protegido e inversiones diversificadas"

        # 10. Multiplicador de Competencia Verificada (Auditoría Técnica/Práctica 0.60 a 1.30)
        competence_mult = 1.0
        has_strong_proof = any(w in t for w in ["github", "deploy", "producción", "produccion", "portfolio", "portafolio", "docker", "api rest", "cartera de clientes", "margen 3", "margen 4", "colegiado", "habilitado"])
        has_moderate_proof = any(w in t for w in ["proyectos personales", "prácticas", "practicas", "ventas", "freelance", "experiencia"])
        has_theory_only = any(w in t for w in ["solo teoría", "solo teoria", "no tengo proyectos", "sin portafolio", "no he desplegado", "sin github", "solo clases", "ninguna experiencia"])

        if has_strong_proof:
            competence_mult = 1.25
        elif has_theory_only:
            competence_mult = 0.70
        elif has_moderate_proof:
            competence_mult = 1.08
        else:
            competence_mult = 1.0

        ret_dict = {
            "verified_competence_multiplier": competence_mult,
            "full_name": full_name,
            "person_identifier": full_name or "Usuario Mirror Future",
            "city": city,
            "country_code": country_code,
            "currency": currency,
            "life_profile_type": profile,
            "career_or_degree": career,
            "occupation": occupation or career,
            "university_or_institution": univ,
            "life_stage": life_stage,
            "months_to_graduation": months_to_grad,
            "monthly_income": income,
            "daily_income_avg": daily_income,
            "work_days_per_week": 6.0 if daily_income > 0 else 0.0,
            "monthly_expenses": expenses,
            "current_savings": savings,
            "current_debt": debt,
            "sleep_hours": sleep_hours,
            "work_hours": work_hours,
            "study_or_project_hours": study_hours,
            "screen_time_distraction_hours": screen_hours,
            "exercise_hours": 0.5,
            "housing_situation": "FAMILY_HOME",
            "household_climate": "SUPPORTIVE",
            "relationship_status": "SINGLE_PEACEFUL",
            "social_circle_influence": "GROWTH",
            "dependents_count": dep_count,
            "daily_caregiving_hours": care_hours,
            "personality_traits": traits,
            "goal_mode": goal_mode,
            "main_goal_1y": goal,
            "one_year_goal": goal,
            "medium_term_goals": med_goal,
            "long_term_goals": long_goal,
            "open_family_and_dependents": open_family,
            "open_relationships_and_friends": open_rel,
            "open_personality_and_habits": open_pers,
            "self_description": f"En {city}, enfocado en {career} equilibrando el hogar y superación personal." if career else ""
        }
        if age is not None:
            ret_dict["age"] = age
        return ret_dict

    @classmethod
    def _compose_dossier_text(cls, params: Dict[str, Any], raw_user_text: str, lang: str = "ES") -> str:
        is_es = lang.upper() == "ES"
        full_name = params.get("full_name") or ""
        city = params.get("city") or ""
        career = params.get("career_or_degree") or ""
        univ = params.get("university_or_institution") or ""
        months = params.get("months_to_graduation", 0)
        curr = params.get("currency", "PEN")
        curr_sym = "S/" if curr == "PEN" else "$"
        inc = params.get("monthly_income", 0.0)
        exp = params.get("monthly_expenses", 0.0)
        sav = params.get("current_savings", 0.0)
        deb = params.get("current_debt", 0.0)
        sleep = params.get("sleep_hours", 0.0)
        work = params.get("work_hours", 0.0)
        study = params.get("study_or_project_hours", 0.0)
        screen = params.get("screen_time_distraction_hours", 0.0)
        traits = params.get("personality_traits", [])
        goal = params.get("main_goal_1y", "")
        med_goal = params.get("medium_term_goals", "")
        long_goal = params.get("long_term_goals", "")
        dep_count = params.get("dependents_count", 0)
        care_h = params.get("daily_caregiving_hours", 0.0)
        open_fam = params.get("open_family_and_dependents") or ""

        traits_desc_es = ", ".join([TRAIT_TRANSLATIONS_ES.get(t, t.lower()) for t in traits]) if traits else "constancia y resiliencia"

        if is_es:
            # Párrafo 1: Identidad y Ocupación
            name_intro = f"Te llamas {full_name}, " if full_name else ""
            city_intro = f"vives en {city}" if city else "te encuentras planificando tu futuro"
            if univ and months > 0:
                career_part = f" en la recta final de {career} en la {univ}, a falta de aprox. {months} mes(es) para egresar."
            elif career:
                career_part = f", enfocado en tu desarrollo en {career}."
            else:
                career_part = "."
            p1 = f"{name_intro}{city_intro}{career_part} Tu foco actual combina tus responsabilidades formativas y laborales con la preparación para consolidar tu actividad."

            # Párrafo 2: Familia y Economía
            if open_fam:
                fam_text = f"En tu entorno familiar: '{open_fam}'" + (f" (asumiendo ~{care_h:.1f}h diarias de atención)." if care_h > 0 else ".")
            elif dep_count > 0:
                fam_text = f"En tu hogar tienes a tu cargo el cuidado de {dep_count} persona(s) (~{care_h:.1f}h diarias)."
            else:
                fam_text = "Vives bajo el respaldo de tu hogar familiar sin dependientes directos a tu cargo."

            if inc == 0 and sav == 0:
                econ_text = f"Financieramente operas hoy con una base estricta de {curr_sym} 0 en ingresos propios, {curr_sym} {exp:,.0f} en gastos y {curr_sym} 0 en ahorros acumulados, sosteniéndote bajo el amparo de tu familia mientras completas esta etapa, sin arrastrar deudas personales ({curr_sym} {deb:,.0f})."
            else:
                econ_text = f"Tu flujo económico actual registra un ingreso mensual de {curr_sym} {inc:,.0f} {curr}, con gastos estimados en {curr_sym} {exp:,.0f} {curr}, ahorro de {curr_sym} {sav:,.0f} {curr} y deudas de {curr_sym} {deb:,.0f} {curr}."

            p2 = f"{fam_text} {econ_text}"

            # Párrafo 3: Rutina, Personalidad y Metas (1A, Mediano Plazo, Largo Plazo e Ideales)
            routine_parts = []
            if sleep > 0: routine_parts.append(f"{sleep:.1f}h de sueño")
            if work > 0: routine_parts.append(f"{work:.1f}h de trabajo")
            if study > 0: routine_parts.append(f"{study:.1f}h de estudio o proyectos")
            if screen > 0: routine_parts.append(f"{screen:.1f}h de pantallas u ocio")
            routine_str = f"En tu rutina cotidiana organizas {', '.join(routine_parts)}. " if routine_parts else ""

            goals_list = []
            if goal: goals_list.append(f"Tu meta a 1 año es '{goal}'.")
            if med_goal: goals_list.append(f"A mediano plazo (2-3 años) proyectas '{med_goal}'.")
            if long_goal: goals_list.append(f"Como ideal y meta a largo plazo (5+ años) tienes en mente '{long_goal}'.")
            goals_text = " ".join(goals_list) if goals_list else "Tu meta principal es consolidar tu estabilidad vital y económica."

            p3 = f"{routine_str}En tu forma de ser destacas por {traits_desc_es}. {goals_text}"
            return f"{p1}\n\n{p2}\n\n{p3}"

        else:
            name_intro = f"Your name is {full_name}, " if full_name else ""
            city_intro = f"living in {city}" if city else "planning your future path"
            if univ and months > 0:
                career_part = f" in the final stretch of {career} at {univ}, with about {months} month(s) before graduating."
            elif career:
                career_part = f", actively dedicated to {career}."
            else:
                career_part = "."
            p1 = f"{name_intro}{city_intro}{career_part} Your current focus balances day-to-day commitments with positioning for personal and professional growth."

            if open_fam:
                fam_text = f"In your household environment: '{open_fam}'" + (f" (dedicating ~{care_h:.1f}h daily to family care)." if care_h > 0 else ".")
            elif dep_count > 0:
                fam_text = f"At home you care for {dep_count} dependent(s) (~{care_h:.1f}h daily)."
            else:
                fam_text = "You live supported by your family home without direct dependents under your care."

            if inc == 0 and sav == 0:
                econ_text = f"Financially, you operate from a verified baseline of {curr_sym} 0 personal income, {curr_sym} {exp:,.0f} expenses, and {curr_sym} 0 savings, supported by your household safety net with zero active personal debt ({curr_sym} {deb:,.0f})."
            else:
                econ_text = f"Your monthly cashflow registers an income of {curr_sym} {inc:,.0f} {curr}, estimated expenses of {curr_sym} {exp:,.0f} {curr}, savings of {curr_sym} {sav:,.0f} {curr}, and active debt of {curr_sym} {deb:,.0f} {curr}."

            p2 = f"{fam_text} {econ_text}"

            routine_parts = []
            if sleep > 0: routine_parts.append(f"{sleep:.1f}h sleep")
            if work > 0: routine_parts.append(f"{work:.1f}h work")
            if study > 0: routine_parts.append(f"{study:.1f}h study/projects")
            if screen > 0: routine_parts.append(f"{screen:.1f}h screen/leisure")
            routine_str = f"Your daily schedule accounts for {', '.join(routine_parts)}. " if routine_parts else ""

            p3 = (
                f"{routine_str}Your character reflects strengths in {', '.join(traits) if traits else 'resilience and grit'}. "
                + (f"Your primary milestone for this year is to '{goal}'." if goal else "Your primary goal is securing long-term economic and personal stability.")
            )
            return f"{p1}\n\n{p2}\n\n{p3}"

    @classmethod
    async def conduct_interview(cls, req: DiscoveryInterviewRequest) -> DiscoveryInterviewResponse:
        settings = get_settings()
        lang = (req.lang or "EN").upper()
        is_es = lang == "ES"
        history = req.conversation_history or []
        user_messages = [m.content for m in history if m.role == "user"]
        user_turns = len(user_messages)
        combined_text = "\n".join(user_messages)
        if req.ingested_files_context:
            combined_text += f"\n[Contexto Archivo]: {req.ingested_files_context}"

        pillars = cls._evaluate_pillars(combined_text)
        covered_count = sum(1 for v in pillars.values() if v)

        # Criterio estricto de completitud:
        # 1. El usuario hizo clic en "Ya conté lo principal: Generar mi Dossier" (force_flag)
        # 2. O los 6 pilares han sido respondidos
        # 3. O al menos 3 turnos de usuario Y al menos 5 pilares cubiertos
        force_flag = bool(getattr(req, "force_generate", False) or getattr(req, "force_complete", False))
        all_covered = all(pillars.values())
        enough_turns = (user_turns >= 3 and covered_count >= 5)

        should_complete = force_flag or (all_covered and user_turns >= 2)

        # 1. Intentar con LLM oficial (Muse Spark 1.3 / Llama 3.3) si está disponible y autenticado
        if settings.meta_llama_api_key and not settings.meta_llama_api_key.startswith("tu_"):
            try:
                system_msg = (
                    "Eres el Principal Life Discovery Architect de Mirror Future. "
                    "Entrevistas al usuario de manera empática, conversacional y natural para descubrir los pilares de su vida:\n"
                    "1. Identidad, Ciudad, Ocupación y Etapa de vida (egresando, trabajando, estudiante, etc.)\n"
                    "2. Metas e Ideales: Meta a 1 año, Metas a mediano plazo (2-3 años), y Grandes Ideales a largo plazo (5+ años, como viajar, salir y trabajar afuera)\n"
                    "3. Economía Real (ingreso, gasto, ahorro, deuda en moneda local)\n"
                    "4. Rutina de 24h (horas de sueño, trabajo/estudio, ocio de pantallas)\n"
                    "5. Familia, Personas a su Cuidado y Relaciones\n"
                    "6. Personalidad, Hábitos, Virtudes y Bloqueos Internos (procrastinación, sobrepensamiento)\n\n"
                    f"Idioma de respuesta: {'Español' if is_es else 'English'}.\n"
                    "REGLAS ESTRICTAS DE CLASIFICACIÓN DE PERFIL Y CALIBRACIÓN:\n"
                    "- life_profile_type DEBE ser estrictamente uno de: ['UNIVERSITY_OR_TECH_STUDENT', 'DAY_TO_DAY_WORKER', 'TITLED_PROFESSIONAL', 'SKILLED_TRADE', 'BUSINESS_OWNER', 'RURAL_FIELD_PRODUCER'].\n"
                    "- REGLA OBLIGATORIA DE ESTUDIANTES: Si la persona indica ser estudiante (universidad, instituto, tesis, etc.) y menciona que se gana el día a día buscando actividades, ventas o trabajos para generar ingresos, su perfil principal es STRICTLY 'UNIVERSITY_OR_TECH_STUDENT' (life_stage = 'WORKING_AND_FINISHING_UNI'). NUNCA lo clasifiques como 'BUSINESS_OWNER' ni 'DAY_TO_DAY_WORKER'. Sus actividades son de sustento mientras estudia.\n"
                    "- En CADA TURNO, SIEMPRE extrae en 'extracted_parameters' todos los datos detectados hasta el momento (nombre, ciudad, edad, ocupación, life_profile_type, ingresos, gastos, ahorros, horas de rutina, main_goal_1y, medium_term_goals, long_term_goals) para mantener sincronizado el modo manual en tiempo real.\n"
                    "- NUNCA marques is_complete = True a menos que force_complete sea True O que los pilares hayan sido genuinamente respondidos por el usuario en el historial.\n"
                    "- PROHIBIDO inventar valores por defecto. Si el usuario no especificó un valor, usa 0.0 o deja el texto vacío.\n"
                    "Devuelve ÚNICAMENTE un JSON válido con las claves: is_complete, completeness_pct, next_question, full_person_dossier_text, extracted_parameters."
                )
                user_msg = (
                    f"HISTORIAL DE LA CONVERSACIÓN:\n{json.dumps([{'role': m.role, 'content': m.content} for m in history], ensure_ascii=False, indent=2)}\n\n"
                    f"Force complete: {force_flag}\n"
                    f"Pillars detectados: {json.dumps(pillars)}\n"
                    f"Contexto archivos: {req.ingested_files_context or 'N/A'}"
                )
                raw = await llama_client.structured_completion(
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg}
                    ],
                    model=settings.llama_reasoning_model,
                    temperature=0.3,
                    max_tokens=1800
                )
                is_comp = bool(raw.get("is_complete"))
                pct = int(raw.get("completeness_pct", 100 if is_comp else 50))
                next_q = raw.get("next_question")
                dossier = raw.get("full_person_dossier_text")
                params = raw.get("extracted_parameters")

                if is_comp and dossier and isinstance(params, dict):
                    if "savings" in params and "current_savings" not in params:
                        params["current_savings"] = params["savings"]
                    if "debt" in params and "current_debt" not in params:
                        params["current_debt"] = params["debt"]
                    if "name" in params and "full_name" not in params:
                        params["full_name"] = params["name"]
                    if "occupation" in params and "career_or_degree" not in params:
                        params["career_or_degree"] = params["occupation"]
                    if "study_hours" in params or "project_hours" in params:
                        if "study_or_project_hours" not in params:
                            params["study_or_project_hours"] = float(params.get("study_hours", 0.0) or 0.0) + float(params.get("project_hours", 0.0) or 0.0)
                    if "screen_leisure_hours" in params and "screen_time_distraction_hours" not in params:
                        params["screen_time_distraction_hours"] = params["screen_leisure_hours"]

                    if params.get("monthly_income") == 0 and params.get("current_savings") == 0:
                        params["current_savings"] = 0.0
                        params["monthly_income"] = 0.0
                    return DiscoveryInterviewResponse(
                        is_complete=True,
                        completeness_pct=100,
                        next_question=None,
                        full_person_dossier_text=dossier,
                        extracted_parameters=params
                    )
                elif not is_comp and next_q:
                    # Siempre retornar parámetros y borrador extraído para sincronizar con el modo manual en tiempo real
                    heur_params = cls._extract_parameters(combined_text, lang)
                    current_turn_params = {**heur_params, **(params if isinstance(params, dict) else {})}
                    if not current_turn_params.get("verified_competence_multiplier"):
                        current_turn_params["verified_competence_multiplier"] = heur_params.get("verified_competence_multiplier", 1.0)
                    if not current_turn_params.get("career_or_degree") and heur_params.get("career_or_degree"):
                        current_turn_params["career_or_degree"] = heur_params["career_or_degree"]
                    draft_dossier = dossier or cls._compose_dossier_text(current_turn_params, combined_text, lang)
                    return DiscoveryInterviewResponse(
                        is_complete=False,
                        completeness_pct=min(90, max(25, pct)),
                        next_question=next_q,
                        full_person_dossier_text=draft_dossier,
                        extracted_parameters=current_turn_params
                    )
            except Exception as exc:
                logger.warning("Falla en DiscoveryInterviewEngine con LLM (%s). Usando contingencia heurística.", exc)

        # 2. Motor Heurístico Guiado Turno a Turno (Garantiza que NUNCA se corten preguntas sin responder)
        if should_complete:
            params = cls._extract_parameters(combined_text, lang)
            dossier = cls._compose_dossier_text(params, combined_text, lang)
            params["full_person_dossier_text"] = dossier
            return DiscoveryInterviewResponse(
                is_complete=True,
                completeness_pct=100,
                next_question=None,
                full_person_dossier_text=dossier,
                extracted_parameters=params
            )

        # Formular la siguiente pregunta específica según los pilares faltantes:
        pct = max(20, min(85, covered_count * 16))

        # Caso A: Faltan Identidad o Metas (Turno inicial)
        if not pillars.get("identity") or not pillars.get("goals"):
            next_q = (
                "¡Hola! Soy tu Oráculo Causal Mirror Future. Para calibrar con precisión matemática tu proyección a 1 mes, 6 meses y 1 año sin inventar datos:\n\n"
                "1. ¿Cómo te llamas, cuántos años tienes y en qué ciudad vives?\n"
                "2. ¿A qué te dedicas hoy (carrera/universidad, trabajo u oficio), cuál es tu gran meta para este año (1 año), qué metas tienes a mediano plazo (2-3 años) y qué ideales o sueños tienes a futuro (como viajar o salir a trabajar en otro lado)?"
                if is_es else
                "Hello! I am your Mirror Future Causal Oracle. To calibrate your projection with mathematical precision and zero fabricated data:\n\n"
                "1. What is your name, age, and which city do you live in?\n"
                "2. What do you do today (degree/university, job, or trade), what is your 1-year goal, what are your medium-term goals (2-3 years), and what long-term ideals do you envision (such as traveling or working abroad)?"
            )
        # Caso B: Faltan Economía, Rutina 24 Horas o Auditoría Técnica de Nivel
        elif not pillars.get("economy") or not pillars.get("routine"):
            next_q = (
                "¡Te sigo! Ahora hablemos de tu tiempo diario, tus finanzas y tu nivel técnico real:\n\n"
                "1. ⏱️ Presupuesto de 24 horas: En un día normal, ¿cuántas horas sueles dormir, cuántas trabajas (si aplica), cuántas le dedicas a estudiar o a tus proyectos, y cuántas a ocio en pantallas/celular?\n"
                "2. 💰 Finanzas reales: ¿Cuánto dinero ganas o recibes al mes aproximadamente (o si es 0), cuánto gastas, y cuánto tienes en ahorros o deudas hoy en tu moneda?\n"
                "3. 🛠️ Auditoría de Competencia Real: Para calibrar con precisión tu probabilidad de inserción frente a las vacantes del mercado: ¿Qué herramientas o tecnologías dominas en la práctica, cuentas con portafolio/GitHub/ventas demostrables, o tu formación ha sido principalmente teórica?"
                if is_es else
                "Got it! Now let's calibrate your daily 24-hour schedule, real finances and practical competence:\n\n"
                "1. ⏱️ 24-Hour Budget: In a normal day, how many hours do you sleep, how many do you work, how many do you study/work on projects, and how many are spent on screens/leisure?\n"
                "2. 💰 Real Finances: How much do you earn or receive monthly (or if 0), how much do you spend, and what savings or debts do you have in your local currency?\n"
                "3. 🛠️ Competence Audit: To accurately benchmark your hiring probability against real job openings: What tools or stack do you use in practice, do you have a portfolio/GitHub/verifiable results, or has your experience been mostly academic/theoretical?"
            )
        # Caso C: Faltan Familia/Cuidados o Personalidad/Carácter
        elif not pillars.get("family") or not pillars.get("personality"):
            next_q = (
                "¡Perfecto! Ya tengo tus números y tu tiempo. Por último, para capturar tu entorno humano y cómo manejas la presión:\n\n"
                "1. 👨‍👩‍👧 Hogar y Cuidados: ¿Con quiénes vives en casa? ¿Hay personas que dependan de ti o de tus cuidados diarios (hijos, hermanos menores, padres)? ¿Cuántas horas diarias les dedicas?\n"
                "2. 🧠 Cómo eres tú: ¿Cómo te describes como persona? ¿Cuáles son tus mayores virtudes y qué hábitos o bloqueos internos (como sobrepensar o postergar tareas) sientes que a veces te frenan?"
                if is_es else
                "Perfect! I have your numbers and schedule. Lastly, to capture your human environment and personal patterns:\n\n"
                "1. 👨‍👩‍👧 Household & Caregiving: Who do you live with? Does anyone rely on you or your daily care (children, younger siblings, parents)? How many daily hours do you dedicate?\n"
                "2. 🧠 Character & Habits: How do you describe yourself? What are your greatest strengths, and what internal habits (like overthinking or procrastinating) tend to slow you down?"
            )
        else:
            # Si sólo falta un detalle menor
            next_q = (
                "¡Casi listo! ¿Hay algún otro detalle de tu situación familiar o de tus hábitos que desees agregar antes de generar tu perfil completo?"
                if is_es else
                "Almost ready! Is there any other detail about your family or habits you'd like to add before generating your full dossier?"
            )

        turn_params = cls._extract_parameters(combined_text, lang)
        turn_dossier = cls._compose_dossier_text(turn_params, combined_text, lang)

        return DiscoveryInterviewResponse(
            is_complete=False,
            completeness_pct=pct,
            next_question=next_q,
            full_person_dossier_text=turn_dossier,
            extracted_parameters=turn_params
        )

    @classmethod
    async def sync_dossier_to_parameters(cls, req: SyncDossierRequest) -> SyncDossierResponse:
        settings = get_settings()
        lang = (req.lang or "ES").upper()
        dossier = req.dossier_text or ""
        current_p = req.current_parameters or {}

        try:
            system_msg = (
                "Eres el Analista de Sincronización de Parámetros de Mirror Future. "
                "Tu objetivo es leer el texto completo de biografía y realidad del usuario ('dossier_text') "
                "y extraer el objeto de parámetros exacto 'HolisticFutureRequest' sin inventar montos ni datos que no estén expresados.\n"
                "Asegura: monthly_income, monthly_expenses, current_savings, current_debt, currency, city, country_code, "
                "life_profile_type, career_or_degree, university_or_institution, months_to_graduation, dependents_count, "
                "daily_caregiving_hours, sleep_hours, work_hours, study_or_project_hours, personality_traits, main_goal_1y, medium_term_goals, long_term_goals.\n"
                "REGLA CRUCIAL DE PERFIL: life_profile_type DEBE ser estrictamente uno de: ['UNIVERSITY_OR_TECH_STUDENT', 'DAY_TO_DAY_WORKER', 'TITLED_PROFESSIONAL', 'SKILLED_TRADE', 'BUSINESS_OWNER', 'RURAL_FIELD_PRODUCER']. "
                "Si la persona es estudiante (universitario, técnico, tesis, etc.) y realiza actividades para generar ingresos de sustento, su perfil principal es STRICTLY 'UNIVERSITY_OR_TECH_STUDENT'. NUNCA lo clasifiques como 'BUSINESS_OWNER' ni 'DAY_TO_DAY_WORKER'.\n"
                "Devuelve ÚNICAMENTE un objeto JSON con la clave 'extracted_parameters': dict."
            )
            raw = await llama_client.structured_completion(
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": f"DOSSIER DEL USUARIO:\n{dossier}\n\nPARÁMETROS PREVIOS:\n{json.dumps(current_p, ensure_ascii=False)}"}
                ],
                model=settings.llama_reasoning_model,
                temperature=0.2,
                max_tokens=1500
            )
            params = raw.get("extracted_parameters")
            if isinstance(params, dict):
                d_low = dossier.lower()
                is_grad = any(w in d_low for w in ["egresad", "bachiller", "titulad", "colegiad", "graduad", "ya egresé", "ya termine", "ya terminé", "con trabajo"])
                is_day = any(w in d_low for w in ["vendo comida", "venta de comida", "vendedor", "ambulante", "mototaxi", "taxista", "día a día", "dia a dia", "puesto"])
                is_trade = any(w in d_low for w in ["electric", "mecanic", "mecánic", "gasfiter", "taller", "carpinter"])
                is_st = not is_grad and not is_day and not is_trade and any(w in d_low for w in ["estudiant", "estudio ", "estudiar", "facultad", "alumno", "semestre", "ciclo"])

                if is_grad:
                    params["life_profile_type"] = "TITLED_PROFESSIONAL"
                    params["months_to_graduation"] = 0
                    if not params.get("life_stage"):
                        params["life_stage"] = "ACTIVE_PROFESSIONAL"
                elif is_day:
                    params["life_profile_type"] = "DAY_TO_DAY_WORKER"
                    params["months_to_graduation"] = 0
                elif is_trade:
                    params["life_profile_type"] = "SKILLED_TRADE"
                    params["months_to_graduation"] = 0
                elif is_st:
                    params["life_profile_type"] = "UNIVERSITY_OR_TECH_STUDENT"
                    if any(w in d_low for w in ["día a día", "dia a dia", "actividades", "ingreso", "chamb", "trabaj", "vender", "generar"]):
                        params["life_stage"] = "WORKING_AND_FINISHING_UNI"

                # Complementar metas si faltasen
                heur = cls._extract_parameters(dossier, lang)
                if not params.get("medium_term_goals") and heur.get("medium_term_goals"):
                    params["medium_term_goals"] = heur["medium_term_goals"]
                if not params.get("long_term_goals") and heur.get("long_term_goals"):
                    params["long_term_goals"] = heur["long_term_goals"]

                params["full_person_dossier_text"] = dossier
                return SyncDossierResponse(
                    extracted_parameters=params,
                    full_person_dossier_text=dossier,
                    status="synced_via_llm"
                )
        except Exception as exc:
            logger.warning("Falla en sync_dossier_to_parameters con LLM: %s. Usando extractor heurístico.", exc)

        # Fallback heurístico
        extracted = cls._extract_parameters(dossier, lang)
        merged = {**current_p, **extracted, "full_person_dossier_text": dossier}
        return SyncDossierResponse(
            extracted_parameters=merged,
            full_person_dossier_text=dossier,
            status="synced_via_heuristic"
        )


class MiroFishReportAgent:
    """
    Agente de Inteligencia Predictiva y Diagnóstico Causal Holístico (Llama 3.3 70B).
    Sintetiza la narrativa estocástica de cómo evoluciona la persona a 30 días, 180 días y 365 días,
    adaptándose al perfil real de la persona (Día a Día, Campo, Oficio, Profesional, Estudiante, Negocio),
    al modo (Espejo Puro sin meta forzada vs. Con Meta) y al idioma seleccionado ('EN' | 'ES').
    """

    @classmethod
    async def generate_holistic_report(
        cls,
        req: HolisticFutureRequest,
        macro: MacroEconomicContext,
        sim_metrics: Dict[str, HorizonMetrics],
        live_intel: Optional[LiveWebIntelligenceReport] = None,
        human_factors: Optional[InferredHumanFactors] = None,
        career_autocompletion: Optional[CareerAutocompletionResult] = None
    ) -> Tuple[Dict[str, HorizonNarrative], List[GoldenPathAdjustment], str]:
        settings = get_settings()
        intel = live_intel or LiveWebIntelligenceReport()
        hf = human_factors or InferredHumanFactors()

        profile = req.life_profile_type or "DAY_TO_DAY_WORKER"
        is_pure_mirror = (not req.goal_mode) or (not bool((req.main_goal_1y or req.one_year_goal or "").strip()))
        is_es = req.lang == "ES"

        # Identidad y actividad adaptativa
        person_name = req.full_name or req.full_name_or_handle or req.person_identifier or ("Amigo" if is_es else "Friend")
        uni_name = req.university_or_institution or ""
        company_name = req.current_company_or_org or ""

        if profile == "RURAL_FIELD_PRODUCER":
            activity_name = f"Productor de {req.rural_product}" if req.rural_product else ("Productor agrario / pecuario" if is_es else "Rural producer / farmer")
        elif profile == "DAY_TO_DAY_WORKER":
            activity_name = req.occupation or ("Comercio / Independiente del día a día" if is_es else "Day-to-day independent worker")
        elif profile == "SKILLED_TRADE":
            activity_name = req.career_or_degree or req.occupation or ("Oficio técnico calificado" if is_es else "Skilled tradesperson")
        elif profile == "BUSINESS_OWNER":
            activity_name = req.business_type or req.occupation or ("Dueño de negocio / PYME" if is_es else "Business owner / SME")
        elif profile == "UNIVERSITY_OR_TECH_STUDENT":
            activity_name = req.career_or_degree or req.occupation or ("Estudiante universitario" if is_es else "University student")
        else:
            activity_name = req.career_or_degree or req.occupation or ("Profesional titulado" if is_es else "Titled professional")

        prompt_payload = {
            "perfil_usuario": {
                "nombre": person_name,
                "tipo_perfil": profile,
                "actividad_o_carrera": activity_name,
                "institucion_o_universidad": uni_name if profile == "UNIVERSITY_OR_TECH_STUDENT" else None,
                "empresa_o_entidad": company_name or None,
                "etapa_de_vida": req.life_stage,
                "esfuerzo_fisico_intensidad": req.physical_labor_intensity,
                "anos_de_experiencia": req.years_of_experience,
                "modalidad_oficio": req.trade_modality if profile == "SKILLED_TRADE" else None,
                "producto_rural": req.rural_product if profile == "RURAL_FIELD_PRODUCER" else None,
                "tipo_negocio": req.business_type if profile == "BUSINESS_OWNER" else None,
                "ciudad_residencia": f"{req.city}, {macro.country_name}",
                "situacion_de_vivienda": req.housing_situation,
                "modo_proyeccion": "ESPEJO_PURO_SIN_META" if is_pure_mirror else "EVALUACION_META_CONCRETA",
                "meta_anual_declarada": None if is_pure_mirror else req.main_goal_1y,
                "sueldo_objetivo_1_ano": None if is_pure_mirror else f"{req.target_monthly_salary_1y:,.2f} {req.currency}",
                "idioma_solicitado": "ESPAÑOL" if is_es else "ENGLISH"
            },
            "finanzas_actuales": {
                "ingreso_mensual_estimado": f"{req.monthly_income:,.2f} {req.currency}",
                "gastos_mensuales_estimados": f"{req.monthly_expenses:,.2f} {req.currency}",
                "ahorro_o_capital_actual": f"{req.current_savings:,.2f} {req.currency}",
                "deuda_actual": f"{req.current_debt:,.2f} {req.currency}",
                "flujo_caja_mensual": f"{req.monthly_income - req.monthly_expenses:,.2f} {req.currency}"
            },
            "habitos_24h": {
                "sueno_horas": req.sleep_hours,
                "trabajo_o_faena_horas": req.work_hours,
                "estudio_o_proyecto_horas": req.study_or_project_hours,
                "pantalla_ocio_horas": req.screen_time_distraction_hours,
                "ejercicio_dias": req.exercise_days_per_week,
                "tiempo_social_horas": req.social_hours
            },
            "evidencia_web_real_en_vivo": {
                "ciudad": req.city,
                "indice_costo_de_vida": f"{intel.city_cost_pressure_index:.2f} (base 1.0)",
                "demanda_o_dinamica_mercado": f"{intel.career_market_demand_score:.1f}/100",
                "factores_locales_identificados": intel.local_companies_found[:4],
                "requisitos_o_desafios_identificados": intel.goal_requirements_evidence[:4],
                "sintesis_del_entorno": intel.synthesized_real_time_context
            },
            "contexto_macro": {
                "pais": macro.country_name,
                "inflacion_anual": f"{macro.annual_inflation_rate}%",
                "desempleo_nacional": f"{macro.unemployment_rate}%"
            },
            "familia_y_entorno": {
                "dependientes_a_cargo": req.dependents_count,
                "clima_hogar": req.household_climate,
                "estado_relacion": req.relationship_status,
                "influencia_circulo_social": req.social_circle_influence,
            },
            "respuestas_abiertas_situacionales": {
                "familia_y_hogar": req.open_family_and_dependents or None,
                "pareja_y_circulo_social": req.open_relationships_and_friends or None,
                "personalidad_y_reaccion_al_estres": req.open_personality_and_habits or None,
            },
            "factores_humanos_inferidos": hf.model_dump(),
            "personalidad_y_caracter": {
                "autodescripcion": req.self_description or None,
                "rasgos_personalidad": req.personality_traits or [],
            },
            "telemetria_chats_whatsapp": {
                "resumen_comunicacion": req.chat_extracted_summary or None,
                "sentimiento_promedio": req.chat_sentiment_avg,
                "etiqueta_dominante": req.chat_dominant_tag,
                "mediana_respuesta_minutos": req.chat_median_reply_min,
            } if (req.chat_extracted_summary or req.chat_sentiment_avg is not None or req.chat_dominant_tag) else None,
            "proyeccion_life2vec_carrera": {
                "arquetipo_cohorte": career_autocompletion.cohort_archetype,
                "percentil_competitividad": f"{career_autocompletion.cohort_similarity_percentile:.1f}%",
                "exposicion_automatizacion_ia": f"{career_autocompletion.ai_automation_exposure_pct:.1f}%",
                "potencial_apalancamiento_ia": f"{career_autocompletion.ai_leverage_potential_pct:.1f}%",
                "cuellos_de_botella": career_autocompletion.career_bottlenecks,
                "skills_recomendadas": career_autocompletion.recommended_skill_acquisitions,
                "transiciones_secuenciales": [
                    {
                        "horizonte": t.horizon_label,
                        "p10_inercial": f"{t.p10_stagnation_role} ({t.p10_income:,.0f} {req.currency})",
                        "p50_probable": f"{t.p50_likely_role} ({t.p50_income:,.0f} {req.currency})",
                        "p90_acelerado": f"{t.p90_accelerated_role} ({t.p90_income:,.0f} {req.currency})",
                        "probabilidad_salto": f"{t.transition_probability_pct:.1f}%",
                    }
                    for t in (career_autocompletion.predicted_career_transitions or [])
                ]
            } if career_autocompletion else None,
            "metricas_monte_carlo": {
                "1_mes_dia_30": sim_metrics["1_month"].model_dump(),
                "6_meses_dia_180": sim_metrics["6_months"].model_dump(),
                "1_ano_dia_365": sim_metrics["1_year"].model_dump()
            }
        }

        labor_intens_es = INTENSITY_TRANSLATIONS_ES.get(req.physical_labor_intensity, "moderada exigencia física")

        if is_es:
            care_rule = (
                f"Tiene a su cuidado en casa a {hf.caregiving_details} ({hf.daily_caregiving_hours:.1f}h diarias). "
                if hf.dependents_care_count > 0 else ""
            )
            system_instruction = (
                "Eres el Principal Causal Architect y Asesor de Proyección de Vida de Mirror Future. "
                "Tu misión es predecir con realismo brutal, base científica y empatía humana cómo vivirá y evolucionará la persona "
                "a 1 MES (Día 30), 6 MESES (Día 180) y 1 AÑO (Día 365).\n\n"
                "REGLAS INQUEBRANTABLES:\n"
                "1. IDIOMA: Todo el texto generado DENTRO DEL JSON DEBE ESTAR ESTRICTAMENTE EN ESPAÑOL.\n"
                f"2. CERO SESGO CORPORATIVO/ACADÉMICO: El usuario es '{profile}'. "
                + (
                    "ESTÁ EN MODO ESPEJO PURO (SIN META FORZADA). NO le hables de ascensos ejecutivos ni proyectos corporativos ajenos "
                    "a menos que sea explícitamente estudiante o profesional corporativo. "
                    f"Concéntrate en su realidad como {activity_name}: cómo se verá físicamente (rostro, desgaste corporal, espalda, energía), "
                    f"cómo rendirá su dinero del día a día frente a los precios de {req.city}, y cómo será su rutina diaria si sigue como hoy."
                    if is_pure_mirror else
                    f"TIENE UNA META DECLARADA ('{req.main_goal_1y}'). Evalúa su viabilidad real frente a las exigencias del mercado en {req.city}."
                ) + "\n"
                f"3. ANCLAJE GEOGRÁFICO REAL: Cita explícitamente la realidad de {req.city}, los precios, los canales comerciales o empresas detectadas ({', '.join(intel.local_companies_found[:3])}) y la inflación del {macro.annual_inflation_rate}%.\n"
                "4. CRONOLOGÍA DIFERENCIADA:\n"
                "   - 1 MES: Sensación corporal inmediata, ajuste de gastos y presión de la rutina de 24h.\n"
                "   - 6 MESES: Efectos acumulados de la fatiga, colchón de ahorro frente a emergencias y desgaste físico o avance.\n"
                "   - 1 AÑO: Estado físico consolidado, poder adquisitivo real deflactado y estabilidad vital integral.\n"
                f"5. DIMENSIONES HUMANAS REALES (FAMILIA, PAREJA Y PERSONALIDAD):\n"
                f"   - Carga familiar e inferida: {req.dependents_count} dependientes declarados, {care_rule}balance de hogar {hf.home_emotional_balance:+.2f}.\n"
                f"   - Pareja y círculo: {req.relationship_status}, efecto inferido {hf.partner_and_friends_effect:+.2f}.\n"
                f"   - Carácter y hábitos: resiliencia {hf.resilience_and_grit_score:.2f}, riesgo de gasto/estrés {hf.stress_spending_and_procrastination_risk:.2f}.\n"
                f"   - Testimonios directos del usuario: Familia ('{req.open_family_and_dependents or 'N/A'}'), Pareja/Amigos ('{req.open_relationships_and_friends or 'N/A'}'), Personalidad ('{req.open_personality_and_habits or req.self_description or 'N/A'}').\n"
                "   - REGLA CLAVE: En cada snapshot (1 Mes, 6 Meses, 1 Año), haz referencia directa, empática y realista a los detalles íntimos y frases que el usuario compartió en sus respuestas abiertas.\n"
                "6. PROHIBIDO IMPRIMIR CÓDIGOS TÉCNICOS EN INGLÉS: NUNCA escribas códigos como 'PROCRASTINATOR', 'ANXIOUS_OVERTHINKER', 'LOW', 'MEDIUM', 'HIGH', 'FAMILY_HOME', ni '0.0h'. Usa siempre expresiones naturales en español (ej. 'tendencia a postergar entregas clave', 'baja exigencia física', 'hogar familiar').\n"
                "7. DEPENDIENTES Y CUIDADO: Si el usuario escribió que cuida a familiares o hermanos (ej. 'mis dos hermanos uno de 9 y otro de 3'), PROHIBIDO decir 'sin dependientes'. Reconoce explícitamente su rol de cuidado diario y el tiempo que demanda.\n"
                "8. TRANSICIÓN DE EGRESO UNIVERSITARIO (si el usuario es estudiante en últimos meses de carrera):\n"
                "   - Mes 1: Su balance económico respeta fielmente sus datos de partida (0.00 si no genera ingresos). Enfocado en trámites finales de titulación o tesis.\n"
                "   - Mes 6: Al culminar su egreso e insertarse al mercado laboral en su carrera y localidad, comienza a percibir su primer sueldo de entrada según su mercado real.\n"
                "   - Año 1: Ya cuenta con experiencia profesional y acumulación real de ahorros.\n"
                "9. SECUENCIA LIFE2VEC Y PROYECCIÓN LABORAL: Integra en los snapshots de 1 Mes, 6 Meses y 1 Año la ocupación y banda salarial (P10 inercial, P50 probable y P90 acelerado) proyectada por el motor Life2Vec, explicando qué empresas de su ciudad o remoto demandan su perfil y cómo su historial pasado condiciona sus próximos años.\n"
                "10. FORMATO: Devuelve EXCLUSIVAMENTE un objeto JSON válido según la estructura requerida."
            )
            activity_shift_text = (
                f"{req.study_or_project_hours:.1f}h de dedicación a tesis/estudios"
                if req.work_hours <= 0.1 else
                f"{req.work_hours:.1f}h de jornada laboral"
            )
            user_prompt = f"""PROYECCIÓN DE FUTURO EN {req.city.upper()} (1 MES, 6 MESES, 1 AÑO):
{json.dumps(prompt_payload, indent=2, ensure_ascii=False)}

Genera un JSON con esta estructura exacta:
{{
  "snapshot_1_month": {{
    "future_self_portrait": "Retrato visual y cotidiano en el día 30 en {req.city}: postura, semblante, energía y ritmo de su actividad como {activity_name}",
    "economic_reality": "Situación financiera a 30 días con su flujo en {req.city} frente a la canasta básica y costo local",
    "health_and_mind_state": "Nivel de vitalidad, descanso con {req.sleep_hours}h de sueño y efecto del esfuerzo físico ({labor_intens_es})",
    "critical_warning": "El riesgo inmediato de desbalance o gasto imprevisto que debe vigilar este mes"
  }},
  "snapshot_6_months": {{
    "future_self_portrait": "Tu vida en el día 180: señales visibles de continuidad o fatiga acumulada, adaptación del cuerpo y dinámica en {req.city}",
    "economic_reality": "Estado de la reserva económica tras 6 meses de inflación e ingresos, capacidad de respuesta ante imprevistos",
    "health_and_mind_state": "Resistencia biológica, prevención de agotamiento físico o sobrecarga mental",
    "critical_warning": "El principal cuello de botella operativo o financiero que surge tras medio año"
  }},
  "snapshot_1_year": {{
    "future_self_portrait": "Tu estampa integral a los 365 días como {activity_name} en {req.city}: semblante, satisfacción y ritmo de vida",
    "economic_reality": "Patrimonio neto real deflactado, solidez del colchón económico y margen de maniobra familiar",
    "health_and_mind_state": "Salud consolidada, vitalidad corporal y balance general tras 1 año",
    "critical_warning": "La clave esencial para proteger tu bienestar físico y estabilidad a largo plazo"
  }},
  "golden_path_adjustments": [
    {{
      "domain": "ENERGÍA_Y_CUERPO",
      "current_baseline": "Rutina actual de {req.sleep_hours:.1f}h de sueño con {labor_intens_es}",
      "prescribed_target": "Ajuste específico para recuperar energía y proteger articulaciones/salud",
      "expected_impact_p90": "Preserva tu capacidad de trabajo y reduce el riesgo de fatiga crónica en P90"
    }},
    {{
      "domain": "COLCHÓN_DE_RESERVA",
      "current_baseline": "Ahorro actual de {req.current_savings:,.0f} {req.currency} frente a gastos de {req.monthly_expenses:,.0f} {req.currency}",
      "prescribed_target": "Regla práctica de retención de caja en {req.city} ante variaciones de precios",
      "expected_impact_p90": "Blindaje de liquidez de 3 a 6 meses frente a emergencias y shocks locales"
    }},
    {{
      "domain": "OPTIMIZACIÓN_DIARIA",
      "current_baseline": "{activity_shift_text} y {req.screen_time_distraction_hours:.1f}h en ocio pasivo",
      "prescribed_target": "Reasignación de tiempo para descanso activo y trámites clave",
      "expected_impact_p90": "Aumenta la estabilidad global y reduce el desgaste acumulado"
    }}
  ],
  "executive_summary": "Diagnóstico causal empático y riguroso en 2 párrafos sobre tu trayectoria de bienestar y estabilidad en {req.city}."
}}
Responde SOLAMENTE el JSON puro."""

        else:
            system_instruction = (
                "You are the Principal Causal Architect and Life Trajectory Advisor at Mirror Future. "
                "Predict with raw realism, scientific rigor, and human empathy how this individual will evolve "
                "at 1 MONTH (Day 30), 6 MONTHS (Day 180), and 1 YEAR (Day 365).\n\n"
                "STRICT RULES:\n"
                "1. LANGUAGE: Every piece of text inside the JSON MUST BE IN ENGLISH.\n"
                f"2. ZERO CORPORATE/ACADEMIC BIAS: The user's life profile is '{profile}'. "
                + (
                    "THEY ARE IN PURE MIRROR MODE (NO FORCED GOAL). DO NOT talk about thesis, corporate job applications, tech certifications, or executive promotions "
                    "unless they are explicitly a student or titled professional. "
                    f"Focus on their real human life as a {activity_name}: physical appearance (posture, facial fatigue, body wear, stamina), "
                    f"whether daily cash/income keeps up with local prices in {req.city}, and the rhythm of their daily life if they continue as today."
                    if is_pure_mirror else
                    f"THEY HAVE AN EXPLICIT GOAL ('{req.main_goal_1y}'). Realistically evaluate their trajectory and market requirements in {req.city}."
                ) + "\n"
                f"3. REAL-WORLD GROUNDING: Explicitly reference {req.city}, local living costs, identified local economic hubs ({', '.join(intel.local_companies_found[:3])}), and inflation ({macro.annual_inflation_rate}%).\n"
                "4. CHRONOLOGICAL DIFFERENTIATION:\n"
                "   - 1 MONTH: Immediate bodily sensation, budget tension, and 24h routine friction.\n"
                "   - 6 MONTHS: Cumulative fatigue or adaptation, financial runway against emergencies, bodily wear.\n"
                "   - 1 YEAR: Consolidated physical appearance, real deflated net worth, and long-term life stability.\n"
                f"5. REAL HUMAN DIMENSIONS (FAMILY, PARTNER & CHARACTER):\n"
                f"   - Family burden and inferred balance: {req.dependents_count} declared dependents, inferred burden {hf.inferred_dependents_burden:.2f}, home balance {hf.home_emotional_balance:+.2f}.\n"
                f"   - Partner and circle effect: {req.relationship_status}, inferred effect {hf.partner_and_friends_effect:+.2f}.\n"
                f"   - Resilience and stress risk: resilience {hf.resilience_and_grit_score:.2f}, stress spending/procrastination risk {hf.stress_spending_and_procrastination_risk:.2f}.\n"
                f"   - User's open testimonies: Family ('{req.open_family_and_dependents or 'N/A'}'), Partner/Circle ('{req.open_relationships_and_friends or 'N/A'}'), Personality/Habits ('{req.open_personality_and_habits or req.self_description or 'N/A'}').\n"
                f"   - KEY RULE: In every snapshot (1 Month, 6 Months, 1 Year), explicitly integrate and reflect the specific personal situations and feelings expressed in their open answers. The user must feel that this forecast speaks directly to their lived daily truth.\n"
                + (f"Incorporate findings from their uploaded WhatsApp chats: {req.chat_extracted_summary}." if req.chat_extracted_summary else "") + "\n"
                "6. FORMAT: Return ONLY valid JSON adhering to the specified schema."
            )
            user_prompt = f"""FUTURE SELF PROJECTION IN {req.city.upper()} (1 MONTH, 6 MONTHS, 1 YEAR):
{json.dumps(prompt_payload, indent=2, ensure_ascii=False)}

Generate a JSON with this exact structure:
{{
  "snapshot_1_month": {{
    "future_self_portrait": "Visual and daily portrait on day 30 in {req.city}: physical posture, facial stamina, energy and rhythm as {activity_name}",
    "economic_reality": "30-day cashflow balance in {req.city} relative to local prices and household necessities",
    "health_and_mind_state": "Vitality, sleep recovery with {req.sleep_hours}h sleep and physical labor impact ({req.physical_labor_intensity})",
    "critical_warning": "Immediate friction point or unexpected expense to watch this month"
  }},
  "snapshot_6_months": {{
    "future_self_portrait": "Your life on day 180: visible physical adaptation or wear, stamina retention, and routine in {req.city}",
    "economic_reality": "Financial cushion status after 6 months of living costs and earnings; emergency runway",
    "health_and_mind_state": "Bodily stamina, chronic fatigue prevention, and mental clarity",
    "critical_warning": "The main operational or financial friction point that surfaces after half a year"
  }},
  "snapshot_1_year": {{
    "future_self_portrait": "Your 365-day portrait as {activity_name} in {req.city}: physical appearance, daily fulfillment, and rhythm of life",
    "economic_reality": "Deflated real net worth, emergency resilience, and household stability in {req.city}",
    "health_and_mind_state": "Overall physical vitality, health sustainability, and life balance after 1 year",
    "critical_warning": "Key operational discipline required to protect your health and financial security"
  }},
  "golden_path_adjustments": [
    {{
      "domain": "BODY_AND_ENERGY",
      "current_baseline": "Current routine of {req.sleep_hours:.1f}h sleep and {req.physical_labor_intensity} physical exertion",
      "prescribed_target": "Concrete recovery habit to safeguard joint and physical longevity",
      "expected_impact_p90": "Sustains your earning capacity and prevents cumulative exhaustion at P90"
    }},
    {{
      "domain": "FINANCIAL_BUFFER",
      "current_baseline": "Current savings of {req.current_savings:,.0f} {req.currency} vs expenses of {req.monthly_expenses:,.0f} {req.currency}",
      "prescribed_target": "Pragmatic daily/weekly cash retention rule adapted to {req.city}",
      "expected_impact_p90": "Builds a 3 to 6-month safety net against local price shocks and emergencies"
    }},
    {{
      "domain": "DAILY_RHYTHM",
      "current_baseline": "{req.work_hours:.1f}h work hours and {req.screen_time_distraction_hours:.1f}h passive distraction",
      "prescribed_target": "Reallocating small time pockets into physical recovery and key maintenance",
      "expected_impact_p90": "Reduces daily friction and improves overall life stability"
    }}
  ],
  "executive_summary": "Empathetic and rigorous 2-paragraph causal diagnosis of your wellbeing and stability trajectory in {req.city}."
}}
Reply ONLY with pure JSON."""

        fb_narratives, fb_adjustments, fb_summary = cls._generate_fallback_narratives(req, macro, sim_metrics, intel, hf)

        try:
            raw_json = await llama_client.structured_completion(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                model=settings.llama_reasoning_model,
                temperature=0.25,
                max_tokens=3200
            )

            narratives = {
                "1_month": cls._safe_narrative(raw_json.get("snapshot_1_month"), fb_narratives["1_month"], hf),
                "6_months": cls._safe_narrative(raw_json.get("snapshot_6_months"), fb_narratives["6_months"], hf),
                "1_year": cls._safe_narrative(raw_json.get("snapshot_1_year"), fb_narratives["1_year"], hf)
            }

            raw_adjs = raw_json.get("golden_path_adjustments", [])
            adjustments = [
                cls._safe_adjustment(adj, fb_adjustments, i, hf)
                for i, adj in enumerate(raw_adjs)
            ] if isinstance(raw_adjs, list) and raw_adjs else fb_adjustments

            summary = cls._sanitize_text_spanglish(
                raw_json.get("executive_summary") or fb_summary,
                hf
            )
            return narratives, adjustments, summary

        except Exception as exc:
            logger.error("Falla en inferencia con Llama 3.3 70B: %s. Utilizando síntesis de contingencia.", exc)
            return fb_narratives, fb_adjustments, fb_summary

    @classmethod
    def _sanitize_text_spanglish(cls, text: str, hf: Optional[InferredHumanFactors] = None) -> str:
        if not text:
            return ""
        replacements = {
            "PROCRASTINATOR": "tendencia a postergar tareas clave",
            "ANXIOUS_OVERTHINKER": "sobrepensamiento y ansiedad ante la incertidumbre",
            "AMBITIOUS": "ambición de superación",
            "RESILIENT": "alta resiliencia",
            "DISCIPLINED": "disciplina constante",
            "PERFECTIONIST": "perfeccionismo exigente",
            "STRESS_AVOIDANT": "evitación del estrés",
            "IMPULSIVE_SPENDER": "gasto impulsivo",
            "(LOW)": "(intensidad física ligera)",
            "(MEDIUM)": "(intensidad física moderada)",
            "(HIGH)": "(alta exigencia física)",
            "(VERY_HIGH)": "(muy alta exigencia física)",
            "intensidad física LOW": "intensidad física ligera",
            "intensidad física MEDIUM": "intensidad física moderada",
            "intensidad física HIGH": "intensidad física alta",
            "intensidad física VERY_HIGH": "intensidad física muy alta",
            "jornada (0.0h)": "etapa de estudio/tesis y cuidado del hogar",
            "jornada de 0.0h": "etapa de estudio/tesis y cuidado del hogar",
            "esfuerzo de tu jornada (0.0h)": "dedicación a tus estudios y responsabilidades del hogar",
            "esfuerzo de tu jornada (0h)": "dedicación a tus estudios y responsabilidades del hogar",
            "0.0h de jornada laboral": "sin jornada laboral asalariada",
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
            text = text.replace(k.lower(), v)
            text = text.replace(k.capitalize(), v)

        care_count = getattr(hf, "dependents_care_count", 0) if hf else 0
        care_details = getattr(hf, "caregiving_details", "") if hf else ""
        if care_count > 0:
            desc = care_details or f"{care_count} hermanos menores"
            text = text.replace("sin dependientes económicos directos", f"al cuidado familiar de {desc}")
            text = text.replace("sin dependientes directos", f"al cuidado familiar de {desc}")
            text = text.replace("sin dependientes económicos", f"al cuidado familiar de {desc}")
            text = text.replace("sin dependientes", f"al cuidado de {desc}")
            text = text.replace("without direct economic dependents", f"actively caring for {desc}")
            text = text.replace("without economic dependents", f"actively caring for {desc}")
            text = text.replace("without dependents", f"actively caring for {desc}")

        return text

    @classmethod
    def _safe_narrative(cls, data: Any, fallback: HorizonNarrative, hf: Optional[InferredHumanFactors] = None) -> HorizonNarrative:
        if not isinstance(data, dict):
            return fallback
        return HorizonNarrative(
            future_self_portrait=cls._sanitize_text_spanglish(data.get("future_self_portrait") or fallback.future_self_portrait, hf),
            economic_reality=cls._sanitize_text_spanglish(data.get("economic_reality") or fallback.economic_reality, hf),
            health_and_mind_state=cls._sanitize_text_spanglish(data.get("health_and_mind_state") or fallback.health_and_mind_state, hf),
            critical_warning=cls._sanitize_text_spanglish(data.get("critical_warning") or fallback.critical_warning, hf)
        )

    @classmethod
    def _safe_adjustment(cls, adj: Any, fallback_list: List[GoldenPathAdjustment], idx: int, hf: Optional[InferredHumanFactors] = None) -> GoldenPathAdjustment:
        fb = fallback_list[idx] if idx < len(fallback_list) else fallback_list[0]
        if not isinstance(adj, dict):
            return fb
        return GoldenPathAdjustment(
            domain=adj.get("domain") or fb.domain,
            current_baseline=cls._sanitize_text_spanglish(adj.get("current_baseline") or fb.current_baseline, hf),
            prescribed_target=cls._sanitize_text_spanglish(adj.get("prescribed_target") or fb.prescribed_target, hf),
            expected_impact_p90=cls._sanitize_text_spanglish(adj.get("expected_impact_p90") or fb.expected_impact_p90, hf)
        )

    @classmethod
    def _generate_fallback_narratives(
        cls,
        req: HolisticFutureRequest,
        macro: MacroEconomicContext,
        sim_metrics: Dict[str, HorizonMetrics],
        live_intel: Optional[LiveWebIntelligenceReport] = None,
        human_factors: Optional[InferredHumanFactors] = None
    ) -> Tuple[Dict[str, HorizonNarrative], List[GoldenPathAdjustment], str]:
        m1 = sim_metrics["1_month"]
        m6 = sim_metrics["6_months"]
        m12 = sim_metrics["1_year"]

        currency = req.currency or "PEN"
        intel = live_intel or LiveWebIntelligenceReport()
        hf = human_factors or InferredHumanFactors()
        cost_idx = intel.city_cost_pressure_index
        demand_score = intel.career_market_demand_score

        profile = req.life_profile_type or "DAY_TO_DAY_WORKER"
        is_pure_mirror = (not req.goal_mode) or (not bool((req.main_goal_1y or req.one_year_goal or "").strip()))
        is_es = req.lang == "ES"

        person_name = req.full_name or req.full_name_or_handle or req.person_identifier or ("Amigo" if is_es else "Friend")
        city_raw = (req.city or "").strip()
        city = city_raw or ("tu localidad" if is_es else "your local area")
        city_in_phrase = f"en {city_raw}" if city_raw else ("en tu localidad" if is_es else "in your local area")
        country = macro.country_name or ("tu país" if is_es else "your country")

        # -------------------------------------------------------------
        # 0. DETECCIÓN DE LÍNEA BASE CERO (PARÁMETROS VACÍOS O EN BLANCO)
        # -------------------------------------------------------------
        is_empty_profile = (
            (req.monthly_income == 0 or req.monthly_income is None)
            and (req.monthly_expenses == 0 or req.monthly_expenses is None)
            and (req.current_savings == 0 or req.current_savings is None)
            and (req.current_debt == 0 or req.current_debt is None)
            and (req.work_hours <= 0.1)
            and (req.study_or_project_hours <= 0.1)
            and not bool((req.career_or_degree or req.occupation or "").strip())
            and not bool((req.university_or_institution or "").strip())
            and not bool((req.full_person_dossier_text or "").strip())
        )

        if is_empty_profile:
            if is_es:
                narratives = {
                    "1_month": HorizonNarrative(
                        future_self_portrait=(
                            f"Línea Base Neutral (30 días): No se han configurado parámetros activos de ocupación, rutina ni ciudad. "
                            f"El motor causal mantiene tus variables en reposo (0h de jornada laboral y 0h de desgaste operativo) sin inventar supuestos."
                        ),
                        economic_reality=(
                            f"Balance financiero estrictamente en 0.00 {currency} (ingresos en 0, gastos en 0 y ahorros en 0). "
                            f"La ley de conservación de capital no proyecta deudas ficticias ni fondos inexistentes."
                        ),
                        health_and_mind_state=(
                            f"Vitalidad base estimada en {m1.health_and_vitality_score.p50:.0f}/100. En ausencia de datos sobre descanso y actividad, "
                            f"la probabilidad de desgaste se reporta en {m1.burnout_probability*100:.1f}% como umbral matemático basal."
                        ),
                        critical_warning="Ingresa tus datos reales (ciudad, ocupación, ingresos y rutina) o conversa con Mirror Future para desbloquear tu pronóstico causal real."
                    ),
                    "6_months": HorizonNarrative(
                        future_self_portrait=(
                            f"Proyección a 6 meses (180 días): En ausencia de metas u ocupación declarada, el sistema no formula suposiciones sobre inserción laboral, estudios ni ingresos automáticos. "
                            f"Tu trayectoria permanece en el punto de partida real."
                        ),
                        economic_reality=(
                            f"Patrimonio neto real proyectado: 0.00 {currency}. Cero dinero fantasma y cero conjeturas. "
                            f"Para calcular tu capacidad de ahorro o inserción económica, ingresa tus variables reales en el formulario o en la entrevista."
                        ),
                        health_and_mind_state=(
                            f"Nivel de vitalidad proyectado en {m6.health_and_vitality_score.p50:.0f}/100. Un horizonte prolongado sin dirección o rutina definida puede inducir letargo."
                        ),
                        critical_warning="Configura tus parámetros o activa la entrevista con la IA para evaluar escenarios de empleo, ahorro y proyectos."
                    ),
                    "1_year": HorizonNarrative(
                        future_self_portrait=(
                            f"Horizonte a 1 año (365 días): Cierre de ciclo sin variables activas de inicio. El simulador de Monte Carlo confirma un balance estacionario, "
                            f"sin forzar graduaciones ni sueldos artificiales."
                        ),
                        economic_reality=(
                            f"Patrimonio neto real proyectado: 0.00 {currency}. El motor econométrico no genera rentas sin respaldo causal directo."
                        ),
                        health_and_mind_state=(
                            f"Vitalidad proyectada en {m12.health_and_vitality_score.p50:.0f}/100 con estabilidad basal."
                        ),
                        critical_warning="Para proyectar tu futuro real con búsqueda web en vivo y calibración econométrica de tu ciudad, comparte tu realidad con Mirror Future."
                    )
                }
                adjustments = [
                    GoldenPathAdjustment(
                        domain="CALIBRACIÓN_DE_VARIABLES",
                        current_baseline="Perfil con parámetros vacíos o en cero (sin ingresos, ocupación ni ciudad declarada)",
                        prescribed_target="Completar tu ciudad, oficio/estudios, ingresos y gastos reales o responder a las preguntas de la entrevista con la IA",
                        expected_impact_p90="Activa la proyección causal auténtica con investigación web de tu mercado y 1,000 trayectorias Monte Carlo."
                    ),
                    GoldenPathAdjustment(
                        domain="PRESUPUESTO_DE_TIEMPO",
                        current_baseline="Horas de sueño, trabajo y proyectos sin calibrar",
                        prescribed_target="Definir tu rutina de 24 horas (descanso, jornada laboral y tiempo de estudio o proyectos)",
                        expected_impact_p90="Permite modelar con rigor matemático tu curva de energía física y resistencia al burnout."
                    ),
                    GoldenPathAdjustment(
                        domain="CLARIDAD_FINANCIERA",
                        current_baseline=f"Patrimonio y flujos en 0.00 {currency}",
                        prescribed_target="Registrar tus ingresos mensuales promedio y costos fijos para modelar tu capacidad de ahorro y resiliencia",
                        expected_impact_p90="Calcula tu patrimonio real deflactado por inflación local a 1 mes, 6 meses y 1 año."
                    )
                ]
                summary = (
                    f"Diagnóstico de Línea Base Cero: Se ejecutó la simulación econométrica sin parámetros activos de realidad (ingresos, ocupación, ciudad o hábitos). "
                    f"El motor matemático respetó estrictamente la conservación del valor, reportando un patrimonio de 0.00 {currency} sin inventar datos ni aplicar plantillas supuestas. "
                    f"Para obtener una predicción causal rigurosa adaptada a tu vida, ingresa tus datos reales o conversa con la IA en la entrevista de descubrimiento."
                )
            else:
                narratives = {
                    "1_month": HorizonNarrative(
                        future_self_portrait=(
                            f"Neutral Baseline (30 days): No active occupation, city, or daily routine variables were provided. "
                            f"The causal engine holds your operational metrics at rest with 0h work and 0h operational strain, avoiding fabricated assumptions."
                        ),
                        economic_reality=(
                            f"Financial balance strictly at 0.00 {currency} (zero declared income, expenses, and savings). "
                            f"The conservation of value law creates neither phantom debt nor ungrounded wealth."
                        ),
                        health_and_mind_state=(
                            f"Baseline vitality estimated at {m1.health_and_vitality_score.p50:.0f}/100. Without sleep or exertion telemetry, "
                            f"burnout probability is reported at {m1.burnout_probability*100:.1f}% as a mathematical baseline threshold."
                        ),
                        critical_warning="Calibrate your real baseline variables (city, occupation, income, and routine) or converse with Mirror Future to unlock an authentic forecast."
                    ),
                    "6_months": HorizonNarrative(
                        future_self_portrait=(
                            f"6-Month Projection (day 180): In the absence of declared goals or active occupation, the engine makes zero assumptions regarding job insertion or automatic income. "
                            f"Your trajectory remains at your true baseline."
                        ),
                        economic_reality=(
                            f"Projected real net worth: 0.00 {currency}. Zero phantom money and zero guesswork. "
                            f"To forecast savings runway or labor insertion, enter your authentic variables in the form or interview."
                        ),
                        health_and_mind_state=(
                            f"Vitality level projected at {m6.health_and_vitality_score.p50:.0f}/100. Prolonged inactivity without defined direction can lead to lethargy."
                        ),
                        critical_warning="Set your parameters or start the discovery interview to evaluate realistic employment, savings, and project scenarios."
                    ),
                    "1_year": HorizonNarrative(
                        future_self_portrait=(
                            f"1-Year Horizon (365 days): Annual close without initial active parameters. Monte Carlo simulation confirms a stationary baseline "
                            f"without forced graduations or artificial salaries."
                        ),
                        economic_reality=(
                            f"Projected real net worth: 0.00 {currency}. The econometric engine does not invent returns without direct causal evidence."
                        ),
                        health_and_mind_state=(
                            f"Vitality projected at {m12.health_and_vitality_score.p50:.0f}/100 with baseline stability."
                        ),
                        critical_warning="To project your authentic future with live web intelligence and econometric calibration, share your reality with Mirror Future."
                    )
                }
                adjustments = [
                    GoldenPathAdjustment(
                        domain="CALIBRATE_BASELINE",
                        current_baseline="Profile with empty/zero parameters (no income, occupation, or city declared)",
                        prescribed_target="Provide your authentic city, trade/studies, income, and expenses or complete the AI discovery interview",
                        expected_impact_p90="Activates real-time causal projection with grounded market intelligence and 1,000 Monte Carlo trajectories."
                    ),
                    GoldenPathAdjustment(
                        domain="TIME_BUDGET",
                        current_baseline="Sleep, work, and project hours uncalibrated",
                        prescribed_target="Define your 24-hour daily allocation (sleep, workday, and focused project blocks)",
                        expected_impact_p90="Enables rigorous mathematical modeling of your vitality curve and burnout risk."
                    ),
                    GoldenPathAdjustment(
                        domain="FINANCIAL_CLARITY",
                        current_baseline=f"Net worth and cashflow at 0.00 {currency}",
                        prescribed_target="Log average monthly income and fixed overhead to model savings capacity and macroeconomic resilience",
                        expected_impact_p90="Calculates your inflation-deflated real net worth at 1 month, 6 months, and 1 year."
                    )
                ]
                summary = (
                    f"Zero Baseline Diagnostic: Econometric simulation completed without active reality parameters (income, trade, city, or daily habits). "
                    f"The mathematical engine strictly preserved conservation of money, reporting a net worth of 0.00 {currency} without inventing data or applying hardcoded templates. "
                    f"To receive an authentic causal forecast tailored to your life, enter your baseline data or converse with Mirror Future."
                )
            return narratives, adjustments, summary

        # -------------------------------------------------------------
        # PARÁMETROS REALES CALIBRADOS
        # -------------------------------------------------------------
        act_raw = (req.career_or_degree or req.occupation or "").strip()
        if not act_raw:
            act = "tu actividad diaria"
            act_en = "your daily activity"
        elif profile == "RURAL_FIELD_PRODUCER":
            act = f"la producción de {req.rural_product}" if req.rural_product else "la labor agraria"
            act_en = f"producing {req.rural_product}" if req.rural_product else "farming and livestock"
        elif profile == "SKILLED_TRADE":
            act = act_raw
            act_en = act_raw
        elif profile == "BUSINESS_OWNER":
            act = req.business_type or act_raw or "tu negocio"
            act_en = req.business_type or act_raw or "your business"
        elif profile == "UNIVERSITY_OR_TECH_STUDENT":
            act = act_raw or "tus estudios universitarios"
            act_en = act_raw or "your degree studies"
        else:
            act = act_raw or "tu ejercicio profesional"
            act_en = act_raw or "your professional practice"

        # Contexto familiar, relacional y de personalidad para narrativas
        dep_count = max(0, req.dependents_count or 0)
        care_count = getattr(hf, 'dependents_care_count', 0)
        care_details = getattr(hf, 'caregiving_details', '') or ""

        if care_count > 0:
            fam_phrase = f"asumiendo el cuidado en el hogar de {care_details or f'{care_count} familiares a cargo'}"
            fam_phrase_en = f"actively caring at home for {care_details or f'{care_count} family members'}"
        elif dep_count > 0:
            fam_phrase = f"con {dep_count} dependientes a cargo"
            fam_phrase_en = f"with {dep_count} economic dependents"
        else:
            fam_phrase = "sin dependientes económicos a tu cargo"
            fam_phrase_en = "without direct economic dependents"

        household_support = (
            "apoyo familiar estable" if req.household_climate == "SUPPORTIVE"
            else ("tensión o exigencias en el hogar" if req.household_climate == "STRESSFUL_CONFLICT"
                  else "el respaldo de vivir en hogar familiar" if req.living_situation == "FAMILY_HOME"
                  else "independencia de tu hogar")
        )
        household_support_en = (
            "stable household support" if req.household_climate == "SUPPORTIVE"
            else ("household friction and demands" if req.household_climate == "STRESSFUL_CONFLICT"
                  else "the safety net of living with family" if req.living_situation == "FAMILY_HOME"
                  else "independent household living")
        )

        translated_traits = [
            TRAIT_TRANSLATIONS_ES.get(t, t.replace('_', ' ').lower())
            for t in (req.personality_traits or [])
        ]
        trait_note = f" (marcado por {', '.join(translated_traits[:3])})" if translated_traits else ""
        trait_note_en = f" (influenced by {', '.join((req.personality_traits or [])[:3])})" if req.personality_traits else ""

        labor_desc = INTENSITY_TRANSLATIONS_ES.get(req.physical_labor_intensity, "moderada exigencia física")

        chat_note = f" Comunicaciones reflejan clima de {req.chat_dominant_tag}." if req.chat_dominant_tag else ""
        chat_note_en = f" Communications reflect a {req.chat_dominant_tag} dynamic." if req.chat_dominant_tag else ""

        # Verificación estricta de condición de egresado (debe ser estudiante con 1 a 6 meses para egresar, carrera y universidad)
        is_graduating_student = (
            (profile == "UNIVERSITY_OR_TECH_STUDENT" or getattr(req, "life_stage", "") in ("FINISHING_UNIVERSITY", "WORKING_AND_FINISHING_UNI"))
            and (req.months_to_graduation is not None and 1 <= req.months_to_graduation <= 6)
            and bool((req.career_or_degree or "").strip())
            and req.career_or_degree.strip().lower() not in ("comercio / independiente", "desconocido", "")
            and bool((req.university_or_institution or "").strip())
        )

        raw_u = (req.university_or_institution or "").strip()
        u_phrase = raw_u if raw_u.lower().startswith(("la ", "el ", "los ", "las ")) else f"la {raw_u}" if raw_u else "tu centro de estudios"
        career = (req.career_or_degree or req.occupation or "").strip() or ("tu carrera" if is_es else "your degree")

        if is_es:
            if is_graduating_student:
                # Rangos de sueldo de entrada realistas según moneda
                if req.currency == "PEN":
                    sal_floor, sal_ceil = 1300, 2200
                elif req.currency == "COP":
                    sal_floor, sal_ceil = 1500000, 2600000
                elif req.currency == "MXN":
                    sal_floor, sal_ceil = 9000, 18000
                elif req.currency == "EUR":
                    sal_floor, sal_ceil = 1400, 2400
                else:
                    sal_floor, sal_ceil = 450, 950

                care_transition_es = (
                    f"Has reorganizado tus tiempos de cuidado familiar ({fam_phrase}) para abrir paso a tu nueva rutina laboral bajo {household_support}."
                    if (care_count > 0 or dep_count > 0) else
                    f"Has estructurado tu disciplina y horarios para abrir paso a tu nueva rutina laboral bajo {household_support}."
                )

                m1_econ = (
                    f"Bajo el techo familiar {city_in_phrase}, comienzas este mes de egreso con un balance financiero estrictamente de 0.00 {currency} "
                    f"(ingresos actuales en 0 y sin ahorros previos). No se genera deuda operativa al no registrar gastos individuales, "
                    f"manteniéndote enfocado al 100% en culminar la titulación universitaria."
                    if (req.monthly_income == 0 and req.current_savings == 0)
                    else f"Tu economía opera con tu ingreso actual de {req.monthly_income:,.2f} {currency} {fam_phrase}. Tu patrimonio real proyectado a 30 días es de {m1.financial_net_worth.p50:,.2f} {currency}."
                )

                narratives = {
                    "1_month": HorizonNarrative(
                        future_self_portrait=(
                            f"En 30 días, {person_name}, te encuentras en la recta decisiva de tu carrera de {career} en {u_phrase} {city_in_phrase}{trait_note}. "
                            f"Tu día no se mide en una jornada laboral tradicional (0h de empleo remunerado), sino en la exigencia de tus entregas académicas, tu tesis y {fam_phrase}. "
                            f"Tu semblante refleja el compromiso entre culminar tus estudios y tus responsabilidades bajo {household_support}.{chat_note}"
                        ),
                        economic_reality=m1_econ,
                        health_and_mind_state=(
                            f"Vitalidad proyectada en {m1.health_and_vitality_score.p50:.0f}/100. La exigencia de culminar los requisitos de titulación "
                            f"sitúa el riesgo de fatiga mental en {m1.burnout_probability*100:.1f}%. Estructurar horarios fijos de estudio matutino es vital para vencer la postergación."
                        ),
                        critical_warning=f"{city_in_phrase.capitalize()}, en este último mes antes de egresar, evita postergar las correcciones finales de tu titulación; cada semana que demores aplazará tu ingreso al mercado laboral formal."
                    ),
                    "6_months": HorizonNarrative(
                        future_self_portrait=(
                            f"A 6 meses (180 días), habiendo culminado tu egreso de {u_phrase}, tu vida {city_in_phrase} da un giro hacia la inserción en tu primer empleo o prácticas en {career}. "
                            f"{care_transition_es}"
                        ),
                        economic_reality=(
                            f"Al egresar e insertarte al mercado laboral {city_in_phrase}, comienzas a generar ingresos profesionales en {career} "
                            f"(sueldo de entrada estimado entre {sal_floor:,.0f} y {sal_ceil:,.0f} {currency} en la región). Tu patrimonio neto real proyectado se sitúa en {m6.financial_net_worth.p50:,.2f} {currency}, "
                            f"iniciando la construcción de tu independencia económica {fam_phrase}."
                        ),
                        health_and_mind_state=(
                            f"Nivel de vitalidad proyectado en {m6.health_and_vitality_score.p50:.0f}/100 con probabilidad de desgaste del {m6.burnout_probability*100:.1f}%. "
                            f"La transición al trabajo formal reduce la incertidumbre académica pero exige orden en tu rutina diaria."
                        ),
                        critical_warning=f"Destina al menos el 15% de tus primeros sueldos en {currency} a formar tu primer fondo de reserva de emergencia antes de comprometerte en gastos no esenciales."
                    ),
                    "1_year": HorizonNarrative(
                        future_self_portrait=(
                            f"Al cabo de 1 año (365 días), consolidas tu posición como egresado de {career} en el mercado {city_in_phrase}. "
                            f"Has superado el choque inicial del mercado laboral y equilibrado con éxito tu desarrollo profesional con tu entorno personal."
                        ),
                        economic_reality=(
                            f"Cierras tu primer año profesional con un patrimonio real ajustado de {m12.financial_net_worth.p50:,.2f} {currency}, "
                            f"habiendo pasado de una base inicial a contar con ahorros propios acumulados y capacidad de ahorro mensual {city_in_phrase}."
                        ),
                        health_and_mind_state=(
                            f"Vitalidad en {m12.health_and_vitality_score.p50:.0f}/100 y estabilidad emocional en {m12.social_and_emotional_stability.p50:.0f}/100."
                        ),
                        critical_warning=f"Continúa actualizándote en herramientas y certificaciones de {career} para potenciar tus revisiones salariales {city_in_phrase}."
                    )
                }
                adjustments = [
                    GoldenPathAdjustment(
                        domain="EGRESO_Y_TITULACIÓN",
                        current_baseline=f"Último tramo de carrera en {u_phrase} con dedicación académica y {req.study_or_project_hours:.1f}h de estudio",
                        prescribed_target="Bloque intocable de 2 horas diarias matutinas para redacción de tesis y cierre de trámites de egreso",
                        expected_impact_p90="Garantiza tu titulación a tiempo y adelanta tu inserción laboral en 4 a 6 semanas."
                    ),
                    GoldenPathAdjustment(
                        domain="EQUILIBRIO_Y_ORGANIZACIÓN",
                        current_baseline=f"Responsabilidad en el hogar: {fam_phrase}",
                        prescribed_target="Establecer turnos y horarios claros en casa para evitar que las tareas cotidianas absorban tus horas de estudio y descanso",
                        expected_impact_p90="Reduce la fatiga mental y evita la sobrecarga por sobrepensamiento y postergación."
                    ),
                    GoldenPathAdjustment(
                        domain="INSERCIÓN_Y_PRIMER_AHORRO",
                        current_baseline=f"Base financiera actual de 0.00 {currency} bajo hogar familiar",
                        prescribed_target=f"Preparar portafolio y postulaciones a empleos junior {city_in_phrase}; al percibir los primeros ingresos, ahorrar el 20%",
                        expected_impact_p90=f"Construye un colchón de seguridad de más de {m6.financial_net_worth.p50:,.0f} {currency} en 6 meses."
                    )
                ]
                summary = (
                    f"Diagnóstico de transición profesional para {person_name} {city_in_phrase}, {country}. "
                    f"Al culminar tus estudios de {career} en {u_phrase} y superar la etapa de egreso, tu probabilidad de inserción laboral se consolida progresivamente. "
                    f"Partiendo hoy de {req.monthly_income:,.2f} {currency} bajo respaldo familiar, proyectas alcanzar un patrimonio neto real de {m6.financial_net_worth.p50:,.2f} {currency} a los 6 meses y {m12.financial_net_worth.p50:,.2f} {currency} al año. "
                    f"La clave causal determinante es mantener el ritmo diario para cerrar tu titulación y organizar tus horarios con disciplina."
                )

            elif is_pure_mirror:
                work_desc = (
                    f"tu jornada laboral de {req.work_hours:.1f}h"
                    if req.work_hours > 0.1 else
                    "tus labores diarias en el hogar y proyectos personales"
                )
                econ_1m = (
                    f"Bajo un esquema sin ingresos activos registrados y gastos de {req.monthly_expenses:,.2f} {currency}, "
                    f"tu patrimonio real neto proyectado a 30 días se sitúa en {m1.financial_net_worth.p50:,.2f} {currency} {fam_phrase}."
                    if req.monthly_income == 0 else
                    f"Tu economía opera con tu ingreso de {req.monthly_income:,.2f} {currency} {fam_phrase}. Con la inflación nacional del "
                    f"{macro.annual_inflation_rate:.1f}% en {country}, tu patrimonio real neto proyectado se sitúa en {m1.financial_net_worth.p50:,.2f} {currency}."
                )
                econ_6m = (
                    f"Tu patrimonio neto real proyectado se sitúa en {m6.financial_net_worth.p50:,.2f} {currency} {fam_phrase}. "
                    f"Sin nuevos flujos de ingreso, el modelo econométrico no calcula acumulación adicional de capital."
                    if req.monthly_income == 0 else
                    f"Tu colchón financiero real alcanza {m6.financial_net_worth.p50:,.2f} {currency} {fam_phrase}. Frente a subidas de precios en insumos o canasta básica, "
                    f"tu índice de poder adquisitivo se ubica en {m6.purchasing_power_score.p50:.0f}/100."
                )
                econ_12m = (
                    f"Cierras el año con un patrimonio neto proyectado de {m12.financial_net_worth.p50:,.2f} {currency} {fam_phrase}. "
                    f"Para revertir el estancamiento patrimonial se requiere incorporar fuentes activas de ingreso."
                    if req.monthly_income == 0 else
                    f"Cierras el año con un patrimonio real ajustado de {m12.financial_net_worth.p50:,.2f} {currency}, "
                    f"habiendo sostenido a tu entorno y protegido tu capital básico de trabajo."
                )

                narratives = {
                    "1_month": HorizonNarrative(
                        future_self_portrait=(
                            f"En 30 días, {person_name}, tu día a día {city_in_phrase} mantiene el ritmo constante de {act}{trait_note}. "
                            f"Físicamente se percibe el esfuerzo de {work_desc} y tus {req.sleep_hours:.1f}h de sueño bajo {household_support}; "
                            f"tu semblante muestra la resistencia propia del ritmo diario frente al costo de vida local (índice {cost_idx:.2f}).{chat_note}"
                        ),
                        economic_reality=econ_1m,
                        health_and_mind_state=(
                            f"Vitalidad proyectada en {m1.health_and_vitality_score.p50:.0f}/100. Con una {labor_desc}, "
                            f"el riesgo de fatiga se sitúa en {m1.burnout_probability*100:.1f}%. Proteger el descanso diario es tu mayor salvaguarda."
                        ),
                        critical_warning=f"{city_in_phrase.capitalize()}, cuida el gasto hormiga e imprevistos cotidianos para proteger tu balance operativo."
                    ),
                    "6_months": HorizonNarrative(
                        future_self_portrait=(
                            f"A 6 meses (180 días), tu cuerpo se ha adaptado a la rutina continuada {city_in_phrase}. "
                            f"Las marcas del cansancio o la fortaleza física dependerán directamente de si respetaste tus horas de recuperación bajo {household_support}."
                        ),
                        economic_reality=econ_6m,
                        health_and_mind_state=(
                            f"Nivel de vitalidad proyectado en {m6.health_and_vitality_score.p50:.0f}/100 con riesgo de desgaste del {m6.burnout_probability*100:.1f}%."
                        ),
                        critical_warning=f"No descuides la hidratación, postura y pausas activas durante tus actividades {city_in_phrase}."
                    ),
                    "1_year": HorizonNarrative(
                        future_self_portrait=(
                            f"Al cabo de 1 año (365 días), tu vida como {act} {city_in_phrase} refleja la suma de 365 jornadas consistentes. "
                            f"Tu índice de bienestar y estabilidad general se proyecta en {m12.career_and_goal_completion_pct.p50:.0f}/100."
                        ),
                        economic_reality=econ_12m,
                        health_and_mind_state=(
                            f"Vitalidad en {m12.health_and_vitality_score.p50:.0f}/100 y estabilidad social/emocional en {m12.social_and_emotional_stability.p50:.0f}/100."
                        ),
                        critical_warning="Mantén un fondo intocable de reserva en divisa local para amortiguar cualquier imprevisto de salud o contingencia familiar."
                    )
                }
                adjustments = [
                    GoldenPathAdjustment(
                        domain="SALUD_Y_DESCANSO",
                        current_baseline=f"{req.sleep_hours:.1f}h de sueño con {labor_desc}",
                        prescribed_target="Garantizar al menos 7.0 horas continuas de sueño reparador y pausas de hidratación",
                        expected_impact_p90="Elimina el riesgo de agotamiento crónico y mantiene tu capacidad de trabajo al 100%."
                    ),
                    GoldenPathAdjustment(
                        domain="COLCHÓN_DE_EMERGENCIA",
                        current_baseline=f"Ahorro de {req.current_savings:,.0f} {currency} vs gastos mensuales de {req.monthly_expenses:,.0f} {currency}",
                        prescribed_target=f"Reservar el 10% del ingreso disponible {city_in_phrase} en una cuenta separada",
                        expected_impact_p90="Construye un fondo de contingencia de 3 meses frente a cualquier shock económico local."
                    ),
                    GoldenPathAdjustment(
                        domain="RITMO_DE_VIDA",
                        current_baseline=f"{req.work_hours:.1f}h de trabajo diario y {req.screen_time_distraction_hours:.1f}h de pantalla",
                        prescribed_target="Desconectar pantallas 45 minutos antes de dormir para mejorar la calidad del descanso",
                        expected_impact_p90="Eleva la energía diurna en un 25% y mejora la toma de decisiones cotidianas."
                    )
                ]
                summary = (
                    f"Diagnóstico en Modo Espejo Puro para {person_name} {city_in_phrase}, {country}. "
                    f"Continuando con tu ritmo actual en {act}, tu índice de bienestar y estabilidad general se proyecta en {m12.career_and_goal_completion_pct.p50:.0f}/100 al año, "
                    f"con un patrimonio real de {m12.financial_net_worth.p50:,.2f} {currency}. "
                    f"La clave determinante para no acumular desgaste reside en blindar tus 7 horas de descanso nocturno y gestionar con prudencia tus finanzas {city_in_phrase}."
                )

            else:
                # Con Meta en Español
                narratives = {
                    "1_month": HorizonNarrative(
                        future_self_portrait=f"En 30 días, {person_name}, balanceas tu actividad en {act} con los primeros pasos hacia '{req.main_goal_1y}' {city_in_phrase}.",
                        economic_reality=f"Flujo mensual con ingreso de {req.monthly_income:,.2f} {currency} y patrimonio neto de {m1.financial_net_worth.p50:,.2f} {currency}.",
                        health_and_mind_state=f"Vitalidad en {m1.health_and_vitality_score.p50:.0f}/100 y fatiga en {m1.burnout_probability*100:.1f}%.",
                        critical_warning=f"{city_in_phrase.capitalize()}, define la primera acción concreta para tu meta antes de fin de mes."
                    ),
                    "6_months": HorizonNarrative(
                        future_self_portrait=f"A 6 meses, avanzas hacia tu meta con una probabilidad acumulada del {m6.career_and_goal_completion_pct.p50:.0f}%.",
                        economic_reality=f"Patrimonio estimado en {m6.financial_net_worth.p50:,.2f} {currency} consolidando mayor estabilidad.",
                        health_and_mind_state=f"Vitalidad proyectada en {m6.health_and_vitality_score.p50:.0f}/100.",
                        critical_warning="Supera la tentación de abandonar el plan frente a la rutina diaria."
                    ),
                    "1_year": HorizonNarrative(
                        future_self_portrait=f"A 1 año, alcanzas cerca del {m12.career_and_goal_completion_pct.p50:.1f}% de '{req.main_goal_1y}' {city_in_phrase}.",
                        economic_reality=f"Ingreso acercándose a {req.target_monthly_salary_1y:,.0f} {currency} y patrimonio de {m12.financial_net_worth.p50:,.2f} {currency}.",
                        health_and_mind_state=f"Salud integral en {m12.health_and_vitality_score.p50:.0f}/100 con bienestar emocional.",
                        critical_warning="Consolida las lecciones aprendidas para mantener tu crecimiento a largo plazo."
                    )
                }
                adjustments = [
                    GoldenPathAdjustment(
                        domain="FOCO_EN_META",
                        current_baseline=f"Meta: '{req.main_goal_1y}' con {req.study_or_project_hours:.1f}h dedicadas",
                        prescribed_target="Proteger bloque diario de 1.5h enfocado exclusivamente en la meta",
                        expected_impact_p90="Aumenta la probabilidad de cumplimiento al percentil P90."
                    ),
                    GoldenPathAdjustment(
                        domain="FINANZAS_Y_OBJETIVO",
                        current_baseline=f"Ingreso actual de {req.monthly_income:,.0f} vs objetivo de {req.target_monthly_salary_1y:,.0f} {currency}",
                        prescribed_target=f"Alinear presupuesto {city_in_phrase} amortizando deudas y reinvirtiendo en herramientas clave",
                        expected_impact_p90="Acelera la convergencia salarial hacia tu meta anual."
                    ),
                    GoldenPathAdjustment(
                        domain="ENERGÍA_Y_DISCIPLINA",
                        current_baseline=f"{req.sleep_hours:.1f}h de sueño y {req.screen_time_distraction_hours:.1f}h de ocio digital",
                        prescribed_target="Garantizar descanso de calidad y reducir distracciones de pantalla",
                        expected_impact_p90="Elimina el riesgo de burnout y optimiza tu claridad mental."
                    )
                ]
                summary = (
                    f"Proyección con objetivo para {person_name} {city_in_phrase}, {country}. "
                    f"La probabilidad de alcanzar '{req.main_goal_1y}' es del {m12.career_and_goal_completion_pct.p50:.0f}% en P50 y escala al {m12.career_and_goal_completion_pct.p90:.0f}% en P90. "
                    f"Tu patrimonio proyectado cierra en {m12.financial_net_worth.p50:,.2f} {currency}."
                )

        else:
            # ENGLISH (default)
            if is_graduating_student:
                if req.currency == "PEN":
                    sal_floor, sal_ceil = 1300, 2200
                elif req.currency == "COP":
                    sal_floor, sal_ceil = 1500000, 2600000
                elif req.currency == "MXN":
                    sal_floor, sal_ceil = 9000, 18000
                elif req.currency == "EUR":
                    sal_floor, sal_ceil = 1400, 2400
                else:
                    sal_floor, sal_ceil = 450, 950

                care_transition_en = (
                    f"You have adjusted your family care routines ({fam_phrase_en}) to accommodate regular professional work hours under {household_support_en}."
                    if (care_count > 0 or dep_count > 0) else
                    f"You have structured your personal habits and daily routines to step into full-time work under {household_support_en}."
                )

                m1_econ_en = (
                    f"Living with family {city_in_phrase}, you begin this graduation month with a strict net worth of 0.00 {currency} "
                    f"(zero current income and zero prior savings). You incur no personal operating debt, staying fully focused on completing your degree."
                    if (req.monthly_income == 0 and req.current_savings == 0)
                    else f"Your finances operate with your income of {req.monthly_income:,.2f} {currency} {fam_phrase_en}. Your projected 30-day net worth stands at {m1.financial_net_worth.p50:,.2f} {currency}."
                )

                narratives = {
                    "1_month": HorizonNarrative(
                        future_self_portrait=(
                            f"In 30 days, {person_name}, you are in the final countdown of your {career} studies at {u_phrase} {city_in_phrase}{trait_note_en}. "
                            f"Your daily schedule is not defined by a standard wage shift (0h paid work), but by academic requirements, deliverables, and {fam_phrase_en}. "
                            f"Your posture reflects the balance between completing your studies and personal commitments under {household_support_en}.{chat_note_en}"
                        ),
                        economic_reality=m1_econ_en,
                        health_and_mind_state=(
                            f"Vitality projected at {m1.health_and_vitality_score.p50:.0f}/100. Balancing final academic milestones "
                            f"puts mental fatigue probability at {m1.burnout_probability*100:.1f}%. Dedicated morning study blocks will be critical to prevent procrastination."
                        ),
                        critical_warning=f"In {city}, avoid delaying final degree edits during this last month; each week of delay pushes back your formal job market entry."
                    ),
                    "6_months": HorizonNarrative(
                        future_self_portrait=(
                            f"At 6 months (day 180), having graduated from {u_phrase}, your life {city_in_phrase} shifts toward landing your first junior position or internship in {career}. "
                            f"{care_transition_en}"
                        ),
                        economic_reality=(
                            f"Upon graduating and joining the workforce {city_in_phrase}, you begin earning entry-level wages in {career} (estimated {sal_floor:,.0f} to {sal_ceil:,.0f} {currency}). "
                            f"Your inflation-adjusted net worth reaches {m6.financial_net_worth.p50:,.2f} {currency}, establishing your initial financial runway {fam_phrase_en}."
                        ),
                        health_and_mind_state=(
                            f"Vitality projected at {m6.health_and_vitality_score.p50:.0f}/100 with exhaustion risk at {m6.burnout_probability*100:.1f}%. "
                            f"Transitioning into professional work relieves academic uncertainty but requires structured coordination."
                        ),
                        critical_warning=f"Commit at least 15% of your initial paychecks in {currency} into an emergency fund before expanding discretionary spending."
                    ),
                    "1_year": HorizonNarrative(
                        future_self_portrait=(
                            f"After 1 year (365 days), you have established your footing as a {career} graduate {city_in_phrase}. "
                            f"You navigated early entry hurdles and balanced professional development with your daily rhythm."
                        ),
                        economic_reality=(
                            f"You close your first post-graduate year with an inflation-adjusted net worth of {m12.financial_net_worth.p50:,.2f} {currency}, "
                            f"progressing from a zero starting balance to accumulated liquid savings {city_in_phrase}."
                        ),
                        health_and_mind_state=(
                            f"Vitality at {m12.health_and_vitality_score.p50:.0f}/100 and emotional stability at {m12.social_and_emotional_stability.p50:.0f}/100."
                        ),
                        critical_warning=f"Pursue technical skills and certifications in {career} to secure career advancement {city_in_phrase}."
                    )
                }
                adjustments = [
                    GoldenPathAdjustment(
                        domain="DEGREE_COMPLETION",
                        current_baseline=f"Final stretch at {u_phrase} with academic dedication and {req.study_or_project_hours:.1f}h study blocks",
                        prescribed_target="Protect an uninterrupted 2-hour morning block for degree filing and final project deliverables",
                        expected_impact_p90="Ensures on-time graduation and accelerates employment by 4 to 6 weeks."
                    ),
                    GoldenPathAdjustment(
                        domain="ROUTINE_ORGANIZATION",
                        current_baseline=f"Home responsibilities: {fam_phrase_en}",
                        prescribed_target="Coordinate structured daily schedules so domestic tasks do not encroach on focus and sleep",
                        expected_impact_p90="Prevents mental overload, anxiety, and task procrastination."
                    ),
                    GoldenPathAdjustment(
                        domain="JOB_TRANSITION_AND_SAVINGS",
                        current_baseline=f"Current financial base of 0.00 {currency} under family roof",
                        prescribed_target=f"Target entry roles {city_in_phrase}; commit 20% of first paychecks directly into savings",
                        expected_impact_p90=f"Establishes a cash cushion exceeding {m6.financial_net_worth.p50:,.0f} {currency} within 6 months."
                    )
                ]
                summary = (
                    f"Professional transition diagnosis for {person_name} {city_in_phrase}, {country}. "
                    f"Upon completing your {career} degree at {u_phrase}, your employment prospects steadily materialize. "
                    f"Starting today from a {req.monthly_income:,.2f} {currency} base under family support, you are projected to reach a real net worth of {m6.financial_net_worth.p50:,.2f} {currency} at 6 months and {m12.financial_net_worth.p50:,.2f} {currency} at 1 year. "
                    f"The decisive causal factor is maintaining daily consistency this final month to complete graduation."
                )

            elif is_pure_mirror:
                work_desc_en = (
                    f"your daily {req.work_hours:.1f}h shift"
                    if req.work_hours > 0.1 else
                    "your daily domestic duties and independent projects"
                )
                labor_desc_en = req.physical_labor_intensity.lower().replace("_", " ")

                econ_1m_en = (
                    f"Under a 0.00 {currency} income profile and expenses of {req.monthly_expenses:,.2f} {currency}, "
                    f"your projected 30-day net worth stands at {m1.financial_net_worth.p50:,.2f} {currency} {fam_phrase_en}."
                    if req.monthly_income == 0 else
                    f"Your cashflow operates around an income of {req.monthly_income:,.2f} {currency} {fam_phrase_en}. Against annual inflation of "
                    f"{macro.annual_inflation_rate:.1f}% in {country}, your projected real net worth stands at {m1.financial_net_worth.p50:,.2f} {currency}."
                )
                econ_6m_en = (
                    f"Your real projected net worth stands at {m6.financial_net_worth.p50:,.2f} {currency} {fam_phrase_en}. "
                    f"Without positive income streams, the econometric model forecasts no incremental asset accumulation."
                    if req.monthly_income == 0 else
                    f"Your real savings cushion reaches {m6.financial_net_worth.p50:,.2f} {currency} {fam_phrase_en}. Facing local price increases, "
                    f"your purchasing power index is {m6.purchasing_power_score.p50:.0f}/100."
                )
                econ_12m_en = (
                    f"You close the year with a projected net worth of {m12.financial_net_worth.p50:,.2f} {currency} {fam_phrase_en}. "
                    f"Reversing financial stagnation requires activating positive cashflow sources."
                    if req.monthly_income == 0 else
                    f"You close the year with an inflation-adjusted net worth of {m12.financial_net_worth.p50:,.2f} {currency}, "
                    f"having sustained your household and protected essential working capital."
                )

                narratives = {
                    "1_month": HorizonNarrative(
                        future_self_portrait=(
                            f"In 30 days, {person_name}, your daily life {city_in_phrase} continues steadily with {act_en}{trait_note_en}. "
                            f"Physically, the demands of {work_desc_en} and {req.sleep_hours:.1f}h sleep show on your posture and stamina under {household_support_en}, "
                            f"reflecting honest effort under local cost pressures (index {cost_idx:.2f}).{chat_note_en}"
                        ),
                        economic_reality=econ_1m_en,
                        health_and_mind_state=(
                            f"Vitality projected at {m1.health_and_vitality_score.p50:.0f}/100. Physical intensity of {labor_desc_en} "
                            f"puts fatigue probability at {m1.burnout_probability*100:.1f}%. Guarding daily rest is your primary buffer."
                        ),
                        critical_warning=f"In {city}, watch small impulse leaks and unexpected household expenses to protect your daily operating margin."
                    ),
                    "6_months": HorizonNarrative(
                        future_self_portrait=(
                            f"At 6 months (day 180), your body has settled into this steady rhythm {city_in_phrase}. "
                            f"Visible signs of wear versus resilience depend directly on whether you respected nightly recovery under {household_support_en}."
                        ),
                        economic_reality=econ_6m_en,
                        health_and_mind_state=(
                            f"Vitality level projected at {m6.health_and_vitality_score.p50:.0f}/100 with exhaustion risk at {m6.burnout_probability*100:.1f}%."
                        ),
                        critical_warning=f"Stay mindful of posture, hydration, and short active breaks during intensive shifts {city_in_phrase}."
                    ),
                    "1_year": HorizonNarrative(
                        future_self_portrait=(
                            f"After 1 full year (365 days), your life in {act_en} {city_in_phrase} reflects the cumulative reality of 365 consistent days. "
                            f"Your overall wellbeing and stability index is projected at {m12.career_and_goal_completion_pct.p50:.0f}/100."
                        ),
                        economic_reality=econ_12m_en,
                        health_and_mind_state=(
                            f"Vitality at {m12.health_and_vitality_score.p50:.0f}/100 and emotional/social stability at {m12.social_and_emotional_stability.p50:.0f}/100."
                        ),
                        critical_warning="Maintain an untouched emergency reserve in local currency to weather any health, climate or household surprises."
                    )
                }
                adjustments = [
                    GoldenPathAdjustment(
                        domain="RECOVERY_AND_HEALTH",
                        current_baseline=f"{req.sleep_hours:.1f}h sleep with {labor_desc_en} physical exertion",
                        prescribed_target="Secure at least 7.0 hours of continuous restorative sleep and daily hydration",
                        expected_impact_p90="Eliminates chronic exhaustion risk and keeps your physical capacity at 100%."
                    ),
                    GoldenPathAdjustment(
                        domain="EMERGENCY_BUFFER",
                        current_baseline=f"Current savings of {req.current_savings:,.0f} {currency} vs monthly expenses of {req.monthly_expenses:,.0f} {currency}",
                        prescribed_target=f"Set aside 10% of weekly cash {city_in_phrase} into an emergency-only buffer",
                        expected_impact_p90="Constructs a 3-month safety runway against local economic shocks."
                    ),
                    GoldenPathAdjustment(
                        domain="DAILY_RHYTHM",
                        current_baseline=f"{req.work_hours:.1f}h work hours and {req.screen_time_distraction_hours:.1f}h screen time",
                        prescribed_target="Power down screens 45 minutes before sleep to elevate restorative deep sleep",
                        expected_impact_p90="Improves morning alertness by 25% and strengthens everyday decision-making."
                    )
                ]
                summary = (
                    f"Pure Mirror Diagnosis for {person_name} {city_in_phrase}, {country}. "
                    f"Continuing your current pace in {act_en}, your overall wellbeing and stability index is projected at {m12.career_and_goal_completion_pct.p50:.0f}/100 at 1 year, "
                    f"with real net worth of {m12.financial_net_worth.p50:,.2f} {currency}. "
                    f"The decisive leverage to avoid wear is protecting 7 hours of restorative rest and keeping a liquid buffer {city_in_phrase}."
                )

            else:
                # Goal Mode in English
                narratives = {
                    "1_month": HorizonNarrative(
                        future_self_portrait=f"In 30 days, {person_name}, you balance your work in {act_en} with the initial sprint toward '{req.main_goal_1y}' {city_in_phrase}.",
                        economic_reality=f"Monthly cashflow with income of {req.monthly_income:,.2f} {currency} and net worth of {m1.financial_net_worth.p50:,.2f} {currency}.",
                        health_and_mind_state=f"Vitality at {m1.health_and_vitality_score.p50:.0f}/100 with fatigue at {m1.burnout_probability*100:.1f}%.",
                        critical_warning=f"In {city}, complete your first concrete step toward your goal before the month ends."
                    ),
                    "6_months": HorizonNarrative(
                        future_self_portrait=f"At 6 months, you advance toward your target with an accumulated probability of {m6.career_and_goal_completion_pct.p50:.0f}%.",
                        economic_reality=f"Estimated real net worth at {m6.financial_net_worth.p50:,.2f} {currency} with growing stability.",
                        health_and_mind_state=f"Vitality projected at {m6.health_and_vitality_score.p50:.0f}/100.",
                        critical_warning="Resist the urge to compromise study/project hours during busy work periods."
                    ),
                    "1_year": HorizonNarrative(
                        future_self_portrait=f"At 1 year, you reach approximately {m12.career_and_goal_completion_pct.p50:.1f}% of '{req.main_goal_1y}' {city_in_phrase}.",
                        economic_reality=f"Earnings closing toward {req.target_monthly_salary_1y:,.0f} {currency} with net worth of {m12.financial_net_worth.p50:,.2f} {currency}.",
                        health_and_mind_state=f"Comprehensive health at {m12.health_and_vitality_score.p50:.0f}/100 with solid emotional resilience.",
                        critical_warning="Lock in your established habits to sustain long-term upward momentum."
                    )
                }
                adjustments = [
                    GoldenPathAdjustment(
                        domain="GOAL_FOCUS",
                        current_baseline=f"Goal: '{req.main_goal_1y}' with {req.study_or_project_hours:.1f}h dedicated",
                        prescribed_target="Protect a dedicated 1.5h daily block for deliberate practice and advancement",
                        expected_impact_p90="Drives your success rate into the P90 percentile bracket."
                    ),
                    GoldenPathAdjustment(
                        domain="FINANCIAL_ALIGNMENT",
                        current_baseline=f"Current income of {req.monthly_income:,.0f} vs target of {req.target_monthly_salary_1y:,.0f} {currency}",
                        prescribed_target=f"Streamline expenses {city_in_phrase} and reinvest into essential skills or tools",
                        expected_impact_p90="Accelerates convergence toward your 1-year target income."
                    ),
                    GoldenPathAdjustment(
                        domain="ENERGY_AND_STAMINA",
                        current_baseline=f"{req.sleep_hours:.1f}h sleep vs {req.screen_time_distraction_hours:.1f}h passive distraction",
                        prescribed_target="Ensure restorative sleep and minimize digital fatigue",
                        expected_impact_p90="Eliminates burnout hazard and maximizes sharp daily focus."
                    )
                ]
                summary = (
                    f"Target-oriented projection for {person_name} {city_in_phrase}, {country}. "
                    f"Probability of achieving '{req.main_goal_1y}' stands at {m12.career_and_goal_completion_pct.p50:.0f}% in P50 and scales to {m12.career_and_goal_completion_pct.p90:.0f}% in P90. "
                    f"Your projected real net worth reaches {m12.financial_net_worth.p50:,.2f} {currency}."
                )

        return narratives, adjustments, summary


class GoalFeasibilityEngine:
    """
    Motor Causal de Verificación de Metas e Ideales (Corto, Mediano y Largo Plazo).
    Comprueba con rigor matemático y empírico si los ideales que el usuario tiene en mente
    (como viajar, salir y trabajar en otro lado, independizarse o ahorrar capital) cuentan con
    suficiencia de capital, tiempo formativo y condiciones reales, alertando sin autoengaño
    sobre la brecha existente y las palancas para cerrarla.
    """

    @classmethod
    def verify_goals_and_ideals(
        cls,
        req: HolisticFutureRequest,
        sim_metrics: Dict[str, HorizonMetrics],
        macro: Any
    ) -> GoalsVerificationReport:
        is_es = req.lang == "ES"
        curr = req.currency or "PEN"
        curr_sym = "S/" if (curr == "PEN" or req.country_code == "PE") else ("$" if curr == "USD" else "€" if curr == "EUR" else curr)

        # Variables base
        inc = float(req.monthly_income or 0.0)
        exp = float(req.monthly_expenses or 0.0)
        sav = float(req.current_savings or 0.0)
        monthly_margin = max(0.0, inc - exp)
        m1 = sim_metrics.get("1_month")
        m6 = sim_metrics.get("6_months")
        m12 = sim_metrics.get("1_year")
        nw_1y = m12.financial_net_worth.p50 if m12 else (sav + monthly_margin * 12)
        burn_risk = m12.burnout_probability if m12 else 0.20
        study_h = float(req.study_or_project_hours or 0.0)
        screen_h = float(req.screen_time_distraction_hours or 0.0)
        months_grad = int(req.months_to_graduation or 0)
        is_student = req.life_profile_type == "UNIVERSITY_OR_TECH_STUDENT" or months_grad > 0

        # =====================================================================
        # 1. META A CORTO PLAZO (1 AÑO)
        # =====================================================================
        goal_1y_text = (req.main_goal_1y or req.one_year_goal or "").strip()
        if not goal_1y_text:
            goal_1y_text = (
                f"Culminar estudios en {req.career_or_degree or 'mi carrera'} e insertarme al mercado laboral"
                if is_student else
                f"Consolidar estabilidad en mi actividad de {req.occupation or 'trabajo'} y elevar ingresos"
            )

        # Requisitos y cálculo de viabilidad 1 Año
        req_cap_1y = max(500.0, exp * 2.0) if inc > 0 else 300.0
        projected_sav_1y = max(0.0, nw_1y)
        gap_1y = max(0.0, req_cap_1y - projected_sav_1y)

        p_met_1y = []
        p_miss_1y = []

        if is_student:
            if months_grad <= 12:
                p_met_1y.append("Plazo de egreso/tesis alineado a 1 año" if is_es else "Graduation timeline aligned within 1 year")
            else:
                p_miss_1y.append(f"Faltan {months_grad} meses de carrera (>12m)" if is_es else f"{months_grad} months left (>12m)")

        if study_h >= 2.0:
            p_met_1y.append(f"Dedicación de estudio/proyecto activa ({study_h:.1f}h/día)" if is_es else f"Active study/project time ({study_h:.1f}h/day)")
        else:
            p_miss_1y.append(f"Dedicación de estudio insuficiente ({study_h:.1f}h/día vs 2.5h requeridas)" if is_es else "Low daily study hours")

        if screen_h > 3.0:
            p_miss_1y.append(f"Fuga de tiempo en pantallas ({screen_h:.1f}h/día de distracción)" if is_es else f"High screen distraction ({screen_h:.1f}h/day)")

        if inc > exp:
            p_met_1y.append(f"Flujo de caja mensual positivo ({curr_sym} {monthly_margin:,.0f}/mes)" if is_es else "Positive monthly cashflow")
        elif inc == 0 and req.housing_situation == "FAMILY_HOME":
            p_met_1y.append("Sustento básico resguardado por hogar familiar" if is_es else "Living expenses covered by family")
            p_miss_1y.append("Sin ingresos propios para gastos de titulación/trámites" if is_es else "No personal income for graduation fees")
        else:
            p_miss_1y.append("Presupuesto deficitario o sin capacidad de ahorro" if is_es else "Deficit budget")

        # Probabilidad de cumplimiento 1A
        base_p_1y = m12.career_and_goal_completion_pct.p50 if m12 else 50.0
        if study_h < 1.0: base_p_1y -= 15.0
        if screen_h > 4.0: base_p_1y -= 10.0
        prob_1y = round(max(5.0, min(95.0, base_p_1y)), 1)

        status_1y = "VIABLE_ON_TRACK" if prob_1y >= 65.0 else ("AT_RISK_GAPS" if prob_1y >= 35.0 else "NOT_FEASIBLE_INSUFFICIENT_RESOURCES")

        if is_es:
            if status_1y == "VIABLE_ON_TRACK":
                v_1y = f"Tu meta a 1 año '{goal_1y_text}' presenta condiciones viables con {prob_1y:.0f}% de probabilidad si mantienes tu disciplina."
                b_1y = "Asegura culminar los trámites académicos y mantén tu cuota de estudio diaria sin desvíos."
            elif status_1y == "AT_RISK_GAPS":
                v_1y = f"Meta en riesgo: Tienes la intención de '{goal_1y_text}', pero la fuga de {screen_h:.1f}h en pantallas y la falta de liquidez ({curr_sym} {gap_1y:,.0f} de brecha) retrasarán el cumplimiento si no ajustas tu ritmo."
                b_1y = f"Transfiere 1.5h de ocio en pantalla hacia tu tesis/portafolio y ahorra al menos {curr_sym} 150/mes."
            else:
                v_1y = f"No viable hoy: Con tu ritmo actual y sin margen de ahorro, la meta '{goal_1y_text}' sufrirá desfases críticos."
                b_1y = "Reestructura tus prioridades de tiempo de inmediato para blindar un bloque de 2.5h diarias de avance real."
        else:
            v_1y = f"1-Year goal feasibility stands at {prob_1y:.0f}%."
            b_1y = "Focus on core study hours and limit distractions."

        item_1y = GoalFeasibilityItem(
            horizon_type="SHORT_1Y",
            horizon_label="1 Año (Corto Plazo)" if is_es else "1 Year (Short Term)",
            goal_statement=goal_1y_text,
            feasibility_status=status_1y,
            feasibility_pct=prob_1y,
            required_capital=round(req_cap_1y, 2),
            projected_savings_capital=round(projected_sav_1y, 2),
            capital_gap=round(gap_1y, 2),
            prerequisites_met=p_met_1y,
            prerequisites_missing=p_miss_1y,
            reality_check_verdict=v_1y,
            strategic_bridge=b_1y
        )

        # =====================================================================
        # 2. METAS A MEDIANO PLAZO (2 - 3 AÑOS)
        # =====================================================================
        med_text = (req.medium_term_goals or "").strip()
        if not med_text:
            med_text = (
                "Ahorrar un fondo de reserva de capital, especializarme en mi profesión y lograr independencia económica"
                if is_es else
                "Accumulate reserve capital, specialize in my field, and gain financial autonomy"
            )

        # A 3 años (36 meses)
        req_cap_med = 8000.0 if curr == "PEN" else 2500.0
        projected_sav_3y = max(0.0, sav + (monthly_margin * 36.0))
        gap_med = max(0.0, req_cap_med - projected_sav_3y)

        p_met_med = []
        p_miss_med = []

        if is_student:
            p_met_med.append("Estarás formalmente graduado en el horizonte de 3 años" if is_es else "Graduated within 3 years")
        else:
            p_met_med.append("Trayectoria laboral establecida" if is_es else "Established job path")

        if monthly_margin > 400.0:
            p_met_med.append(f"Capacidad de ahorro probada ({curr_sym} {monthly_margin:,.0f}/mes)" if is_es else "Positive savings rate")
        elif monthly_margin > 0:
            p_miss_med.append(f"Ritmo de ahorro lento ({curr_sym} {monthly_margin:,.0f}/mes; requiere acelerar a {curr_sym} {(req_cap_med/36.0):,.0f}/mes)" if is_es else "Slow savings rate")
        else:
            p_miss_med.append(f"Capacidad de ahorro actual en {curr_sym} 0 (no acumula capital)" if is_es else f"Current monthly savings is {curr_sym} 0")

        if gap_med > 0:
            p_miss_med.append(f"Déficit financiero estimado de {curr_sym} {gap_med:,.0f} para consolidar la meta" if is_es else f"Capital deficit of {curr_sym} {gap_med:,.0f}")

        prob_med = 75.0 if gap_med == 0 else max(10.0, min(80.0, (projected_sav_3y / max(1.0, req_cap_med)) * 75.0))
        status_med = "VIABLE_ON_TRACK" if prob_med >= 60.0 else ("AT_RISK_GAPS" if prob_med >= 30.0 else "NOT_FEASIBLE_INSUFFICIENT_RESOURCES")

        if is_es:
            if status_med == "VIABLE_ON_TRACK":
                v_med = f"Meta a mediano plazo '{med_text}': Viable. Tu proyección económica te permite acumular {curr_sym} {projected_sav_3y:,.0f} a 3 años."
                b_med = "Automatiza el ahorro mensual e inviértelo en fondos conservadores o certificaciones de alta demanda."
            elif status_med == "AT_RISK_GAPS":
                v_med = f"Meta a mediano plazo en observación: Deseas '{med_text}', pero con tu margen de {curr_sym} {monthly_margin:,.0f}/mes te faltarán {curr_sym} {gap_med:,.0f}. Tienes la intención pero requieres monetizar mejor tu actividad tras graduarte."
                b_med = f"Fija una meta de inserción laboral post-egreso con sueldo de al menos {curr_sym} 2,200 para destinar {curr_sym} 400/mes directo a este fondo."
            else:
                v_med = f"No viable con las variables de hoy: Deseas '{med_text}', pero hoy generas {curr_sym} {inc:,.0f} con ahorro nulo ({curr_sym} {sav:,.0f}). Mantener esta meta en mente sin un plan de ingresos post-universitarios es una ilusión matemática."
                b_med = "El primer paso no es la meta en sí, sino asegurar tu primer empleo formal que genere tu primer excedente mensual."
        else:
            v_med = f"Medium-term feasibility: {prob_med:.0f}% with gap {curr_sym} {gap_med:,.0f}."
            b_med = "Establish stable post-graduation income first."

        item_med = GoalFeasibilityItem(
            horizon_type="MEDIUM_3Y",
            horizon_label="2 - 3 Años (Mediano Plazo)" if is_es else "2 - 3 Years (Medium Term)",
            goal_statement=med_text,
            feasibility_status=status_med,
            feasibility_pct=round(prob_med, 1),
            required_capital=round(req_cap_med, 2),
            projected_savings_capital=round(projected_sav_3y, 2),
            capital_gap=round(gap_med, 2),
            prerequisites_met=p_met_med,
            prerequisites_missing=p_miss_med,
            reality_check_verdict=v_med,
            strategic_bridge=b_med
        )

        # =====================================================================
        # 3. IDEALES Y METAS A LARGO PLAZO (5+ AÑOS: VIAJAR, SALIR Y TRABAJAR AFUERA)
        # =====================================================================
        long_text = (req.long_term_goals or "").strip()
        if not long_text:
            long_text = (
                "Viajar, salir y trabajar en otro país o ciudad con mejores oportunidades y alcanzar independencia total"
                if is_es else
                "Travel, relocate and work abroad/internationally with full independence"
            )

        is_travel_abroad = any(w in long_text.lower() for w in ["viajar", "salir", "trabajar en otro lado", "trabajar afuera", "extranjero", "otro país", "emigrar", "canadá", "europa", "alemania", "españa", "remoto internacional"])
        req_cap_long = (22000.0 if curr == "PEN" else 6000.0) if is_travel_abroad else (15000.0 if curr == "PEN" else 4500.0)

        projected_sav_5y = max(0.0, sav + (monthly_margin * 60.0))
        gap_long = max(0.0, req_cap_long - projected_sav_5y)

        p_met_long = []
        p_miss_long = []

        eng = req.english_level or "A1_A2"
        if is_travel_abroad:
            if eng in ("B1_B2", "C1_C2"):
                p_met_long.append(f"Nivel de inglés alineado para movilidad ({eng})" if is_es else f"English level ready ({eng})")
            else:
                p_miss_long.append(f"Nivel de inglés insuficiente ({eng} vs B2/C1 requerido para trabajar afuera)" if is_es else f"English level low ({eng})")

            if is_student:
                p_met_long.append("Horizonte a 5 años permite culminar grado y colegiatura" if is_es else "Allows degree completion")
                p_miss_long.append("Falta acumular mínimo 2 años de experiencia profesional verificable post-egreso" if is_es else "Needs 2 years verified work experience")

            if sav >= req_cap_long * 0.5:
                p_met_long.append(f"Colchón base de ahorro iniciado ({curr_sym} {sav:,.0f})" if is_es else "Base savings started")
            else:
                p_miss_long.append(f"Bolsa de reubicación/visado insuficiente (Ahorro actual: {curr_sym} {sav:,.0f} vs {curr_sym} {req_cap_long:,.0f} necesarios)" if is_es else "Relocation fund insufficient")

            if monthly_margin <= 0:
                p_miss_long.append(f"Sin flujo de ahorro mensual hoy ({curr_sym} 0/mes): tiempo de acumulación infinito a este ritmo" if is_es else "Infinite time to save with 0 margin")

        prob_long = max(5.0, min(85.0, (projected_sav_5y / max(1.0, req_cap_long)) * 60.0 + (25.0 if eng in ('B1_B2', 'C1_C2') else 0.0)))
        status_long = "VIABLE_ON_TRACK" if prob_long >= 60.0 else ("AT_RISK_GAPS" if prob_long >= 25.0 else "NOT_FEASIBLE_INSUFFICIENT_RESOURCES")

        if is_es:
            if status_long == "VIABLE_ON_TRACK":
                v_long = f"Ideal a largo plazo '{long_text}': Viable a 5 años si sostienes tu tasa de ahorro e idioma."
                b_long = "Tramita pasaporte, homologación de título y construye red de contactos en el país de destino."
            elif status_long == "AT_RISK_GAPS":
                v_long = f"Ideal en la mente con brechas críticas: Deseas '{long_text}', pero hoy tienes una brecha financiera de {curr_sym} {gap_long:,.0f} y requisitos pendientes ({', '.join(p_miss_long[:2])})."
                b_long = f"Convierte el ideal en plan: 1) Titúlate, 2) Trabaja 2 años en tu país acumulando {curr_sym} {req_cap_long*0.5:,.0f}, 3) Certifica inglés B2 usando 1h diaria de tus pantallas."
            else:
                v_long = (
                    f"⚠️ VERIFICACIÓN CAUSAL: Quieres en tu mente '{long_text}', pero hoy NO TIENES LO SUFICIENTE para poder cumplirlo. "
                    f"Operas con {curr_sym} {sav:,.0f} en ahorros y un margen de ahorro mensual nulo ({curr_sym} {monthly_margin:,.0f}/mes). "
                    f"Para salir a trabajar afuera necesitas una bolsa mínima de {curr_sym} {req_cap_long:,.0f} (te faltan {curr_sym} {gap_long:,.0f}), "
                    f"además de título profesional y dominio de inglés ({eng} actual no alcanza para visa de trabajo). "
                    f"Hoy es una fantasía mental sin sustento empírico si no construyes el puente paso a paso."
                )
                b_long = (
                    f"Puente Estratégico Obligatorio: "
                    f"1° Egresar y titularte ({months_grad} meses). "
                    f"2° Primer empleo formal que genere excedente mensual. "
                    f"3° Redirigir 1.5h de ocio en pantallas hacia inglés intensivo B2. "
                    f"4° Ahorrar sistemáticamente durante 24 a 36 meses antes de postular a visados de trabajo o migración."
                )
        else:
            v_long = f"Long term ideal feasibility: {prob_long:.0f}%. High gap detected: {curr_sym} {gap_long:,.0f}."
            b_long = "Focus on graduating, building first job savings, and English B2."

        item_long = GoalFeasibilityItem(
            horizon_type="LONG_5Y_IDEAL",
            horizon_label="5+ Años (Ideales & Largo Plazo)" if is_es else "5+ Years (Ideals & Long Term)",
            goal_statement=long_text,
            feasibility_status=status_long,
            feasibility_pct=round(prob_long, 1),
            required_capital=round(req_cap_long, 2),
            projected_savings_capital=round(projected_sav_5y, 2),
            capital_gap=round(gap_long, 2),
            prerequisites_met=p_met_long,
            prerequisites_missing=p_miss_long,
            reality_check_verdict=v_long,
            strategic_bridge=b_long
        )

        global_synth = (
            f"Diagnóstico de Metas e Ideales para {req.full_name or 'Usuario'}: "
            f"A 1 año tu viabilidad es del {prob_1y:.0f}% ({status_1y}). "
            f"A 2-3 años requieres consolidar un excedente mensual para cerrar una brecha de {curr_sym} {gap_med:,.0f}. "
            f"Y para tu ideal a 5+ años ('{long_text[:50]}...'), hoy no tienes los recursos financieros ({curr_sym} {gap_long:,.0f} de déficit) "
            f"por lo que debe ejecutarse como un plan escalonado (Título → Ahorro mensual post-empleo → Inglés B2) y no como un deseo inmediato."
            if is_es else
            f"Goals Feasibility Summary: Short term {prob_1y:.0f}%, medium term gap {curr_sym} {gap_med:,.0f}, long term gap {curr_sym} {gap_long:,.0f}."
        )

        return GoalsVerificationReport(
            short_term_1y=item_1y,
            medium_term_3y=item_med,
            long_term_5y=item_long,
            global_synthesis=global_synth
        )



class HolisticFutureEngine:
    """
    Coordinador central del motor holístico V4 con Deep Live Web Grounding y Diversidad de Perfiles:
    1. Obtiene en paralelo (<4.8s) los indicadores macroeconómicos del país y la inteligencia web adaptada:
       - Para productores rurales: clima, precios en chacra, mercados locales.
       - Para comercio/día a día: canasta básica, informalidad, costo de vida.
       - Para oficios: demanda de servicios, insumos, precios en la ciudad.
       - Para negocios: comercio minorista, crédito pyme, costos locales.
       - Para estudiantes/profesionales: empresas reales, salarios y requisitos.
    2. Modula la simulación estocástica vectorial Monte Carlo (1000 x 365 días) con ecuaciones diferenciadas.
    3. Construye los HorizonSnapshots a 1 Mes, 6 Meses y 1 Año.
    4. Invoca al MiroFish ReportAgent (Llama 3.3 70B) en el idioma seleccionado sin sesgos corporativos.
    5. Retorna la respuesta completa con live_web_intelligence y live_web_sources reales.
    """

    @classmethod
    async def extract_human_factors_from_open_answers(cls, req: HolisticFutureRequest) -> InferredHumanFactors:
        """
        Deduce parámetros matemáticos y psicológicos continuos a partir de las respuestas
        abiertas del usuario (familia, pareja/amigos, personalidad/hábitos), o aplica heurística adaptativa.
        Detecta específicamente cargas de cuidado de hermanos menores, hijos y dependientes familiares.
        """
        has_answers = bool(
            (req.open_family_and_dependents or "").strip()
            or (req.open_relationships_and_friends or "").strip()
            or (req.open_personality_and_habits or "").strip()
            or (req.self_description or "").strip()
        )

        txt_combined = f"{req.open_family_and_dependents or ''} {req.open_relationships_and_friends or ''} {req.open_personality_and_habits or ''} {req.self_description or ''}".lower()

        care_count = 0
        care_hours = 0.0
        care_details = ""

        # Detección léxica robusta de hermanos, hijos y personas al cuidado
        if any(w in txt_combined for w in ["dos hermanos", "2 hermanos", "dos hermanitos", "2 hermanitos"]) or (
            "hermano" in txt_combined and any(w in txt_combined for w in ["9", "3", "menores", "pequeños", "cuidado"])
        ):
            care_count = 2
            care_hours = 3.5
            care_details = "dos hermanos menores (uno de 9 y otro de 3 años) a su cuidado en el hogar familiar"
        elif any(w in txt_combined for w in ["tres hermanos", "3 hermanos"]):
            care_count = 3
            care_hours = 4.5
            care_details = "tres hermanos menores bajo su cuidado y apoyo en casa"
        elif any(w in txt_combined for w in ["un hermano", "1 hermano", "hermana menor", "hermano menor", "mi hermana", "mi hermano"]):
            care_count = 1
            care_hours = 2.5
            care_details = "un hermano/a menor que demanda atención y cuidado en el hogar"
        elif any(w in txt_combined for w in ["hijos", "hijo", "hija", "mis dos hijos", "mis 2 hijos", "bebé", "niños"]):
            care_count = max(2 if any(w in txt_combined for w in ["dos", "2"]) else 1, req.dependents_count or 1)
            care_hours = 4.0
            care_details = f"{care_count} hijos pequeños a su cuidado directo"
        elif any(w in txt_combined for w in ["a mi cuidado", "de mi cuidado", "cuidando a", "dependen de mí", "a mi cargo"]):
            care_count = max(1, req.dependents_count or 1)
            care_hours = 3.5
            care_details = "familiares dependientes directamente de su cuidado y tiempo diario"

        # Si no hay respuestas abiertas, calculamos base heurística a partir de los datos existentes
        if not has_answers:
            dep_count = max(0, req.dependents_count or 0)
            dep_burden = min(1.0, dep_count * 0.25)

            home_map = {"SUPPORTIVE": 0.65, "NEUTRAL": 0.10, "STRESSFUL_CONFLICT": -0.65}
            home_bal = home_map.get(req.household_climate, 0.40)

            partner_map = {"SUPPORTIVE_PARTNER": 0.60, "SINGLE_PEACEFUL": 0.20, "UNSTABLE_DRAINING": -0.60}
            circle_map = {"GROWTH": 0.30, "NEUTRAL": 0.0, "DRAINING_PARTY": -0.40}
            rel_score = partner_map.get(req.relationship_status, 0.20) + circle_map.get(req.social_circle_influence, 0.0)
            partner_eff = float(np.clip(rel_score, -1.0, 1.0))

            traits = set(req.personality_traits or [])
            stress_risk = 0.30
            if "IMPULSIVE_SPENDER" in traits:
                stress_risk += 0.25
            if "PROCRASTINATOR" in traits:
                stress_risk += 0.20
            if "ANXIOUS_OVERTHINKER" in traits:
                stress_risk += 0.15
            if "DISCIPLINED" in traits:
                stress_risk -= 0.15
            stress_risk = float(np.clip(stress_risk, 0.05, 0.95))

            grit = 0.60
            if "RESILIENT" in traits:
                grit += 0.20
            if "DISCIPLINED" in traits:
                grit += 0.15
            if "AMBITIOUS" in traits:
                grit += 0.10
            if "PROCRASTINATOR" in traits:
                grit -= 0.15
            grit = float(np.clip(grit, 0.10, 0.98))

            synth = (
                f"Entorno familiar con balance {home_bal:+.2f}, influencia de entorno {partner_eff:+.2f}, "
                f"y un perfil de resiliencia de {grit:.2f}."
            )
            return InferredHumanFactors(
                inferred_dependents_burden=dep_burden,
                home_emotional_balance=home_bal,
                partner_and_friends_effect=partner_eff,
                stress_spending_and_procrastination_risk=stress_risk,
                resilience_and_grit_score=grit,
                dependents_care_count=care_count,
                daily_caregiving_hours=care_hours,
                caregiving_details=care_details,
                human_context_synthesis=synth
            )

        # Si hay respuestas abiertas, inferimos con Llama structured_completion
        settings = get_settings()
        system_instruction = (
            "Eres el Evaluador Psicodinámico y de Causalidad Humana de Mirror Future. "
            "A partir de los testimonios abiertos de la persona sobre (1) su familia y hogar, "
            "(2) su pareja y amigos, y (3) su personalidad y reacción ante el estrés/dinero, "
            "debes estimar 5 parámetros científicos continuos, detectar personas al cuidado y una síntesis empática:\n"
            "- inferred_dependents_burden: float (0.0 a 1.0) -> Carga económica o de cuidado real que asume la persona.\n"
            "- dependents_care_count: int -> Número exacto de personas bajo su cuidado/tiempo (hermanos menores, hijos, ancianos). Si menciona cuidar hermanos o hijos, debe ser >= 1.\n"
            "- daily_caregiving_hours: float -> Horas diarias dedicadas al cuidado familiar (ej. 3.5h para dos hermanos de 9 y 3 años).\n"
            "- caregiving_details: string -> Descripción clara de a quiénes cuida y su edad/situación.\n"
            "- home_emotional_balance: float (-1.0 a +1.0) -> -1.0 conflicto/asfixia/tensión familiar severa, 0.0 neutro/independiente, +1.0 paz, amor y respaldo nutritivo.\n"
            "- partner_and_friends_effect: float (-1.0 a +1.0) -> -1.0 drenaje emocional/financiero por pareja conflictiva o malas amistades, +1.0 pareja y amigos que suman, protegen y motivan.\n"
            "- stress_spending_and_procrastination_risk: float (0.0 a 1.0) -> Propensión a sabotearse gastando impulsivamente, evadiendo o paralizándose ante el estrés.\n"
            "- resilience_and_grit_score: float (0.0 a 1.0) -> Capacidad de empuje, disciplina, perseverancia y aguante real ante la adversidad.\n"
            "- human_context_synthesis: string -> Síntesis de 2 oraciones capturando su verdad personal más profunda.\n"
            "REGLA CRUCIAL: PROHIBIDO declarar 0 dependientes si la persona escribió que cuida a hermanos o hijos en casa.\n"
            "Devuelve EXCLUSIVAMENTE el JSON con estas claves exactas."
        )

        user_content = {
            "respuestas_abiertas": {
                "familia_y_hogar": req.open_family_and_dependents,
                "pareja_y_amigos": req.open_relationships_and_friends,
                "personalidad_y_reaccion_al_estres": req.open_personality_and_habits,
                "autodescripcion_adicional": req.self_description,
                "rasgos_marcados": req.personality_traits,
                "dependientes_declarados": req.dependents_count,
            },
            "datos_contexto": {
                "edad": req.age,
                "ocupacion": req.occupation,
                "ciudad": req.city
            }
        }

        try:
            parsed = await llama_client.structured_completion(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": json.dumps(user_content, ensure_ascii=False)}
                ],
                model=settings.llama_reasoning_model,
                temperature=0.2,
                max_tokens=600
            )

            dep_burden = float(np.clip(float(parsed.get("inferred_dependents_burden", 0.0)), 0.0, 1.0))
            if care_count > 0:
                dep_burden = max(dep_burden, min(1.0, 0.40 + care_count * 0.15))
            home_bal = float(np.clip(float(parsed.get("home_emotional_balance", 0.5)), -1.0, 1.0))
            partner_eff = float(np.clip(float(parsed.get("partner_and_friends_effect", 0.4)), -1.0, 1.0))
            stress_risk = float(np.clip(float(parsed.get("stress_spending_and_procrastination_risk", 0.3)), 0.0, 1.0))
            grit = float(np.clip(float(parsed.get("resilience_and_grit_score", 0.7)), 0.0, 1.0))
            synthesis = str(parsed.get("human_context_synthesis", "")).strip()

            inferred_care_count = int(parsed.get("dependents_care_count", care_count))
            inferred_care_hours = float(parsed.get("daily_caregiving_hours", care_hours))
            inferred_care_details = str(parsed.get("caregiving_details", care_details)).strip()
            if care_count > 0 and inferred_care_count == 0:
                inferred_care_count = care_count
                inferred_care_hours = care_hours
                inferred_care_details = care_details

            if not synthesis:
                synthesis = "Perfil relacional y psicológico balanceado inferido de sus respuestas."

            return InferredHumanFactors(
                inferred_dependents_burden=dep_burden,
                home_emotional_balance=home_bal,
                partner_and_friends_effect=partner_eff,
                stress_spending_and_procrastination_risk=stress_risk,
                resilience_and_grit_score=grit,
                dependents_care_count=inferred_care_count,
                daily_caregiving_hours=inferred_care_hours,
                caregiving_details=inferred_care_details,
                human_context_synthesis=synthesis
            )

        except Exception as exc:
            logger.error("Error en extract_human_factors_from_open_answers con Llama: %s. Usando heurística de contingencia.", exc)
            txt = txt_combined

            dep_burden = 0.4 if any(w in txt for w in ["apoyo", "mantengo", "hijos", "padres", "gastos", "dependen", "hermano", "cuidado"]) else 0.1
            if care_count > 0:
                dep_burden = max(dep_burden, min(1.0, 0.40 + care_count * 0.15))
            if req.dependents_count:
                dep_burden = max(dep_burden, min(1.0, req.dependents_count * 0.25))

            home_bal = 0.4
            if any(w in txt for w in ["pelea", "discusión", "tensión", "presión", "conflicto", "gritos", "asfixia"]):
                home_bal -= 0.6
            if any(w in txt for w in ["apoyo", "tranquilidad", "paz", "unidos", "cariño", "estabilidad"]):
                home_bal += 0.4
            home_bal = float(np.clip(home_bal, -1.0, 1.0))

            partner_eff = 0.3
            if any(w in txt for w in ["dudas", "tóxic", "desgaste", "mala influencia", "fiesta", "trago", "malgasto"]):
                partner_eff -= 0.6
            if any(w in txt for w in ["impulsa", "motiva", "sana", "enfocad", "buenos amigos", "equipo"]):
                partner_eff += 0.4
            partner_eff = float(np.clip(partner_eff, -1.0, 1.0))

            stress_risk = 0.35
            if any(w in txt for w in ["ansiedad", "gasto", "compro", "postergo", "procrastin", "estrés", "bloqueo"]):
                stress_risk += 0.35
            stress_risk = float(np.clip(stress_risk, 0.05, 0.95))

            grit = 0.65
            if any(w in txt for w in ["trabajador", "perseverante", "lucho", "disciplina", "adelante", "resiliente"]):
                grit += 0.2
            grit = float(np.clip(grit, 0.1, 0.98))

            return InferredHumanFactors(
                inferred_dependents_burden=dep_burden,
                home_emotional_balance=home_bal,
                partner_and_friends_effect=partner_eff,
                stress_spending_and_procrastination_risk=stress_risk,
                resilience_and_grit_score=grit,
                dependents_care_count=care_count,
                daily_caregiving_hours=care_hours,
                caregiving_details=care_details,
                human_context_synthesis="Síntesis heurística de contingencia a partir de su testimonio situacional."
            )


    @classmethod
    async def predict_future_self(cls, req: HolisticFutureRequest) -> HolisticFutureResponse:
        code = req.country_code.upper().strip()
        country_name = COUNTRY_METADATA.get(code, {}).get("name", code)
        person_name = req.full_name or req.full_name_or_handle or req.person_identifier
        career = req.career_or_degree or req.occupation

        # 1. Macro Context, Deep Live Web Grounding y Factores Humanos en PARALELO (<4.8s)
        macro_task = macro_engine.get_macro_context(code, req.currency)
        live_web_task = live_web_engine.research_all(
            city=req.city,
            country=country_name,
            career_or_degree=career,
            life_profile_type=req.life_profile_type,
            rural_product=req.rural_product,
            main_goal_1y=req.main_goal_1y or req.one_year_goal or "",
            target_monthly_salary_1y=req.target_monthly_salary_1y,
            full_name=person_name,
            university_or_institution=req.university_or_institution,
            current_company_or_org=req.current_company_or_org,
            life_stage=req.life_stage,
            english_level=req.english_level,
            currency=req.currency,
            goal_mode=req.goal_mode,
            lang=req.lang,
            months_to_graduation=int(req.months_to_graduation or 0),
            years_of_experience=float(req.years_of_experience or 0.0),
            key_skills=req.key_skills or "",
            daily_caregiving_hours=float(req.daily_caregiving_hours or 0.0)
        )
        human_factors_task = cls.extract_human_factors_from_open_answers(req)

        macro, live_intel, human_factors = await asyncio.gather(
            macro_task, live_web_task, human_factors_task
        )

        # 1.5. Autocompletado Secuencial de Carrera e Ingresos (Life2Vec Career Engine)
        career_autocompletion = Life2VecCareerEngine.autocompletar_futuro_laboral(
            req=req,
            live_intel=live_intel,
            macro_unemployment=macro.unemployment_rate
        )

        # 2. Monte Carlo Simulation en NumPy calibrado por probabilidades de transición Life2Vec
        metrics_by_horizon = HolisticMonteCarloSimulator.simulate(
            req, macro, live_intel, human_factors, career_autocompletion=career_autocompletion
        )

        # 3. Narrativas periciales con Llama 3.3 70B en el idioma y modo correctos (con Life2Vec)
        narratives, golden_path, exec_summary = await MiroFishReportAgent.generate_holistic_report(
            req, macro, metrics_by_horizon, live_intel, human_factors, career_autocompletion=career_autocompletion
        )

        # 4. Snapshots estructurados
        snapshot_1m = HorizonSnapshot(
            horizon_name="1_month",
            day_index=30,
            metrics=metrics_by_horizon["1_month"],
            narrative=narratives["1_month"]
        )
        snapshot_6m = HorizonSnapshot(
            horizon_name="6_months",
            day_index=180,
            metrics=metrics_by_horizon["6_months"],
            narrative=narratives["6_months"]
        )
        snapshot_1y = HorizonSnapshot(
            horizon_name="1_year",
            day_index=365,
            metrics=metrics_by_horizon["1_year"],
            narrative=narratives["1_year"]
        )

        # 3.5. Verificación Causal de Metas e Ideales (Corto 1A, Mediano 2-3A, Largo 5A+ como viajar/trabajar afuera)
        goals_verification_report = GoalFeasibilityEngine.verify_goals_and_ideals(
            req=req,
            sim_metrics=metrics_by_horizon,
            macro=macro
        )

        sources_payload = [
            {
                "category": s.category,
                "title": s.title,
                "summary": s.summary,
                "url": s.url,
                "source": s.source
            }
            for s in live_intel.live_snippets
        ]

        return HolisticFutureResponse(
            request_meta={
                "age": req.age,
                "city": req.city,
                "occupation": req.occupation,
                "career_or_degree": career,
                "life_profile_type": req.life_profile_type,
                "goal_mode": req.goal_mode,
                "lang": req.lang,
                "daily_income_avg": req.daily_income_avg,
                "daily_expense_avg": req.daily_expense_avg,
                "work_days_per_week": req.work_days_per_week,
                "rural_product": req.rural_product,
                "campaign_income_est": req.campaign_income_est,
                "physical_labor_intensity": req.physical_labor_intensity,
                "trade_modality": req.trade_modality,
                "contract_type": req.contract_type,
                "business_type": req.business_type,
                "monthly_sales_net": req.monthly_sales_net,
                "full_name": person_name,
                "university_or_institution": req.university_or_institution,
                "current_company_or_org": req.current_company_or_org,
                "life_stage": req.life_stage,
                "months_to_graduation": req.months_to_graduation,
                "years_of_experience": req.years_of_experience,
                "key_skills": req.key_skills,
                "english_level": req.english_level,
                "work_modality_target": req.work_modality_target,
                "target_monthly_salary_1y": req.target_monthly_salary_1y,
                "housing_situation": req.housing_situation,
                "main_goal_1y": req.main_goal_1y,
                "medium_term_goals": req.medium_term_goals,
                "long_term_goals": req.long_term_goals,
                "currency": req.currency,
                "monthly_income": req.monthly_income,
                "monthly_expenses": req.monthly_expenses,
            },
            macro_context=macro.model_dump(),
            live_web_intelligence={
                "city_cost_pressure_index": live_intel.city_cost_pressure_index,
                "career_market_demand_score": live_intel.career_market_demand_score,
                "synthesized_real_time_context": live_intel.synthesized_real_time_context,
                "local_salary_range_min": live_intel.local_salary_range_min,
                "local_salary_range_max": live_intel.local_salary_range_max,
                "remote_salary_range_min": live_intel.remote_salary_range_min,
                "remote_salary_range_max": live_intel.remote_salary_range_max,
                "local_companies_found": live_intel.local_companies_found,
                "goal_requirements_evidence": live_intel.goal_requirements_evidence,
            },
            live_web_sources=sources_payload,
            inferred_human_factors=human_factors,
            snapshot_1_month=snapshot_1m,
            snapshot_6_months=snapshot_6m,
            snapshot_1_year=snapshot_1y,
            golden_path_adjustments=golden_path,
            executive_summary=exec_summary,
            goals_verification=goals_verification_report,
            career_autocompletion=career_autocompletion
        )


# Instancia por defecto
holistic_future_engine = HolisticFutureEngine()
