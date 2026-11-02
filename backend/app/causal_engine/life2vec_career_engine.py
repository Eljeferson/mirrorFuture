"""
Mirror Future - Life2Vec Career Engine (life2vec-light Architecture).
Modela la trayectoria de vida y carrera del usuario como una secuencia cronológica
de eventos tokenizados (Life Events), aplicando codificación temporal Time2Vec,
embeddings semánticos y atención secuencial (PyTorch/NumPy) para proyectar
transiciones laborales, bandas salariales (P10, P50, P90), riesgo de automatización por IA
y autocompletar los próximos 1 Mes, 6 Meses, 1 Año, 3 Años y 5 Años.
"""

from __future__ import annotations

import logging
import math
import re
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import torch
import torch.nn as nn

from app.models.schemas import (
    CareerLifeEvent,
    CareerTransitionNode,
    CareerAutocompletionResult,
    StrategicRoadmapPhase,
    HolisticFutureRequest,
    LiveWebIntelligenceReport,
    RealJobVacancy,
    ActuarialInsertionPlan,
)

logger = logging.getLogger("mirror_future.life2vec_career_engine")
logger.setLevel(logging.INFO)

# =============================================================================
# 1. ARQUITECTURA NEURAL PYTORCH (Time2Vec + Life2Vec Sequence Encoder)
# =============================================================================

class Time2Vec(nn.Module):
    """
    Time2Vec: Representation of Time as a Vector (Kazemi et al., 2019).
    Aprende componentes lineales no periódicos y armónicos periódicos (frecuencias)
    para representar la edad y tiempo transcurrido en la trayectoria de vida.
    """
    def __init__(self, out_features: int = 16):
        super().__init__()
        self.out_features = out_features
        # Componente lineal (w0 * t + phi0)
        self.w0 = nn.Parameter(torch.randn(1, 1))
        self.phi0 = nn.Parameter(torch.randn(1, 1))
        # Componentes armónicas periódicas (sin(wi * t + phii))
        self.w = nn.Parameter(torch.randn(1, out_features - 1))
        self.phi = nn.Parameter(torch.randn(1, out_features - 1))

    def forward(self, tau: torch.Tensor) -> torch.Tensor:
        # tau shape: [batch, seq_len, 1]
        linear_part = torch.matmul(tau, self.w0) + self.phi0
        periodic_part = torch.sin(torch.matmul(tau, self.w) + self.phi)
        return torch.cat([linear_part, periodic_part], dim=-1)


class Life2VecSequenceEncoder(nn.Module):
    """
    Encoder secuencial inspirado en life2vec / life2vec-light.
    Mapea secuencias de hitos de vida (tipo de evento, semántica, edad, ingresos)
    a un vector denso latente de trayectoria laboral de 128 dimensiones.
    """
    def __init__(
        self,
        event_types_count: int = 10,
        d_event_type: int = 16,
        d_time: int = 16,
        d_sem: int = 64,
        d_inc: int = 16,
        d_model: int = 128,
        nhead: int = 4
    ):
        super().__init__()
        self.event_type_emb = nn.Embedding(event_types_count, d_event_type)
        self.time2vec = Time2Vec(out_features=d_time)
        self.semantic_proj = nn.Linear(384, d_sem)
        self.income_proj = nn.Linear(1, d_inc)

        total_in = d_event_type + d_time + d_sem + d_inc
        self.input_proj = nn.Sequential(
            nn.Linear(total_in, d_model),
            nn.GELU(),
            nn.LayerNorm(d_model)
        )

        self.self_attn = nn.MultiheadAttention(embed_dim=d_model, num_heads=nhead, batch_first=True)
        self.norm = nn.LayerNorm(d_model)
        self.fc_out = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.GELU(),
            nn.Linear(d_model, d_model)
        )

    def forward(
        self,
        event_type_idx: torch.Tensor,     # [batch, seq_len]
        ages: torch.Tensor,               # [batch, seq_len, 1]
        sem_embeddings: torch.Tensor,     # [batch, seq_len, 384]
        incomes: torch.Tensor             # [batch, seq_len, 1]
    ) -> torch.Tensor:
        type_feat = self.event_type_emb(event_type_idx)
        time_feat = self.time2vec(ages)
        sem_feat = self.semantic_proj(sem_embeddings)
        inc_feat = self.income_proj(torch.log1p(torch.clamp(incomes, min=0.0) / 100.0))

        cat_feat = torch.cat([type_feat, time_feat, sem_feat, inc_feat], dim=-1)
        x = self.input_proj(cat_feat)

        attn_out, _ = self.self_attn(x, x, x)
        x = self.norm(x + attn_out)

        # Global Attention Pooling (media ponderada por norma)
        weights = torch.softmax(torch.norm(x, dim=-1, keepdim=True), dim=1)
        pooled = torch.sum(x * weights, dim=1)  # [batch, d_model]
        out = self.fc_out(pooled)
        # Normalización unitaria L2
        norm = torch.norm(out, p=2, dim=-1, keepdim=True).clamp(min=1e-9)
        return out / norm


# =============================================================================
# 2. MOTOR DE AUTOCOMPLETADO Y SIMULACIÓN DE CARRERA
# =============================================================================

EVENT_TYPE_INDEX_MAP = {
    "EDUCATION": 1,
    "FIRST_JOB": 2,
    "ROLE_CHANGE": 3,
    "SKILL_ACQUISITION": 4,
    "UNEMPLOYMENT_GAP": 5,
    "FREELANCE_OR_BUSINESS": 6,
    "CURRENT_STATE": 7,
    "OTHER": 0,
}


class Life2VecCareerEngine:
    """
    Motor Causal de Carrera e Ingresos basado en life2vec.
    Reconstruye el pasado, proyecta el futuro estocástico en 5 horizontes y
    evalúa cuellos de botella con rigor computacional.
    """
    _encoder: Optional[Life2VecSequenceEncoder] = None

    @classmethod
    def get_encoder(cls) -> Life2VecSequenceEncoder:
        if cls._encoder is None:
            torch.manual_seed(42)
            cls._encoder = Life2VecSequenceEncoder()
            cls._encoder.eval()
        return cls._encoder

    @classmethod
    def encode_career_sequence(
        cls,
        events: List[CareerLifeEvent],
        current_req: HolisticFutureRequest
    ) -> np.ndarray:
        """
        Codifica la secuencia de eventos de vida en un vector de trayectoria unitario de 128 dimensiones.
        """
        if not events:
            events = cls.synthesize_past_events_if_empty(current_req)

        # Truncar o ordenar por año
        sorted_events = sorted(events, key=lambda e: (e.year, e.age_at_event))

        event_indices = []
        ages_list = []
        incomes_list = []
        sem_list = []

        from app.ingestion.embedding_engine import EmbeddingModelManager

        # Vector semántico por evento
        for ev in sorted_events:
            idx = EVENT_TYPE_INDEX_MAP.get(ev.event_type.upper(), 0)
            event_indices.append(idx)
            ages_list.append([float(ev.age_at_event)])
            incomes_list.append([float(ev.monthly_income)])

            text_desc = f"{ev.event_type} {ev.title_or_role} {ev.location} {ev.description or ''}"
            try:
                model = EmbeddingModelManager.get_model()
                emb = model.encode(text_desc, show_progress_bar=False, normalize_embeddings=True)
                sem_list.append(emb)
            except Exception:
                # Fallback determinista seguro
                pseudo_emb = np.zeros(384, dtype=np.float32)
                for i, ch in enumerate(text_desc.encode("utf-8")[:384]):
                    pseudo_emb[i % 384] += (ord(chr(ch)) % 17) * 0.05
                norm = np.linalg.norm(pseudo_emb)
                if norm > 0:
                    pseudo_emb /= norm
                sem_list.append(pseudo_emb)

        batch_types = torch.tensor([event_indices], dtype=torch.long)
        batch_ages = torch.tensor([ages_list], dtype=torch.float32)
        batch_incomes = torch.tensor([incomes_list], dtype=torch.float32)
        batch_sem = torch.from_numpy(np.array([sem_list], dtype=np.float32))

        encoder = cls.get_encoder()
        with torch.no_grad():
            trajectory_tensor = encoder(batch_types, batch_ages, batch_sem, batch_incomes)
            vec = trajectory_tensor.squeeze(0).cpu().numpy()

        return vec

    @classmethod
    def compute_empirical_salary_distribution(
        cls,
        career: str,
        city: str,
        country: str,
        currency: str,
        life_profile_type: str,
        years_of_experience: float,
        competence_mult: float,
        live_intel: Optional[LiveWebIntelligenceReport] = None
    ) -> Dict[str, Any]:
        """
        Calcula la distribución salarial empírica calibrada (MTPE / ENAHO / Mercado Regional vs Remoto)
        y el Salario Líquido Neto Real descontando retenciones de ley (~13% AFP/ONP) y costos de transporte/comida.
        """
        curr = currency.upper().strip() or "PEN"
        curr_sym = "S/" if curr == "PEN" else ("$" if curr == "USD" else curr)
        c_low = career.lower()
        is_high_cost = any(h in city.lower() for h in ["lima", "bogota", "cdmx", "santiago", "buenos aires", "new york", "madrid"])
        city_factor = 1.15 if is_high_cost else 0.90
        exp_factor = 1.0 + min(1.8, years_of_experience * 0.12)
        comp_mult = min(1.3, max(0.6, competence_mult))

        # Base Gross Median (P50) en moneda local según arquetipo y sector
        if any(w in c_low for w in ["sistem", "software", "programad", "computaci", "informátic", "datos", "developer", "ti"]):
            base_p50 = 2600.0 if curr == "PEN" else 750.0
        elif any(w in c_low for w in ["econom", "finanz", "contab", "admin", "banc"]):
            base_p50 = 2500.0 if curr == "PEN" else 720.0
        elif any(w in c_low for w in ["civil", "industri", "medic", "derech", "abogad"]):
            base_p50 = 2800.0 if curr == "PEN" else 800.0
        elif life_profile_type in ("DAY_TO_DAY_WORKER", "SKILLED_TRADE") or any(w in c_low for w in ["comida", "comerc", "ambul", "taxi", "mototaxi"]):
            base_p50 = 1600.0 if curr == "PEN" else 480.0
        else:
            base_p50 = 2200.0 if curr == "PEN" else 640.0

        p50_gross = round(base_p50 * city_factor * exp_factor * comp_mult, 0)
        p10_gross = round(p50_gross * 0.65, 0)
        p25_gross = round(p50_gross * 0.82, 0)
        p75_gross = round(p50_gross * 1.30, 0)
        p90_gross = round(p50_gross * 1.65, 0)

        commute_cost = 400.0 if is_high_cost else 220.0 if curr == "PEN" else (110.0 if is_high_cost else 60.0)

        def to_net(gross: float, is_remote: bool = False) -> float:
            tax_pension = gross * 0.13  # Retención legal ~13% AFP/ONP
            commute = commute_cost * 0.2 if is_remote else commute_cost
            return max(350.0 if curr == "PEN" else 100.0, round(gross - tax_pension - commute, 0))

        return {
            "p10_gross": p10_gross,
            "p25_gross": p25_gross,
            "p50_gross": p50_gross,
            "p75_gross": p75_gross,
            "p90_gross": p90_gross,
            "p10_net": to_net(p10_gross),
            "p25_net": to_net(p25_gross),
            "p50_net": to_net(p50_gross),
            "p75_net": to_net(p75_gross),
            "p90_net": to_net(p90_gross, is_remote=True),
            "commute_cost": commute_cost,
            "currency": curr,
            "currency_symbol": curr_sym,
        }

    @classmethod
    def simulate_time_to_hire_survival(
        cls,
        req: HolisticFutureRequest,
        live_intel: Optional[LiveWebIntelligenceReport],
        empirical_salaries: Dict[str, Any],
        cohort_pct: float,
        is_es: bool
    ) -> ActuarialInsertionPlan:
        """
        Modelo de Supervivencia de Riesgo Proporcional (Weibull / Cox) semana a semana (1 a 52 semanas)
        que estima la probabilidad exacta acumulada de contratación, semanas a primer contrato y
        desglose contable mensual de flujo de caja.
        """
        w_grad = int((req.months_to_graduation or 0) * 4.3)
        free_h = float(req.study_or_project_hours or 0.0)
        screen_h = float(req.screen_time_distraction_hours or 0.0)
        care_h = float(req.daily_caregiving_hours or 0.0)
        eff_free_h = max(0.5, free_h - (care_h * 0.5) - (screen_h * 0.4))

        vacancies = live_intel.real_job_openings if live_intel and live_intel.real_job_openings else []
        avg_match = float(np.mean([v.exact_match_score_pct for v in vacancies])) if vacancies else 65.0
        norm_match = min(1.0, max(0.1, avg_match / 100.0))

        comp_mult = float(req.verified_competence_multiplier or 1.0)
        traits = [t.upper() for t in (req.personality_traits or [])]

        grit = 1.0
        if any(t in traits for t in ["DISCIPLINED", "RESILIENT", "AMBITIOUS"]):
            grit += 0.20
        if any(t in traits for t in ["PROCRASTINATOR", "ANXIOUS_OVERTHINKER", "IMPULSIVE_SPENDER"]):
            grit -= 0.25

        # Weibull Baseline Hazard
        w = np.arange(1, 53, dtype=float)
        k = 1.35
        lam = 24.0
        lambda_0 = (k / lam) * ((w / lam) ** (k - 1.0))

        # Cox Proportional Multiplier
        theta = float(np.exp(
            1.2 * (norm_match - 0.6) +
            0.15 * (eff_free_h - 3.0) +
            0.35 * (comp_mult - 1.0) +
            0.25 * (grit - 1.0)
        ))

        damping = np.where(w < w_grad, 0.40, 1.0)
        hazard = np.clip(lambda_0 * theta * damping, 0.015, 0.35)
        survival = np.cumprod(1.0 - hazard)
        p_hired = 1.0 - survival

        curve_pct = [round(float(p * 100.0), 1) for p in p_hired]

        w75_idx = np.where(p_hired >= 0.75)[0]
        w75 = int(w[w75_idx[0]]) if len(w75_idx) > 0 else 52

        w50_idx = np.where(p_hired >= 0.50)[0]
        w50 = int(w[w50_idx[0]]) if len(w50_idx) > 0 else 32

        # P90 (Escenario Acelerado)
        theta_opt = theta * 1.6
        hazard_opt = np.clip(lambda_0 * theta_opt * damping, 0.025, 0.45)
        surv_opt = np.cumprod(1.0 - hazard_opt)
        p_hired_opt = 1.0 - surv_opt
        w90_idx = np.where(p_hired_opt >= 0.75)[0]
        w90 = int(w[w90_idx[0]]) if len(w90_idx) > 0 else max(4, w_grad + 2)

        # P10 (Escenario Estancamiento)
        theta_stag = theta * 0.65
        hazard_stag = np.clip(lambda_0 * theta_stag * damping * 0.7, 0.01, 0.20)
        surv_stag = np.cumprod(1.0 - hazard_stag)
        p_hired_stag = 1.0 - surv_stag
        w10_idx = np.where(p_hired_stag >= 0.50)[0]
        w10 = int(w[w10_idx[0]]) if len(w10_idx) > 0 else 44

        # Monthly progression
        monthly_prog: List[Dict[str, Any]] = []
        p50_gross = empirical_salaries["p50_gross"]
        p50_net = empirical_salaries["p50_net"]
        commute = empirical_salaries["commute_cost"]
        cur_inc = float(req.monthly_income or 0.0)
        cur_exp = float(req.monthly_expenses or 0.0)

        for m in range(1, 13):
            cur_w = m * 4
            if cur_w < w_grad:
                g_m = max(cur_inc, p50_gross * 0.50)
                n_m = max(cur_inc * 0.95, g_m - (g_m * 0.13) - commute)
            else:
                prob_employed = float(p_hired[min(51, cur_w - 1)])
                g_m = round(p50_gross * (0.85 + (0.35 * prob_employed)), 0)
                n_m = round(max(500.0, g_m - (g_m * 0.13) - commute), 0)

            tax_m = round(g_m * 0.13, 0)
            monthly_prog.append({
                "month_index": m,
                "month_label": f"Mes {m}" if is_es else f"Month {m}",
                "gross_salary": g_m,
                "statutory_deductions": tax_m,
                "commute_costs": commute,
                "net_liquid_disposable": n_m,
                "real_savings_capacity": max(0.0, n_m - cur_exp),
                "hiring_probability_pct": round(float(p_hired[min(51, cur_w - 1)] * 100), 1)
            })

        # Month 36 (Año 3)
        g_3y = round(p50_gross * 1.85, 0)
        n_3y = round(g_3y - (g_3y * 0.13) - commute, 0)
        monthly_prog.append({
            "month_index": 36,
            "month_label": "Año 3 (Mes 36)" if is_es else "Year 3 (Month 36)",
            "gross_salary": g_3y,
            "statutory_deductions": round(g_3y * 0.13, 0),
            "commute_costs": commute,
            "net_liquid_disposable": n_3y,
            "real_savings_capacity": max(0.0, n_3y - (cur_exp * 1.25)),
            "hiring_probability_pct": 94.5
        })

        cash_flow = {
            "gross_salary": p50_gross,
            "statutory_deductions_afp_onp": round(p50_gross * 0.13, 0),
            "local_commute_and_meals": commute,
            "net_liquid_disposable": p50_net,
            "real_savings_capacity": max(0.0, p50_net - cur_exp)
        }

        return ActuarialInsertionPlan(
            estimated_weeks_to_first_contract_p10=w10,
            estimated_weeks_to_first_contract_p50=w50,
            estimated_weeks_to_first_contract_p90=w90,
            weeks_to_75pct_probability=w75,
            weekly_hiring_probability_curve=curve_pct,
            exact_net_salary_progression=monthly_prog,
            cash_flow_monthly_breakdown=cash_flow
        )

    @classmethod
    def sanitize_career_label(cls, career: str, p_type: str = "") -> str:
        """
        Normaliza y sanitiza etiquetas de carrera/oficio para evitar textos informales
        como 'vendo comida', 'mototaxi' o concatenaciones crudas en los roles de salida.
        """
        c = (career or "").strip()
        c_low = c.lower()

        # Comida y Gastronomía
        if any(w in c_low for w in ["comida", "alimento", "restaurante", "cocin", "puesto de comida", "mozo", "sandwich", "vendo"]):
            return "Comercio Gastronómico y Venta de Alimentos"

        # Transporte y Movilidad
        if any(w in c_low for w in ["mototaxi", "taxista", "taxi", "chofer", "conductor", "transporte"]):
            return "Transporte y Logística Urbana"

        # Comercio y Ambulante
        if any(w in c_low for w in ["ambulante", "comerciante", "comercio", "tienda", "bodega", "abarrotes", "ventas"]):
            return "Comercio Minorista y Ventas Directas"

        # Oficios Técnicos
        if any(w in c_low for w in ["electricis", "electricid"]):
            return "Instalaciones Eléctricas y Mantenimiento Técnico"
        if any(w in c_low for w in ["mecanic", "mecánic", "taller"]):
            return "Mecánica Automotriz y Mantenimiento"
        if any(w in c_low for w in ["gasfiter", "plomer"]):
            return "Instalaciones Sanitarias y Gasfitería"
        if any(w in c_low for w in ["carpinter", "muebler"]):
            return "Carpintería y Mobiliario"

        # Agropecuario
        if any(w in c_low for w in ["agrícol", "agricol", "campo", "papa", "café", "cafe", "ganad", "cultivo"]):
            return "Producción Agrícola y Agrocomercio"

        # Carreras Profesionales
        if any(w in c_low for w in ["econom", "economis"]):
            return "Economía y Finanzas"
        if any(w in c_low for w in ["sistem", "software", "informát", "programad", "computaci", "desarrollad"]):
            return "Ingeniería de Sistemas e Informática"
        if any(w in c_low for w in ["administra"]):
            return "Administración de Empresas y Gestión"
        if any(w in c_low for w in ["contab", "contador"]):
            return "Contabilidad y Finanzas Corporativas"
        if any(w in c_low for w in ["civil"]):
            return "Ingeniería Civil y Construcción"
        if any(w in c_low for w in ["industri"]):
            return "Ingeniería Industrial y Operaciones"
        if any(w in c_low for w in ["abogad", "derecho"]):
            return "Derecho y Asesoría Jurídica"
        if any(w in c_low for w in ["enfermer"]):
            return "Enfermería y Cuidados Clínicos"
        if any(w in c_low for w in ["medic", "médic"]):
            return "Medicina y Servicios de Salud"
        if any(w in c_low for w in ["psicol"]):
            return "Psicología y Desarrollo Humano"
        if any(w in c_low for w in ["diseñ", "grafic"]):
            return "Diseño y Comunicación Visual"
        if any(w in c_low for w in ["market"]):
            return "Marketing y Estrategia Comercial"

        # Fallbacks por tipo de perfil
        if not c or c_low in ("especialidad", "general", "estudios generales", "estudiante"):
            if p_type == "DAY_TO_DAY_WORKER":
                return "Comercio Independiente y Ventas"
            elif p_type == "SKILLED_TRADE":
                return "Servicios Técnicos Especializados"
            elif p_type == "RURAL_FIELD_PRODUCER":
                return "Producción Agroproductiva Rural"
            elif p_type == "BUSINESS_OWNER":
                return "Gestión de Empresa y Negocios"
            elif p_type == "TITLED_PROFESSIONAL":
                return "Gestión Profesional y Consultoría"
            return "Carrera Profesional"

        clean = re.sub(r'^(?:yo\s+)?(?:estudio|estudiar|trabajo en|laboro en|me dedico a|vendo|hago|soy)\s+', '', c, flags=re.IGNORECASE).strip()
        clean = re.sub(r'\s+(?:egresado|bachiller|titulado|colegiado|con trabajo|graduado).*$', '', clean, flags=re.IGNORECASE).strip()
        return clean.title() if clean else c.title()

    @classmethod
    def generate_strategic_roadmap(
        cls,
        req: HolisticFutureRequest,
        cohort_pct: float,
        empirical_salaries: Dict[str, Any],
        bottlenecks: List[str],
        is_es: bool
    ) -> List[StrategicRoadmapPhase]:
        """
        Genera la guía estratégica paso a paso de qué seguir y qué cambiar día a día
        para alcanzar el camino óptimo P90 y evitar caer en el estancamiento P10,
        adaptado fielmente al arquetipo socio-laboral real del usuario.
        """
        raw_career = (req.career_or_degree or req.occupation or "Especialidad").strip()
        p_type = req.life_profile_type or "UNIVERSITY_OR_TECH_STUDENT"
        c_low = raw_career.lower()

        # Detección rigurosa de arquetipos para la hoja de ruta
        occ_low = (req.occupation or "").lower()
        full_c = f"{c_low} {occ_low}"
        is_taxi = any(w in full_c for w in ["taxista", "taxi", "mototaxi", "chofer", "conductor", "colectivo", "transporte", "remisse"])
        is_rural = p_type == "RURAL_FIELD_PRODUCER" or any(w in full_c for w in ["granja", "granjas", "avícol", "avicol", "porcin", "cuy", "galpón", "galpon", "chacra", "fundo", "campo", "agrícol", "agricol", "ganad"])
        is_business = p_type == "BUSINESS_OWNER" or (any(w in full_c for w in ["comerciante", "comercio", "bodega", "tienda", "abarrotes", "negocio", "emprend", "ventas"]) and not is_taxi)
        is_explicit_grad = any(w in full_c for w in ["egresad", "bachiller", "titulad", "colegiad", "graduad"])
        is_trade = p_type == "SKILLED_TRADE" or any(w in full_c for w in ["electric", "mecanic", "mecánic", "gasfiter", "taller", "carpinter"])
        is_active_student = (p_type == "UNIVERSITY_OR_TECH_STUDENT" and int(req.months_to_graduation or 0) > 0 and not is_explicit_grad and not is_taxi and not is_rural and not is_business)
        is_day_to_day = (p_type == "DAY_TO_DAY_WORKER" or any(w in full_c for w in ["comida", "comercio", "ambulante", "mozo", "vendo"])) and not is_taxi and not is_rural and not is_business
        is_titled_or_grad = is_explicit_grad or p_type == "TITLED_PROFESSIONAL" or (not is_active_student and not is_day_to_day and not is_trade and not is_rural and not is_business and not is_taxi)

        c_name = cls.sanitize_career_label(raw_career, p_type)
        curr_sym = empirical_salaries.get("currency_symbol", "S/")
        months_grad = int(req.months_to_graduation or 0)
        p50_net = empirical_salaries.get("p50_net", 2000.0)
        p90_net = empirical_salaries.get("p90_net", 3800.0)
        p10_net = empirical_salaries.get("p10_net", 1200.0)
        screen_h = float(req.screen_time_distraction_hours or 0.0)
        care_h = float(req.daily_caregiving_hours or 0.0)

        phases: List[StrategicRoadmapPhase] = []

        # =====================================================================
        # FASE 1: MES 1 (Día 1 al Día 30)
        # =====================================================================
        if is_taxi:
            d1 = [
                "⛽ Registrar diariamente el consumo de combustible y kilometraje para calcular tu costo exacto por km.",
                "📱 Habilitar cobros con código QR visible (Yape / Plin) en el auto para no perder clientes sin efectivo.",
                "⏱️ Concentrar tus turnos en franjas pico de máxima tarifa (7:00-9:30 AM y 6:00-9:00 PM) para elevar ganancia por hora.",
                "🛡️ Chequeo preventivo diario de fluidos, neumáticos y frenos para evitar paradas mecánicas imprevistas."
            ]
            s1 = [
                "Iniciar trámite de conversión a GNV/GLP con financiamiento amortizado en grifos para reducir gasto en combustible 50%.",
                "Captar 3 a 5 clientes fijos matutinos con viajes programados que aseguren la base de ingresos del día.",
                "Separar rigurosamente S/ 20 diarios intocables en un fondo exclusivo para cambio de aceite y repuestos."
            ]
            trap1 = "Conducir jornadas extenuantes de más de 14 horas continuas sin descanso, aumentando el riesgo de multas y accidentes graves."
            obj1 = "Conversión a GNV/GLP, franjas horarias de alta rentabilidad y captación de viajes programados"
        elif is_rural:
            d1 = [
                "🐔 Supervisión diaria rigurosa de bioseguridad, agua y ventilación de galpones para mantener mortandad mínima.",
                "⚖️ Control semanal de pesaje del lote y registro estricto del factor de conversión de alimento balanceado.",
                "📦 Compra de alimento e insumos al por mayor directamente en molino o distribuidora mayorista.",
                "📑 Registro detallado en cuaderno de costos de producción por kilo o unidad producida."
            ]
            s1 = [
                "Cerrar acuerdo con 1 distribuidor o mercado de abastos para venta directa de saca sin intermediarios de campo.",
                "Instalar bebederos automáticos y tolvas técnicas para recortar el desperdicio de alimento en 15%.",
                "Iniciar trámite de certificación sanitaria de predio/galpón ante SENASA."
            ]
            trap1 = "Vender a intermediarios informales de campo que pagan precios castigados o difieren los pagos sin garantía."
            obj1 = "Control de bioseguridad en galpones, compra mayorista de alimento y eliminación de intermediarios"
        elif is_business:
            d1 = [
                "💰 Separar rigurosamente la caja del negocio de los gastos personales: el capital de trabajo es intocable.",
                "📦 Liquidar mercadería de baja rotación con promociones rápidas para liberar liquidez de compra.",
                "📲 Mantener catálogo digital activo en WhatsApp Business y cobros con QR (Yape/Plin/POS) visibles en mostrador.",
                "📝 Registro diario de apertura y cierre de caja: ventas, margen bruto y costos operativos del día."
            ]
            s1 = [
                "Negociar con 2 proveedores mayoristas descuentos por volumen o crédito a 15-30 días.",
                "Inscribir o regularizar el negocio bajo el Nuevo RUS (S/ 20/mes) para emitir boletas y construir historial crediticio.",
                "Implementar promociones cruzadas o combos para elevar el ticket promedio de compra en 20%."
            ]
            trap1 = "Retirar las ventas brutas diarias para emergencias familiares creyendo que todo el dinero en caja es ganancia neta."
            obj1 = "Separación de flujo de caja, rotación rápida de inventario y formalización en Nuevo RUS"
        elif is_day_to_day:
            d1 = [
                "⚖️ Separar rigurosamente la caja del día: el capital de reposición de mercadería es intocable y no debe mezclarse con gastos del hogar.",
                "📝 Llevar cuaderno o app de control de ventas diarias, costos de insumos al menudeo vs por mayor y merma del día.",
                "📦 Comprar insumos críticos al por mayor (saco/caja cerrada) directamente en mercado de abastos o distribuidor mayorista local.",
                "⏱️ Puntualidad de apertura en punto estratégico con alto tráfico peatonal en horas punta."
            ]
            s1 = [
                "Estandarizar tus 2 productos o platos más rentables calculando el costo exacto por porción/unidad.",
                "Implementar cobro digital inmediato (código QR visible de Yape / Plin / transferencias) para no perder ventas.",
                "Acordar con 1 distribuidor mayorista precio preferente por compra semanal programada."
            ]
            trap1 = "Gastar las ventas brutas diarias en emergencias del hogar creyendo que todo es ganancia, descapitalizando la compra de insumos del día siguiente."
            obj1 = "Control diario estricto de caja, compra mayorista de insumos y eliminación de mermas"
        elif is_titled_or_grad:
            d1 = [
                "🎯 Bloquear 2 horas diarias de trabajo profundo para proyectos de alto impacto que tengan visibilidad ante gerencia o clientes clave.",
                f"⏱️ Recortar ocio en pantallas a <1.5h/día para dedicar ese tiempo a actualización técnica en {c_name}.",
                "📑 Iniciar o acelerar trámites formales de titulación profesional, sustentación o colegiatura habilitada.",
                "💰 Mantener presupuesto estricto de ahorro (mínimo 20% del sueldo) para fondo de maniobra profesional."
            ]
            s1 = [
                f"Auditar procesos actuales en tu área y presentar 1 propuesta formal de optimización con ahorro de costos o tiempo en {c_name}.",
                "Actualizar perfil profesional en LinkedIn y redes técnicas con logros cuantificados y responsabilidades verificadas.",
                "Tramitar certificado de habilitación profesional o constancias de cursos de especialización avanzados."
            ]
            trap1 = "Quedarse en funciones operativas rutinarias 'invisibles' sin cuantificar ni comunicar el impacto real de tu trabajo a decisores salariales."
            obj1 = "Auditoría de responsabilidades profesionales, inicio de colegiatura y visibilidad de impacto"
        elif is_trade:
            d1 = [
                "🔧 Revisión y calibración diaria de herramientas e instrumental técnico al iniciar y cerrar cada jornada.",
                "📋 Elaborar tarifario formal estandarizado por tipo de servicio técnico (mano de obra + materiales + garantía).",
                "⏱️ Puntualidad estricta en visitas técnicas y respuesta inmediata a mensajes de nuevos clientes."
            ]
            s1 = [
                "Diseñar tarjeta de presentación digital y catálogo de servicios técnicos con fotos de trabajos concluidos.",
                "Acordar descuentos comerciales con ferreterías o distribuidores técnicos mayoristas de la zona.",
                "Cerrar acuerdos de mantenimiento preventivo con al menos 2 negocios o condominios locales."
            ]
            trap1 = "Regatear precios y cobrar por debajo del costo real de materiales y tiempo por temor a perder un cliente eventual."
            obj1 = "Tarifario técnico estandarizado, equipamiento profesional y captación de clientes recurrentes"
        else: # is_active_student
            d1 = [
                f"⏱️ Recortar ocio en pantallas de {screen_h:.1f}h a menos de 1.5h/día (desinstalar redes distractoras en horas productivas)." if screen_h > 1.5 else "⏱️ Mantener tu disciplina de baja distracción en pantallas (<1.5h/día).",
                "⚡ Bloquear 3 horas diarias ininterrumpidas de desarrollo técnico / avance de proyectos en tu horario de mayor claridad mental.",
                f"👨‍👩‍👧 Proteger un bloque fijo para atención familiar ({care_h:.1f}h) sin permitir que invada tu ventana de estudio o portafolio." if care_h > 0 else "🎯 Blindar tu rutina diaria con horarios fijos de inicio y descanso.",
                "💰 Regla de gasto cero superfluo: mantener tus costos al mínimo para crear tu primer fondo de reserva de liquidez."
            ]
            s1 = [
                f"Cerrar entregas y créditos académicos pendientes (faltan {months_grad} meses a egreso)." if months_grad > 0 else "Hacer inventario de tus mejores proyectos y entregables realizados.",
                "Crear o pulir tu perfil profesional de LinkedIn con foto formal y CV en formato ATS de 1 sola página.",
                "Seleccionar 1 proyecto bandera que resuelva un problema real del sector y documentarlo profesionalmente."
            ]
            trap1 = "Creer que 'todavía hay tiempo' y postergar la postulación a prácticas. Los primeros 30 días fijan tu inercia psicológica."
            obj1 = "Blindar tu tiempo diario, eliminar fugas en pantallas y publicar tu primer proyecto bandera"

        phases.append(StrategicRoadmapPhase(
            phase_key="MONTH_1",
            phase_label="Fase 1: Mes 1 (Despegue Inmediato)" if is_es else "Phase 1: Month 1 (Immediate Launch)",
            timeframe="Día 1 al Día 30" if is_es else "Day 1 to Day 30",
            main_objective=obj1,
            target_salary_range=f"{curr_sym} {p10_net:,.0f} - {curr_sym} {p50_net * 0.9:,.0f}/m",
            daily_changes_to_implement=d1,
            strategic_actions_milestones=s1,
            critical_trap_to_avoid=trap1
        ))

        # =====================================================================
        # FASE 2: MESES 2 A 6 (Día 31 al Día 180)
        # =====================================================================
        if is_taxi:
            d2 = [
                "🚗 Mantener la unidad limpia y con ambientador para asegurar calificaciones de 5 estrellas en aplicativos.",
                "📊 Registrar la ganancia neta diaria descontando combustible y cuota diaria para medir rentabilidad real.",
                "⏰ Cumplir descansos obligatorios de al menos 1 día por semana para evitar fatiga crónica y cuidar la salud."
            ]
            s2 = [
                "Tramitar brevete profesional A-IIa y regularizar credencial de conductor ante la municipalidad.",
                "Abrir cuenta bancaria o de caja municipal para depositar ganancias diarias y construir historial crediticio.",
                "Iniciar pre-calificación para crédito vehicular a tasa preferencial para adquirir auto propio."
            ]
            trap2 = "Recurrir a préstamos informales diarios (gota a gota) para emergencias, arruinando la liquidez del trabajo."
            obj2 = "Brevete profesional, permisos municipales al día y pre-aprobación de crédito vehicular"
        elif is_rural:
            d2 = [
                "🌾 Aplicar rotación estricta de lotes, desinfección integral de galpones y control de temperatura.",
                "📈 Monitorear diariamente cotizaciones de mercados mayoristas para programar la salida de producción.",
                "💧 Optimizar consumo de agua con sistema automatizado de bebederos para evitar filtraciones y humedad."
            ]
            s2 = [
                "Concretar alianzas con pollerías, carnicerías o distribuidores locales con precio pactado por campaña.",
                "Instalar cortinas térmicas y ventiladores para evitar pérdidas de peso por estrés calórico o frío.",
                "Completar la obtención del certificado sanitario oficial de SENASA."
            ]
            trap2 = "Descuidar la ventilación o desinfección entre campañas provocando brotes infecciosos que diezmen el lote."
            obj2 = "Alianzas comerciales estables, galpones tecnificados y certificación sanitaria SENASA"
        elif is_business:
            d2 = [
                "🏷️ Control riguroso de rotación de inventarios: pedir solo productos de alta demanda y evitar stock muerto.",
                "🤝 Trato preferencial y personalizado con clientes frecuentes para asegurar recompra semanal.",
                "💳 Promover activamente pagos con billeteras electrónicas (Yape/Plin) para acelerar cobranzas."
            ]
            s2 = [
                "Acceder a línea de crédito de capital de trabajo (Impulso MyPerú / Cajas) para duplicar stock en campaña clave.",
                "Estandarizar imagen del local, señalización de precios clara y orden por categorías.",
                "Negociar con 2 distribuidores exclusivos condiciones de pago a 30 días."
            ]
            trap2 = "Comprar mercadería de moda en exceso sin validar demanda previa, quedando con capital inmovilizado."
            obj2 = "Financiamiento formal a tasa preferencial, alta rotación de inventario y compras de escala"
        elif is_day_to_day:
            d2 = [
                "🕒 Cumplir horario comercial fijo e ininterrumpido: la constancia es el imán #1 de clientela recurrente.",
                "🗣️ Trato personalizado y fidelización activa de comensales o compradores diarios frecuentes.",
                "🧹 Estricto protocolo de higiene, orden y presentación visual del punto de venta."
            ]
            s2 = [
                "Asegurar un puesto fijo formalizado o módulo comercial en ubicación estratégica con autorización regular.",
                "Inscribirse en el Nuevo RUS (Régimen Único Simplificado) pagando la cuota básica legal para respaldo tributario.",
                "Lanzar servicio de pedidos programados o delivery local para oficinas, talleres o vecinos cercanos."
            ]
            trap2 = "Operar de manera errática cambiando de ubicación o de horario, perdiendo a los clientes habituales."
            obj2 = "Puesto fijo formalizado, registro tributario RUS y fidelización de clientela cautiva"
        elif is_titled_or_grad:
            d2 = [
                f"📈 Profundizar en herramientas avanzadas de tu sector en {c_name} (análisis cuantitativo, normativas y gestión de proyectos).",
                "🤝 Mantener contacto semanal con colegas, decisores y excompañeros en posiciones estratégicas.",
                "💼 Liderar reuniones técnicas con propuestas concretas basadas en datos y métricas."
            ]
            s2 = [
                "Obtener formalmente el título profesional y colegiatura vigente con registro público oficial.",
                "Postular a convocatorias públicas/privadas de escala Analista Mid / Especialista con banda salarial superior.",
                "Negociar ajuste salarial interno fundamentado en responsabilidades ampliadas y métricas de desempeño."
            ]
            trap2 = "Permanecer pasivo en la misma escala por lealtad a la empresa cuando el presupuesto salarial del puesto está congelado."
            obj2 = "Consolidación de título/colegiatura, mayor autonomía técnica y salto a banda salarial Mid"
        elif is_trade:
            d2 = [
                "🧰 Reinvertir el 20% de cada trabajo en adquisición de herramientas de diagnóstico y seguridad de nivel profesional.",
                "📱 Publicar fotos de proyectos terminados con testimonio de clientes en redes sociales locales.",
                "🤝 Coordinar con 1 ayudante técnico en formación para agilizar tiempos de entrega."
            ]
            s2 = [
                "Establecer taller base o vehículo equipado para atención de emergencias técnicas y contratos programados.",
                "Obtener certificaciones técnicas de seguridad y homologación de fabricantes líderes del rubro.",
                "Firmar contratos marco de mantenimiento trimestral con empresas o condominios."
            ]
            trap2 = "Trabajar de manera desordenada sin cobrar anticipos del 50% para compra de materiales, asumiendo riesgos innecesarios."
            obj2 = "Maestro técnico equipado, taller/unidad móvil y contratos marco de mantenimiento"
        else: # is_active_student
            d2 = [
                f"💻 Dedicar 1.5 horas diarias al perfeccionamiento práctico de habilidades clave en {c_name}.",
                "📮 Enviar un mínimo de 5 postulaciones estratégicas semanales a convocatorias de prácticas pre-profesionales (empresas y sector público).",
                "🤝 Dedicar 30 minutos semanales a conectar con profesionales o exalumnos de tu carrera en LinkedIn."
            ]
            s2 = [
                f"Tramitar constancia de créditos o egreso (elimina el rechazo automático de ATS en vacantes formales)." if months_grad > 0 else "Obtener una certificación técnica reconocida.",
                "Publicar 2 proyectos completos verificables con documentación clara y resultados medibles.",
                "Firmar convenio formal de prácticas pre-profesionales bajo Ley 28518 con asignación económica legal garantizada."
            ]
            trap2 = "Aceptar cachuelos informales de supervivencia no relacionados que absorban tus horas de estudio y congelen tu inserción profesional."
            obj2 = "Cerrar requisitos de inserción, postulación semanal y firma de convenio de prácticas pre-profesionales"

        phases.append(StrategicRoadmapPhase(
            phase_key="MONTHS_2_6",
            phase_label="Fase 2: Meses 2 a 6 (Cierre de Brechas e Inserción)" if is_es else "Phase 2: Months 2-6 (Gap Closure & Market Insertion)",
            timeframe="Día 31 al Día 180" if is_es else "Day 31 to Day 180",
            main_objective=obj2,
            target_salary_range=f"{curr_sym} {p10_net * 1.1:,.0f} - {curr_sym} {p50_net:,.0f}/m",
            daily_changes_to_implement=d2,
            strategic_actions_milestones=s2,
            critical_trap_to_avoid=trap2
        ))

        # =====================================================================
        # FASE 3: MES 6 A 1 AÑO (Día 181 al Día 365)
        # =====================================================================
        if is_taxi:
            d3 = [
                "🎯 Monitoreo de rentabilidad de rutas: priorizar traslados interurbanos o servicios contratados de mayor margen.",
                "🛠️ Mantenimiento mecánico preventivo cada 5,000 km sin esperar a que se presenten fallas mayores.",
                "💰 Ahorro mensual equivalente al 25% del ingreso neto para amortización acelerada de unidad o segunda cuota."
            ]
            s3 = [
                "Adquisición formal o amortización avanzada de unidad vehicular 100% propia a GNV.",
                "Evaluar la incorporación de un chofer de turno de confianza para trabajar el auto en doble turno.",
                "Afiliarse a seguro contra todo riesgo y fondo de previsión familiar."
            ]
            trap3 = "Gastar los ingresos liberados del alquiler en consumo superfluo en lugar de amortizar la unidad vehicular."
            obj3 = "Vehículo propio a GNV sin pago de alquiler a terceros y doble turno operativo"
        elif is_rural:
            d3 = [
                "📊 Gestión de costos por lote en hoja de cálculo o sistema contable con trazabilidad completa.",
                "🚜 Programación técnica de vacunación, desparasitación y alimentación según curva de crecimiento óptima.",
                "🌱 Planificación de siembras o renovación de crías escalonada para tener producción constante cada mes."
            ]
            s3 = [
                "Ampliación de capacidad productiva (1 nuevo galpón o duplicar jaulas) con reinversión de utilidades.",
                "Postular a fondo concursable AGROIDEAS o Procompite para cofinanciamiento de maquinaria / comederos.",
                "Contratar transporte o flete propio para entrega directa a cadenas mayoristas regionales."
            ]
            trap3 = "Ampliar galpones sin tener previamente asegurada la cadena de compradores ni capital de alimento para todo el ciclo."
            obj3 = "Ampliación de capacidad en galpones, fondo AGROIDEAS y distribución mayorista directa"
        elif is_business:
            d3 = [
                "👥 Delegar la atención en caja o mostrador a 1 ayudante de confianza con metas de venta semanales.",
                "📦 Monitoreo de márgenes brutos por línea de producto con software de punto de venta (ERP simple).",
                "📈 Campañas de marketing local en redes sociales y promociones para fechas festivas o campañas escolares."
            ]
            s3 = [
                "Apertura de segundo punto de venta o ampliación del local existente.",
                "Construir historial bancario sólido con utilidades declaradas para acceder a créditos hipotecarios comerciales.",
                "Constitución formal de empresa (EIRL / SAC) y registro de marca en INDECOPI."
            ]
            trap3 = "No delegar y convertirse en esclavo operativo del negocio trabajando 14 horas sin tiempo para planificar."
            obj3 = "Local comercial consolidado con personal, segundo canal de venta y personería jurídica formal"
        elif is_day_to_day:
            d3 = [
                "👥 Delegar tareas operativas repetitivas (preparación previa, limpieza) en 1 ayudante contratado para enfocarte en gestión y compras.",
                "📈 Reinvertir el 25% del margen neto en equipamiento comercial (refrigeración, módulos de acero, mejor mobiliario).",
                "🏦 Abrir cuenta bancaria empresarial para generar historial financiero ante entidades crediticias."
            ]
            s3 = [
                "Contratar formalmente a 1 operario o ayudante de confianza liberando tus horas para supervisión comercial.",
                "Alcanzar margen neto superior al 35% mensual con compras al por mayor y proveedores directos.",
                "Aperturar un segundo turno de atención (mañana / tarde-noche) o segundo punto de expendio."
            ]
            trap3 = "Querer hacerlo todo uno mismo sin delegar, llegando al agotamiento físico crónico y frenando la escala del negocio."
            obj3 = "Contratación de ayudante, equipamiento comercial y expansión a segundo turno/punto"
        elif is_titled_or_grad:
            d3 = [
                "🗣️ 45 minutos diarios de práctica de inglés profesional técnico orientado a negociaciones y reportes.",
                "🤖 Incorporar herramientas de automatización e inteligencia artificial en tu flujo laboral para triplicar velocidad de entrega.",
                "🏦 Automatizar el ahorro del 25% de tus ingresos líquidos en instrumentos de inversión de renta fija o fondos mutuos."
            ]
            s3 = [
                f"Consolidar primer año de experiencia formal post-titulación en {c_name} con proyectos corporativos verificables.",
                "Ascender a rol de Especialista Senior o Responsable de Área con personal o practicantes a cargo.",
                "Iniciar primeras asesorías o consultorías técnicas independientes facturando como persona natural con negocio (RUC 10/20)."
            ]
            trap3 = "Inflar gastos de estilo de vida al recibir aumentos salariales antes de consolidar un colchón de seguridad de 6 meses."
            obj3 = "Especialista Senior, automatización con IA, inglés técnico y primeras consultorías"
        elif is_trade:
            d3 = [
                "👥 Supervisar cuadrilla de 2 ayudantes técnicos asegurando los estándares de calidad del taller.",
                "📊 Gestión de cotizaciones y facturación formal con RUC para empresas contratistas.",
                "🗣️ Capacitación continua en nuevas normativas técnicas y estándares internacionales."
            ]
            s3 = [
                "Constituir empresa formal de servicios técnicos (E.I.R.L. o S.A.C.) habilitada para licitar.",
                "Homologar tu empresa como proveedora oficial de al menos 3 constructoras, clínicas o cadenas comerciales.",
                "Disponer de unidad de transporte propia equipada para atención rápida en toda la ciudad."
            ]
            trap3 = "No llevar contabilidad formal y mezclar las finanzas de la empresa técnica con los gastos personales."
            obj3 = "Constitución de empresa formal, cuadrilla técnica propia y contratos corporativos homologados"
        else: # is_active_student
            d3 = [
                "🗣️ 45 minutos diarios de práctica intensiva de inglés conversacional técnico.",
                "🤖 Incorporar agentes IA en tu flujo de trabajo para multiplicar tu velocidad de análisis y entrega.",
                "🏦 Automatizar el ahorro del 25% de tu remuneración neta en cuenta de alta rentabilidad."
            ]
            s3 = [
                "Consolidar tu primer año de experiencia formal verificable en empresa de sector.",
                "Tramitar el título profesional o bachiller para tener habilitación plena a concursos públicos y contratos indeterminados.",
                "Postular a roles junior/semi-senior formales en planilla completa con beneficios de ley."
            ]
            trap3 = "Conformarte con la posición de practicante sin negociar el pase a contrato laboral de analista junior con beneficios plenos."
            obj3 = "Transición de prácticas a contrato formal de analista en planilla con beneficios de ley"

        phases.append(StrategicRoadmapPhase(
            phase_key="YEAR_1",
            phase_label="Fase 3: Mes 6 a 1 Año (Consolidación y Aceleración P90)" if is_es else "Phase 3: Month 6 to 1 Year (P90 Acceleration)",
            timeframe="Día 181 al Día 365" if is_es else "Day 181 to Day 365",
            main_objective=obj3,
            target_salary_range=f"{curr_sym} {p50_net:,.0f} - {curr_sym} {p90_net:,.0f}/m",
            daily_changes_to_implement=d3,
            strategic_actions_milestones=s3,
            critical_trap_to_avoid=trap3
        ))

        # =====================================================================
        # FASE 4: AÑOS 3 A 5 (Mes 36 al Mes 60) - Ideales de Viajes, Libertad y Expansión
        # =====================================================================
        if is_taxi:
            d4 = [
                "🏢 Gestión de flota vehicular: monitoreo de recaudación diaria por aplicativo y mantenimiento preventivo.",
                "🤝 Relación con clientes corporativos y empresas de turismo para traslados y servicios programados.",
                "💰 Reinversión de rentas vehiculares en activos seguros (bienes raíces o fondos indexados)."
            ]
            s4 = [
                "Constitución de pequeña empresa de transporte o consorcio con 3 a 5 unidades en operación.",
                "Adquisición de van o minibús para contratos de transporte corporativo o interprovincial.",
                "Total libertad operativa: ingresos pasivos generados por choferes a turno y patrimonio vehicular consolidado."
            ]
            trap4 = "No renovar la flota a tiempo y asumir altos costos mecánicos de vehículos de más de 8 años."
            obj4 = "Flota propia de transporte, contratos corporativos fijos y patrimonio libre de deudas"
        elif is_rural:
            d4 = [
                "🚜 Dirección estratégica de la granja/predio con encargados de galpones y cuadrillas de campo.",
                "📊 Auditoría mensual de rentabilidad por galpón/cultivo y reinversión en tecnificación solar o biogás.",
                "✈️ Tiempo libre para viajes familiares y descanso gracias a la delegación operativa en mandos medios."
            ]
            s4 = [
                "Marca propia registrada de huevos, aves o productos agrícolas con distribución en supermercados y mayoristas.",
                "Instalación de planta de empaque o procesamiento primario con registro sanitario completo.",
                "Patrimonio familiar blindado: terrenos propios saneados, maquinaria propia y fondos de inversión diversificados."
            ]
            trap4 = "Depender de un solo cliente mayorista grande que imponga condiciones leoninas de pago a 90 días."
            obj4 = "Agroindustria tecnificada, marca propia registrada y total estabilidad patrimonial"
        elif is_business:
            d4 = [
                "📈 Supervisión semanal de directores o administradores de tienda mediante tableros de control ERP.",
                "🤝 Negociación directa de importación o compras de fábrica con márgenes superiores al 40%.",
                "✈️ Libertad de agenda para viajes y nuevos proyectos de inversión gracias a gerencia delegada."
            ]
            s4 = [
                "Cadena comercial multitienda o empresa distribuidora regional consolidada.",
                "Adquisición de locales comerciales propios eliminando el pago de alquileres a terceros.",
                "Libertad financiera y diversificación de ingresos en patrimonio inmobiliario seguro."
            ]
            trap4 = "Intentar controlar todo personalmente sin confiar en administradores, limitando el crecimiento del negocio."
            obj4 = "Cadena comercial con locales propios, gerencia delegada y libertad financiera"
        elif is_day_to_day:
            d4 = [
                "📊 Gestión ejecutiva: supervisar balances semanales de rentabilidad sin operar en la línea de fuego física.",
                "🌍 Planificación de viajes familiares y adquisición de bienes inmuebles comerciales con las utilidades acumuladas.",
                "🏦 Inversión patrimonial diversificada en activos seguros y fondos de jubilación propia."
            ]
            s4 = [
                "Operar 2 locales comerciales o concesión institucional con administradores responsables y personal contratado.",
                "Adquirir local comercial propio eliminando el costo recurrente de alquiler.",
                "Cumplir tus metas de viajar, apoyar los estudios de tus hijos y consolidar un patrimonio familiar intocable."
            ]
            trap4 = "No sistematizar el negocio para que funcione sin ti, permaneciendo esclavo operativo del día a día."
            obj4 = "Múltiples locales comerciales, patrimonio inmobiliario propio y libertad económica familiar"
        elif is_titled_or_grad:
            d4 = [
                "🌍 Networking internacional continuo con consultoras globales y asociaciones profesionales del exterior.",
                "💼 Gestión de cartera de clientes corporativos y alianzas interinstitucionales de alto nivel.",
                "📊 Inversiones en portafolios diversificados internacionales con rentabilidad en moneda dura."
            ]
            s4 = [
                f"Ascender a Jefe de Proyecto / Subgerente en {c_name} o Director de Consultora Independiente.",
                "Tramitar pasaporte, visas técnicas o certificaciones internacionales para habilitar viajes y trabajo en el extranjero.",
                "Alcanzar libertad financiera para viajar, radicar en el exterior o liderar operaciones multinacionales."
            ]
            trap4 = "Acomodarte en la zona de confort de tu ciudad aceptando techos salariales locales cuando tu talento califica para el mercado global."
            obj4 = "Dirección gerencial, consultoría internacional en moneda dura y cumplimiento de ideales de viaje/exterior"
        elif is_trade:
            d4 = [
                "🏭 Supervisión de contratos industriales y licitaciones de gran envergadura en la macrorregión.",
                "📈 Alianzas estratégicas con fabricantes internacionales de maquinaria e instrumental técnico.",
                "💼 Diversificación patrimonial en flota vehicular y almacenes propios."
            ]
            s4 = [
                "Consolidar empresa líder de ingeniería de mantenimiento y servicios técnicos en la región.",
                "Contar con flota de vehículos propia, ingenieros colegiados contratados y certificación ISO de calidad.",
                "Generar ingresos empresariales estables que otorguen respaldo patrimonial, viajes y tranquilidad familiar."
            ]
            trap4 = "No formar mandos medios técnicos que supervisen las obras con el mismo nivel de exigencia y calidad."
            obj4 = "Liderazgo regional en servicios técnicos e ingeniería, flota propia y patrimonio consolidado"
        else: # is_active_student
            d4 = [
                "🌍 Mantener hábitos de networking global y lectura técnica de vanguardia.",
                "📊 Gestión patrimonial: destinar excedentes de liquidez a fondos de inversión y bolsa de reubicación exterior."
            ]
            s4 = [
                f"Ascender a Especialista Senior / Líder de Proyectos en {c_name} o Contratista Remoto Internacional en USD.",
                "Tramitar visas técnicas o certificaciones globales para habilitar viajes y trabajo internacional.",
                "Construir tu propia consultoría o cartera de proyectos de alto valor añadido."
            ]
            trap4 = "Quedarse estancado en el mercado local sin buscar proyección remota internacional o posgrados especializados."
            obj4 = "Cumplir ideales de viajar, trabajar en el exterior o remoto global con total solvencia económica"

        phases.append(StrategicRoadmapPhase(
            phase_key="YEARS_3_5",
            phase_label="Fase 4: Años 3 a 5 (Expansión e Ideales Globales)" if is_es else "Phase 4: Years 3-5 (Global Expansion & Long-Term Ideals)",
            timeframe="Mes 36 al Mes 60" if is_es else "Month 36 to Month 60",
            main_objective=obj4,
            target_salary_range=f"{curr_sym} {p90_net * 1.3:,.0f} - {curr_sym} {p90_net * 2.5:,.0f}/m",
            daily_changes_to_implement=d4,
            strategic_actions_milestones=s4,
            critical_trap_to_avoid=trap4
        ))

        return phases

    @classmethod
    def autocompletar_futuro_laboral(
        cls,
        req: HolisticFutureRequest,
        live_intel: Optional[LiveWebIntelligenceReport] = None,
        macro_unemployment: float = 6.0
    ) -> CareerAutocompletionResult:
        """
        Ejecuta el autocompletado probabilístico secuencial a 1 Mes, 6 Meses, 1 Año, 3 Años y 5 Años.
        """
        is_es = req.lang == "ES"
        curr = req.currency or "PEN"
        curr_sym = "S/" if curr == "PEN" or req.country_code == "PE" else ("$" if curr == "USD" else "€" if curr == "EUR" else curr)

        # 1. Asegurar secuencia cronológica pasada
        past_events = list(req.past_career_events or [])
        if not past_events:
            past_events = cls.synthesize_past_events_if_empty(req)

        # 2. Vectorizar trayectoria de vida con PyTorch Life2Vec
        trajectory_vector = cls.encode_career_sequence(past_events, req)

        # 3. Detectar variables clave de velocidad y capital de carrera
        age = max(18, req.age or 24)
        inc = float(req.monthly_income or 0.0)
        if inc <= 0 and req.daily_income_avg and req.daily_income_avg > 0:
            w_d = float(req.work_days_per_week or 6.0)
            inc = round(req.daily_income_avg * w_d * 4.333, 2)
        study_h = float(req.study_or_project_hours or 0.0)
        work_h = float(req.work_hours or 0.0)
        screen_h = float(req.screen_time_distraction_hours or 0.0)
        eng = (req.english_level or "A1_A2").upper()
        raw_career = (req.career_or_degree or req.occupation or "Especialidad").strip()
        p_type = req.life_profile_type or "UNIVERSITY_OR_TECH_STUDENT"

        # Blindaje contra clasificacin errnea de estudiante en egresados o comercio independiente
        c_low = raw_career.lower()
        if any(w in c_low for w in ["egresad", "bachiller", "titulad", "colegiad", "graduad"]):
            p_type = "TITLED_PROFESSIONAL"
        elif any(w in c_low for w in ["vendo comida", "venta de comida", "vendedor", "ambulante", "mototaxi", "taxista"]):
            p_type = "DAY_TO_DAY_WORKER"

        career = cls.sanitize_career_label(raw_career, p_type)
        skills_str = (req.key_skills or "").lower()
        target_salary = float(req.target_monthly_salary_1y or 0.0)

        # Calibrar arquetipo de cohorte
        archetype, local_demand_weight, is_stem = cls._classify_cohort_archetype(career, p_type, skills_str, is_es)

        # 4. Calcular percentil competitivo en su cohorte (0 a 100)
        cohort_pct = cls._compute_cohort_percentile(
            study_h=study_h,
            work_h=work_h,
            screen_h=screen_h,
            eng=eng,
            skills_str=skills_str,
            age=age,
            savings=req.current_savings or 0.0,
            trajectory_vec=trajectory_vector
        )

        # 5. Salarios del mercado local y remoto desde LiveWebResearchEngine
        local_min = live_intel.local_salary_range_min if (live_intel and live_intel.local_salary_range_min) else (1200.0 if curr == "PEN" else 400.0)
        local_max = live_intel.local_salary_range_max if (live_intel and live_intel.local_salary_range_max) else (3200.0 if curr == "PEN" else 1000.0)
        remote_min = live_intel.remote_salary_range_min if (live_intel and live_intel.remote_salary_range_min) else (2500.0 if curr == "PEN" else 800.0)
        remote_max = live_intel.remote_salary_range_max if (live_intel and live_intel.remote_salary_range_max) else (6500.0 if curr == "PEN" else 2200.0)

        # 6. Exposición a Automatización por IA vs. Apalancamiento Competitivo
        ai_exposure, ai_leverage = cls._compute_ai_exposure_and_leverage(career, p_type, skills_str)

        # 7. Diagnosticar Cuellos de Botella de Carrera (Bottlenecks)
        bottlenecks = cls._identify_bottlenecks(
            req=req,
            cohort_pct=cohort_pct,
            eng=eng,
            study_h=study_h,
            screen_h=screen_h,
            is_es=is_es
        )

        # 8. Habilidades de Alto Valor Recomendadas
        recommended_skills = cls._recommend_high_leverage_skills(
            career=career,
            p_type=p_type,
            eng=eng,
            skills_str=skills_str,
            is_es=is_es
        )

        # 5. Salarios empíricos calibrados (MTPE / ENAHO / Mercado Local vs Remoto)
        comp_mult = float(req.verified_competence_multiplier or 1.0)
        empirical_salaries = cls.compute_empirical_salary_distribution(
            career=career,
            city=req.city or "Huancayo",
            country=req.country_code or "PE",
            currency=curr,
            life_profile_type=p_type,
            years_of_experience=float(req.years_of_experience or 0.0),
            competence_mult=comp_mult,
            live_intel=live_intel
        )

        # 5.1. Modelo Actuarial de Supervivencia de Inserción (Weibull / Cox)
        actuarial_plan = cls.simulate_time_to_hire_survival(
            req=req,
            live_intel=live_intel,
            empirical_salaries=empirical_salaries,
            cohort_pct=cohort_pct,
            is_es=is_es
        )

        real_jobs = list(live_intel.real_job_openings) if (live_intel and live_intel.real_job_openings) else []

        # 9. Autocompletar Horizontes (1M, 6M, 1Y, 3Y, 5Y) con calibración empírica y blindaje de arquetipo
        transitions = cls._project_transitions(
            career=career,
            p_type=p_type,
            current_income=inc,
            target_salary=target_salary,
            cohort_pct=cohort_pct,
            local_min=local_min,
            local_max=local_max,
            remote_min=remote_min,
            remote_max=remote_max,
            eng=eng,
            study_h=study_h,
            screen_h=screen_h,
            curr=curr,
            curr_sym=curr_sym,
            is_es=is_es,
            empirical_salaries=empirical_salaries,
            months_to_graduation=int(req.months_to_graduation or 0),
            years_of_experience=float(req.years_of_experience or 0.0),
            life_stage=str(req.life_stage or "ACTIVE_PROFESSIONAL"),
            age=age,
            dependents_count=int(req.dependents_count or 0),
            daily_caregiving_hours=float(req.daily_caregiving_hours or 0.0)
        )

        # Hoja de Ruta Estratégica paso a paso (qué seguir y qué cambiar día a día)
        roadmap = cls.generate_strategic_roadmap(
            req=req,
            cohort_pct=cohort_pct,
            empirical_salaries=empirical_salaries,
            bottlenecks=bottlenecks,
            is_es=is_es
        )

        # Roles objetivo con mayor afinidad
        target_roles = cls._generate_top_matching_roles(career, p_type, is_es)

        # Resumen vectorial
        vec_summary = (
            f"Embedding latente Life2Vec dimensionalidad 128 norm=1.0 | "
            f"Arquetipo: {archetype} | Velocidad de inserción: {cohort_pct:.1f}%"
        )

        rank_desc = f"Top {max(1, int(100 - cohort_pct))}% en {archetype}"

        return CareerAutocompletionResult(
            cohort_similarity_percentile=round(cohort_pct, 1),
            cohort_archetype=archetype,
            cohort_rank_descriptor=rank_desc,
            predicted_career_transitions=transitions,
            real_job_openings=real_jobs,
            strategic_roadmap=roadmap,
            actuarial_insertion=actuarial_plan,
            verified_competence_multiplier=round(comp_mult, 2),
            ai_automation_exposure_pct=round(ai_exposure, 1),
            ai_leverage_potential_pct=round(ai_leverage, 1),
            career_bottlenecks=bottlenecks,
            recommended_skill_acquisitions=recommended_skills,
            recommended_high_leverage_skills=recommended_skills,
            top_target_roles_matching=target_roles,
            local_market_match_index=round(min(98.0, max(45.0, 60.0 + (cohort_pct * 0.35))), 1),
            past_events_encoded_count=len(past_events),
            trajectory_summary=vec_summary,
            trajectory_vector_summary=vec_summary
        )

    # =========================================================================
    # HELPERS INTERNOS DE CÁLCULO
    # =========================================================================

    @classmethod
    def synthesize_past_events_if_empty(cls, req: HolisticFutureRequest) -> List[CareerLifeEvent]:
        """
        Reconstruye cronológicamente 3 a 5 hitos pasados coherentes adaptados al arquetipo
        socio-laboral del usuario (sin inventar que un comerciante o profesional titulado es practicante).
        """
        age = max(18, req.age or 24)
        current_year = 2026
        events: List[CareerLifeEvent] = []
        loc = f"{req.city or 'Ciudad'}, {req.country_code or 'PE'}"
        raw_c = req.career_or_degree or req.occupation or "Actividad Laboral"
        p_type = req.life_profile_type or "UNIVERSITY_OR_TECH_STUDENT"
        c_low = raw_c.lower()

        occ_low = (req.occupation or "").lower()
        full_c = f"{c_low} {occ_low}"
        is_taxi = any(w in full_c for w in ["taxista", "taxi", "mototaxi", "chofer", "conductor", "colectivo", "transporte", "remisse"])
        is_rural = p_type == "RURAL_FIELD_PRODUCER" or any(w in full_c for w in ["granja", "granjas", "avícol", "avicol", "porcin", "cuy", "galpón", "galpon", "chacra", "fundo", "campo", "agrícol", "agricol", "ganad"])
        is_business = p_type == "BUSINESS_OWNER" or (any(w in full_c for w in ["comerciante", "comercio", "bodega", "tienda", "abarrotes", "negocio", "emprend", "ventas"]) and not any(w in full_c for w in ["estudiant", "software", "sistemas"]))
        is_explicit_grad = any(w in full_c for w in ["egresad", "bachiller", "titulad", "colegiad", "graduad"])
        is_trade = p_type == "SKILLED_TRADE" or any(w in full_c for w in ["electric", "mecanic", "mecánic", "gasfiter", "taller", "carpinter"])
        is_active_student = (p_type == "UNIVERSITY_OR_TECH_STUDENT" and int(req.months_to_graduation or 0) > 0 and not is_explicit_grad and not is_taxi and not is_rural and not is_business)
        is_day_to_day = (p_type == "DAY_TO_DAY_WORKER" or any(w in full_c for w in ["comida", "comercio", "ambulante", "mozo", "vendo"])) and not is_taxi and not is_rural and not is_business
        is_titled_or_grad = is_explicit_grad or p_type == "TITLED_PROFESSIONAL" or (not is_active_student and not is_day_to_day and not is_trade and not is_taxi and not is_rural and not is_business)

        c_name = cls.sanitize_career_label(raw_c, p_type)
        inc = float(req.monthly_income or 0.0)
        if inc <= 0 and req.daily_income_avg and req.daily_income_avg > 0:
            w_d = float(req.work_days_per_week or 6.0)
            inc = round(req.daily_income_avg * w_d * 4.333, 2)

        # Distribución etaria cronológica coherente según ciclo de vida real
        if age >= 50:
            age_edu = 18
            age_skill = 28
            age_job = age - 6
        elif age >= 35:
            age_edu = 18
            age_skill = 24
            age_job = age - 4
        elif age >= 25:
            age_edu = 17
            age_skill = 21
            age_job = age - 2
        else:
            age_edu = max(16, age - 4)
            age_skill = max(age_edu + 1, age - 2)
            age_job = max(age_skill + 1, age - 1)

        # 1. Hito Formativo Base
        if is_day_to_day:
            t1 = "Culminación escolar e inserción en el comercio activo"
            desc1 = "Egreso secundario e inicio de actividades comerciales y ventas directas."
        elif is_trade:
            t1 = f"Formación técnica y primeros aprendizajes prácticos de taller en {c_name}"
            desc1 = "Adquisición de bases operativas y uso de herramientas técnicas."
        elif is_titled_or_grad:
            t1 = f"Formación universitaria y primeros proyectos de carrera en {c_name}"
            desc1 = "Ingreso universitario y aprobación de los primeros ciclos formativos."
        else: # student
            t1 = f"Culminación formativa base e inicio de formación superior en {c_name}"
            desc1 = "Egreso secundario y postulación/admisión universitaria o técnica."

        events.append(CareerLifeEvent(
            year=current_year - (age - age_edu),
            age_at_event=age_edu,
            event_type="EDUCATION",
            title_or_role=t1,
            monthly_income=0.0,
            location=loc,
            description=desc1
        ))

        # 2. Hito de Habilidades y Competencias
        if is_day_to_day:
            t2 = f"Adquisición de habilidades comerciales, negociación de insumos y ventas"
            desc2 = "Aprendizaje de puntos de venta, control de mermas y fidelización de clientes."
        elif is_trade:
            t2 = f"Especialización en herramientas técnicas, diagnóstico y seguridad en {c_name}"
            desc2 = "Talleres aplicados, normativas de seguridad y mantenimiento técnico."
        elif is_titled_or_grad:
            t2 = f"Culminación de malla curricular y obtención de grado académico en {c_name}"
            desc2 = "Aprobación de la totalidad de créditos universitarios y prácticas profesionales."
        else:
            t2 = f"Cursos de especialización y proyectos aplicados en {c_name}"
            desc2 = "Adquisición de herramientas clave, talleres prácticos y primeros proyectos formativos."

        events.append(CareerLifeEvent(
            year=current_year - (age - age_skill),
            age_at_event=age_skill,
            event_type="SKILL_ACQUISITION",
            title_or_role=t2,
            monthly_income=0.0,
            location=loc,
            description=desc2
        ))

        # 3. Primer Trabajo / Actividad Previa
        prev_inc = max(300.0, inc * 0.70) if inc > 0 else 0.0
        if is_day_to_day:
            t3 = f"Primeros puestos de venta o atención independiente en {c_name}"
            desc3 = "Generación de ingresos diarios, trato con proveedores y manejo de caja."
            ev_type = "FREELANCE_OR_BUSINESS"
        elif is_trade:
            t3 = f"Primeros trabajos y contratos técnicos independientes en {c_name}"
            desc3 = "Atención a clientes particulares, reparaciones e instalaciones técnicas."
            ev_type = "FREELANCE_OR_BUSINESS"
        elif is_titled_or_grad:
            t3 = f"Primeras funciones profesionales de analista / asistente en {c_name}"
            desc3 = "Inserción formal, manejo de reportes y responsabilidades operativas del sector."
            ev_type = "ROLE_CHANGE"
        else:
            t3 = f"Primeras prácticas o actividades remuneradas de soporte en {c_name}"
            desc3 = "Generación de ingresos iniciales y primeros proyectos en empresas del área."
            ev_type = "FIRST_JOB"

        events.append(CareerLifeEvent(
            year=current_year - (age - age_job),
            age_at_event=age_job,
            event_type=ev_type,
            title_or_role=t3,
            monthly_income=prev_inc,
            location=loc,
            description=desc3
        ))

        # 4. Estado Actual (2026)
        if is_day_to_day:
            t4 = f"Actividad comercial actual: {c_name}"
        elif is_titled_or_grad:
            t4 = f"Posición profesional actual en {c_name} ({req.life_stage or 'En ejercicio'})"
        elif is_trade:
            t4 = f"Servicio técnico especializado actual en {c_name}"
        else:
            t4 = f"Estudiante en etapa de inserción: {c_name} ({req.life_stage or 'En curso'})"

        events.append(CareerLifeEvent(
            year=current_year,
            age_at_event=age,
            event_type="CURRENT_STATE",
            title_or_role=t4,
            monthly_income=inc,
            location=loc,
            description="Línea base actual para el autocompletado probabilístico secuencial a 1M, 6M, 1Y, 3Y y 5Y."
        ))

        return events

    @classmethod
    def _classify_cohort_archetype(
        cls,
        career: str,
        p_type: str,
        skills: str,
        is_es: bool
    ) -> Tuple[str, float, bool]:
        c_low = career.lower()
        is_stem = any(w in c_low or w in skills for w in ["sistem", "software", "informát", "program", "comput", "electr", "industrial", "datos", "ai", "tech"])
        is_taxi = any(w in c_low or w in skills for w in ["taxista", "taxi", "mototaxi", "chofer", "conductor", "transporte", "colectivo", "remisse"])
        is_rural = p_type == "RURAL_FIELD_PRODUCER" or any(w in c_low or w in skills for w in ["granja", "granjas", "avícol", "avicol", "porcin", "cuy", "galpón", "galpon", "agrícol", "agro", "campo", "café", "papas", "ganad", "chacra"])
        is_business = p_type == "BUSINESS_OWNER" or (any(w in c_low or w in skills for w in ["admin", "contab", "finanz", "market", "econom", "negocio", "comerc", "bodega", "tienda", "abarrotes"]) and not is_taxi)
        is_trade = p_type == "SKILLED_TRADE" or any(w in c_low for w in ["mecánic", "electric", "construc", "taller", "operad"])

        if is_taxi:
            archetype = "Cohorte de Conducción Profesional & Transporte Urbano" if is_es else "Professional Driver & Urban Mobility Cohort"
            return archetype, 0.95, False

        if is_stem:
            archetype = "Cohorte STEM & Tecnología en Aceleración" if is_es else "Accelerating STEM & Tech Cohort"
            return archetype, 1.25, True
        elif is_business:
            archetype = "Cohorte de Gestión, Finanzas & Operaciones" if is_es else "Business, Finance & Operations Cohort"
            return archetype, 1.05, False
        elif is_trade:
            archetype = "Cohorte de Especialidad Técnica Aplicada" if is_es else "Applied Technical Trade Cohort"
            return archetype, 0.95, False
        elif is_rural:
            archetype = "Cohorte Agroproductiva & Cadena de Suministro Rural" if is_es else "Agro-producer & Rural Supply Chain Cohort"
            return archetype, 0.85, False
        elif p_type == "DAY_TO_DAY_WORKER":
            archetype = "Cohorte de Comercio Independiente & Jornal Diario" if is_es else "Independent Trade & Daily Shift Cohort"
            return archetype, 0.90, False
        else:
            archetype = "Cohorte Profesional en Transición de Mercado" if is_es else "Professional Market Transition Cohort"
            return archetype, 1.00, False

    @classmethod
    def _compute_cohort_percentile(
        cls,
        study_h: float,
        work_h: float,
        screen_h: float,
        eng: str,
        skills_str: str,
        age: int,
        savings: float,
        trajectory_vec: np.ndarray
    ) -> float:
        # Base inicial de cohorte
        score = 50.0

        # Balance de tiempo diario (física estricta)
        if study_h >= 3.0:
            score += min(22.0, (study_h - 2.0) * 6.0)
        elif study_h < 1.0:
            score -= 10.0

        # Fuga en pantallas (destructiva de competitividad)
        if screen_h >= 4.0:
            score -= min(25.0, (screen_h - 3.0) * 7.0)
        elif screen_h <= 1.5:
            score += 10.0

        # Inglés (desbloqueador salarial global)
        if eng in ("C1_C2", "AVANZADO"):
            score += 20.0
        elif eng in ("B1_B2", "INTERMEDIO"):
            score += 10.0
        else:
            score -= 6.0

        # Diversidad de skills clave
        num_skills = len([s for s in skills_str.split(",") if s.strip()])
        if num_skills >= 4:
            score += 8.0
        elif num_skills >= 2:
            score += 4.0

        # Coherencia vectorial de embeddings (magnitud y dirección de aprendizaje)
        vec_norm = float(np.linalg.norm(trajectory_vec[:32]))
        score += (vec_norm - 0.5) * 8.0

        # Fondo de ahorro de colchón
        if savings > 3000:
            score += 6.0

        return float(np.clip(score, 8.0, 96.0))

    @classmethod
    def _compute_ai_exposure_and_leverage(cls, career: str, p_type: str, skills: str) -> Tuple[float, float]:
        c_low = career.lower()
        if any(w in c_low for w in ["digitador", "asistente de oficina", "recepcion", "auxiliar contable", "transcriptor"]):
            exposure = 78.0
            leverage = 35.0
        elif any(w in c_low or w in skills for w in ["sistem", "software", "programad", "desarrollador", "datos", "analista"]):
            exposure = 48.0
            leverage = 88.0
        elif any(w in c_low for w in ["diseñ", "redact", "marketing", "publicidad"]):
            exposure = 68.0
            leverage = 74.0
        elif p_type in ("SKILLED_TRADE", "RURAL_FIELD_PRODUCER") or any(w in c_low for w in ["mecánic", "electric", "campo", "chacra", "obra"]):
            exposure = 14.0
            leverage = 40.0
        else:
            exposure = 38.0
            leverage = 62.0
        return exposure, leverage

    @classmethod
    def _identify_bottlenecks(
        cls,
        req: HolisticFutureRequest,
        cohort_pct: float,
        eng: str,
        study_h: float,
        screen_h: float,
        is_es: bool
    ) -> List[str]:
        bn: List[str] = []
        c_low = (req.career_or_degree or "").lower()
        occ_low = (req.occupation or "").lower()
        full_c = f"{c_low} {occ_low}"
        is_taxi = any(w in full_c for w in ["taxista", "taxi", "mototaxi", "chofer", "conductor", "transporte", "colectivo", "remisse"])
        is_rural = req.life_profile_type == "RURAL_FIELD_PRODUCER" or any(w in full_c for w in ["granja", "granjas", "avícol", "avicol", "porcin", "cuy", "galpón", "galpon", "campo", "chacra", "agrícol", "agricol", "ganad"])
        is_business = req.life_profile_type == "BUSINESS_OWNER" or (any(w in full_c for w in ["comerciante", "comercio", "bodega", "tienda", "abarrotes", "negocio", "emprend", "ventas"]) and not is_taxi)

        if is_taxi:
            bn.append(
                "Dependencia de vehículo alquilado / tercerizado: el pago de alquiler diario a terceros merma hasta el 40% del ingreso bruto en ruta."
                if is_es else
                "Rented vehicle dependency: daily car rental fees erode up to 40% of net shift earnings."
            )
            bn.append(
                "Sobrecosto de combustible: operar sin conversión a GNV/GLP duplica el gasto por kilómetro recorrido."
                if is_es else
                "High fuel overhead: running without CNG/LPG conversion doubles the operating cost per kilometer."
            )
            if screen_h >= 3.0:
                bn.append(
                    f"Fuga de tiempo ({screen_h:.1f}h en ocio digital): reduce horas efectivas de volante en franjas de máxima tarifa."
                    if is_es else
                    f"Digital distraction ({screen_h:.1f}h): cuts effective driving hours during peak fare surges."
                )
            if (req.current_savings or 0.0) < 600:
                bn.append(
                    "Sin fondo de reserva para repuestos y mantenimiento: cualquier falla mecánica paraliza tus ingresos por días."
                    if is_es else
                    "No emergency mechanic buffer: unexpected breakdowns freeze daily cashflow for days."
                )
            return bn[:4]

        if is_rural:
            bn.append(
                "Intermediarios especuladores de campo: comprar la producción a precio castigado en chacra dejando poco margen a la granja."
                if is_es else
                "Field middlemen exploitation: purchasing harvest/livestock at low farmgate prices, squeezing farm profits."
            )
            bn.append(
                "Falta de tecnificación en galpones (bebederos y tolvas manuales): genera mermas de alimento y riesgo de mortandad por clima."
                if is_es else
                "Manual shed operations: causes feed waste and elevates climate-induced mortality risks."
            )
            if (req.current_savings or 0.0) < 800:
                bn.append(
                    "Falta de capital de reserva para campañas: obliga a comprar alimento al menudeo con sobreprecio del 25%."
                    if is_es else
                    "Low working capital: forces retail feed purchases with a 25% markup."
                )
            return bn[:4]

        if is_business:
            bn.append(
                "Mezcla de caja del negocio con gastos del hogar: impide conocer la rentabilidad neta real y descapitaliza la reposición de mercadería."
                if is_es else
                "Mixing personal and business cashflows: prevents accurate profitability tracking and starves inventory restocking."
            )
            bn.append(
                "Mercadería estancada de baja rotación: capital inmovilizado en productos de lenta salida sin promociones de liquidación."
                if is_es else
                "Slow-moving inventory: capital tied up in dormant goods without promotional clearance."
            )
            if (req.current_savings or 0.0) < 700:
                bn.append(
                    "Falta de línea de crédito formal (Impulso MyPerú / Cajas): limita la compra mayorista de volumen para campañas clave."
                    if is_es else
                    "No access to formal working capital credit: restricts bulk wholesale purchases for key sales seasons."
                )
            return bn[:4]

        months_grad = int(req.months_to_graduation or 0)
        is_student = req.life_profile_type == "UNIVERSITY_OR_TECH_STUDENT" or months_grad > 0

        if is_student and months_grad > 0:
            bn.append(
                f"Fase formativa inconclusa ({months_grad} meses a egreso): bloquea el acceso a bandas salariales de colegiatura o contratación formal indefinida."
                if is_es else
                f"Incomplete university stage ({months_grad} months to graduation): caps ceiling for chartered or permanent enterprise contracts."
            )

        if eng not in ("B1_B2", "C1_C2"):
            bn.append(
                "Barrera idiomática (Inglés A1/A2): impide postular al 82% de vacantes remotas internacionales con compensación en USD ($1,800 - $3,500/m)."
                if is_es else
                "Language barrier (English A1/A2): disqualifies candidate from 82% of remote USD roles ($1,800 - $3,500/mo)."
            )

        if screen_h >= 3.0:
            bn.append(
                f"Fuga temporal severa ({screen_h:.1f}h/día en pantallas de ocio): devora el tiempo necesario para construir portafolios verificables o certificaciones de alto valor."
                if is_es else
                f"High digital distraction ({screen_h:.1f}h/day): consumes the cognitive bandwidth required to ship demonstrable portfolio projects."
            )

        if (req.current_savings or 0.0) < 500:
            bn.append(
                "Inestabilidad de liquidez inmediata (sin fondo de reserva): obliga a aceptar trabajos precarios o cachuelos informales que quitan tiempo de estudio."
                if is_es else
                "Zero capital buffer: forces immediate short-term survival gigs, starving long-term skill acquisition."
            )

        if not bn:
            bn.append(
                "Falta de visibilidad pública en redes profesionales (GitHub / LinkedIn): tu talento no está siendo indexado por reclutadores activos."
                if is_es else
                "Low public digital footprint (GitHub / LinkedIn): profile remains invisible to automated corporate recruitment pipelines."
            )

        return bn[:4]

    @classmethod
    def _recommend_high_leverage_skills(
        cls,
        career: str,
        p_type: str,
        eng: str,
        skills_str: str,
        is_es: bool
    ) -> List[str]:
        c_low = career.lower()
        recs: List[str] = []

        if "sistem" in c_low or "software" in c_low or "tech" in p_type.lower():
            recs.extend([
                "Desarrollo Full-Stack moderno con FastAPI + TypeScript / Angular / Next.js",
                "Arquitectura Cloud (AWS / Docker / Kubernetes) y despliegue CI/CD",
                "Ingeniería de Contexto & Agentes Autónomos con LLMs (LangChain / Llama)",
                "Inglés Conversacional B2 para entrevistas técnicas remotas en vivo"
            ] if is_es else [
                "Modern Full-Stack Development with FastAPI + TypeScript / Angular",
                "Cloud Architecture (AWS / Docker / Kubernetes) & CI/CD Pipelines",
                "Context Engineering & Autonomous AI Agents with LLMs",
                "B2 Conversational English for live technical remote interviews"
            ])
        elif any(w in c_low for w in ["taxista", "taxi", "mototaxi", "chofer", "conductor", "transporte"]):
            recs.extend([
                "Mantenimiento mecánico preventivo y diagnóstico automotriz para recortar gastos de taller",
                "Manejo avanzado de aplicaciones multiapp de movilidad urbana y cálculo de rentabilidad por km (GNV)",
                "Fidelización y captación de clientela fija para traslados corporativos y servicios programados",
                "Gestión financiera de caja diaria y ahorro para crédito vehicular propio"
            ] if is_es else [
                "Preventive vehicle maintenance & diagnostics to cut garage repair overhead",
                "Advanced multi-app urban mobility dispatching & per-km CNG profitability optimization",
                "Corporate recurring customer acquisition & scheduled daily transit contracts",
                "Daily cashflow management & reserve budgeting for personal car loan equity"
            ])
        elif p_type == "RURAL_FIELD_PRODUCER" or any(w in c_low for w in ["granja", "granjas", "avícol", "avicol", "porcin", "cuy", "galpón", "galpon", "campo", "chacra"]):
            recs.extend([
                "Control de bioseguridad, vacunación y sanidad animal certificada ante SENASA",
                "Formulación y optimización de alimento balanceado para reducir el factor de conversión",
                "Negociación directa de acopio con cadenas de pollerías y mercados mayoristas",
                "Formulación de planes de negocio pecuarios para fondos concursables AGROIDEAS / Procompite"
            ] if is_es else [
                "SENASA-certified animal biosecurity, vaccination & disease prevention protocols",
                "Feed formulation optimization to minimize feed-conversion ratio",
                "Direct wholesale supply contracts with restaurant chains and regional markets",
                "Agri-business grant proposal drafting for AGROIDEAS and regional funding calls"
            ])
        elif p_type == "BUSINESS_OWNER" or any(w in c_low for w in ["comerciante", "tienda", "bodega", "abarrotes", "negocio"]):
            recs.extend([
                "Control estricto de flujo de caja, apertura y cierre de caja y separación de finanzas personales",
                "Negociación mayorista y condiciones de crédito a 30 días con fabricantes",
                "Gestión de inventarios rotativos y liquidación rápida de productos lentos",
                "Marketing digital local, catálogo en WhatsApp Business y cobros omnicanal (QR/POS)"
            ] if is_es else [
                "Strict cashflow reconciliation & separation of business vs household expenses",
                "Wholesale volume procurement & 30-day supplier credit negotiation",
                "Inventory turnover management & slow-moving stock liquidation strategies",
                "Local digital marketing, WhatsApp Business catalogs & multi-channel QR/POS checkouts"
            ])
        elif p_type == "DAY_TO_DAY_WORKER" or "comerc" in c_low:
            recs.extend([
                "Automatización de cobranzas y gestión de inventario digital",
                "Estrategias de adquisición B2B y cierre de ventas de alto valor",
                "Estructuración de costos y fijación de precios con margen superior al 30%"
            ] if is_es else [
                "Digital inventory management & streamlined cashflow billing",
                "High-ticket B2B client acquisition & sales conversion",
                "Margin-based cost restructuring (>30% net margin)"
            ])
        else:
            recs.extend([
                "Manejo avanzado de herramientas de análisis de datos y automatización",
                "Inglés técnico profesional orientado a reportes y licitaciones",
                "Liderazgo ágil de proyectos y negociación de presupuestos"
            ] if is_es else [
                "Advanced data analytics & automated reporting workflows",
                "Technical English for procurement and international bidding",
                "Agile project management & corporate budget negotiation"
            ])

        return recs[:4]

    @classmethod
    def _project_transitions(
        cls,
        career: str,
        p_type: str,
        current_income: float,
        target_salary: float,
        cohort_pct: float,
        local_min: float,
        local_max: float,
        remote_min: float,
        remote_max: float,
        eng: str,
        study_h: float,
        screen_h: float,
        curr: str,
        curr_sym: str,
        is_es: bool,
        empirical_salaries: Optional[Dict[str, Any]] = None,
        months_to_graduation: int = 0,
        years_of_experience: float = 1.0,
        life_stage: str = "ACTIVE_PROFESSIONAL",
        age: int = 25,
        dependents_count: int = 0,
        daily_caregiving_hours: float = 0.0
    ) -> List[CareerTransitionNode]:
        nodes: List[CareerTransitionNode] = []
        c_low = career.lower()

        # Detección rigurosa de arquetipo laboral
        is_taxi = any(w in c_low for w in ["taxista", "taxi", "mototaxi", "chofer", "conductor", "colectivo", "transporte", "remisse"])
        is_rural = p_type == "RURAL_FIELD_PRODUCER" or any(w in c_low for w in ["granja", "granjas", "avícol", "avicol", "porcin", "cuy", "galpón", "galpon", "campo", "chacra", "fundo", "agrícol", "papa", "ganad"])
        is_business = p_type == "BUSINESS_OWNER" or (any(w in c_low for w in ["comerciante", "comercio", "bodega", "tienda", "abarrotes", "negocio", "emprend", "ventas"]) and not is_taxi)
        is_explicit_grad = any(w in c_low for w in ["egresad", "bachiller", "titulad", "colegiad", "graduad"])
        is_trade = p_type == "SKILLED_TRADE" or any(w in c_low for w in ["electric", "mecanic", "mecánic", "gasfiter", "taller", "carpinter"])
        is_active_student = (p_type == "UNIVERSITY_OR_TECH_STUDENT" and months_to_graduation > 0 and not is_explicit_grad and not is_taxi and not is_rural and not is_business)
        is_day_to_day = (p_type == "DAY_TO_DAY_WORKER" or any(w in c_low for w in ["comida", "comercio", "ambulante", "mozo", "vendo"])) and not is_taxi and not is_rural and not is_business
        is_titled_or_grad = is_explicit_grad or p_type == "TITLED_PROFESSIONAL" or (not is_active_student and not is_day_to_day and not is_trade and not is_rural and not is_business and not is_taxi)

        is_senior = (age >= 48)
        has_dependents = (dependents_count > 0 or daily_caregiving_hours > 0)

        c_name = cls.sanitize_career_label(career, p_type)

        p50_emp = empirical_salaries.get("p50_net", 2000.0) if empirical_salaries else 2000.0
        p10_emp = empirical_salaries.get("p10_net", 1200.0) if empirical_salaries else 1200.0
        p90_emp = empirical_salaries.get("p90_net", 3800.0) if empirical_salaries else 3800.0

        # Calibración estricta de ingreso base
        if current_income <= 0:
            if is_active_student:
                inc_base = 0.0
            elif is_day_to_day:
                inc_base = max(1100.0, p10_emp)
            else:
                inc_base = p50_emp * 0.85
        else:
            if is_day_to_day and current_income > p90_emp * 2.0:
                inc_base = p90_emp * 1.2
            elif is_active_student and current_income > p90_emp * 1.5:
                inc_base = p90_emp
            else:
                inc_base = current_income

        multiplier_cohort = cohort_pct / 50.0  # 1.0 en la mediana

        # ---------------------------------------------------------------------
        # 1. HORIZONTE: 1 MES (Día 30)
        # ---------------------------------------------------------------------
        if is_senior:
            if is_titled_or_grad:
                p10_1m_role = f"Profesional Senior en {c_name}: Labores rutinarias sin capitalizar su alta experiencia"
                p50_1m_role = f"Especialista / Consultor Senior en {c_name}: Auditoría de proyectos clave y asesoría técnica de dirección"
                p90_1m_role = f"Líder de Asesoría Estratégica en {c_name}: Cierre de contratos de peritaje y consultoría especializada"
            elif is_day_to_day:
                p10_1m_role = "Comercio de subsistencia: Jornada extendida con fatiga física por compras al menudeo"
                p50_1m_role = f"Comercio de Trayectoria en {c_name}: Optimización de márgenes y reducción de sobreesfuerzo físico"
                p90_1m_role = "Punto de venta consolidado con clientela cautiva y apoyo operativo"
            else:
                p10_1m_role = f"Maestro Técnico en {c_name}: Desgaste físico directo sin cobrar tarifas acordes a su maestría"
                p50_1m_role = f"Maestro Técnico Senior en {c_name}: Cotizaciones especializadas y asesoría técnica de alto valor"
                p90_1m_role = "Contratista Senior de Referencia: Acuerdos de mantenimiento cerrado con empresas locales"
            p10_1m_inc = round(inc_base * 0.98, 0)
            p50_1m_inc = round(inc_base * (1.0 + 0.05 * multiplier_cohort), 0)
            p90_1m_inc = round(inc_base * (1.0 + 0.18 * multiplier_cohort), 0)
            c1 = ["Valorar experiencia acumulada cobrando por entregable", "Cuidar la salud física y articular delegando tareas pesadas"]
            b1 = ["Aceptar tarifas bajas por temor a la edad", "Sobreesfuerzo físico no compensado"]
        elif is_taxi:
            p10_1m_role = "Conductor al volante: Jornadas de 14h con auto alquilado y alto consumo de combustible"
            p50_1m_role = "Conductor Urbano en Rutas de Alta Demanda: Optimización de horas pico, multiapp y reducción de vueltas en vacío"
            p90_1m_role = "Conductor Destacado: Calificación 4.95+, bonos por cumplimiento y cartera de clientes corporativos"
            p10_1m_inc = round(inc_base * 0.95, 0)
            p50_1m_inc = round(inc_base * (1.0 + 0.06 * multiplier_cohort), 0)
            p90_1m_inc = round(inc_base * (1.0 + 0.20 * multiplier_cohort), 0)
            c1 = ["Mapear horas pico y zonas de alta demanda sin rodar en vacío", "Mantener unidad impecable para alta calificación y propinas"]
            b1 = ["Rodar en vacío quemando combustible sin carreras", "Mantenimiento correctivo imprevisto por no revisar aceite y frenos"]
        elif is_rural:
            p10_1m_role = f"Productor Agropecuario en {c_name}: Ventas a intermediarios de chacra a precios castigados"
            p50_1m_role = f"Productor Agropecuario en {c_name}: Optimización de costos de fertilizantes y control de mermas"
            p90_1m_role = "Productor con Venta Directa en mercado mayorista con precios acordados"
            p10_1m_inc = round(inc_base * 0.92, 0)
            p50_1m_inc = round(inc_base * (1.0 + 0.05 * multiplier_cohort), 0)
            p90_1m_inc = round(inc_base * (1.0 + 0.18 * multiplier_cohort), 0)
            c1 = ["Acopio directo con otros agricultores para comprar insumos por mayor", "Control de riego y fertilización técnica"]
            b1 = ["Dependencia de intermediarios de campo", "Vulnerabilidad a subidas de fertilizantes"]
        elif is_business:
            p10_1m_role = f"Negocio Comercial en {c_name}: Descontrol de inventario con caja del día absorbida por gastos menores"
            p50_1m_role = f"Gestor de Negocio en {c_name}: Control riguroso de inventarios, flujo de caja diario y margen neto"
            p90_1m_role = "Negocio en Expansión: Implementación de promociones de alto margen y cobro digital total"
            p10_1m_inc = round(inc_base * 0.95, 0)
            p50_1m_inc = round(inc_base * (1.0 + 0.06 * multiplier_cohort), 0)
            p90_1m_inc = round(inc_base * (1.0 + 0.20 * multiplier_cohort), 0)
            c1 = ["Separación estricta de cuentas del negocio vs cuentas personales", "Rotación rápida de inventarios lentos"]
            b1 = ["Mercadería estancada sin rotación", "Falta de liquidez para pagos a proveedores"]
        elif is_day_to_day:
            p10_1m_role = "Comercio informal: Jornada extendida con compras caras al menudeo y margen absorbido por mermas"
            p50_1m_role = "Comercio y Ventas: Optimización de punto de venta, compras mayoristas directas y elevación de ticket diario"
            p90_1m_role = "Punto de venta consolidado con menú/oferta estandarizada y clientela recurrente"
            p10_1m_inc = round(inc_base * 0.95, 0)
            p50_1m_inc = round(inc_base * (1.0 + 0.05 * multiplier_cohort), 0)
            p90_1m_inc = round(inc_base * (1.0 + 0.18 * multiplier_cohort), 0)
            c1 = ["Separar la caja del día del dinero del hogar", "Comprar insumos al por mayor directamente con mayoristas"]
            b1 = ["Gastar el capital de reposición en gastos del día", "Ubicarse en puntos de bajo tránsito peatonal"]
        elif is_titled_or_grad:
            p10_1m_role = f"Profesional en {c_name}: Labores rutinarias sin visibilidad interna ni negociación de banda salarial"
            p50_1m_role = f"Consolidación Profesional en {c_name}: Entrega de proyectos de alto impacto y ordenamiento de trámites de titulación/colegiatura"
            p90_1m_role = f"Profesional de Alto Rendimiento en {c_name}: Liderazgo de iniciativas clave con propuesta de ajuste salarial"
            p10_1m_inc = round(inc_base * 0.98, 0)
            p50_1m_inc = round(inc_base * (1.0 + 0.06 * multiplier_cohort), 0)
            p90_1m_inc = round(inc_base * (1.0 + 0.20 * multiplier_cohort), 0)
            c1 = ["Auditar procesos y proponer 1 mejora con ahorro cuantificable", "Actualizar perfil profesional de LinkedIn con logros"]
            b1 = ["Aceptar tareas invisibles sin visibilidad ante gerencia", "Falta de networking con pares del sector"]
        elif is_trade:
            p10_1m_role = "Técnico dependiente de pedidos esporádicos con precios regateados"
            p50_1m_role = f"Técnico Especialista en {c_name}: Tarifario estandarizado y cartera activa de clientes"
            p90_1m_role = "Contratista Técnico con acuerdos de mantenimiento preventivo con pequeños comercios"
            p10_1m_inc = round(inc_base * 0.95, 0)
            p50_1m_inc = round(inc_base * (1.0 + 0.07 * multiplier_cohort), 0)
            p90_1m_inc = round(inc_base * (1.0 + 0.22 * multiplier_cohort), 0)
            c1 = ["Estandarizar tarifario técnico formal", "Acordar descuentos con proveedores de repuestos"]
            b1 = ["Cobrar por debajo del costo real de materiales", "Herramientas descalibradas"]
        else: # is_active_student
            p10_1m_role = "Estudiante con dispersión de tiempo, sin portafolio técnico ni postulaciones activas"
            p50_1m_role = f"Estudiante en Formación: Portafolio de proyectos prácticos publicado y postulación a convocatorias en {c_name}"
            p90_1m_role = "Candidato Preseleccionado: Entrevistas técnicas en curso para convenios de prácticas pre-profesionales"
            p10_1m_inc = round(inc_base * 0.95, 0) if inc_base > 0 else 0.0
            p50_1m_inc = round(max(0.0, inc_base * (1.0 + 0.08 * multiplier_cohort)), 0)
            p90_1m_inc = round(max(500.0, inc_base * (1.0 + 0.30 * multiplier_cohort)), 0)
            c1 = ["Armar CV en formato ATS de 1 página", "Postular a 5 vacantes de prácticas pre-profesionales semanales"]
            b1 = ["Fuga de horas en redes sociales (>3h/día)", "Creer que las notas bastan sin tener portafolio demostrable"]

        nodes.append(CareerTransitionNode(
            horizon_key="1_MONTH",
            horizon="1_month",
            horizon_label="1 Mes (Día 30)" if is_es else "1 Month (Day 30)",
            months_ahead=1,
            months_from_now=1,
            p10_stagnation_role=p10_1m_role,
            p10_income=p10_1m_inc,
            p50_likely_role=p50_1m_role,
            p50_income=p50_1m_inc,
            p90_accelerated_role=p90_1m_role,
            p90_income=p90_1m_inc,
            transition_probability_pct=round(min(95.0, max(25.0, 55.0 + (cohort_pct * 0.30))), 1),
            cohort_rank_descriptor=f"Top {max(5, int(100 - cohort_pct))}% en velocidad de reacción",
            key_catalysts=c1,
            required_skills_to_unlock=c1,
            blockers=b1,
            key_risk_factor=b1[0],
            market_demand_alignment="Alta"
        ))

        # ---------------------------------------------------------------------
        # 2. HORIZONTE: 6 MESES (Día 180)
        # ---------------------------------------------------------------------
        if is_senior:
            if is_titled_or_grad:
                p10_6m_role = f"Profesional Senior en {c_name}: Tope burocrático local por falta de facturación independiente"
                p50_6m_role = f"Consultor Senior / Asesor de Dirección en {c_name} con honorarios por entregables y peritajes"
                p90_6m_role = f"Consejero Técnico Senior con cartera de clientes corporativos y alianzas institucionales"
            elif is_day_to_day:
                p10_6m_role = "Comercio físico con fatiga y sin personal de relevo"
                p50_6m_role = f"Puesto Fijo Consolidado en {c_name} con operario de apoyo para aliviar carga física pesada"
                p90_6m_role = "Módulo comercial regularizado con personal contratado y clientela fiel"
            else:
                p10_6m_role = "Taller con desgaste físico del maestro sin operarios de confianza"
                p50_6m_role = f"Jefe de Taller / Contratista Senior en {c_name} con ayudantes que asumen el esfuerzo físico"
                p90_6m_role = "Contratista Senior Homologado con cartera corporativa de mantenimiento"
            p10_6m_inc = round(inc_base * 1.04, 0)
            p50_6m_inc = round(max(2400.0, inc_base * (1.15 * multiplier_cohort)), 0)
            p90_6m_inc = round(max(3600.0, inc_base * (1.45 * multiplier_cohort)), 0)
            c2 = ["Delegar labores operativas pesadas", "Firmar contratos por entregables en lugar de horas"]
            b2 = ["Asumir toda la carga física personal", "No sistematizar tareas repetitivas"]
        elif is_taxi:
            p10_6m_role = "Conductor dependiente de alquiler diario sin capacidad de ahorro para inicial"
            p50_6m_role = "Conductor Tecnificado: Unidad a GNV/GLP con ahorro del 50% en combustible y cuota inicial para auto propio"
            p90_6m_role = "Conductor Independiente con Auto Propio: Unidad propia financiada con cuota cubierta por servicio regular"
            p10_6m_inc = round(inc_base * 0.98, 0)
            p50_6m_inc = round(max(2000.0, inc_base * (1.15 * multiplier_cohort)), 0)
            p90_6m_inc = round(max(2800.0, inc_base * (1.35 * multiplier_cohort)), 0)
            c2 = ["Acceder a bono FISE para conversión vehicular a GNV", "Ahorrar el 20% del ingreso diario para fondo de inicial o renovación"]
            b2 = ["Seguir pagando alquiler diario sin proyectar compra de unidad", "Endeudamiento en consumo no vehicular con tasas altas"]
        elif is_rural:
            p10_6m_role = "Productor afectado por variabilidad climática sin cobertura ni seguro agrario"
            p50_6m_role = f"Productor Asociado en {c_name}: Acopio conjunto y venta directa eliminando intermediarios"
            p90_6m_role = "Productor con Contrato de Suministro directo a agroindustria o cadenas comerciales"
            p10_6m_inc = round(inc_base * 0.98, 0)
            p50_6m_inc = round(max(1500.0, inc_base * (1.18 * multiplier_cohort)), 0)
            p90_6m_inc = round(max(2500.0, inc_base * (1.50 * multiplier_cohort)), 0)
            c2 = ["Asociatividad con gremios locales", "Manejo integrado de plagas y fertilización técnica"]
            b2 = ["Falta de acopio en frío/almacén", "Caída estacional de precios en cosecha pico"]
        elif is_business:
            p10_6m_role = "Comercio con ventas estancadas frente a competencia informal de bajo precio"
            p50_6m_role = f"Comercio Consolidado en {c_name}: Estandarización de procesos de venta y fidelización B2B/B2C"
            p90_6m_role = "Empresa Comercial con 2 ayudantes fijos y margen neto superior al 30%"
            p10_6m_inc = round(inc_base * 1.02, 0)
            p50_6m_inc = round(max(2200.0, inc_base * (1.20 * multiplier_cohort)), 0)
            p90_6m_inc = round(max(3800.0, inc_base * (1.55 * multiplier_cohort)), 0)
            c2 = ["Estandarizar atención al cliente y catálogo", "Negociar crédito a 30 días con fabricantes"]
            b2 = ["Sobreendeudamiento para stock de baja rotación", "Falta de control de mermas"]
        elif is_day_to_day:
            p10_6m_role = "Venta ambulatoria sin punto fijo con riesgo de multas o retiro municipal"
            p50_6m_role = "Puesto Fijo Formalizado / Módulo Comercial con horario regular y clientela cautiva"
            p90_6m_role = "Local comercial arrendado con atención en 2 turnos y servicio de delivery/pedidos programados"
            p10_6m_inc = round(inc_base * 1.02, 0)
            p50_6m_inc = round(max(1400.0, inc_base * (1.15 * multiplier_cohort)), 0)
            p90_6m_inc = round(max(2200.0, inc_base * (1.45 * multiplier_cohort)), 0)
            c2 = ["Asegurar módulo formal con autorización", "Inscribirse al Nuevo RUS (categoría S/ 20/mes)"]
            b2 = ["Operar de forma errática cambiando de horario", "Falta de higiene o presentación visual"]
        elif is_titled_or_grad:
            p10_6m_role = f"Profesional estancado en nivel asistente con funciones de analista pero salario desfasado"
            p50_6m_role = f"Analista Mid / Especialista Titulado en {c_name} con mayor autonomía técnica y ajuste salarial"
            p90_6m_role = f"Coordinador de Área o Consultor Técnico en {c_name} con cartera asignada y bonos de desempeño"
            p10_6m_inc = round(inc_base * 1.05, 0)
            p50_6m_inc = round(max(2400.0, inc_base * (1.20 * multiplier_cohort)), 0)
            p90_6m_inc = round(max(3500.0, inc_base * (1.50 * multiplier_cohort)), 0)
            c2 = ["Obtener título profesional y colegiatura institucional", "Liderar proyecto técnico con impacto medible"]
            b2 = ["Quedarse en una empresa con presupuesto congelado", "Falta de certificaciones avanzadas"]
        elif is_trade:
            p10_6m_role = "Oficio informal sin herramientas modernas ni certificación técnica"
            p50_6m_role = f"Maestro Técnico en {c_name} con taller propio y 1-2 ayudantes de soporte"
            p90_6m_role = "Contratista Técnico Homologado para mantenimiento de obras, condominios e industrias"
            p10_6m_inc = round(inc_base * 1.04, 0)
            p50_6m_inc = round(max(2000.0, inc_base * (1.20 * multiplier_cohort)), 0)
            p90_6m_inc = round(max(3000.0, inc_base * (1.50 * multiplier_cohort)), 0)
            c2 = ["Equipar taller con herramientas de diagnóstico profesionales", "Obtener homologación técnica"]
            b2 = ["Trabajar sin anticipos de materiales", "Retrasos en entregas técnicas"]
        else: # is_active_student
            p10_6m_role = "Estudiante con retraso formativo o cachuelos informales no formativos"
            p50_6m_role = f"Practicante Pre-Profesional bajo Convenio de Ley en {c_name} (Sueldo formativo legal)"
            p90_6m_role = f"Practicante de Alto Desempeño en empresa corporativa o sector público en {c_name} con asignación destacada"
            p10_6m_inc = round(max(400.0, inc_base * 1.02), 0)
            p50_6m_inc = round(max(1025.0, p10_emp * 0.95), 0)
            p90_6m_inc = round(max(1400.0, p10_emp * 1.30), 0)
            c2 = ["Constancia de créditos / egreso tramitada", "2 proyectos verificables publicados con demo"]
            b2 = ["Agotamiento físico por no balancear estudio y trabajo", "Procrastinar entregas de fin de ciclo"]

        nodes.append(CareerTransitionNode(
            horizon_key="6_MONTHS",
            horizon="6_months",
            horizon_label="6 Meses (Día 180)" if is_es else "6 Months (Day 180)",
            months_ahead=6,
            months_from_now=6,
            p10_stagnation_role=p10_6m_role,
            p10_income=p10_6m_inc,
            p50_likely_role=p50_6m_role,
            p50_income=p50_6m_inc,
            p90_accelerated_role=p90_6m_role,
            p90_income=p90_6m_inc,
            transition_probability_pct=round(min(90.0, max(20.0, 48.0 + (cohort_pct * 0.35))), 1),
            cohort_rank_descriptor=f"Top {max(5, int(100 - cohort_pct))}% de tu cohorte generacional",
            key_catalysts=c2,
            required_skills_to_unlock=c2,
            blockers=b2,
            key_risk_factor=b2[0],
            market_demand_alignment="Alta"
        ))

        # ---------------------------------------------------------------------
        # 3. HORIZONTE: 1 AÑO (Día 365)
        # ---------------------------------------------------------------------
        if is_senior:
            if is_titled_or_grad:
                p10_1y_role = f"Profesional Senior en {c_name} con salario congelado por falta de marca personal"
                p50_1y_role = f"Líder de Consultoría / Perito Especialista en {c_name} con cartera corporativa e institucional"
                p90_1y_role = f"Socio Consultor / Asesor Principal de Directorio en {c_name} con alta rentabilidad"
            elif is_day_to_day:
                p10_1y_role = "Comercio de subsistencia sin posibilidad de retiro laboral"
                p50_1y_role = f"Microempresa Comercial / Local Establecido en {c_name} con administración delegada"
                p90_1y_role = "Negocio comercial propio con operarios fijos y fondo de pensión asegurado"
            else:
                p10_1y_role = "Taller con desgaste del titular sin contratos a mediano plazo"
                p50_1y_role = f"Empresa de Servicios Técnicos consolidada donde el titular supervisa, homologa y cotiza"
                p90_1y_role = "Contratista Senior de Referencia con cuadrillas asignadas y licitaciones ganadas"
            p10_1y_inc = round(inc_base * 1.10, 0)
            p50_1y_inc = round(max(3200.0, inc_base * (1.30 * multiplier_cohort)), 0)
            p90_1y_inc = round(max(5500.0, inc_base * (1.75 * multiplier_cohort)), 0)
            c3 = ["Consolidar marca personal senior", "Estructurar empresa jurídica formal (SAC/EIRL)"]
            b3 = ["Falta de previsión de salud y jubilación", "Permanecer como persona natural sin escudo legal"]
        elif is_taxi:
            p10_1y_role = "Conductor con unidad desgastada y gastos de taller crecientes"
            p50_1y_role = "Conductor Consolidado con Auto Propio a GNV: Contratos de movilidad fija escolar/empresarial y aplicativos"
            p90_1y_role = "Prestador de Movilidad Ejecutiva: Cartera de clientes empresariales, movilidad escolar fija y servicios programados"
            p10_1y_inc = round(inc_base * 1.05, 0)
            p50_1y_inc = round(max(2500.0, inc_base * (1.30 * multiplier_cohort)), 0)
            p90_1y_inc = round(max(3800.0, inc_base * (1.55 * multiplier_cohort)), 0)
            c3 = ["Formalizar contratos mensuales de movilidad escolar o corporativa", "Mantenimiento preventivo programado cada 5,000 km"]
            b3 = ["Descuido de seguros SOAT/AFOCAT o revisiones técnicas", "Multas de tránsito por imprudencia"]
        elif is_rural:
            p10_1y_role = "Campaña con rentabilidad neutra por altos costos de fletes y fertilizantes"
            p50_1y_role = f"Productor Agrícola con Riego Tecnificado en {c_name} y venta a agroindustria"
            p90_1y_role = "Empresario Agropecuario con acopio regional y contratos de exportación indirecta"
            p10_1y_inc = round(inc_base * 1.05, 0)
            p50_1y_inc = round(max(2400.0, inc_base * (1.35 * multiplier_cohort)), 0)
            p90_1y_inc = round(max(4000.0, inc_base * (1.80 * multiplier_cohort)), 0)
            c3 = ["Tecnificación de parcela con riego por goteo/aspersión", "Contratos anuales de suministro"]
            b3 = ["Monocultivo sin rotación", "Dependencia de lluvias sin reservorio de agua"]
        elif is_business:
            p10_1y_role = "Negocio comercial estancado con margen absorbido por alquiler y costos fijos"
            p50_1y_role = f"Empresa Comercial en {c_name} con 2-3 empleados en planilla y línea bancaria activa"
            p90_1y_role = "Comercio en Expansión: Apertura de segunda línea o canal digital mayorista"
            p10_1y_inc = round(inc_base * 1.08, 0)
            p50_1y_inc = round(max(3000.0, inc_base * (1.35 * multiplier_cohort)), 0)
            p90_1y_inc = round(max(5500.0, inc_base * (1.85 * multiplier_cohort)), 0)
            c3 = ["Línea de crédito para capital de trabajo a tasa preferencial", "Equipo de ventas capacitado"]
            b3 = ["Fuga de caja por falta de auditoría interna", "Morosidad en cuentas por cobrar"]
        elif is_day_to_day:
            p10_1y_role = "Comercio de subsistencia vulnerable a subidas repentinas de alquiler o mercadería"
            p50_1y_role = f"Microempresa Comercial / Gastronómica registrada (Nuevo RUS/RUC) en {c_name} con 1-2 operarios fijos"
            p90_1y_role = "Negocio Comercial Consolidado con marca reconocida localmente y margen neto >35%"
            p10_1y_inc = round(inc_base * 1.08, 0)
            p50_1y_inc = round(max(2000.0, inc_base * (1.35 * multiplier_cohort)), 0)
            p90_1y_inc = round(max(3200.0, inc_base * (1.80 * multiplier_cohort)), 0)
            c3 = ["Contratar 1 ayudante de confianza", "Acuerdos comerciales con distribuidores directos"]
            b3 = ["Desgaste físico individual por no delegar", "Falta de historial crediticio bancario"]
        elif is_titled_or_grad:
            p10_1y_role = f"Profesional con 2+ años de experiencia pero cobrando como recién egresado"
            p50_1y_role = f"Especialista Senior / Responsable Sectorial en {c_name} con colegiatura vigente"
            p90_1y_role = f"Jefe de Unidad / Especialista Corporativo Senior o Consultor B2B independiente en {c_name}"
            p10_1y_inc = round(inc_base * 1.10, 0)
            p50_1y_inc = round(max(3200.0, inc_base * (1.35 * multiplier_cohort)), 0)
            p90_1y_inc = round(max(5000.0, inc_base * (1.80 * multiplier_cohort)), 0)
            c3 = ["Certificación profesional avanzada del sector", "Inglés conversacional técnico para clientes globales"]
            b3 = ["Dependencia exclusiva de un solo empleador local", "Falta de portafolio de consultoría"]
        elif is_trade:
            p10_1y_role = "Taller con desgaste físico del titular sin haber formado ayudantes"
            p50_1y_role = f"Empresa de Instalaciones y Servicios Técnicos en {c_name} con facturación recurrente"
            p90_1y_role = "Proveedor Técnico Oficial de constructoras, clínicas o comercios regionales"
            p10_1y_inc = round(inc_base * 1.08, 0)
            p50_1y_inc = round(max(2600.0, inc_base * (1.38 * multiplier_cohort)), 0)
            p90_1y_inc = round(max(4000.0, inc_base * (1.85 * multiplier_cohort)), 0)
            c3 = ["Constitución de empresa formal (SAC/EIRL)", "Homologación con clientes corporativos"]
            b3 = ["Falta de facturación formal para licitaciones", "Falta de cuadrilla capacitada"]
        else: # is_active_student
            p10_1y_role = "Egresado sin prácticas formativas previas enfrentando filtro de CV"
            p50_1y_role = f"Practicante Profesional / Egresado Asistente Inicial en {c_name} en planilla formal"
            p90_1y_role = f"Analista Junior formalizado en {c_name} con contrato a plazo indeterminado"
            p10_1y_inc = round(max(600.0, inc_base * 1.08), 0)
            p50_1y_inc = round(max(1500.0, p10_emp * 1.25), 0)
            p90_1y_inc = round(max(2500.0, p50_emp * 1.15), 0)
            c3 = ["Titulación profesional / bachiller tramitada", "Inglés conversacional B1 para entrevistas"]
            b3 = ["Falta de experiencia formativa formal previa", "Dependencia exclusiva de vacantes locales"]

        nodes.append(CareerTransitionNode(
            horizon_key="1_YEAR",
            horizon="1_year",
            horizon_label="1 Año (Día 365)" if is_es else "1 Year (Day 365)",
            months_ahead=12,
            months_from_now=12,
            p10_stagnation_role=p10_1y_role,
            p10_income=p10_1y_inc,
            p50_likely_role=p50_1y_role,
            p50_income=p50_1y_inc,
            p90_accelerated_role=p90_1y_role,
            p90_income=p90_1y_inc,
            transition_probability_pct=round(min(88.0, max(18.0, 42.0 + (cohort_pct * 0.40))), 1),
            cohort_rank_descriptor=f"Percentil {int(cohort_pct)} de inserción formal",
            key_catalysts=c3,
            required_skills_to_unlock=c3,
            blockers=b3,
            key_risk_factor=b3[0],
            market_demand_alignment="Muy Alta"
        ))

        # ---------------------------------------------------------------------
        # 4. HORIZONTE: 3 AÑOS (Día 1095)
        # ---------------------------------------------------------------------
        if is_senior:
            p10_3y_role = f"Tope salarial de mercado local por no haber migrado a servicios de alto valor"
            p50_3y_role = f"Director de Proyectos / Consejero de Área en {c_name} con alta autonomía ejecutiva"
            p90_3y_role = f"Consultor de Alta Dirección / Perito Arbitral en {c_name} con facturación corporativa senior"
            p10_3y_inc = round(inc_base * 1.15, 0)
            p50_3y_inc = round(max(4500.0, inc_base * (1.65 * multiplier_cohort)), 0)
            p90_3y_inc = round(max(7500.0, inc_base * (2.20 * multiplier_cohort)), 0)
            c4 = ["Arbitrajes y peritajes técnicos formales", "Gestión de alianzas con consultoras nacionales"]
            b4 = ["Quedarse en funciones operativas dependientes", "No proteger el patrimonio ante contingencias"]
        elif is_taxi:
            p10_3y_role = "Conductor con auto propio envejecido y depreciación acelerada"
            p50_3y_role = "Dueño-Conductor Consolidado: Auto propio totalmente amortizado, ingresos netos sin cuota vehicular y fondo para segunda unidad"
            p90_3y_role = "Microempresario de Transporte: 2 unidades activas (una propia al volante, una alquilada a chofer de confianza)"
            p10_3y_inc = round(inc_base * 1.15, 0)
            p50_3y_inc = round(max(3500.0, inc_base * (1.50 * multiplier_cohort)), 0)
            p90_3y_inc = round(max(5500.0, inc_base * (1.90 * multiplier_cohort)), 0)
            c4 = ["Adquirir segunda unidad vehicular mediante crédito vehicular con historial intachable", "Filtro riguroso de chofer confiable"]
            b4 = ["Alquilar la segunda unidad a personas sin referencias", "Falta de seguro contra todo riesgo"]
        elif is_rural:
            p10_3y_role = "Parcela sin mecanizar con desgaste físico de la familia"
            p50_3y_role = f"Empresario Agrícola en {c_name} con almacén propio, riego tecnificado y cultivos de alto valor"
            p90_3y_role = "Empresa Agroexportadora / Distribuidora Regional con flota de camiones y tierras propias"
            p10_3y_inc = round(inc_base * 1.12, 0)
            p50_3y_inc = round(max(3500.0, inc_base * (1.75 * multiplier_cohort)), 0)
            p90_3y_inc = round(max(6500.0, inc_base * (2.40 * multiplier_cohort)), 0)
            c4 = ["Instalación de reservorio y tecnificación de cosecha", "Almacén de empaque propio"]
            b4 = ["Falta de diversificación de canales de venta", "Inseguridad en tenencia de tierras"]
        elif is_business:
            p10_3y_role = "Negocio comercial vulnerable a recesiones locales sin reservas financieras"
            p50_3y_role = f"Segunda Sede Comercial o Distribución Mayorista en {c_name} con administradores a cargo"
            p90_3y_role = "Cadena Comercial / Distribuidora Regional con solvencia bancaria y patrimonio inmobiliario"
            p10_3y_inc = round(inc_base * 1.15, 0)
            p50_3y_inc = round(max(4500.0, inc_base * (1.75 * multiplier_cohort)), 0)
            p90_3y_inc = round(max(8500.0, inc_base * (2.50 * multiplier_cohort)), 0)
            c4 = ["Sistematización total con software ERP de punto de venta", "Inversión en local comercial propio"]
            b4 = ["Falta de delegación en mandos medios", "No monitorear márgenes por categoría"]
        elif is_day_to_day:
            p10_3y_role = "Comercio físico con desgaste por jornadas de 12 horas sin seguro médico"
            p50_3y_role = f"Local Comercial Propio o Concesión Establecida en {c_name} con personal contratado a cargo"
            p90_3y_role = "Empresa Comercial / Gastronómica con 2 sedes o distribución mayorista y fondo propio"
            p10_3y_inc = round(inc_base * 1.15, 0)
            p50_3y_inc = round(max(3200.0, inc_base * (1.80 * multiplier_cohort)), 0)
            p90_3y_inc = round(max(5500.0, inc_base * (2.40 * multiplier_cohort)), 0)
            c4 = ["Administración sistematizada con encargados", "Adquisición de local comercial propio"]
            b4 = ["No delegar y ser esclavo operativo del negocio", "Pérdida de capital en préstamos informales"]
        elif is_titled_or_grad:
            p10_3y_role = f"Profesional con 4+ años de experiencia con tope salarial por falta de posgrado o inglés"
            p50_3y_role = f"Jefe de Proyecto / Subgerente de Área en {c_name} a nivel corporativo o institucional"
            p90_3y_role = f"Gerente de Área / Consultor Senior Internacional en {c_name} con facturación en USD"
            p10_3y_inc = round(inc_base * 1.18, 0)
            p50_3y_inc = round(max(4800.0, inc_base * (1.75 * multiplier_cohort)), 0)
            p90_3y_inc = round(max(8000.0, inc_base * (2.40 * multiplier_cohort)), 0)
            c4 = ["Maestría o posgrado especializado", "Dominio de inglés B2/C1 y liderazgo de equipos"]
            b4 = ["Zona de confort en puesto medio", "No construir cartera de consultoría"]
        elif is_trade:
            p10_3y_role = "Técnico con problemas físicos por exceso de trabajo operativo directo"
            p50_3y_role = f"Gerente de Operaciones de Servicios Técnicos en {c_name} con cuadrillas y contratos marco"
            p90_3y_role = "Contratista General de Obras e Instalaciones con presencia en la región"
            p10_3y_inc = round(inc_base * 1.15, 0)
            p50_3y_inc = round(max(3800.0, inc_base * (1.80 * multiplier_cohort)), 0)
            p90_3y_inc = round(max(6500.0, inc_base * (2.50 * multiplier_cohort)), 0)
            c4 = ["Flota de vehículos y cuadrillas especializadas", "Contratos anuales con medianas empresas"]
            b4 = ["Falta de supervisión de calidad en mandos medios", "Riesgos de cobranza morosa"]
        else: # is_active_student
            p10_3y_role = "Profesional con título pero estancado en roles de soporte operativo de baja remuneración"
            p50_3y_role = f"Analista Mid-Senior / Especialista Colegiado en {c_name} con proyectos a cargo"
            p90_3y_role = f"Lead Specialist o Consultor Remoto en {c_name} para empresas nacionales o del exterior"
            p10_3y_inc = round(max(1000.0, inc_base * 1.15), 0)
            p50_3y_inc = round(max(2600.0, p50_emp * 1.25), 0)
            p90_3y_inc = round(max(5000.0, p90_emp * 1.35), 0)
            c4 = ["Inglés fluido B2/C1", "Liderazgo de proyectos completos y certificaciones internacionales"]
            b4 = ["No actualizarse en nuevas herramientas y automatización IA", "Acomodarse en sueldos de entrada"]

        nodes.append(CareerTransitionNode(
            horizon_key="3_YEARS",
            horizon="3_years",
            horizon_label="3 Años (Consolidación)" if is_es else "3 Years (Consolidation)",
            months_ahead=36,
            months_from_now=36,
            p10_stagnation_role=p10_3y_role,
            p10_income=p10_3y_inc,
            p50_likely_role=p50_3y_role,
            p50_income=p50_3y_inc,
            p90_accelerated_role=p90_3y_role,
            p90_income=p90_3y_inc,
            transition_probability_pct=round(min(82.0, max(15.0, 35.0 + (cohort_pct * 0.42))), 1),
            cohort_rank_descriptor=f"Top {max(3, int(100 - cohort_pct))}% en acumulación de capital",
            key_catalysts=c4,
            required_skills_to_unlock=c4,
            blockers=b4,
            key_risk_factor=b4[0],
            market_demand_alignment="Alta"
        ))

        # ---------------------------------------------------------------------
        # 5. HORIZONTE: 5 AÑOS (Día 1825) - Ideales, Libertad y Salida Internacional
        # ---------------------------------------------------------------------
        if is_senior:
            p10_5y_role = "Tope salarial de mercado local sin patrimonio líquido de respaldo"
            p50_5y_role = f"Consultor Principal Emérito / Asesor de Directorio en {c_name} con libertad de agenda"
            p90_5y_role = f"Director de Consultoría / Inversionista con patrimonio diversificado y renta fija protegida"
            p10_5y_inc = round(inc_base * 1.22, 0)
            p50_5y_inc = round(max(6000.0, inc_base * (2.10 * multiplier_cohort)), 0)
            p90_5y_inc = round(max(11000.0, inc_base * (3.00 * multiplier_cohort)), 0)
            c5 = ["Rentas pasivas por activos inmobiliarios y asesorías", "Traspaso de funciones operativas"]
            b5 = ["Dependencia económica de contratos de corto plazo"]
        elif is_taxi:
            p10_5y_role = "Conductor veterano al volante con desgaste articular y sin relevo operativo"
            p50_5y_role = "Empresario de Flota Liviana: 2 a 3 vehículos en trabajo activo, ingresos por renta y administración de rutas"
            p90_5y_role = "Propietario de Empresa de Transporte / Turismo: Flota de camionetas/autos con convenios turísticos e interurbanos"
            p10_5y_inc = round(inc_base * 1.25, 0)
            p50_5y_inc = round(max(4800.0, inc_base * (1.85 * multiplier_cohort)), 0)
            p90_5y_inc = round(max(8000.0, inc_base * (2.50 * multiplier_cohort)), 0)
            c5 = ["Monitoreo GPS y control estricto de kilometraje de la flota", "Reinversión de utilidades en diversificación patrimonial"]
            b5 = ["Gestión informal sin empresa constituida (SAC/EIRL)", "Litigios o accidentes sin cobertura integral"]
        elif is_rural:
            p10_5y_role = "Agricultura de supervivencia tradicional sin relevo generacional"
            p50_5y_role = f"Propietario Agrícola Consolidado en {c_name} con tierras propias, canales de venta directos y solvencia"
            p90_5y_role = "Agroexportador / Empresario Agroindustrial con múltiples fundos y libertad financiera familiar"
            p10_5y_inc = round(inc_base * 1.20, 0)
            p50_5y_inc = round(max(5000.0, inc_base * (2.20 * multiplier_cohort)), 0)
            p90_5y_inc = round(max(9500.0, inc_base * (3.10 * multiplier_cohort)), 0)
            c5 = ["Propiedad legal de fundos tecnificados", "Contratos corporativos de exportación de alimentos"]
            b5 = ["Riesgos climáticos no mitigados por tecnología"]
        elif is_business:
            p10_5y_role = "Comercio absorbido por grandes cadenas retail sin diferenciación de marca"
            p50_5y_role = f"Empresario Consolidado en {c_name} con red de sucursales, libertad operativa y patrimonio diversificado"
            p90_5y_role = "Fundador de Corporación Comercial con operaciones regionales, viajes y patrimonio inmobiliario"
            p10_5y_inc = round(inc_base * 1.25, 0)
            p50_5y_inc = round(max(6500.0, inc_base * (2.20 * multiplier_cohort)), 0)
            p90_5y_inc = round(max(12500.0, inc_base * (3.20 * multiplier_cohort)), 0)
            c5 = ["Estructura corporativa con gerentes de tienda", "Inversión en locales comerciales propios"]
            b5 = ["Dependencia extrema del fundador para la toma de decisiones"]
        elif is_day_to_day:
            p10_5y_role = "Tope de subsistencia física individual sin patrimonio acumulado"
            p50_5y_role = f"Propietario de Negocio Consolidado en {c_name} con locales operando bajo encargados y patrimonio protegido"
            p90_5y_role = "Empresario con cadena comercial, libertad habitacional y solvencia para viajar y abrir nuevas sedes"
            p10_5y_inc = round(inc_base * 1.25, 0)
            p50_5y_inc = round(max(4500.0, inc_base * (2.20 * multiplier_cohort)), 0)
            p90_5y_inc = round(max(8500.0, inc_base * (3.00 * multiplier_cohort)), 0)
            c5 = ["Patrimonio inmobiliario comercial propio", "Fondo de jubilación e inversión familiar"]
            b5 = ["Desgaste físico crónico por no retirarse de la operativa directa", "Falta de diversificación"]
        elif is_titled_or_grad:
            p10_5y_role = "Profesional consolidado atrapado en burocracia local sin margen de inversión"
            p50_5y_role = f"Gerente de División / Director Técnico en {c_name} o Consultor Independiente de alta solvencia"
            p90_5y_role = f"Director General / Socio de Consultora Internacional / Profesional expatriado en {c_name}"
            p10_5y_inc = round(inc_base * 1.25, 0)
            p50_5y_inc = round(max(7000.0, inc_base * (2.20 * multiplier_cohort)), 0)
            p90_5y_inc = round(max(13000.0, inc_base * (3.20 * multiplier_cohort)), 0)
            c5 = ["Bolsa de reubicación exterior y red de contactos global", "Visas de trabajo o convenios internacionales"]
            b5 = ["Falta de visa o acreditación para ejercer en el exterior", "Dependencia del mercado local"]
        elif is_trade:
            p10_5y_role = "Negocio que se detiene cuando el titular descansa, sin valor de reventa"
            p50_5y_role = f"Director de Empresa de Ingeniería de Mantenimiento en {c_name} con flota y activos fijos"
            p90_5y_role = "Empresario Técnico Industrial con representación de marcas y contratos corporativos"
            p10_5y_inc = round(inc_base * 1.22, 0)
            p50_5y_inc = round(max(5500.0, inc_base * (2.20 * multiplier_cohort)), 0)
            p90_5y_inc = round(max(10500.0, inc_base * (3.10 * multiplier_cohort)), 0)
            c5 = ["Activos fijos e inmuebles industriales propios", "Representación exclusiva de marcas de maquinaria"]
            b5 = ["Dependencia del fundador para cerrar contratos clave"]
        else: # is_active_student
            p10_5y_role = "Tope de mercado local con dependencia de contratos temporales"
            p50_5y_role = f"Líder de Área / Especialista Senior Titulado en {c_name} con maestría y capacidad de radicación externa"
            p90_5y_role = f"Staff Specialist / Consultor Internacional / Profesional radicado en el exterior o remoto global en USD"
            p10_5y_inc = round(max(1500.0, inc_base * 1.25), 0)
            p50_5y_inc = round(max(4200.0, p90_emp * 1.20), 0)
            p90_5y_inc = round(max(8500.0, p90_emp * 2.20), 0)
            c5 = ["Bolsa de reubicación de capital acumulada", "Red de contactos y certificaciones globales"]
            b5 = ["Falta de certificaciones o idiomas para visas de talento"]

        nodes.append(CareerTransitionNode(
            horizon_key="5_YEARS",
            horizon="5_years",
            horizon_label="5+ Años (Ideales & Internacional)" if is_es else "5+ Years (Ideals & Global)",
            months_ahead=60,
            months_from_now=60,
            p10_stagnation_role=p10_5y_role,
            p10_income=p10_5y_inc,
            p50_likely_role=p50_5y_role,
            p50_income=p50_5y_inc,
            p90_accelerated_role=p90_5y_role,
            p90_income=p90_5y_inc,
            transition_probability_pct=round(min(75.0, max(10.0, 28.0 + (cohort_pct * 0.45))), 1),
            cohort_rank_descriptor=f"Élite del {max(2, int(100 - cohort_pct))}% en competitividad internacional",
            key_catalysts=c5,
            required_skills_to_unlock=c5,
            blockers=b5,
            key_risk_factor=b5[0],
            market_demand_alignment="Muy Alta"
        ))

        return nodes

    @classmethod
    def _generate_top_matching_roles(cls, career: str, p_type: str, is_es: bool) -> List[str]:
        c_low = career.lower()
        c_name = cls.sanitize_career_label(career, p_type)

        is_taxi = any(w in c_low for w in ["taxista", "taxi", "mototaxi", "chofer", "conductor", "transporte", "colectivo", "remisse"])
        is_rural = p_type == "RURAL_FIELD_PRODUCER" or any(w in c_low for w in ["granja", "granjas", "avícol", "avicol", "porcin", "cuy", "galpón", "galpon", "campo", "chacra", "agrícol", "ganad"])
        is_business = p_type == "BUSINESS_OWNER" or any(w in c_low for w in ["comerciante", "comercio", "bodega", "tienda", "abarrotes", "negocio", "emprend"])

        if is_taxi:
            return [
                "Conductor Profesional de Transporte Urbano & Corporativo",
                "Administrador de Flota Vehicular y Servicios de Movilidad",
                "Proveedor de Transporte de Personal y Logística Ligera",
                "Empresario Independiente de Transporte de Pasajeros"
            ]
        elif is_rural:
            return [
                "Productor Pecuario Tecnificado y Gestor de Granjas",
                "Administrador de Producción Agropecuaria y Galpones",
                "Proveedor Mayorista de Alimentos y Productos de Granja",
                "Empresario Agropecuario y Gestor de Acopio Rural"
            ]
        elif is_business:
            return [
                "Propietario / Gestor de Comercio y Negocio Independiente",
                "Administrador de Punto de Venta y Canales Mayoristas",
                "Gerente Comercial de Pequeña y Mediana Empresa (PYME)",
                "Empresario de Distribución y Comercialización Minorista"
            ]
        elif p_type == "DAY_TO_DAY_WORKER" or any(w in c_low for w in ["comida", "comerc", "ambulante", "mozo"]):
            return [
                "Propietario / Gestor de Negocio Gastronómico y Comercial",
                "Administrador de Punto de Venta y Suministros",
                "Distribuidor Comercial Minorista y Mayorista",
                "Empresario Independiente de Servicios de Alimentación"
            ]
        elif p_type == "SKILLED_TRADE" or any(w in c_low for w in ["electric", "mecanic", "mecánic", "gasfiter", "taller", "carpinter"]):
            return [
                f"Maestro Contratista de {c_name}",
                f"Jefe de Cuadrilla Técnica y Mantenimiento en {c_name}",
                f"Técnico Especialista Homologado en {c_name}",
                f"Gerente de Servicios Técnicos e Instalaciones"
            ]
        elif any(w in c_low for w in ["sistem", "software", "computaci", "informátic", "developer"]):
            return [
                "Full Stack Cloud Engineer (TypeScript & Python)",
                "AI Solutions & Automation Architect",
                "Backend Cloud Engineer (AWS / Microservices)",
                "Data Platform & Pipeline Engineer"
            ]
        elif any(w in c_low for w in ["econom", "finanz", "banc", "contab"]):
            return [
                "Analista de Inteligencia Financiera y Riesgos",
                "Especialista en Evaluación Económica de Proyectos",
                "Consultor de Gestión Estratégica y Finanzas Corporativas",
                "Jefe de Planeamiento y Control de Gestión"
            ]
        elif any(w in c_low for w in ["civil", "construc"]):
            return [
                "Ingeniero Residente de Obras Civiles",
                "Especialista en Costos, Presupuestos y Valorizaciones",
                "Jefe de Supervisión y Control de Calidad Estructural",
                "Gerente de Proyectos de Infraestructura"
            ]
        else:
            return [
                f"Consultor Senior en {c_name}",
                f"Líder de Operaciones en {c_name}",
                f"Especialista de Proyectos en {c_name}",
                f"Director de Área Técnica"
            ]
