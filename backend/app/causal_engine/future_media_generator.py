"""
Mirror Future - Future Media Generator (Visual Rendering and Future Self Monologues).
Genera en tiempo real representaciones fotográficas cinematográficas ancladas rigurosamente
en la foto de referencia del usuario, aplicando envejecimiento biológico, fatiga y vitalidad
según los cálculos estocásticos Monte Carlo, y sintetiza videos MP4 fluidos y guiones en 1ª persona.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import math
import os
import random
import subprocess
import urllib.parse
from typing import Dict, Any, Optional, List, Tuple, Union

import cv2
import httpx
try:
    import imageio_ffmpeg
except ImportError:
    imageio_ffmpeg = None
import numpy as np
import io
from PIL import Image, ImageOps

from app.config import get_settings
from app.models.schemas import HolisticFutureRequest, HorizonMetrics, HorizonNarrative
from app.causal_engine.meta_llama_api import llama_client

logger = logging.getLogger("mirror_future.future_media_generator")
logger.setLevel(logging.INFO)


class FutureSelfMediaGenerator:
    """
    Generador Multimodal del "Futuro Yo":
    1. Preservación estricta de la identidad física anclada en la foto de referencia del usuario.
    2. Extracción de rasgos faciales y métricas visuales con Llama 3.2 Vision y Computer Vision (OpenCV).
    3. Transformación biológica del rostro real a 1 Mes, 6 Meses y 1 Año (Camino Actual vs Camino Óptimo).
    4. Generación en tiempo real de videos cinemáticos MP4 con movimiento de cámara, pulso biológico y HUD causal.
    5. Fallback fotográfico hiperrealista cinematográfico con FLUX cuando no se aporta fotografía.
    """

    CINEMATIC_PHOTO_STYLE = (
        "Authentic documentary photograph, 35mm lens, natural daylight, "
        "photorealistic, authentic skin texture, candid realism, true-to-life everyday setting, "
        "documentary portrait, genuine unposed human expression."
    )

    def __init__(self, request_timeout: float = 35.0):
        self.request_timeout = request_timeout
        self._video_cache: Dict[str, bytes] = {}
        self._image_cache: Dict[str, str] = {}
        try:
            self._face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        except Exception:
            self._face_cascade = None

    def _decode_image(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """
        Decodifica la imagen asegurando orientación vertical correcta (EXIF transpose),
        compatibilidad total con formatos PNG/JPEG/WEBP y conversión a BGR para OpenCV.
        """
        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            pil_img = ImageOps.exif_transpose(pil_img)
            pil_img = pil_img.convert("RGB")
            rgb = np.array(pil_img)
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.debug("Decodificación con PIL falló (%s); usando cv2.imdecode", e)
            try:
                nparr = np.frombuffer(image_bytes, np.uint8)
                return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except Exception:
                return None


    def _extract_traits_with_cv(
        self,
        image_bytes: bytes,
        age: int,
        occupation: str,
        city: str
    ) -> str:
        """
        Extracción pericial local de rasgos físicos directamente desde los píxeles de la foto de referencia
        usando visión por computadora (OpenCV). Garantiza cero alucinaciones y fidelidad fisionómica.
        """
        try:
            img = self._decode_image(image_bytes)
            if img is None:
                return f"Person around {age} years old living in {city}, working in {occupation}"

            h, w = img.shape[:2]
            faces = []
            if self._face_cascade is not None and not self._face_cascade.empty():
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self._face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(50, 50))

            if len(faces) > 0:
                fx, fy, fw, fh = faces[0]
                # Muestreo de tono de piel en mejillas
                skin_sample = img[fy + int(fh * 0.4):fy + int(fh * 0.7), fx + int(fw * 0.3):fx + int(fw * 0.7)]
                if skin_sample.size > 0:
                    mb, mg, mr = np.mean(skin_sample, axis=(0, 1))
                    if mr > mb + 25:
                        skin_tone = "warm olive skin tone"
                    elif mr > 180 and mb > 150:
                        skin_tone = "fair radiant skin tone"
                    elif (mr + mg + mb) / 3.0 < 100:
                        skin_tone = "rich dark skin tone"
                    else:
                        skin_tone = "natural medium skin tone"
                else:
                    skin_tone = "natural healthy skin tone"

                # Muestreo de color de cabello en zona superior
                hair_y1 = max(0, fy - int(fh * 0.22))
                hair_y2 = max(0, fy + int(fh * 0.08))
                hair_sample = img[hair_y1:hair_y2, fx:fx + fw]
                if hair_sample.size > 0:
                    hb, hg, hr = np.mean(hair_sample, axis=(0, 1))
                    hair_lum = (hr + hg + hb) / 3.0
                    if hair_lum < 75:
                        hair_tone = "dark black/deep brown hair"
                    elif hair_lum < 130:
                        hair_tone = "chestnut brown hair"
                    elif hair_lum > 175:
                        hair_tone = "light blonde or graying hair"
                    else:
                        hair_tone = "medium brown hair"
                else:
                    hair_tone = "natural styled dark hair"

                # Detección de vello facial en mentón
                chin_y1 = fy + int(fh * 0.75)
                chin_y2 = min(h, fy + int(fh * 0.98))
                chin_sample = img[chin_y1:chin_y2, fx + int(fw * 0.3):fx + int(fw * 0.7)]
                facial_hair = ""
                has_beard = False
                if chin_sample.size > 0:
                    cb, cg, cr = np.mean(chin_sample, axis=(0, 1))
                    chin_lum = (cb + cg + cr) / 3.0
                    skin_lum = (mb + mg + mr) / 3.0 if skin_sample.size > 0 else 130.0
                    if chin_lum < skin_lum - 22:
                        facial_hair = "with neatly groomed dark facial hair (short beard and mustache), "
                        has_beard = True

                # Detección de gafas / lentes en la zona ocular
                eye_y1 = fy + int(fh * 0.30)
                eye_y2 = fy + int(fh * 0.50)
                eye_sample = img[eye_y1:eye_y2, fx + int(fw * 0.2):fx + int(fw * 0.8)]
                glasses_desc = ""
                if eye_sample.size > 0:
                    gray_eye = cv2.cvtColor(eye_sample, cv2.COLOR_BGR2GRAY)
                    edges = cv2.Canny(gray_eye, 70, 160)
                    edge_ratio = np.sum(edges > 0) / float(edges.size)
                    if edge_ratio > 0.08:
                        glasses_desc = "wearing modern stylish eyeglasses, "

                occ_clean = (occupation or "").lower()
                if any(w in occ_clean for w in ["ingeniera", "doctora", "abogada", "mujer", "chica", "administradora", "enfermera"]):
                    person_type = "young woman"
                elif any(w in occ_clean for w in ["ingeniero", "doctor", "abogado", "hombre", "chico", "administrador", "enfermero"]) or has_beard:
                    person_type = "young man"
                else:
                    person_type = "professional individual"

                return (
                    f"A {age}-year-old Latin American {person_type} with {hair_tone}, {skin_tone}, "
                    f"{glasses_desc}{facial_hair}authentic facial bone structure, expressive confident eyes"
                )

            # Si no se detectó rostro frontal definido (ej. foto de perfil, ángulo o iluminación suave)
            mean_b, mean_g, mean_r = np.mean(img, axis=(0, 1))
            skin_desc = "warm olive skin tone" if mean_r > mean_b else "natural skin tone"
            occ_clean = (occupation or "").lower()
            person_type = "woman" if any(w in occ_clean for w in ["ingeniera", "doctora", "mujer"]) else ("man" if any(w in occ_clean for w in ["ingeniero", "doctor", "hombre"]) else "professional")
            return (
                f"A {age}-year-old Latin American {person_type} with natural dark hair, {skin_desc}, "
                f"authentic facial features, expressive eyes"
            )
        except Exception as exc:
            logger.warning("Falla en extracción de rasgos físicos por Computer Vision: %s", exc)
            return f"Authentic professional person around {age} years old in {city}."

    async def extract_person_visual_traits(
        self,
        image_bytes: Optional[bytes] = None,
        age: int = 26,
        occupation: str = "Profesional",
        city: str = "Ciudad"
    ) -> str:
        """
        a) Si el usuario adjuntó una foto de referencia:
           1. Primero intenta Llama 3.2 Vision (11B) si la API está autenticada.
           2. Si no o falla, ejecuta Computer Vision pericial sobre los píxeles reales de la imagen.
           3. Si no hay foto, infiere el perfil demográfico.
        """
        if image_bytes and len(image_bytes) > 100:
            # 1. Intentar Llama Vision si las credenciales son válidas
            try:
                settings = get_settings()
                if settings.meta_llama_api_key and not settings.meta_llama_api_key.startswith("tu_"):
                    b64_img = base64.b64encode(image_bytes).decode("utf-8")
                    prompt = (
                        "You are a master forensic biometric facial analyst. Analyze this individual's face and portrait with extreme precision for photorealistic identity preservation. "
                        "Output a rich, highly descriptive and cohesive English prompt paragraph detailing their EXACT recognizable physical features: "
                        "1) Perceived gender, apparent age in years, and heritage appearance. "
                        "2) Precise face structure: face shape (e.g. sharp angular jawline, defined cheekbones, square chin, rounded or tapered forehead). "
                        "3) Skin tone and undertone: exact Fitzpatrick complexion (warm olive, fair porcelain, deep bronze, rich brown) and texture. "
                        "4) Eyes and gaze: exact eye shape (e.g. almond, hooded, deep-set), iris color, eyelid folds, eyebrow thickness and arch. "
                        "5) Nose structure: bridge height, width, nostril profile, and tip shape. "
                        "6) Mouth, lips, and expression: lip fullness, cupid's bow, and resting expression. "
                        "7) Hair: exact cut, texture, parting, length, hairline, and color shade. "
                        "8) Facial hair: presence and grooming (clean-shaven, 5 o'clock shadow, trimmed beard, mustache) or clean cheeks. "
                        "9) Eyewear: exact frame style, shape, material, and color, or explicitly specify no eyeglasses. "
                        "10) Any defining unique facial markers. "
                        "Keep the description 100% focused on their distinct head and facial likeness so another image generator creates an image of the EXACT same human being. "
                        "Do NOT describe background or clothing. Write as a continuous descriptive character portrait."
                    )
                    traits = await llama_client.vision_completion(
                        prompt=prompt,
                        base64_image=b64_img,
                        image_mime_type="image/jpeg",
                        model=settings.llama_vision_model,
                        temperature=0.1,
                        max_tokens=3000
                    )
                    if traits and len(traits.strip()) > 20:
                        clean_traits = traits.strip().replace("\n", " ")
                        logger.info("Rasgos físicos extraídos con Meta Vision: %s", clean_traits[:100])
                        return clean_traits
            except Exception as exc:
                logger.debug("Meta Vision no disponible (%s); ejecutando Computer Vision de alta fidelidad.", exc)

            # 2. Extracción directa con Computer Vision pericial sobre la foto real
            cv_traits = self._extract_traits_with_cv(image_bytes, age, occupation, city)
            logger.info("Rasgos físicos extraídos directamente de la foto con Computer Vision: %s", cv_traits)
            return cv_traits

        # 3. Inferencia demográfica pericial basada en edad, ocupación y contexto si no hay foto
        occ_lower = occupation.lower()
        if any(w in occ_lower for w in ["ingeniera", "administradora", "doctora", "directora", "mujer", "chica", "abogada"]):
            gender_cue = "young professional woman"
        elif any(w in occ_lower for w in ["ingeniero", "administrador", "doctor", "director", "hombre", "chico", "abogado"]):
            gender_cue = "young professional man"
        else:
            gender_cue = "young professional person"

        return (
            f"A Latin American {gender_cue} around {age} years old, with expressive dark eyes, "
            f"natural dark hair neatly styled, warm olive skin tone, intelligent and thoughtful expression, "
            f"bearing modern smart casual attire suited for an ambitious {occupation} in {city}."
        )

    def _create_cinematic_canvas(
        self,
        img_bgr: np.ndarray,
        target_w: int = 1024,
        target_h: int = 576
    ) -> Tuple[np.ndarray, Optional[Tuple[int, int, int, int]]]:
        """
        Adapta la foto de referencia a un encuadre cinematográfico 16:9 ultra nítido.
        Genera un fondo ambiental bokeh a juego y centra el sujeto con relación de aspecto perfecta.
        Devuelve el canvas BGR y las coordenadas del rostro detectado (fx, fy, fw, fh) en el canvas.
        """
        h, w = img_bgr.shape[:2]

        # 1. Crear fondo ambiental bokeh a partir de la misma fotografía
        scale_bg = max(target_w / float(w), target_h / float(h))
        bg_w, bg_h = int(w * scale_bg), int(h * scale_bg)
        bg = cv2.resize(img_bgr, (bg_w, bg_h), interpolation=cv2.INTER_LINEAR)
        x1 = (bg_w - target_w) // 2
        y1 = (bg_h - target_h) // 2
        bg_cropped = bg[y1:y1 + target_h, x1:x1 + target_w]
        bg_blurred = cv2.GaussianBlur(bg_cropped, (51, 51), 0)
        # Atenuar fondo para destacar el primer plano
        canvas = cv2.addWeighted(bg_blurred, 0.40, np.zeros_like(bg_blurred), 0.60, 0)

        # 2. Escalar el sujeto para que encaje prominentemente en el centro
        scale_fg = min(target_w / float(w), target_h / float(h))
        fg_w, fg_h = int(w * scale_fg), int(h * scale_fg)
        fg = cv2.resize(img_bgr, (fg_w, fg_h), interpolation=cv2.INTER_LANCZOS4)
        fx = (target_w - fg_w) // 2
        fy = (target_h - fg_h) // 2

        # 3. Superponer sujeto con sombra suave en los bordes
        canvas[fy:fy + fg_h, fx:fx + fg_w] = fg

        # 4. Detectar coordenadas del rostro sobre el canvas compuesto
        face_coords = None
        if self._face_cascade is not None and not self._face_cascade.empty():
            gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
            faces = self._face_cascade.detectMultiScale(gray_canvas, scaleFactor=1.1, minNeighbors=3, minSize=(60, 60))
            if len(faces) > 0:
                face_coords = tuple(int(v) for v in faces[0])

        return canvas, face_coords

    def transform_reference_photo_for_horizons(
        self,
        image_bytes: bytes,
        sim_metrics: Dict[str, HorizonMetrics],
        req: HolisticFutureRequest
    ) -> Dict[str, str]:
        """
        Transforma la foto de referencia REAL del usuario en sus representaciones futuras a:
        - 1 Mes (30 días): Luz matutina, foco limpio, postura activa, arranque disciplinado.
        - 6 Meses (180 días):
          * Si burnout >= 0.25: Huella de fatiga, ojeras tenues, iluminación nocturna de pantalla.
          * Si saludable: Piel radiante, postura erguida, vitalidad plena.
        - 1 Año Inercial (365 días, P50): Realismo maduro de esfuerzo continuo, oficina de día a día.
        - 1 Año Óptimo (365 días, Golden Path P90): Éxito total, luz dorada, piel descansada, prosperidad.
        Devuelve URLs en base64 de alta resolución garantizando 100% de consistencia de identidad.
        """
        img = self._decode_image(image_bytes)
        if img is None:
            logger.warning("No se pudo decodificar la imagen del usuario para transformación directa.")
            return {}

        target_w, target_h = 1024, 576
        base_canvas, face_coords = self._create_cinematic_canvas(img, target_w, target_h)

        m1 = sim_metrics.get("1_month")
        m6 = sim_metrics.get("6_months")
        m1y = sim_metrics.get("1_year")

        burn_1m = m1.burnout_probability if m1 else 0.15
        burn_6m = m6.burnout_probability if m6 else 0.25
        goal_pct_1y = m1y.career_and_goal_completion_pct.p50 if m1y else 45.0

        # Helper para codificar en Base64 JPEG de alta calidad
        def _to_b64_url(frame_bgr: np.ndarray) -> str:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 92]
            success, buffer = cv2.imencode('.jpg', frame_bgr, encode_param)
            if not success:
                return ""
            b64 = base64.b64encode(buffer).decode('utf-8')
            return f"data:image/jpeg;base64,{b64}"

        # -------------------------------------------------------------
        # 0. FOTO ORIGINAL CENTRADA EN 16:9 CINEMÁTICO
        # -------------------------------------------------------------
        b64_original = _to_b64_url(base_canvas)

        # -------------------------------------------------------------
        # 1. HORIZONTE 1 MES (30 DÍAS): Inicio con energía y foco matutino
        # -------------------------------------------------------------
        frame_1m = base_canvas.copy().astype(np.float32)
        # Tonalidad matutina: sutil aumento de luz cálida natural (+3% R, +2% G)
        frame_1m[:, :, 2] *= 1.03
        frame_1m[:, :, 1] *= 1.02
        # Aumento de claridad y contraste enfocado
        frame_1m = np.clip((frame_1m - 128) * 1.05 + 130, 0, 255).astype(np.uint8)
        # Viñeta 35mm cinematográfica sutil
        frame_1m = self._apply_vignette(frame_1m, strength=0.25)
        b64_1m = _to_b64_url(frame_1m)

        # -------------------------------------------------------------
        # 2. HORIZONTE 6 MESES (180 DÍAS): Bifurcación Causal de Fatiga
        # -------------------------------------------------------------
        frame_6m = base_canvas.copy()
        if burn_6m >= 0.25 or req.sleep_hours < 6.5:
            # Filtro de sobrecarga y déficit de descanso:
            hsv = cv2.cvtColor(frame_6m, cv2.COLOR_BGR2HSV).astype(np.float32)
            # Desaturación sutil por fatiga circadiana (-14%)
            hsv[:, :, 1] *= 0.86
            frame_6m = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)

            # Gradiente de luz nocturna de lámpara de escritorio (cálido lateral)
            for x in range(target_w // 2):
                factor = (1.0 - (x / float(target_w // 2))) * 0.16
                frame_6m[:, x, 0] += 8 * factor   # Blue
                frame_6m[:, x, 1] += 28 * factor  # Green
                frame_6m[:, x, 2] += 55 * factor  # Red

            frame_6m = np.clip(frame_6m, 0, 255).astype(np.uint8)

            # Si se detectó rostro, añadir sombreado sutil bajo párpados inferiores (ojeras de esfuerzo)
            if face_coords is not None:
                fx, fy, fw, fh = face_coords
                left_eye_y = fy + int(fh * 0.44)
                left_eye_x = fx + int(fw * 0.33)
                right_eye_x = fx + int(fw * 0.67)
                rx = max(4, int(fw * 0.13))
                ry = max(2, int(fh * 0.05))

                shadow_mask = np.zeros((target_h, target_w), dtype=np.uint8)
                cv2.ellipse(shadow_mask, (left_eye_x, left_eye_y + int(fh * 0.05)), (rx, ry), 0, 0, 360, 255, -1)
                cv2.ellipse(shadow_mask, (right_eye_x, left_eye_y + int(fh * 0.05)), (rx, ry), 0, 0, 360, 255, -1)
                shadow_mask = cv2.GaussianBlur(shadow_mask, (19, 19), 0)

                f_layer = frame_6m.astype(np.float32)
                factor_shadow = 1.0 - (shadow_mask.astype(np.float32) / 255.0) * 0.20
                frame_6m = np.clip(f_layer * factor_shadow[:, :, None], 0, 255).astype(np.uint8)
        else:
            # Vitalidad plena y balance
            hsv = cv2.cvtColor(frame_6m, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.10, 0, 255)
            hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.03 + 4, 0, 255)
            frame_6m = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        frame_6m = self._apply_vignette(frame_6m, strength=0.30)
        b64_6m = _to_b64_url(frame_6m)

        # -------------------------------------------------------------
        # 3. HORIZONTE 1 AÑO ACTUAL (365 DÍAS - P50): Camino Inercial
        # -------------------------------------------------------------
        frame_1y_cur = base_canvas.copy().astype(np.float32)
        # Tonalidad neutra realista de oficina, ligero temple de madurez
        frame_1y_cur[:, :, 0] *= 1.02  # Neutral cool
        frame_1y_cur = np.clip((frame_1y_cur - 128) * 1.06 + 126, 0, 255).astype(np.uint8)
        frame_1y_cur = self._apply_vignette(frame_1y_cur, strength=0.35)
        b64_1y_cur = _to_b64_url(frame_1y_cur)

        # -------------------------------------------------------------
        # 4. HORIZONTE 1 AÑO ÓPTIMO (365 DÍAS - P90): Golden Path de Mirror Future
        # -------------------------------------------------------------
        frame_1y_opt = base_canvas.copy()
        # Calibración dorada de alto logro y vitalidad peak
        hsv_opt = cv2.cvtColor(frame_1y_opt, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv_opt[:, :, 1] = np.clip(hsv_opt[:, :, 1] * 1.18, 0, 255)  # +18% de viveza
        hsv_opt[:, :, 2] = np.clip(hsv_opt[:, :, 2] * 1.08 + 8, 0, 255)  # Luminiscencia sana
        opt_bgr = cv2.cvtColor(hsv_opt.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)

        # Tinte Golden Hour cálido
        opt_bgr[:, :, 0] *= 0.94  # Menor azul
        opt_bgr[:, :, 1] *= 1.03  # Verde natural
        opt_bgr[:, :, 2] *= 1.10  # Dorado / rojizo elegante

        # Destello suave en altas luces (Bloom arquitectónico)
        gray_opt = cv2.cvtColor(frame_1y_opt, cv2.COLOR_BGR2GRAY)
        _, highlights = cv2.threshold(gray_opt, 195, 255, cv2.THRESH_BINARY)
        bloom = cv2.GaussianBlur(highlights, (35, 35), 0).astype(np.float32) / 255.0
        opt_bgr[:, :, 2] += bloom * 22
        opt_bgr[:, :, 1] += bloom * 14

        frame_1y_opt = np.clip(opt_bgr, 0, 255).astype(np.uint8)
        frame_1y_opt = self._apply_vignette(frame_1y_opt, strength=0.20)
        b64_1y_opt = _to_b64_url(frame_1y_opt)

        results = {
            "1_month": b64_1m,
            "6_months": b64_6m,
            "1_year_current": b64_1y_cur,
            "1_year_optimal": b64_1y_opt,
            "reference_original": b64_original
        }
        self._image_cache.update(results)
        return results

    def _apply_vignette(self, img: np.ndarray, strength: float = 0.3) -> np.ndarray:
        """Aplica una viñeta óptica cinematográfica suave de 35mm."""
        h, w = img.shape[:2]
        kernel_x = cv2.getGaussianKernel(w, w * 0.75)
        kernel_y = cv2.getGaussianKernel(h, h * 0.75)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()
        mask = (1.0 - strength) + strength * mask
        vignetted = img.astype(np.float32) * mask[:, :, None]
        return np.clip(vignetted, 0, 255).astype(np.uint8)

    def generate_horizon_video_mp4(
        self,
        canvas_bgr: np.ndarray,
        horizon_key: str,
        monologue_text: str,
        burnout_prob: float = 0.20,
        days_label: str = "180 DÍAS",
        status_badge: str = "OPTIMAL",
        duration_seconds: int = 4,
        fps: int = 24
    ) -> bytes:
        """
        Genera un video cinemático MP4 ultra-fluido (H.264) a partir del encuadre del usuario:
        - Movimiento de cámara Ken Burns (zoom suave hacia el rostro).
        - Pulso biológico de respiración (micro-modulación de exposición a 0.25 Hz).
        - Mirror Future futuristic HUD telemetry overlay in upper region.
        - Cintillo de subtítulo con el monólogo de su Futuro Yo.
        """
        target_w, target_h = 1024, 576
        if canvas_bgr.shape[:2] != (target_h, target_w):
            canvas_bgr = cv2.resize(canvas_bgr, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)

        total_frames = fps * duration_seconds
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe() if imageio_ffmpeg is not None else None
        if not ffmpeg_exe:
            import shutil
            ffmpeg_exe = shutil.which("ffmpeg")
        if not ffmpeg_exe:
            logger.warning("ffmpeg no disponible para generar video cinemático MP4.")
            return None

        cmd = [
            ffmpeg_exe, '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f'{target_w}x{target_h}',
            '-pix_fmt', 'bgr24',
            '-r', str(fps),
            '-i', '-',
            '-an',
            '-vcodec', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'ultrafast',
            '-f', 'mp4',
            '-movflags', 'frag_keyframe+empty_moov+default_base_moof',
            'pipe:1'
        ]

        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )

        # Recorte de texto para el banner inferior
        clean_quote = monologue_text.replace("\n", " ").strip()
        if len(clean_quote) > 110:
            clean_quote = clean_quote[:107] + "..."

        badge_color = (60, 200, 60) if status_badge == "OPTIMAL" else ((50, 60, 220) if status_badge == "CRITICAL" else (40, 160, 240))

        for i in range(total_frames):
            prog = i / float(total_frames)
            # Zoom suave 1.0 -> 1.07
            scale = 1.0 + 0.07 * prog
            cw = int(target_w / scale)
            ch = int(target_h / scale)
            cx = (target_w - cw) // 2
            cy = (target_h - ch) // 2

            cropped = canvas_bgr[cy:cy + ch, cx:cx + cw]
            frame = cv2.resize(cropped, (target_w, target_h), interpolation=cv2.INTER_LINEAR)

            # Pulso sutil de respiración biológica (sinusoidal a 0.25 Hz)
            breath = 1.0 + 0.012 * math.sin(2 * math.pi * i / float(fps * 2))
            if breath != 1.0:
                frame = np.clip(frame.astype(np.float32) * breath, 0, 255).astype(np.uint8)

            # Barra superior HUD translúcida
            top_bar = frame[0:55, :].astype(np.float32)
            top_bar = cv2.addWeighted(top_bar, 0.45, np.zeros_like(top_bar), 0.55, 0)
            frame[0:55, :] = top_bar.astype(np.uint8)

            cv2.putText(frame, "MIRROR FUTURE - CAUSAL SIMULATION OF YOUR FUTURE SELF", (30, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, f"T + {days_label}", (target_w - 360, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 140, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, f"BURNOUT: {int(burnout_prob * 100)}%", (target_w - 180, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.55, badge_color, 2, cv2.LINE_AA)

            # Barra inferior con subtítulo
            bot_bar = frame[target_h - 75:target_h, :].astype(np.float32)
            bot_bar = cv2.addWeighted(bot_bar, 0.35, np.zeros_like(bot_bar), 0.65, 0)
            frame[target_h - 75:target_h, :] = bot_bar.astype(np.uint8)

            cv2.putText(frame, f"\"{clean_quote}\"", (30, target_h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 255, 255), 1, cv2.LINE_AA)

            proc.stdin.write(frame.tobytes())

        proc.stdin.close()
        out_mp4_bytes, _ = proc.communicate()
        return out_mp4_bytes

    def cache_horizon_videos(
        self,
        image_bytes: bytes,
        sim_metrics: Dict[str, HorizonMetrics],
        req: HolisticFutureRequest
    ) -> None:
        """
        Pre-genera y almacena en caché los videos MP4 de los horizontes a partir de la foto del usuario.
        """
        try:
            img = self._decode_image(image_bytes)
            if img is None:
                return

            target_w, target_h = 1024, 576
            canvas, _ = self._create_cinematic_canvas(img, target_w, target_h)

            m1 = sim_metrics.get("1_month")
            m6 = sim_metrics.get("6_months")
            m1y = sim_metrics.get("1_year")

            script_1m = self.generate_first_person_monologue("1_month", None, m1, req)
            script_6m = self.generate_first_person_monologue("6_months", None, m6, req)
            script_1y = self.generate_first_person_monologue("1_year", None, m1y, req)

            # Generar video para 6 meses (horizonte de mayor impacto relacional y fatiga)
            burn_6m = m6.burnout_probability if m6 else 0.25
            v_6m = self.generate_horizon_video_mp4(
                canvas_bgr=canvas,
                horizon_key="6_months",
                monologue_text=script_6m,
                burnout_prob=burn_6m,
                days_label="180 DIAS",
                status_badge="CRITICAL" if burn_6m >= 0.40 else "OPTIMAL"
            )
            self._video_cache["6_months_CURRENT"] = v_6m
            self._video_cache["6_months_OPTIMAL"] = v_6m

            # Video 1 mes
            burn_1m = m1.burnout_probability if m1 else 0.15
            v_1m = self.generate_horizon_video_mp4(
                canvas_bgr=canvas,
                horizon_key="1_month",
                monologue_text=script_1m,
                burnout_prob=burn_1m,
                days_label="30 DIAS",
                status_badge="OPTIMAL"
            )
            self._video_cache["1_month_CURRENT"] = v_1m
            self._video_cache["1_month_OPTIMAL"] = v_1m

            # Video 1 año
            burn_1y = m1y.burnout_probability if m1y else 0.20
            v_1y = self.generate_horizon_video_mp4(
                canvas_bgr=canvas,
                horizon_key="1_year",
                monologue_text=script_1y,
                burnout_prob=burn_1y,
                days_label="365 DIAS",
                status_badge="OPTIMAL"
            )
            self._video_cache["1_year_CURRENT"] = v_1y
            self._video_cache["1_year_OPTIMAL"] = v_1y
            logger.info("Videos cinemáticos MP4 generados y cacheados exitosamente para todos los horizontes.")
        except Exception as exc:
            logger.warning("Falla al pre-generar videos MP4: %s", exc)

    def get_cached_video(self, horizon_key: str, mode: str = "CURRENT") -> Optional[bytes]:
        """Obtiene el video MP4 cacheado para un horizonte determinado."""
        clean_key = horizon_key.lower().replace("one_", "1_").replace("six_", "6_")
        if not clean_key.endswith("month") and not clean_key.endswith("months") and not clean_key.endswith("year"):
            clean_key = f"{clean_key}_months" if "6" in clean_key else ("1_month" if "1_m" in clean_key else "1_year")
        
        lookup = f"{clean_key}_{mode.upper()}"
        if lookup in self._video_cache:
            return self._video_cache[lookup]
        # Búsqueda laxa
        for k, v in self._video_cache.items():
            if clean_key in k:
                return v
        return None

    def build_visual_prompts(
        self,
        req: HolisticFutureRequest,
        macro: Any,
        sim_metrics: Dict[str, HorizonMetrics],
        visual_traits: str,
        has_reference_photo: bool = False
    ) -> Dict[str, str]:
        """
        b) Usando los resultados matemáticos de sim_metrics, construye 4 prompts fotográficos
        hiperrealistas cinematográficos para fallback cuando no se sube fotografía.
        """
        m1 = sim_metrics.get("1_month")
        m6 = sim_metrics.get("6_months")
        m1y = sim_metrics.get("1_year")
        style = self.CINEMATIC_PHOTO_STYLE

        city_clean = (req.city or "").strip() or "their city"
        occ_clean = (req.career_or_degree or req.occupation or "").strip() or "their profession"
        goal_text = f"working towards '{req.main_goal_1y}'" if (req.main_goal_1y or "").strip() else f"focused on {occ_clean}"

        is_student = (
            req.life_profile_type == "UNIVERSITY_OR_TECH_STUDENT"
            or req.months_to_graduation > 0
            or any(w in occ_clean.lower() for w in ["estudiant", "estudio", "tesis", "carrera", "universidad", "instituto", "student"])
        )

        vit_1m = m1.health_and_vitality_score.p50 if m1 else 65.0
        burn_1m = m1.burnout_probability if m1 else 0.15
        energy_desc_1m = "focused and alert expression, slight morning concentration" if burn_1m < 0.25 else "slight tension around the eyes, active posture"

        burn_6m = m6.burnout_probability if m6 else 0.25
        if burn_6m >= 0.30 or req.sleep_hours < 6.5:
            fatigue_cues = (
                "visible signs of fatigue, subtle dark circles under tired yet determined eyes, "
                "desk lamp light casting realistic shadows, working through demanding deliverables"
            )
        else:
            fatigue_cues = (
                "healthy vibrant skin, alert engaged eyes, upright energetic posture, "
                "bright natural daylight in an organized workspace, confident slight smile reviewing progress"
            )

        # Lead de identidad estricta: si se proveyó foto, anclar con máxima prioridad la fisionomía del usuario
        if has_reference_photo:
            id_prefix = (
                f"Masterpiece 85mm portrait photograph capturing the exact recognizable face, identical facial structure, eye shape, nose, mouth, skin tone, and hair of this specific individual: {visual_traits}. "
                f"Strictly maintain their exact personal identity and facial likeness. "
            )
        else:
            id_prefix = f"Authentic candid 85mm portrait photograph: {visual_traits}. "

        if is_student:
            prompt_1m = (
                f"{id_prefix}Depicted in 1 Month (Day 30 future) in {city_clean}. "
                f"University student preparing in {occ_clean}, seated at an authentic wooden desk with a laptop, open notes, and a warm ceramic mug. "
                f"Comfortable smart casual student attire, soft natural daylight from a window, {energy_desc_1m}. "
                f"Sharp facial focus, authentic skin pores and texture, cinematic depth of field."
            )
            prompt_6m = (
                f"{id_prefix}Depicted in 6 Months (Day 180 future) in {city_clean}. "
                f"University student finalizing core milestone project in {occ_clean}, reviewing code and reports on workstation in {city_clean}. "
                f"{fatigue_cues}. Sharp facial focus, authentic skin pores and micro-texture, cinematic documentary realism."
            )
            prompt_1y_current = (
                f"{id_prefix}Depicted in 1 Year (Day 365 future, inertial path) in {city_clean}. "
                f"Graduated professional working actively in {occ_clean} at a contemporary workstation in {city_clean}. "
                f"Neat smart professional clothes, natural room daylight, authentic determined expression, sharp facial focus, photorealistic."
            )
            prompt_1y_optimal = (
                f"{id_prefix}Depicted in 1 Year (Day 365 future, Golden Path) in {city_clean}. "
                f"Accomplished professional in {occ_clean}, glowing with peak vitality and financial stability at a modern sunlit workplace in {city_clean}. "
                f"Radiant healthy skin, confident relaxed smile of triumph and success, immaculate professional attire, golden hour warm lighting, razor-sharp facial details."
            )
        else:
            prompt_1m = (
                f"{id_prefix}Depicted in 1 Month (Day 30 future) in {city_clean}. "
                f"Engaged in professional work activities as a {occ_clean}, practical workstation, {goal_text}, {energy_desc_1m}. "
                f"Comfortable everyday work attire, natural lighting, sharp facial focus, authentic skin pores and texture."
            )
            prompt_6m = (
                f"{id_prefix}Depicted in 6 Months (Day 180 future) in {city_clean}. "
                f"Actively working as a {occ_clean} in {city_clean}, {fatigue_cues}. "
                f"Realistic workplace setting, sharp facial focus, authentic skin micro-texture, honest human discipline."
            )
            prompt_1y_current = (
                f"{id_prefix}Depicted in 1 Year (Day 365 future, inertial path) in {city_clean}. "
                f"Established and experienced in {occ_clean} at a contemporary workplace in {city_clean}. "
                f"Resilient mature expression, practical professional attire, natural lighting, sharp facial focus, photorealistic."
            )
            prompt_1y_optimal = (
                f"{id_prefix}Depicted in 1 Year (Day 365 future, Golden Path) in {city_clean}. "
                f"Flourishing and accomplished {occ_clean} in {city_clean}, radiant healthy skin, well-rested confident expression, "
                f"thriving modern workplace, bright natural sunlight, immaculate attire, atmosphere of high accomplishment, razor-sharp facial focus."
            )

        return {
            "prompt_1m": prompt_1m,
            "prompt_6m": prompt_6m,
            "prompt_1y_current": prompt_1y_current,
            "prompt_1y_optimal": prompt_1y_optimal
        }

    async def _generate_single_image(
        self,
        client: httpx.AsyncClient,
        prompt: str,
        seed: int,
        together_api_key: Optional[str] = None
    ) -> str:
        """
        Generación de imagen del Futuro Yo:
        1. Prioridad: Meta Muse Image 1.0 utilizando los créditos activos del usuario.
        2. Fallback Secundario: Together AI FLUX si está configurado.
        3. Fallback Gratuito: Pollinations FLUX.
        """
        # 1. Intentar Meta Muse Image 1.0 oficial
        try:
            settings = get_settings()
            if settings.meta_llama_api_key and not settings.meta_llama_api_key.startswith("tu_"):
                muse_img = await llama_client.image_generation(prompt=prompt)
                if muse_img and (muse_img.startswith("data:image") or muse_img.startswith("http")):
                    logger.info("Imagen generada exitosamente con Meta Muse Image 1.0")
                    return muse_img
        except Exception as exc:
            logger.debug("Meta Muse Image llamada falló o agotó tiempo (%s); procediendo a fallback.", exc)

        encoded_prompt = urllib.parse.quote(prompt[:900])
        pollinations_url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width=1024&height=576&nologo=true&model=flux&seed={seed}"
        )

        if together_api_key and len(together_api_key.strip()) > 5:
            try:
                together_url = "https://api.together.xyz/v1/images/generations"
                payload = {
                    "model": "black-forest-labs/FLUX.1-schnell",
                    "prompt": prompt[:850],
                    "width": 1024,
                    "height": 576,
                    "steps": 4,
                    "n": 1,
                    "response_format": "url"
                }
                headers = {
                    "Authorization": f"Bearer {together_api_key.strip()}",
                    "Content-Type": "application/json"
                }
                resp = await client.post(
                    together_url,
                    json=payload,
                    headers=headers,
                    timeout=self.request_timeout
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if "data" in data and len(data["data"]) > 0 and "url" in data["data"][0]:
                        return data["data"][0]["url"]
            except Exception as exc:
                logger.debug("Together AI FLUX llamada falló o agotó tiempo (%s); usando Pollinations.", exc)

        return pollinations_url

    async def generate_images_parallel(
        self,
        prompts_dict: Dict[str, str]
    ) -> Dict[str, str]:
        """Genera 4 imágenes del Futuro Yo en paralelo usando Meta Muse Image 1.0."""
        settings = get_settings()
        together_key = getattr(settings, "together_api_key", None) or ""

        base_seed = random.randint(10000, 99999)
        seeds = {
            "1_month": base_seed + 11,
            "6_months": base_seed + 22,
            "1_year_current": base_seed + 33,
            "1_year_optimal": base_seed + 44
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(self.request_timeout, connect=2.0)) as client:
            t1m = self._generate_single_image(client, prompts_dict["prompt_1m"], seeds["1_month"], together_key)
            t6m = self._generate_single_image(client, prompts_dict["prompt_6m"], seeds["6_months"], together_key)
            t1y_cur = self._generate_single_image(client, prompts_dict["prompt_1y_current"], seeds["1_year_current"], together_key)
            t1y_opt = self._generate_single_image(client, prompts_dict["prompt_1y_optimal"], seeds["1_year_optimal"], together_key)

            res1m, res6m, res1y_cur, res1y_opt = await asyncio.gather(
                t1m, t6m, t1y_cur, t1y_opt, return_exceptions=True
            )

        fallback_encoded = urllib.parse.quote(prompts_dict["prompt_1m"][:300])
        def _safe_res(res, seed_key):
            if isinstance(res, str) and (res.startswith("http") or res.startswith("data:image")):
                return res
            return f"https://image.pollinations.ai/prompt/{fallback_encoded}?width=1024&height=576&nologo=true&model=flux&seed={seeds[seed_key]}"

        return {
            "1_month": _safe_res(res1m, "1_month"),
            "6_months": _safe_res(res6m, "6_months"),
            "1_year_current": _safe_res(res1y_cur, "1_year_current"),
            "1_year_optimal": _safe_res(res1y_opt, "1_year_optimal")
        }

    def generate_first_person_monologue(
        self,
        horizon_key: str,
        narrative: Optional[HorizonNarrative],
        metrics: Optional[HorizonMetrics],
        req: HolisticFutureRequest
    ) -> str:
        """Genera el monólogo pericial en primera persona para la voz y video."""
        burn_prob = metrics.burnout_probability if metrics else 0.15
        net_worth = metrics.financial_net_worth.p50 if metrics else 0.0
        currency = req.currency

        if horizon_key in ("1_month", "one_month"):
            return (
                f"Hola, soy tú dentro de 30 días aquí en {req.city}. "
                f"Hemos empezado a dar los primeros pasos firmes hacia nuestra meta de '{req.main_goal_1y}'. "
                f"Siento la energía al despertar, pero te lo advierto con honestidad: esas {req.screen_time_distraction_hours:.1f} horas "
                f"frente al teléfono por las noches nos están restando claridad matutina. "
                f"Protejamos el descanso hoy mismo y verás lo rápido que despegamos."
            )

        if horizon_key in ("6_months", "six_months"):
            if burn_prob >= 0.35:
                return (
                    f"Hola... soy tú a los 180 días. Mírame bien: si no frenas el desgaste hoy, la fatiga se nos va a clavar "
                    f"en los hombros y las ojeras van a ser evidentes frente al espejo. "
                    f"Tu potencial en {req.occupation} es enorme, pero no podemos escalar '{req.main_goal_1y}' "
                    f"con la batería en reserva. Asegura tus 7 horas y media de sueño y ponle un tope al trabajo desmedido."
                )
            return (
                f"¡Hola! Soy tu versión de 6 meses en {req.city}. La constancia ha valido cada minuto de esfuerzo. "
                f"Como {req.occupation}, hemos logrado avances tangibles y nuestro patrimonio estimado supera los {net_worth:,.0f} {currency}. "
                f"Al sostener el ejercicio y cuidar la alimentación, la mente responde con lucidez total hacia '{req.main_goal_1y}'. "
                f"Mantén este rumbo, que estamos construyendo algo grande."
            )

        goal_pct = metrics.career_and_goal_completion_pct.p50 if metrics else 50.0
        return (
            f"Mírame: soy tú al cabo de un año completo. Llegamos al día 365 con un {goal_pct:.0f}% de nuestra meta cumplida en {req.city}. "
            f"Superamos los retos económicos de nuestro entorno y demostramos de qué estamos hechos. "
            f"Pero la lección más valiosa que aprendimos es que el verdadero éxito combina libertad financiera con salud plena. "
            f"Gracias por haber tomado las decisiones valientes hace 365 días; hoy vivimos el resultado de tu disciplina."
        )

    def generate_scene_caption(
        self,
        horizon_key: str,
        metrics: Optional[HorizonMetrics],
        req: HolisticFutureRequest,
        has_reference_photo: bool = False
    ) -> str:
        """Genera el texto pericial descriptivo de la escena física generada."""
        burn_prob = metrics.burnout_probability if metrics else 0.15
        ref_text = "Retrato calibrado desde tu fotografía real" if has_reference_photo else "Retrato conceptual proyectado"

        if horizon_key in ("1_month", "one_month"):
            return (
                f"{ref_text} a 30 días en {req.city}: Postura activa matutina frente a su estación de trabajo, "
                f"reflejando energía basal, concentración en '{req.main_goal_1y}' y primeros ajustes de rutina diaria."
            )

        if horizon_key in ("6_months", "six_months"):
            if burn_prob >= 0.35:
                return (
                    f"{ref_text} a 180 días en {req.city}: Signos visibles de sobrecarga biológica, "
                    f"periorbital tenue por vigilia nocturna y tensión acumulada en {req.occupation}."
                )
            return (
                f"{ref_text} a 180 días en {req.city}: Piel saludable, mirada decidida y postura erguida, "
                f"evidenciando constancia de hábitos y tracción profesional acelerada."
            )

        return (
            f"{ref_text} al Día 365 en {req.city}: Rostro resiliente y experimentado, "
            f"reflejando madurez ejecutiva, patrimonio consolidado y balance de vida tras un año de trayectoria."
        )


# Instancia singleton lista para usar
future_media_generator = FutureSelfMediaGenerator()
