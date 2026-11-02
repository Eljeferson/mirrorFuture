"""
Mirror Future - Real Production WhatsApp Parser (100% Zero Mocks).
Parsea y estructura exports reales de WhatsApp (.txt o .zip) para Android e iOS,
soportando formatos en español e inglés, 12h (AM/PM, a. m./p. m.) y 24h,
normalización de caracteres Unicode ocultos (LTR/RTL/NBSP) y mensajes multilínea.
"""

from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import dateutil.parser
import pandas as pd


# Expresiones regulares para detección de inicio de mensaje
# 1. Android: "15/09/2023, 14:32 - Contacto: Mensaje" o "15/9/23, 2:32 p. m. - Contacto: Mensaje"
RE_ANDROID_MSG = re.compile(
    r"^(\d{1,4}[/\.-]\d{1,2}[/\.-]\d{1,4},\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s+(?:[aApP]\.?\s*[mM]\.?|[aApP][mM]))?)\s+-\s+([^:]+?):\s+(.*)$",
    re.IGNORECASE
)

# 2. Android Notificación del Sistema (sin remitente con dos puntos)
RE_ANDROID_SYS = re.compile(
    r"^(\d{1,4}[/\.-]\d{1,2}[/\.-]\d{1,4},\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s+(?:[aApP]\.?\s*[mM]\.?|[aApP][mM]))?)\s+-\s+(.*)$",
    re.IGNORECASE
)

# 3. iOS: "[15/09/2023, 14:32:15] Contacto: Mensaje" o "[15/9/23, 2:32:15 p. m.] Contacto: Mensaje"
RE_IOS_MSG = re.compile(
    r"^\[(\d{1,4}[/\.-]\d{1,2}[/\.-]\d{1,4},\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s+(?:[aApP]\.?\s*[mM]\.?|[aApP][mM]))?)\]\s+([^:]+?):\s+(.*)$",
    re.IGNORECASE
)

# 4. iOS Notificación del Sistema
RE_IOS_SYS = re.compile(
    r"^\[(\d{1,4}[/\.-]\d{1,2}[/\.-]\d{1,4},\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s+(?:[aApP]\.?\s*[mM]\.?|[aApP][mM]))?)\]\s+(.*)$",
    re.IGNORECASE
)

# Detección de mensajes de sistema / multimedia omitida
RE_MEDIA_OMITTED = re.compile(
    r"(<media omitted>|<multimedia omitido>|imagen omitida|audio omitido|sticker omitido|video omitido|"
    r"archivo adjunto omitido|gif omitido|contact card omitted|tarjeta de contacto omitida|"
    r"<attached:.*?>|archivo adjunto:)",
    re.IGNORECASE
)

SYSTEM_MESSAGE_PATTERNS = [
    "cifrados de extremo a extremo",
    "end-to-end encrypted",
    "cambió tu código de seguridad",
    "security code changed",
    "creó este grupo",
    "created this group",
    "cambió el ícono del grupo",
    "cambió la descripción del grupo",
    "se unió usando el enlace",
    "salió del grupo",
    "left the group",
    "eliminó a",
    "removed",
    "llamada perdida",
    "missed voice call",
    "missed video call",
    "videollamada perdida"
]

# Unicode ocultos comunes en WhatsApp
UNICODE_JUNK_CHARS = [
    "\u200e",  # Left-to-Right Mark
    "\u200f",  # Right-to-Left Mark
    "\u202a",  # Left-to-Right Embedding
    "\u202b",  # Right-to-Left Embedding
    "\u202c",  # Pop Directional Formatting
    "\u2066",  # Left-to-Right Isolate
    "\u2067",  # Right-to-Left Isolate
    "\u2068",  # First Strong Isolate
    "\u2069",  # Pop Directional Isolate
]


@dataclass
class ParsedMessage:
    """Representación unitaria de un mensaje real de WhatsApp."""
    timestamp: datetime
    sender: str
    text: str
    is_user: bool
    is_media: bool = False
    raw_datetime_str: str = ""


class WhatsAppParser:
    """
    Parser de alta fidelidad para exportaciones reales de WhatsApp (ZIP / TXT).
    Detecta automáticamente plataforma (Android vs iOS), estructura multilínea,
    idioma de fechas y participantes.
    """

    def __init__(
        self,
        user_name: Optional[str] = None,
        contact_name: Optional[str] = None,
        filename: Optional[str] = None
    ):
        """
        :param user_name: Name or alias of the Mirror Future primary user ('You', 'Tú', etc.)
        :param contact_name: Nombre del contacto analizado (si no se indica, se infiere)
        :param filename: Nombre original del archivo exportado para inferencia de metadatos
        """
        self.user_name = user_name
        self.contact_name = contact_name
        self.filename = filename

    @staticmethod
    def clean_unicode(text: str) -> str:
        """Remueve caracteres de dirección invisibles y normaliza espacios duros."""
        for ch in UNICODE_JUNK_CHARS:
            text = text.replace(ch, "")
        # Normalizar espacios no rompibles
        text = text.replace("\u202f", " ").replace("\xa0", " ")
        return text.strip()

    @staticmethod
    def extract_contact_name_from_filename(filename: str) -> Optional[str]:
        """Extrae el nombre del contacto del nombre de archivo exportado."""
        clean_name = Path(filename).name
        patterns = [
            r"^(?:Chat de WhatsApp con|WhatsApp Chat with|Chat de WhatsApp -|WhatsApp Chat -)\s*(.+?)(?:\.txt|\.zip)?$",
            r"^(.+?)(?:\s*-\s*WhatsApp Chat)?(?:\.txt|\.zip)?$"
        ]
        for pat in patterns:
            m = re.match(pat, clean_name, re.IGNORECASE)
            if m:
                extracted = m.group(1).strip()
                # Filtrar nombres genéricos
                if extracted.lower() not in {"_chat", "chat", "whatsapp", "export"}:
                    return extracted
        return None

    def read_source(
        self,
        source: Union[str, Path, bytes, io.BytesIO],
        filename: Optional[str] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Lee el contenido de texto desde archivo .txt, archivo .zip o buffer en memoria.
        Retorna (texto_plano, nombre_contacto_sugerido).
        """
        effective_filename = filename or self.filename
        suggested_contact = self.extract_contact_name_from_filename(effective_filename) if effective_filename else None

        if isinstance(source, (str, Path)):
            path = Path(source)
            if not suggested_contact:
                suggested_contact = self.extract_contact_name_from_filename(path.name)
            if path.suffix.lower() == ".zip":
                with open(path, "rb") as f:
                    return self._read_from_zip(f.read(), suggested_contact)
            else:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    return f.read(), suggested_contact

        elif isinstance(source, (bytes, io.BytesIO)):
            raw_bytes = source.getvalue() if isinstance(source, io.BytesIO) else source
            if zipfile.is_zipfile(io.BytesIO(raw_bytes)):
                return self._read_from_zip(raw_bytes, suggested_contact)
            else:
                return raw_bytes.decode("utf-8", errors="replace"), suggested_contact

        raise ValueError("Fuente no soportada. Debe ser ruta de archivo (.txt/.zip) o bytes.")

    def _read_from_zip(self, zip_bytes: bytes, initial_suggestion: Optional[str]) -> Tuple[str, Optional[str]]:
        """Extrae el archivo de texto principal dentro del zip de WhatsApp."""
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            txt_files = [f for f in z.namelist() if f.lower().endswith(".txt")]
            if not txt_files:
                raise ValueError("El archivo .zip no contiene ningún archivo de chat .txt")

            # Priorizar _chat.txt (iOS) o archivos que comiencen con WhatsApp/Chat
            main_txt = txt_files[0]
            for f in txt_files:
                if f.lower() == "_chat.txt" or "whatsapp" in f.lower():
                    main_txt = f
                    break

            suggested = initial_suggestion or self.extract_contact_name_from_filename(main_txt)
            raw_txt = z.read(main_txt).decode("utf-8", errors="replace")
            return raw_txt, suggested

    @staticmethod
    def _normalize_datetime_str(dt_raw: str) -> str:
        """
        Normaliza representaciones de hora en español a inglés para dateutil:
        'a. m.' / 'a.m.' -> 'AM', 'p. m.' / 'p.m.' -> 'PM', etc.
        IMPORTANTE: No usar clean.replace('.', '') global para no destruir fechas con formato dd.mm.yyyy.
        Elimina los puntos únicamente en a.m. / p.m.
        """
        clean = dt_raw.strip()
        clean = re.sub(r"\ba\.\s*m\.?", "AM", clean, flags=re.IGNORECASE)
        clean = re.sub(r"\bp\.\s*m\.?", "PM", clean, flags=re.IGNORECASE)
        clean = re.sub(r"\bam\b", "AM", clean, flags=re.IGNORECASE)
        clean = re.sub(r"\bpm\b", "PM", clean, flags=re.IGNORECASE)
        return clean

    @classmethod
    def _determine_dayfirst(cls, raw_lines: List[str]) -> bool:
        """Determina estadísticamente si las fechas son día primero (dd/mm/yy)."""
        for line in raw_lines[:200]:
            clean_l = cls.clean_unicode(line)
            m = re.match(r"^\[?(\d{1,4})[/\.-](\d{1,2})[/\.-](\d{1,4})", clean_l)
            if m:
                p1, p2, _ = int(m.group(1)), int(m.group(2)), int(m.group(3))
                if p1 > 12 and p2 <= 12:
                    return True  # 15/09 -> Día primero
                if p2 > 12 and p1 <= 12:
                    return False  # 09/15 -> Mes primero
        return True  # Estándar predominante en WhatsApp en español

    def parse_raw_text(self, text: str, filename_hint: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Parsea el texto crudo línea por línea, manejando multilínea y metadatos.
        """
        lines = text.splitlines()
        if not lines:
            return []

        dayfirst = self._determine_dayfirst(lines)
        messages: List[Dict[str, Any]] = []
        current_msg: Optional[Dict[str, Any]] = None

        for raw_line in lines:
            line = self.clean_unicode(raw_line)
            if not line:
                if current_msg:
                    current_msg["text"] += "\n"
                continue

            # Intentar coincidencia con mensaje Android o iOS
            match_ios = RE_IOS_MSG.match(line)
            match_android = RE_ANDROID_MSG.match(line)

            if match_ios or match_android:
                match = match_ios or match_android
                platform = "ios" if match_ios else "android"
                raw_dt, sender, content = match.group(1), match.group(2).strip(), match.group(3).strip()

                # Verificar si es notificación de sistema disfrazada
                if any(pat in content.lower() for pat in SYSTEM_MESSAGE_PATTERNS):
                    if current_msg:
                        messages.append(current_msg)
                        current_msg = None
                    continue

                try:
                    norm_dt = self._normalize_datetime_str(raw_dt)
                    parsed_dt = dateutil.parser.parse(norm_dt, dayfirst=dayfirst)
                except Exception:
                    # En caso de fallo de parsing de fecha, se concatena como texto
                    if current_msg:
                        current_msg["text"] += "\n" + line
                    continue

                if current_msg:
                    messages.append(current_msg)

                is_media = bool(RE_MEDIA_OMITTED.search(content))
                current_msg = {
                    "timestamp": parsed_dt,
                    "sender": sender,
                    "text": content,
                    "is_media": is_media,
                    "platform": platform,
                    "raw_dt": raw_dt
                }
            else:
                # Verificar si es una línea de notificación del sistema
                match_sys_ios = RE_IOS_SYS.match(line)
                match_sys_android = RE_ANDROID_SYS.match(line)
                if match_sys_ios or match_sys_android:
                    if current_msg:
                        messages.append(current_msg)
                        current_msg = None
                    continue

                # Continuación de mensaje multilínea
                if current_msg:
                    current_msg["text"] += "\n" + line

        if current_msg:
            messages.append(current_msg)

        return messages

    def parse(
        self,
        source: Union[str, Path, bytes, io.BytesIO],
        filename: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Ejecuta el pipeline completo de parseo de chat real.
        Retorna (DataFrame de mensajes, Diccionario de metadatos con participantes identificados).
        """
        effective_filename = filename or self.filename
        raw_text, suggested_contact = self.read_source(source, filename=effective_filename)
        raw_messages = self.parse_raw_text(raw_text, filename_hint=suggested_contact)

        if not raw_messages:
            empty_df = pd.DataFrame(columns=["timestamp", "sender", "text", "is_user", "is_media", "char_count", "word_count"])
            return empty_df, {
                "contact_name": self.contact_name or suggested_contact or "Desconocido",
                "user_name": self.user_name or "Tú",
                "total_messages": 0
            }

        df = pd.DataFrame(raw_messages)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

        # Resolver participantes reales (Tú vs Contacto)
        senders = df["sender"].value_counts().index.tolist()

        detected_user = self.user_name
        detected_contact = self.contact_name or suggested_contact

        user_aliases = {"tú", "tu", "you", "yo", "me"}

        # Si hay 2 interlocutores (chat 1 a 1 típico)
        if len(senders) == 2:
            s1, s2 = senders[0], senders[1]
            if not detected_user and not detected_contact:
                if s1.lower() in user_aliases:
                    detected_user, detected_contact = s1, s2
                elif s2.lower() in user_aliases:
                    detected_user, detected_contact = s2, s1
                else:
                    # Si uno coincide con suggested_contact, el otro es el usuario
                    if suggested_contact and suggested_contact.lower() in s1.lower():
                        detected_contact, detected_user = s1, s2
                    elif suggested_contact and suggested_contact.lower() in s2.lower():
                        detected_contact, detected_user = s2, s1
                    else:
                        # Asignar usuario al más frecuente o al segundo según convención
                        detected_contact, detected_user = s1, s2
            elif detected_contact and not detected_user:
                detected_user = s2 if s1 == detected_contact else s1
            elif detected_user and not detected_contact:
                detected_contact = s2 if s1 == detected_user else s1
        elif len(senders) == 1:
            detected_contact = senders[0]
            detected_user = self.user_name or "Tú"
        else:
            # Multi-usuario o grupo
            if not detected_contact:
                detected_contact = suggested_contact or senders[0]
            if not detected_user:
                for s in senders:
                    if s.lower() in user_aliases:
                        detected_user = s
                        break
                if not detected_user:
                    detected_user = "Tú"

        # Marcar bandera booleana is_user
        df["is_user"] = df["sender"].apply(lambda s: bool(s == detected_user or s.lower() in user_aliases))
        df["char_count"] = df["text"].apply(lambda t: len(t))
        df["word_count"] = df["text"].apply(lambda t: len(t.split()))

        meta = {
            "contact_name": detected_contact,
            "user_name": detected_user,
            "all_senders": senders,
            "total_messages": len(df),
            "user_messages_count": int(df["is_user"].sum()),
            "contact_messages_count": int((~df["is_user"]).sum()),
            "first_message": df["timestamp"].min().isoformat() if not df.empty else None,
            "last_message": df["timestamp"].max().isoformat() if not df.empty else None,
        }

        return df, meta
