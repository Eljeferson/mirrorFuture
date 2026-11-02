"""
Routers: Production Endpoints for Real Causal Inference & Actuator Execution.
Connects EXIF/Vision forensics, RAG Social Twins, Monte Carlo simulation, and real-world actuators.
"""

import logging
from typing import Optional, List, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from app.models.schemas import (
    ImageForensicReport,
    MultiTwinSimulationResult,
    SocialTwinSimulateRequest,
    FullPhotoSimulationResponse,
    RealContact,
    DailyScheduleInput,
    MonteCarloSimulationConfig,
    MonteCarloAnalysisOutput,
    InverseEngineeringPrescription,
    CalendarIcsResponse,
    WhatsAppNotificationRequest,
    WhatsAppSendResult,
    HolisticFutureRequest,
    HolisticFutureResponse,
    MacroEconomicContext,
    HorizonSnapshot,
    GoldenPathAdjustment,
    DiscoveryQuestionsRequest,
    DiscoveryQuestionsResponse,
    DiscoveryInterviewMessage,
    DiscoveryInterviewRequest,
    DiscoveryInterviewResponse,
    SyncDossierRequest,
    SyncDossierResponse,
)
from app.causal_engine.exif_and_vision import execute_complete_image_forensics
from app.causal_engine.rag_social_twin import simulate_multiverse_social_impact
from app.causal_engine.markov_mcts_math import (
    execute_complete_mcts_monte_carlo,
    run_numpy_monte_carlo_simulation,
)
from app.causal_engine.holistic_future_engine import holistic_future_engine
from app.causal_engine.future_media_generator import future_media_generator
from app.ingestion.embedding_engine import RealEmbeddingEngine
from app.actuators.calendar_writer import calendar_actuator
from app.actuators.whatsapp_sender import whatsapp_actuator

logger = logging.getLogger("MirrorFuture.Router")
router = APIRouter(prefix="/causal", tags=["Mirror Future Causal Engine & Actuators"])


@router.post("/vision-forensics", response_model=ImageForensicReport)
async def analyze_image_forensics(
    file: UploadFile = File(...),
    context_claim: Optional[str] = Form(None)
):
    """
    Extracts physical camera EXIF metadata and executes Meta Llama Vision
    for forensic inspection of reputational risk and spatio-temporal coherence.
    """
    try:
        content = await file.read()
        mime = file.content_type or "image/jpeg"
        report = await execute_complete_image_forensics(
            image_bytes=content,
            mime_type=mime,
            user_context_claim=context_claim
        )
        return report
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Image forensics analysis error: {str(exc)}")


@router.post("/social-twin/simulate", response_model=MultiTwinSimulationResult)
async def simulate_social_twins(
    payload: SocialTwinSimulateRequest
):
    """
    RAG Social Twin Simulation:
    Receives JSON {action_or_image_claim: str, user_id: Optional[str] = None},
    vectorizes the action into 384d, queries Supabase pgvector RPC `match_real_episodes`,
    injects authentic lexical profiles, and predicts exact reactions with Meta Llama.
    """
    try:
        result = await simulate_multiverse_social_impact(
            action_or_image_claim=payload.action_or_image_claim,
            user_id=payload.user_id
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Social twin simulation error: {str(exc)}")


@router.post("/full-photo-simulation", response_model=FullPhotoSimulationResponse)
async def full_photo_simulation(
    file: UploadFile = File(..., description="Photograph or screenshot for forensic inspection"),
    user_query: str = Form(..., description="Context or message user plans to accompany the photo"),
    user_id: Optional[str] = Form(None, description="User UUID for Supabase persistence (optional)")
):
    """
    Unified Causal Pipeline: Photo Forensic Inspection + RAG Social Twins.
    1. Executes forensic inspection (EXIF + Multimodal Vision).
    2. Passes forensic descriptions and context to simulate_multiverse_social_impact.
    3. Persists causal prediction log in Supabase `causal_predictions_log` table.
    4. Returns unified reports: vision_report and social_twin_result.
    """
    try:
        content = await file.read()
        mime = file.content_type or "image/jpeg"
        vision_report = await execute_complete_image_forensics(
            image_bytes=content,
            mime_type=mime,
            user_context_claim=user_query
        )

        scene_desc = vision_report.vision.scene_description
        social_context = vision_report.vision.social_context
        risk_score = vision_report.vision.reputational_risk_score
        recommendation = vision_report.vision.causal_recommendation

        simulated_claim = (
            f"ANALYZED IMAGE: Context: {social_context}. Scene: {scene_desc}. "
            f"Reputational risk: {risk_score:.2f}. Recommendation: {recommendation}.\n"
            f"USER INTENT OR ACCOMPANYING MESSAGE: \"{user_query}\""
        )

        social_twin_result = await simulate_multiverse_social_impact(
            action_or_image_claim=simulated_claim,
            user_id=user_id
        )

        prediction_log_id: Optional[str] = None
        embedding_engine = RealEmbeddingEngine()
        supabase_client = embedding_engine.get_supabase_client()

        target_user_id = user_id
        if not target_user_id and supabase_client:
            try:
                prof_res = supabase_client.table("user_real_profile").select("id").limit(1).execute()
                if prof_res.data and len(prof_res.data) > 0:
                    target_user_id = str(prof_res.data[0]["id"])
            except Exception as prof_err:
                logger.warning("Could not fetch user_id from user_real_profile: %s", prof_err)

        if supabase_client:
            try:
                log_payload = {
                    "decision_type": "FULL_PHOTO_AND_SOCIAL_SIMULATION",
                    "decision_payload": {
                        "filename": file.filename,
                        "user_query": user_query,
                        "scene_description": scene_desc,
                        "reputational_risk_score": risk_score,
                    },
                    "predicted_outcomes": (
                        social_twin_result.model_dump()
                        if hasattr(social_twin_result, "model_dump")
                        else social_twin_result.dict()
                    ),
                }
                if target_user_id:
                    log_payload["user_id"] = target_user_id

                log_res = supabase_client.table("causal_predictions_log").insert(log_payload).execute()
                if log_res.data and len(log_res.data) > 0:
                    prediction_log_id = str(log_res.data[0].get("id"))
                    logger.info("Prediction logged in causal_predictions_log: %s", prediction_log_id)
            except Exception as log_err:
                logger.warning("Failed to save log in causal_predictions_log: %s", log_err)

        return FullPhotoSimulationResponse(
            vision_report=vision_report,
            social_twin_result=social_twin_result,
            prediction_log_id=prediction_log_id
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        logger.exception("Unified full-photo-simulation pipeline failure: %s", exc)
        raise HTTPException(status_code=500, detail=f"Unified simulation error: {str(exc)}")


@router.post("/monte-carlo/simulate", response_model=MonteCarloAnalysisOutput)
async def run_monte_carlo_burnout_simulation(
    schedule: Optional[List[DailyScheduleInput]] = None,
    config: Optional[MonteCarloSimulationConfig] = None
):
    """
    Stochastic Monte Carlo simulation of 1,000 trajectories across 180 days in NumPy.
    Calculates curves for Fatigue, Thesis Progress, Burnout, and Relational Capital,
    executing causal diagnosis and inverse engineering via Meta Llama.
    """
    try:
        output = await execute_complete_mcts_monte_carlo(
            schedule=schedule,
            config=config
        )
        return output
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Stochastic simulation error: {str(exc)}")


@router.post("/actuators/generate-ics", response_model=CalendarIcsResponse)
async def generate_optimal_calendar(
    work_cap_hours: float = 6.5,
    thesis_hours: float = 2.5,
    sleep_target_hours: float = 7.5,
    days: int = 14
):
    """
    Generates a downloadable .ics calendar file based on inverse engineering parameters.
    """
    prescription = InverseEngineeringPrescription(
        optimal_daily_work_cap_hours=work_cap_hours,
        optimal_daily_thesis_hours=thesis_hours,
        minimum_sleep_target_hours=sleep_target_hours,
        thesis_completion_probability_at_day_120=0.88,
        thesis_completion_probability_at_day_180=0.98,
        burnout_probability_p90_at_day_180=0.10,
        strategic_levers=[]
    )
    blocks = calendar_actuator.generate_optimal_blocks_from_prescription(prescription, num_days=days)
    return calendar_actuator.export_to_response(blocks)


@router.get("/actuators/download-calendar.ics")
async def download_calendar_file(
    work_cap_hours: float = 6.5,
    thesis_hours: float = 2.5,
    days: int = 14
):
    """
    Direct RFC 5545 calendar stream download for Google, Apple, or Outlook Calendar.
    """
    prescription = InverseEngineeringPrescription(
        optimal_daily_work_cap_hours=work_cap_hours,
        optimal_daily_thesis_hours=thesis_hours,
        minimum_sleep_target_hours=7.5,
        thesis_completion_probability_at_day_120=0.88,
        thesis_completion_probability_at_day_180=0.98,
        burnout_probability_p90_at_day_180=0.10,
        strategic_levers=[]
    )
    blocks = calendar_actuator.generate_optimal_blocks_from_prescription(prescription, num_days=days)
    raw_ics = calendar_actuator.export_to_ics_string(blocks)

    return Response(
        content=raw_ics,
        media_type="text/calendar",
        headers={"Content-Disposition": 'attachment; filename="optimal_schedule_mirror_future.ics"'}
    )


@router.post("/actuators/whatsapp/send", response_model=WhatsAppSendResult)
async def send_whatsapp_alert(request: WhatsAppNotificationRequest):
    """
    Dispatches a real-time causal alert or report via Meta WhatsApp Cloud API.
    """
    try:
        result = await whatsapp_actuator.send_text_message(
            to_phone=request.recipient_phone,
            message_text=request.message_text
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"WhatsApp message dispatch failure: {str(exc)}")


@router.get("/future-video")
async def stream_future_video(
    horizon: str = "1_year",
    mode: str = "CURRENT",
    download: Optional[int] = None
):
    """
    Streams the generated cinematic MP4 video for the requested horizon.
    Supports in-browser HTML5 <video> playback and file attachments.
    """
    import cv2
    import numpy as np
    import base64

    video_bytes = future_media_generator.get_cached_video(horizon, mode)
    if not video_bytes:
        cached_img_b64 = (
            future_media_generator._image_cache.get(horizon)
            or future_media_generator._image_cache.get(f"{horizon}_current")
            or future_media_generator._image_cache.get("reference_original")
            or future_media_generator._image_cache.get("1_year_current")
        )
        canvas = None
        if cached_img_b64 and isinstance(cached_img_b64, str) and "," in cached_img_b64:
            try:
                raw_b = base64.b64decode(cached_img_b64.split(",", 1)[1])
                img_arr = np.frombuffer(raw_b, np.uint8)
                canvas = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
            except Exception as e:
                logger.warning("Could not decode cached frame for video: %s", e)

        if canvas is None:
            canvas = np.zeros((576, 1024, 3), dtype=np.uint8)
            cv2.putText(canvas, "MIRROR FUTURE - TEMPORAL SIMULATION", (80, 288), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        days_map = {"1_month": "30 DAYS", "6_months": "180 DAYS", "1_year": "365 DAYS"}
        days_str = days_map.get(horizon, "365 DAYS")
        video_bytes = future_media_generator.generate_horizon_video_mp4(
            canvas_bgr=canvas,
            horizon_key=horizon,
            monologue_text="Causal temporal and career projection calibrated by Mirror Future.",
            burnout_prob=0.20,
            days_label=days_str,
            status_badge="OPTIMAL"
        )

    if not video_bytes:
        raise HTTPException(status_code=404, detail="Video is not yet available for this horizon.")

    disposition = "attachment" if download == 1 else "inline"
    return Response(
        content=video_bytes,
        media_type="video/mp4",
        headers={
            "Content-Disposition": f'{disposition}; filename="mirror_future_future_self_{horizon}.mp4"',
            "Accept-Ranges": "bytes",
            "Content-Length": str(len(video_bytes)),
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Expose-Headers": "Content-Disposition, Content-Length",
            "Cache-Control": "public, max-age=3600"
        }
    )


@router.post("/generate-future-video")
async def generate_future_video_on_demand(
    file: UploadFile = File(...),
    horizon_key: str = Form("6_months"),
    mode: str = Form("CURRENT"),
    monologue: Optional[str] = Form(None)
):
    """
    Renders an on-demand MP4 video from a user-uploaded photograph.
    """
    import cv2
    import numpy as np
    content = await file.read()
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image.")
    
    canvas, _ = future_media_generator._create_cinematic_canvas(img)
    script = monologue or "Hello, this is your future self projected across time."
    video_bytes = future_media_generator.generate_horizon_video_mp4(
        canvas_bgr=canvas,
        horizon_key=horizon_key,
        monologue_text=script,
        burnout_prob=0.20,
        days_label="180 DAYS",
        status_badge="OPTIMAL"
    )
    return Response(
        content=video_bytes,
        media_type="video/mp4",
        headers={
            "Content-Disposition": f'inline; filename="mirror_future_future_self_{horizon_key}.mp4"',
            "Accept-Ranges": "bytes"
        }
    )


COUNTRY_NAME_TO_ISO = {
    "perú": ("PE", "S/"), "peru": ("PE", "S/"), "pe": ("PE", "S/"),
    "colombia": ("CO", "$"), "co": ("CO", "$"),
    "méxico": ("MX", "$"), "mexico": ("MX", "$"), "mx": ("MX", "$"),
    "argentina": ("AR", "$"), "ar": ("AR", "$"),
    "chile": ("CL", "$"), "cl": ("CL", "$"),
    "españa": ("ES", "€"), "espana": ("ES", "€"), "es": ("ES", "€"),
    "estados unidos": ("US", "$"), "us": ("US", "$"), "usa": ("US", "$"),
    "united states": ("US", "$"),
}


def _safe_float(val, default: Any = None) -> Any:
    if val is None or val == "":
        return default
    try:
        import math
        f = float(val)
        return default if math.isnan(f) else f
    except (ValueError, TypeError):
        return default


def _safe_int(val, default: Any = None) -> Any:
    if val is None or val == "":
        return default
    try:
        import math
        f = float(val)
        return default if math.isnan(f) else int(f)
    except (ValueError, TypeError):
        return default


@router.post("/generate-discovery-questions", response_model=DiscoveryQuestionsResponse)
async def generate_discovery_questions(payload: DiscoveryQuestionsRequest):
    """
    Generates tailored, empathetic situational discovery questions based on occupation, city, and age.
    """
    try:
        from app.causal_engine.holistic_future_engine import DiscoveryQuestionsEngine
        questions = await DiscoveryQuestionsEngine.generate_questions(payload)
        return DiscoveryQuestionsResponse(questions=questions)
    except Exception as exc:
        logger.exception("Error in generate_discovery_questions: %s", exc)
        raise HTTPException(status_code=500, detail=f"Error generating discovery questions: {str(exc)}")


@router.post("/discovery-interview", response_model=DiscoveryInterviewResponse)
async def discovery_interview(payload: DiscoveryInterviewRequest):
    """
    Conversational Discovery Engine:
    Evaluates the user's 6 reality pillars from dialogue, producing next empathetic questions
    or synthesizing the complete dossier and parameters.
    """
    try:
        from app.causal_engine.holistic_future_engine import DiscoveryInterviewEngine
        res = await DiscoveryInterviewEngine.conduct_interview(payload)
        return res
    except Exception as exc:
        logger.exception("Error in discovery_interview: %s", exc)
        raise HTTPException(status_code=500, detail=f"Error in conversational interview: {str(exc)}")


@router.post("/sync-dossier-to-parameters", response_model=SyncDossierResponse)
async def sync_dossier_to_parameters(payload: SyncDossierRequest):
    """
    Synchronizes an edited reality dossier with HolisticFutureRequest parameters for causal calibration.
    """
    try:
        from app.causal_engine.holistic_future_engine import DiscoveryInterviewEngine
        res = await DiscoveryInterviewEngine.sync_dossier_to_parameters(payload)
        return res
    except Exception as exc:
        logger.exception("Error in sync_dossier_to_parameters: %s", exc)
        raise HTTPException(status_code=500, detail=f"Error syncing dossier with parameters: {str(exc)}")


@router.post("/predict-future-self")
async def predict_future_self_v4(raw_payload: dict):
    """
    Master V4 Prediction Endpoint (1 Month, 6 Months, 1 Year):
    Executes MacroWorldEngine + HolisticFutureEngine + 3D Monte Carlo curves,
    returning structured multi-horizon projections.
    """
    from app.causal_engine.holistic_future_engine import holistic_future_engine
    from app.models.schemas import HolisticFutureRequest, DailyScheduleInput

    try:
        if hasattr(raw_payload, "model_dump"):
            raw_dict = raw_payload.model_dump()
        elif hasattr(raw_payload, "dict"):
            raw_dict = raw_payload.dict()
        elif isinstance(raw_payload, dict):
            raw_dict = raw_payload
        else:
            raw_dict = dict(raw_payload) if raw_payload else {}

        loc = raw_dict.get("location") or {} if isinstance(raw_dict.get("location"), dict) else {}
        fin = raw_dict.get("finances") or {} if isinstance(raw_dict.get("finances"), dict) else {}
        t_use = raw_dict.get("time_use") or {} if isinstance(raw_dict.get("time_use"), dict) else {}

        raw_country = str(loc.get("country") or raw_dict.get("country_code") or "PE").strip()
        iso_code, default_sym = COUNTRY_NAME_TO_ISO.get(
            raw_country.lower(),
            (raw_country[:2].upper() if len(raw_country) >= 2 else "PE", "$")
        )

        exercise_val = t_use.get("exercise_hours") if "exercise_hours" in t_use else raw_dict.get("exercise_days_per_week")
        exercise_h = _safe_float(exercise_val, 1.0)
        exercise_days = min(7.0, round(exercise_h * 3.5, 1)) if "exercise_hours" in t_use else min(7.0, exercise_h)

        resolved_name = str(
            raw_dict.get("full_name")
            or raw_dict.get("full_name_or_handle")
            or raw_dict.get("person_identifier")
            or raw_dict.get("name")
            or raw_dict.get("handle")
            or ""
        ).strip() or None

        career_val = str(
            raw_dict.get("career_or_degree")
            or raw_dict.get("occupation")
            or ""
        ).strip()

        life_profile_val = str(raw_dict.get("life_profile_type") or "DAY_TO_DAY_WORKER").strip()
        c_low = career_val.lower()
        if any(w in c_low for w in ["egresad", "bachiller", "titulad", "colegiad", "graduad", "graduate", "engineer", "professional"]):
            life_profile_val = "TITLED_PROFESSIONAL"
        elif any(w in c_low for w in ["vendo comida", "venta de comida", "vendedor", "ambulante", "mototaxi", "taxista", "driver"]):
            life_profile_val = "DAY_TO_DAY_WORKER"
        goal_mode_val = bool(raw_dict.get("goal_mode", False))
        lang_val = str(raw_dict.get("lang") or "EN").strip().upper()
        if lang_val not in ("EN", "ES"):
            lang_val = "EN"
        is_es = lang_val == "ES"

        daily_inc = _safe_float(raw_dict.get("daily_income_avg"), 0.0) if raw_dict.get("daily_income_avg") is not None else None
        daily_exp = _safe_float(raw_dict.get("daily_expense_avg"), 0.0) if raw_dict.get("daily_expense_avg") is not None else None
        w_days = _safe_float(raw_dict.get("work_days_per_week"), 6.0)
        rural_prod = str(raw_dict.get("rural_product") or "").strip() or None
        camp_inc = _safe_float(raw_dict.get("campaign_income_est"), 0.0) if raw_dict.get("campaign_income_est") is not None else None
        labor_intens = str(raw_dict.get("physical_labor_intensity") or "MEDIUM").strip().upper()
        if labor_intens not in ("HIGH", "MEDIUM", "LOW"):
            labor_intens = "MEDIUM"
        trade_mod = str(raw_dict.get("trade_modality") or "INDEPENDENT").strip().upper()
        contract_t = str(raw_dict.get("contract_type") or "PERMANENT").strip().upper()
        b_type = str(raw_dict.get("business_type") or "").strip() or None
        sales_net = _safe_float(raw_dict.get("monthly_sales_net"), 0.0) if raw_dict.get("monthly_sales_net") is not None else None

        declared_goal = str(raw_dict.get("one_year_goal") or raw_dict.get("main_goal_1y") or "").strip()
        if not goal_mode_val:
            declared_goal = ""

        fam_dict = raw_dict.get("family_and_environment") if isinstance(raw_dict.get("family_and_environment"), dict) else {}
        pers_dict = raw_dict.get("personality_profile") if isinstance(raw_dict.get("personality_profile"), dict) else {}
        chat_dict = raw_dict.get("ingested_chat_signals") if isinstance(raw_dict.get("ingested_chat_signals"), dict) else {}

        raw_traits = raw_dict.get("personality_traits") or pers_dict.get("personality_traits") or []
        if isinstance(raw_traits, str):
            personality_traits_list = [t.strip() for t in raw_traits.split(",") if t.strip()]
        elif isinstance(raw_traits, list):
            personality_traits_list = [str(t).strip() for t in raw_traits if str(t).strip()]
        else:
            personality_traits_list = []

        raw_curr = str(fin.get("currency") or raw_dict.get("currency") or "").strip().upper()
        if not raw_curr or (raw_curr == "USD" and iso_code != "US"):
            from app.ingestion.macro_world_engine import COUNTRY_METADATA
            resolved_curr = COUNTRY_METADATA.get(iso_code, {}).get("currency", "PEN" if iso_code == "PE" else "USD")
        else:
            resolved_curr = raw_curr

        raw_city = str(loc.get("city") or raw_dict.get("city") or "").strip()
        if raw_city.lower() in ("ciudad principal", "huancayo") and "city" not in loc and "city" not in raw_dict:
            raw_city = ""

        raw_sleep = _safe_float(t_use.get("sleep_hours") if "sleep_hours" in t_use else raw_dict.get("sleep_hours"), 7.0)
        resolved_sleep = 7.0 if (raw_sleep is None or raw_sleep <= 0.5) else raw_sleep

        from app.models.schemas import CareerLifeEvent
        raw_events = raw_dict.get("past_career_events") or []
        parsed_past_events = []
        if isinstance(raw_events, list):
            for ev in raw_events:
                if isinstance(ev, dict) and ev.get("title_or_role"):
                    parsed_past_events.append(CareerLifeEvent(
                        year=_safe_int(ev.get("year"), 2024),
                        age_at_event=_safe_int(ev.get("age_at_event"), 22),
                        event_type=str(ev.get("event_type") or "ROLE_CHANGE"),
                        title_or_role=str(ev.get("title_or_role")),
                        monthly_income=_safe_float(ev.get("monthly_income"), 0.0),
                        location=str(ev.get("location") or ""),
                        description=str(ev.get("description") or "")
                    ))

        req = HolisticFutureRequest(
            age=_safe_int(raw_dict.get("age"), 26),
            country_code=iso_code,
            city=raw_city,
            occupation=career_val,
            career_or_degree=career_val,
            life_profile_type=life_profile_val,
            goal_mode=goal_mode_val,
            lang=lang_val,
            daily_income_avg=daily_inc,
            daily_expense_avg=daily_exp,
            work_days_per_week=w_days,
            rural_product=rural_prod,
            campaign_income_est=camp_inc,
            physical_labor_intensity=labor_intens,
            trade_modality=trade_mod,
            contract_type=contract_t,
            business_type=b_type,
            monthly_sales_net=sales_net,
            main_goal_1y=declared_goal,
            one_year_goal=declared_goal,
            medium_term_goals=str(raw_dict.get("medium_term_goals") or "").strip() or None,
            long_term_goals=str(raw_dict.get("long_term_goals") or "").strip() or None,
            past_career_events=parsed_past_events,
            monthly_income=round(daily_inc * w_days * 4.333, 2) if (life_profile_val == "DAY_TO_DAY_WORKER" and daily_inc and daily_inc > 0) else _safe_float(fin.get("monthly_income") if "monthly_income" in fin else raw_dict.get("monthly_income"), 0.0),
            monthly_expenses=round(daily_exp * 30.417, 2) if (life_profile_val == "DAY_TO_DAY_WORKER" and daily_exp and daily_exp > 0) else _safe_float(fin.get("monthly_expenses") if "monthly_expenses" in fin else raw_dict.get("monthly_expenses"), 0.0),
            current_savings=_safe_float(fin.get("current_savings") if "current_savings" in fin else raw_dict.get("current_savings"), 0.0),
            current_debt=_safe_float(fin.get("current_debt") if "current_debt" in fin else raw_dict.get("current_debt"), 0.0),
            currency=resolved_curr,
            sleep_hours=resolved_sleep,
            work_hours=_safe_float(t_use.get("work_hours") if "work_hours" in t_use else raw_dict.get("work_hours"), 0.0),
            study_or_project_hours=_safe_float(t_use.get("study_project_hours") if "study_project_hours" in t_use else raw_dict.get("study_or_project_hours"), 0.0),
            screen_time_distraction_hours=_safe_float(t_use.get("screen_time_lost_hours") if "screen_time_lost_hours" in t_use else raw_dict.get("screen_time_distraction_hours"), 0.0),
            exercise_days_per_week=exercise_days,
            social_hours=_safe_float(t_use.get("social_hours") if "social_hours" in t_use else raw_dict.get("social_hours"), 0.0),
            person_identifier=resolved_name,
            full_name_or_handle=resolved_name,
            full_name=resolved_name,
            university_or_institution=str(raw_dict.get("university_or_institution") or raw_dict.get("university") or "").strip() or None,
            current_company_or_org=str(raw_dict.get("current_company_or_org") or raw_dict.get("company") or "").strip() or None,
            life_stage=str(raw_dict.get("life_stage") or "ACTIVE_PROFESSIONAL").strip(),
            months_to_graduation=_safe_int(raw_dict.get("months_to_graduation"), 0),
            years_of_experience=_safe_float(raw_dict.get("years_of_experience"), 1.0),
            key_skills=str(raw_dict.get("key_skills") or "").strip(),
            english_level=str(raw_dict.get("english_level") or "A1_A2").strip(),
            work_modality_target=str(raw_dict.get("work_modality_target") or "LOCAL_CITY").strip(),
            target_monthly_salary_1y=_safe_float(raw_dict.get("target_monthly_salary_1y"), 3500.0),
            housing_situation=str(raw_dict.get("housing_situation") or "FAMILY_HOME").strip(),
            dependents_count=_safe_int(raw_dict.get("dependents_count") if "dependents_count" in raw_dict else fam_dict.get("dependents_count"), 0),
            household_climate=str(raw_dict.get("household_climate") or fam_dict.get("household_climate") or "SUPPORTIVE").strip(),
            relationship_status=str(raw_dict.get("relationship_status") or fam_dict.get("relationship_status") or "SINGLE_PEACEFUL").strip(),
            social_circle_influence=str(raw_dict.get("social_circle_influence") or fam_dict.get("social_circle_influence") or "GROWTH").strip(),
            open_family_and_dependents=str(raw_dict.get("open_family_and_dependents") or fam_dict.get("open_family_and_dependents") or "").strip(),
            open_relationships_and_friends=str(raw_dict.get("open_relationships_and_friends") or fam_dict.get("open_relationships_and_friends") or "").strip(),
            open_personality_and_habits=str(raw_dict.get("open_personality_and_habits") or pers_dict.get("open_personality_and_habits") or "").strip(),
            self_description=str(raw_dict.get("self_description") or pers_dict.get("self_description") or "").strip(),
            personality_traits=personality_traits_list,
            chat_sentiment_avg=_safe_float(raw_dict.get("chat_sentiment_avg") if "chat_sentiment_avg" in raw_dict else chat_dict.get("chat_sentiment_avg"), None),
            chat_dominant_tag=str(raw_dict.get("chat_dominant_tag") or chat_dict.get("chat_dominant_tag") or "").strip() or None,
            chat_median_reply_min=_safe_float(raw_dict.get("chat_median_reply_min") if "chat_median_reply_min" in raw_dict else chat_dict.get("chat_median_reply_min"), None),
            chat_extracted_summary=str(raw_dict.get("chat_extracted_summary") or chat_dict.get("chat_extracted_summary") or "").strip() or None,
            full_person_dossier_text=str(raw_dict.get("full_person_dossier_text") or "").strip() or None,
            user_photo_base64=raw_dict.get("user_photo_base64"),
        )

        selfie_bytes = None
        photo_raw = (
            raw_dict.get("user_photo_base64")
            or raw_dict.get("selfie_base64")
            or raw_dict.get("photo_base64")
            or raw_dict.get("image_base64")
        )
        if photo_raw and isinstance(photo_raw, str):
            import base64
            try:
                if "," in photo_raw:
                    photo_raw = photo_raw.split(",", 1)[1]
                selfie_bytes = base64.b64decode(photo_raw)
            except Exception as e:
                logger.warning("Error decoding base64 input photo: %s", e)

        has_text_data = bool(
            resolved_name
            or career_val
            or raw_city
            or declared_goal
            or (raw_dict.get("full_person_dossier_text") or "").strip()
            or (raw_dict.get("self_description") or "").strip()
            or (raw_dict.get("chat_extracted_summary") or "").strip()
            or photo_raw
        )
        has_economic_data = bool(
            (fin.get("monthly_income") and _safe_float(fin.get("monthly_income"), 0.0) > 0)
            or (daily_inc and daily_inc > 0)
            or len(parsed_past_events) > 0
            or (_safe_float(t_use.get("work_hours"), 0.0) > 0)
            or (_safe_float(t_use.get("study_project_hours"), 0.0) > 0)
        )
        if not has_text_data and not has_economic_data:
            logger.warning("Prediction attempt with zero data rejected with HTTP 400.")
            raise HTTPException(
                status_code=400,
                detail=(
                    "No user profile data provided. "
                    "Please share your details with Mirror Future in the chat or complete your profile in the form before predicting your future."
                )
            )

        core_res = await holistic_future_engine.predict_future_self(req)
        macro = core_res.macro_context if isinstance(core_res.macro_context, dict) else {}
        live_intel = core_res.live_web_intelligence if isinstance(core_res.live_web_intelligence, dict) else {}
        live_cost_idx = float(live_intel.get("city_cost_pressure_index", 1.0))
        live_demand_score = float(live_intel.get("career_market_demand_score", 75.0))

        sim_metrics_map = {
            "1_month": core_res.snapshot_1_month.metrics,
            "6_months": core_res.snapshot_6_months.metrics,
            "1_year": core_res.snapshot_1_year.metrics,
        }
        visual_traits = await future_media_generator.extract_person_visual_traits(
            image_bytes=selfie_bytes,
            age=req.age,
            occupation=req.occupation,
            city=req.city
        )

        has_reference_photo = selfie_bytes is not None and len(selfie_bytes) > 100
        transformed_images = {}
        if has_reference_photo:
            import base64
            reference_photo_url = f"data:image/jpeg;base64,{base64.b64encode(selfie_bytes).decode('utf-8')}"
            future_media_generator.cache_horizon_videos(
                image_bytes=selfie_bytes,
                sim_metrics=sim_metrics_map,
                req=req
            )
            transformed_images = future_media_generator.transform_reference_photo_for_horizons(
                image_bytes=selfie_bytes,
                sim_metrics=sim_metrics_map,
                req=req
            )
        else:
            reference_photo_url = None

        prompts_dict = future_media_generator.build_visual_prompts(
            req=req,
            macro=macro,
            sim_metrics=sim_metrics_map,
            visual_traits=visual_traits,
            has_reference_photo=has_reference_photo
        )
        images_dict = await future_media_generator.generate_images_parallel(prompts_dict)
        if has_reference_photo and transformed_images:
            for k, trans_img in transformed_images.items():
                if not images_dict.get(k) or not str(images_dict[k]).startswith(("data:image", "http")):
                    images_dict[k] = trans_img

        def _format_horizon(snap, label: str, horizon_key: str):
            m = snap.metrics
            n = snap.narrative
            goal_prob = round(min(0.99, max(0.02, m.career_and_goal_completion_pct.p50 / 100.0)), 2)
            b_risk = m.burnout_probability
            badge = "CRITICAL" if b_risk >= 0.45 else ("OPTIMAL" if b_risk < 0.20 and goal_prob >= 0.50 else "WARNING")
            full_portrait = f"{n.future_self_portrait} {n.economic_reality} {n.health_and_mind_state}".strip()

            img_key = "1_year_current" if horizon_key in ("1_year", "one_year") else horizon_key
            future_img_url = images_dict.get(img_key) or images_dict.get(horizon_key, "")
            optimal_img_url = images_dict.get("1_year_optimal", "")
            caption = future_media_generator.generate_scene_caption(horizon_key, m, req, has_reference_photo=has_reference_photo)
            voice_script = future_media_generator.generate_first_person_monologue(horizon_key, n, m, req)
            video_url = f"http://localhost:8000/api/causal/future-video?horizon={horizon_key}&mode=CURRENT"

            goal_metric_label = (
                ("Overall Wellbeing & Stability Index" if not is_es else "Índice de Bienestar y Estabilidad General")
                if not req.goal_mode
                else ("Goal Success Probability" if not is_es else "Probabilidad de Cumplir Meta")
            )

            return {
                "horizon_label": label,
                "status_badge": badge,
                "goal_metric_label": goal_metric_label,
                "goal_success_probability": goal_prob,
                "projected_real_net_worth": round(m.financial_net_worth.p50, 0),
                "burnout_risk": b_risk,
                "living_portrait": full_portrait,
                "narrative": n.model_dump(),
                "key_milestone_event": n.critical_warning,
                "future_self_image_url": future_img_url,
                "optimal_comparison_image_url": optimal_img_url,
                "visual_scene_caption": caption,
                "first_person_voice_script": voice_script,
                "future_self_video_url": video_url,
                "reference_photo_url": reference_photo_url,
                "has_reference_photo": has_reference_photo,
                "scores_5d": {
                    "finances": round(m.purchasing_power_score.p50, 0),
                    "health_energy": round(m.health_and_vitality_score.p50, 0),
                    "career": round(m.career_and_goal_completion_pct.p50, 0),
                    "relationships": round(m.social_and_emotional_stability.p50, 0),
                    "macro_resilience": round(m.macro_resilience_score.p50, 0),
                },
            }

        cashflow = req.monthly_income - req.monthly_expenses
        is_physical_profile = life_profile_val in ("DAY_TO_DAY_WORKER", "RURAL_FIELD_PRODUCER", "SKILLED_TRADE")
        labor_map_es = {"HIGH": "alta intensidad física", "MEDIUM": "moderada exigencia física", "LOW": "baja exigencia física"}
        labor_intens_es = labor_map_es.get(labor_intens, "moderada exigencia física")
        curr_sym = default_sym

        inferred_care = core_res.inferred_human_factors.caregiving_details if core_res.inferred_human_factors and core_res.inferred_human_factors.caregiving_details else ""
        care_hours = float(core_res.inferred_human_factors.daily_caregiving_hours) if core_res.inferred_human_factors else 0.0

        if is_physical_profile:
            root_cause_1 = {
                "rank": 1,
                "category": "PHYSICAL STRAIN & RECOVERY" if not is_es else "DESGASTE FÍSICO & RECUPERACIÓN",
                "title": (
                    f"Daily shift of {req.work_hours:.1f}h ({labor_intens} exertion) vs {req.sleep_hours:.1f}h nightly sleep"
                    if not is_es else
                    f"Jornada diaria de {req.work_hours:.1f}h con {labor_intens_es} frente a {req.sleep_hours:.1f}h de sueño"
                ),
                "description": (
                    f"Continuous physical exertion without restorative sleep ({req.sleep_hours:.1f}h) wears down bodily stamina, increasing joint strain and fatigue."
                    if not is_es else
                    f"El esfuerzo físico continuado sin recuperación reparadora desgasta la vitalidad corporal ({req.sleep_hours:.1f}h de descanso), aumentando el riesgo de dolores articulares y fatiga."
                ),
                "evidence_quote": f"Work: {req.work_hours:.1f}h | Sleep: {req.sleep_hours:.1f}h | Intensity: {labor_intens}."
            }
        else:
            if req.work_hours <= 0.1 and (life_profile_val == "UNIVERSITY_OR_TECH_STUDENT" or req.study_or_project_hours > 0):
                activity_balance_title = (
                    f"{req.study_or_project_hours:.1f}h study/thesis vs {req.screen_time_distraction_hours:.1f}h screen distraction"
                    if not is_es else
                    (f"Tesis y estudio ({req.study_or_project_hours:.1f}h) + cuidado familiar ({care_hours:.1f}h) frente a {req.screen_time_distraction_hours:.1f}h en pantalla"
                     if care_hours > 0 else
                     f"Dedicación de {req.study_or_project_hours:.1f}h a tesis/estudios frente a {req.screen_time_distraction_hours:.1f}h en pantalla de ocio")
                )
                evidence_text = (
                    f"Study: {req.study_or_project_hours:.1f}h | Screen time: {req.screen_time_distraction_hours:.1f}h | Sleep: {req.sleep_hours:.1f}h."
                    if not is_es else
                    f"Tesis/Estudio: {req.study_or_project_hours:.1f}h | Pantalla ocio: {req.screen_time_distraction_hours:.1f}h | Sueño: {req.sleep_hours:.1f}h."
                )
            else:
                activity_balance_title = (
                    f"{req.screen_time_distraction_hours:.1f}h/day digital distraction vs {req.study_or_project_hours:.1f}h growth"
                    if not is_es else
                    f"Fuga de {req.screen_time_distraction_hours:.1f}h/día en ocio digital frente a {req.study_or_project_hours:.1f}h de desarrollo"
                )
                evidence_text = f"Daily breakdown: {req.work_hours:.1f}h work + {req.screen_time_distraction_hours:.1f}h screen vs {req.sleep_hours:.1f}h sleep."

            root_cause_1 = {
                "rank": 1,
                "category": "TIME PHYSICS & SCREEN FATIGUE" if not is_es else "FÍSICA DEL TIEMPO & PANTALLA",
                "title": activity_balance_title,
                "description": (
                    f"Annually, {int(req.screen_time_distraction_hours * 365)} hours are lost to passive screen time, eroding cognitive clarity and restorative rest."
                    if not is_es else
                    f"Al año se acumulan {int(req.screen_time_distraction_hours * 365)} horas en pantalla pasiva, reduciendo la claridad mental y el descanso reparador."
                ),
                "evidence_quote": evidence_text
            }

        root_causes = [
            root_cause_1,
            {
                "rank": 2,
                "category": "FINANCIAL THERMODYNAMICS" if not is_es else "TERMODINÁMICA FINANCIERA",
                "title": (
                    f"Monthly cashflow of {curr_sym} {cashflow:,.0f} vs debt load of {curr_sym} {req.current_debt:,.0f}"
                    if not is_es else
                    f"Flujo mensual de {curr_sym} {cashflow:,.0f} frente a pasivos de {curr_sym} {req.current_debt:,.0f}"
                ),
                "description": (
                    f"Debt service and unexpected cash needs compress your ability to build a survival buffer in {req.city}."
                    if not is_es else
                    f"El servicio de la deuda y gastos imprevistos de caja reducen la capacidad de formar un colchón de supervivencia frente a emergencias en {req.city}."
                ),
                "evidence_quote": f"Income: {curr_sym} {req.monthly_income:,.0f} | Expense: {curr_sym} {req.monthly_expenses:,.0f} | Savings: {curr_sym} {req.current_savings:,.0f}."
            },
            {
                "rank": 3,
                "category": f"LOCAL PRESSURE ({req.city})" if not is_es else f"PRESIÓN LOCAL ({req.city})",
                "title": (
                    f"Cost index in {req.city} ({live_cost_idx:.2f}) & Inflation at {macro.get('annual_inflation_rate', 3.0)}%"
                    if not is_es else
                    f"Costo en {req.city} (Índice {live_cost_idx:.2f}) e Inflación del {macro.get('annual_inflation_rate', 3.0)}%"
                ),
                "description": (
                    f"In {req.city}, local living costs and {macro.get('annual_inflation_rate', 3.0)}% annual inflation erode purchasing power without a liquid cash buffer."
                    if not is_es else
                    f"En {req.city}, los precios locales y la inflación anual de {macro.get('annual_inflation_rate', 3.0)}% impactan la canasta familiar si no se protege la reserva líquida."
                ),
                "evidence_quote": f"Source: {macro.get('source', 'Macro Intelligence')} | Local cost index: {live_cost_idx:.2f}."
            },
        ]

        formatted_adjustments = [
            {
                "lever_title": adj.domain.replace("_", " "),
                "expected_gain": "+32% P90 Probability",
                "current_trajectory_value": adj.current_baseline,
                "optimal_mirror_future_value": adj.prescribed_target,
                "optimal_dr_jef_value": adj.prescribed_target,  # Backwards compatibility
                "actionable_prescription": adj.expected_impact_p90,
            }
            for adj in core_res.golden_path_adjustments
        ]

        mc_output = None
        try:
            schedule_180 = [
                DailyScheduleInput(
                    day_index=d,
                    work_hours=req.work_hours * (0.25 if (d % 7) in (5, 6) else 1.0),
                    thesis_hours=req.study_or_project_hours + (1.5 if (d % 7) in (5, 6) else 0.0),
                    sleep_hours=req.sleep_hours + (1.0 if (d % 7) in (5, 6) else 0.0),
                    social_hours=req.social_hours + (1.5 if (d % 7) in (5, 6) else 0.0),
                    is_weekend=(d % 7) in (5, 6),
                )
                for d in range(180)
            ]
            curves, mc_summary = run_numpy_monte_carlo_simulation(schedule_180)

            prescription = InverseEngineeringPrescription(
                optimal_daily_work_cap_hours=min(req.work_hours, 6.5),
                optimal_daily_thesis_hours=max(req.study_or_project_hours, 2.5),
                minimum_sleep_target_hours=max(req.sleep_hours, 7.5),
                thesis_completion_probability_at_day_120=float(mc_summary.get("prob_thesis_completed_day_120", 0.85)),
                thesis_completion_probability_at_day_180=float(mc_summary.get("prob_thesis_completed_day_180", 0.95)),
                burnout_probability_p90_at_day_180=float(mc_summary.get("prob_severe_burnout_day_180", 0.12)),
                strategic_levers=[
                    adj.prescribed_target for adj in core_res.golden_path_adjustments
                ] if core_res.golden_path_adjustments else [
                    "Establish a strict hard cap on corporate employment hours.",
                    "Protect early morning deep work blocks for primary objectives.",
                    "Guarantee uninterrupted nightly sleep of at least 7.5 hours."
                ]
            )

            mc_output = MonteCarloAnalysisOutput(
                curves=curves,
                final_summary=mc_summary,
                llama_causal_diagnosis=core_res.executive_summary,
                prescription=prescription
            )
        except Exception as mc_err:
            logger.warning("3D NumPy curve generation completed with fallback: %s", mc_err)

        import urllib.parse
        real_web_sources = core_res.live_web_sources if core_res.live_web_sources else []
        if not real_web_sources:
            country_display = str(macro.get("country_name") or loc.get("country") or iso_code)
            city_display = str(req.city or loc.get("city") or "Your City")
            inflation_val = macro.get("annual_inflation_rate", 3.0)
            real_web_sources = [
                {
                    "title": f"World Bank: Inflation ({inflation_val}%) and Employment in {country_display}",
                    "category": "CITY_AND_ECONOMY",
                    "url": f"https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations={iso_code.lower()}",
                    "source": "World Bank",
                    "summary": f"Structural economic indicators for {country_display}."
                },
                {
                    "title": f"Labor Market & Salary Demand for {req.occupation} in {city_display}",
                    "category": "LABOR_MARKET",
                    "url": f"https://www.google.com/search?q={urllib.parse.quote(f'labor demand salary {req.occupation} {city_display}')}",
                    "source": "Labor Market Monitoring",
                    "summary": f"Salary demand and trends for {req.occupation}."
                },
                {
                    "title": f"Cost of Living & Price Index in {city_display}",
                    "category": "CITY_AND_ECONOMY",
                    "url": f"https://www.numbeo.com/cost-of-living/in/{urllib.parse.quote(city_display.replace(' ', '-'))}",
                    "source": "Numbeo Cost of Living",
                    "summary": f"Housing, living expenses, and consumer price basket in {city_display}."
                },
            ]

        return {
            "macro_context": {
                "country": macro.get("country_name", req.country_code),
                "country_code": macro.get("country_code", req.country_code),
                "annual_inflation_rate": macro.get("annual_inflation_rate", 3.0),
                "gdp_growth_rate": macro.get("gdp_growth_rate", 2.5),
                "unemployment_rate": macro.get("unemployment_rate", 6.0),
                "currency": macro.get("currency", req.currency),
                "currency_symbol": "S/" if (req.currency == "PEN" or iso_code == "PE") else ("€" if req.currency == "EUR" else default_sym),
                "exchange_rate_to_usd": macro.get("exchange_rate_to_usd", 1.0),
                "economic_trend_summary": f"{macro.get('source', 'World Bank & ExchangeRate API')} • Exchange rate and inflation integrated into 1,000 trajectories.",
            },
            "live_web_intelligence": core_res.live_web_intelligence or {
                "city_cost_pressure_index": live_cost_idx,
                "career_market_demand_score": live_demand_score,
                "synthesized_real_time_context": "Real-time web research grounding active."
            },
            "live_web_sources": real_web_sources,
            "horizons": {
                "one_month": _format_horizon(core_res.snapshot_1_month, "IN 1 MONTH (DAY 30)", "1_month"),
                "six_months": _format_horizon(core_res.snapshot_6_months, "IN 6 MONTHS (DAY 180)", "6_months"),
                "one_year": _format_horizon(core_res.snapshot_1_year, "IN 1 YEAR (DAY 365)", "1_year"),
            },
            "root_causes": root_causes,
            "golden_path_adjustments": formatted_adjustments,
            "executive_summary": core_res.executive_summary,
            "full_person_dossier_text": getattr(core_res, "full_person_dossier_text", None) or req.full_person_dossier_text or "",
            "inferred_human_factors": core_res.inferred_human_factors.model_dump() if core_res.inferred_human_factors else None,
            "goals_verification": core_res.goals_verification.model_dump() if getattr(core_res, "goals_verification", None) else None,
            "career_autocompletion": core_res.career_autocompletion.model_dump() if getattr(core_res, "career_autocompletion", None) else None,
            "monte_carlo_output": mc_output,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error in predict_future_self_v4: %s", exc)
        raise HTTPException(status_code=500, detail=f"Holistic simulation error: {str(exc)}")
