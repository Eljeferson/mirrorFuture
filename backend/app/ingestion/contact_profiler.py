"""
Mirror Future - Real Production Contact Profiler (100% Zero Mocks).
Calcula métricas matemáticas y estadísticas exactas a partir de historiales
reales de WhatsApp parseados:
1. Mediana real de tiempo de respuesta en minutos (real_median_reply_minutes).
2. Porcentaje de inicio de conversación (user_initiates_pct).
3. Distribución horaria real de actividad de 0 a 23 hrs (active_hours_distribution).
4. Top 25 palabras y modismos reales característicos.
5. Top 10 emojis reales más utilizados.
Estructura conforme al esquema DDL exacto de Supabase real_contacts (sin columnas inexistentes).
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import emoji
import numpy as np
import pandas as pd


# Lista exhaustiva de Stopwords en Español e Inglés para filtrado léxico puro
STOPWORDS_ES_EN = {
    # Español: Artículos, pronombres, preposiciones, conjunciones
    "de", "la", "que", "el", "en", "y", "a", "los", "se", "del", "las", "por", "un", "para", "con", "no", "una",
    "su", "al", "lo", "como", "más", "pero", "sus", "le", "ya", "o", "este", "sí", "porque", "esta", "entre",
    "cuando", "muy", "sin", "sobre", "también", "me", "hasta", "hay", "donde", "quien", "desde", "todo", "nos",
    "durante", "todos", "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mí",
    "antes", "algunos", "qué", "unos", "yo", "otro", "otras", "otra", "él", "tanto", "esa", "estos", "mucho",
    "quienes", "nada", "muchos", "cual", "poco", "ella", "estar", "estas", "algunas", "algo", "nosotros", "mi",
    "mis", "tú", "te", "ti", "tu", "tus", "ellas", "nosotras", "vosotros", "vosotras", "usted", "ustedes",
    "es", "son", "era", "eran", "fue", "fueron", "he", "has", "ha", "hemos", "han", "ser", "haber", "hacer",
    "voy", "va", "vamos", "van", "fui", "tan", "tampoco", "aquí", "ahí", "allí", "acá", "allá", "hoy", "ayer",
    "mañana", "ahora", "después", "luego", "siempre", "nunca", "jamás", "bien", "mal", "casi", "solo", "sólo",
    "dónde", "cuándo", "cómo", "cuanto", "cuánto", "sino", "mas", "aunque", "sea", "sean", "bueno", "dale",
    "hola", "chao", "adiós", "si", "sii", "siii", "ok", "oki", "okey", "va", "vaa", "ah", "oh", "eh", "uh",
    # Modismos de risa y muletillas de chat
    "jaja", "jajaja", "jajajaja", "jajajajaja", "jeje", "jejeje", "jiji", "xd", "xdxd",
    # Multimedia WhatsApp markers
    "multimedia", "omitido", "omitida", "imagen", "audio", "video", "sticker", "adjunto", "archivo",
    "omitted", "media", "attached",
    # English Stopwords
    "the", "and", "to", "of", "in", "is", "it", "you", "that", "he", "was", "for", "on", "are", "as", "with",
    "his", "they", "i", "at", "be", "this", "have", "from", "or", "one", "had", "by", "word", "but", "not",
    "what", "all", "were", "we", "when", "your", "can", "said", "there", "use", "an", "each", "which", "she",
    "do", "how", "their", "if", "will", "up", "other", "about", "out", "many", "then", "them", "these", "so"
}


class ContactProfiler:
    """
    Statistical relational profile engine for Mirror Future.
    Calcula sin heurísticas ficticias las distribuciones reales del contacto.
    """

    def __init__(self, session_inactivity_hours: float = 6.0, max_reply_window_hours: float = 24.0):
        """
        :param session_inactivity_hours: Horas de silencio para considerar el inicio de un nuevo hilo/episodio.
        :param max_reply_window_hours: Límite superior para calcular latencia de réplica activa.
        """
        self.session_inactivity_hours = session_inactivity_hours
        self.max_reply_window_hours = max_reply_window_hours

    def calculate_reply_latencies(self, df: pd.DataFrame) -> Tuple[float, float, List[float]]:
        """
        Calcula la latencia real de respuesta del contacto ante los mensajes del usuario.
        Retorna (mediana_contacto_minutos, mediana_usuario_minutos, lista_minutos_contacto).
        """
        if df.empty or len(df) < 2:
            return 0.0, 0.0, []

        df_sorted = df.sort_values("timestamp").reset_index(drop=True)
        contact_latencies: List[float] = []
        user_latencies: List[float] = []

        max_delta_seconds = self.max_reply_window_hours * 3600.0

        for i in range(1, len(df_sorted)):
            prev_row = df_sorted.iloc[i - 1]
            curr_row = df_sorted.iloc[i]

            # Transición de emisor
            if prev_row["is_user"] != curr_row["is_user"]:
                delta_sec = (curr_row["timestamp"] - prev_row["timestamp"]).total_seconds()
                if 0 < delta_sec <= max_delta_seconds:
                    delta_min = delta_sec / 60.0
                    if curr_row["is_user"]:
                        user_latencies.append(delta_min)
                    else:
                        contact_latencies.append(delta_min)

        median_contact = float(np.median(contact_latencies)) if contact_latencies else 0.0
        median_user = float(np.median(user_latencies)) if user_latencies else 0.0

        return round(median_contact, 2), round(median_user, 2), contact_latencies

    def calculate_initiation_percentage(self, df: pd.DataFrame) -> Tuple[float, int, int]:
        """
        Calcula el porcentaje exacto de inicios de conversación por parte del usuario.
        Un inicio ocurre al principio del chat y tras una pausa >= session_inactivity_hours.
        Retorna (user_initiates_pct, total_sesiones, sesiones_iniciadas_usuario).
        """
        if df.empty:
            return 0.0, 0, 0

        df_sorted = df.sort_values("timestamp").reset_index(drop=True)
        inactivity_threshold_sec = self.session_inactivity_hours * 3600.0

        total_sessions = 0
        user_sessions = 0

        # Primer mensaje de todo el historial
        total_sessions += 1
        if df_sorted.iloc[0]["is_user"]:
            user_sessions += 1

        # Detección de silencios prolongados
        for i in range(1, len(df_sorted)):
            prev_time = df_sorted.iloc[i - 1]["timestamp"]
            curr_time = df_sorted.iloc[i]["timestamp"]
            gap_sec = (curr_time - prev_time).total_seconds()

            if gap_sec >= inactivity_threshold_sec:
                total_sessions += 1
                if df_sorted.iloc[i]["is_user"]:
                    user_sessions += 1

        pct = (user_sessions / total_sessions) * 100.0 if total_sessions > 0 else 0.0
        return round(pct, 2), total_sessions, user_sessions

    @staticmethod
    def calculate_active_hours_distribution(df: pd.DataFrame, for_contact_only: bool = True) -> Dict[str, int]:
        """
        Calcula la distribución horaria real de actividad de 0 a 23 horas.
        Garantiza que todas las horas del día (0-23) estén representadas como claves.
        """
        distribution: Dict[str, int] = {str(h): 0 for h in range(24)}

        if df.empty:
            return distribution

        target_df = df[~df["is_user"]] if for_contact_only else df
        if target_df.empty:
            return distribution

        hours_series = target_df["timestamp"].dt.hour.value_counts()
        for hour, count in hours_series.items():
            distribution[str(hour)] = int(count)

        return distribution

    @staticmethod
    def extract_top_emojis(df: pd.DataFrame, top_n: int = 10, for_contact_only: bool = True) -> List[Dict[str, Any]]:
        """
        Extrae y cuenta los top N emojis reales usados por la persona analizada.
        Maneja con precisión secuencias Unicode y modificadores.
        """
        target_df = df[~df["is_user"]] if for_contact_only else df
        if target_df.empty:
            return []

        emoji_counter: Counter = Counter()

        for text in target_df["text"].dropna():
            emojis_in_text = emoji.emoji_list(str(text))
            for item in emojis_in_text:
                emoji_counter[item["emoji"]] += 1

        total_emojis = sum(emoji_counter.values())
        results: List[Dict[str, Any]] = []

        for em, cnt in emoji_counter.most_common(top_n):
            results.append({
                "emoji": em,
                "count": cnt,
                "percentage": round((cnt / total_emojis) * 100.0, 2) if total_emojis > 0 else 0.0
            })

        return results

    @staticmethod
    def extract_top_words_and_idioms(
        df: pd.DataFrame,
        top_n: int = 25,
        for_contact_only: bool = True
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Extrae las top 25 palabras y los top 10 modismos (bigramas) reales más representativos del contacto.
        Retorna (top_words_list, top_idioms_list).
        """
        target_df = df[~df["is_user"]] if for_contact_only else df
        if target_df.empty:
            return [], []

        word_counter: Counter = Counter()
        bigram_counter: Counter = Counter()

        for text in target_df["text"].dropna():
            clean = str(text).lower()
            clean = re.sub(r"https?://\S+", "", clean)
            clean = re.sub(r"[^\w\sáéíóúüñÁÉÍÓÚÜÑ]", " ", clean)

            tokens = [w.strip() for w in clean.split() if len(w.strip()) >= 3]
            meaningful_tokens = [w for w in tokens if w not in STOPWORDS_ES_EN]

            for token in meaningful_tokens:
                word_counter[token] += 1

            for i in range(len(meaningful_tokens) - 1):
                bg = f"{meaningful_tokens[i]} {meaningful_tokens[i+1]}"
                bigram_counter[bg] += 1

        total_words = sum(word_counter.values())
        words_results: List[Dict[str, Any]] = []

        for word, cnt in word_counter.most_common(top_n):
            words_results.append({
                "word": word,
                "count": cnt,
                "percentage": round((cnt / total_words) * 100.0, 2) if total_words > 0 else 0.0
            })

        idioms_results: List[Dict[str, Any]] = []
        total_idioms = sum(bigram_counter.values())
        for bg, cnt in bigram_counter.most_common(10):
            idioms_results.append({
                "idiom": bg,
                "count": cnt,
                "percentage": round((cnt / total_idioms) * 100.0, 2) if total_idioms > 0 else 0.0
            })

        return words_results, idioms_results

    @staticmethod
    def analyze_syntax_and_punctuation(df: pd.DataFrame) -> Tuple[str, str]:
        """
        Analiza el estilo sintáctico y los rasgos de puntuación reales del contacto.
        """
        contact_df = df[~df["is_user"]]
        if contact_df.empty:
            return "informal", ""

        texts = contact_df["text"].dropna().tolist()
        total_texts = len(texts)
        if total_texts == 0:
            return "informal", ""

        avg_words = float(np.mean([len(t.split()) for t in texts]))

        # Métricas de signos de puntuación
        ellipsis_count = sum(1 for t in texts if "..." in t or "…" in t)
        exclamation_count = sum(1 for t in texts if "!" in t or "¡" in t)
        question_count = sum(1 for t in texts if "?" in t or "¿" in t)
        all_caps_count = sum(1 for t in texts if len(t) > 4 and t.isupper())

        # Estilo sintáctico
        if avg_words <= 3.5:
            syntax_style = "monosilábico_conciso"
        elif avg_words >= 15.0:
            syntax_style = "elocuente_detallado"
        else:
            syntax_style = "coloquial_fluido"

        traits = []
        if ellipsis_count / total_texts > 0.15:
            traits.append("uso frecuente de puntos suspensivos (...)")
        if exclamation_count / total_texts > 0.20:
            traits.append("expresividad enfática con signos de admiración (!)")
        if question_count / total_texts > 0.25:
            traits.append("tendencia indagatoria/preguntas directas")
        if all_caps_count / total_texts > 0.05:
            traits.append("uso de mayúsculas sostenidas para énfasis")

        punctuation_traits = "; ".join(traits) if traits else "puntuación estándar"
        return syntax_style, punctuation_traits

    def build_full_profile(
        self,
        df: pd.DataFrame,
        contact_name: str,
        user_name: str = "Tú",
        relationship_type: str = "FRIEND",
        closeness_level: float = 0.5
    ) -> Dict[str, Any]:
        """
        Genera el objeto integral de perfil real del contacto listo para inserción o .upsert()
        en la tabla `real_contacts` de Supabase.
        
        REGLA DE PRODUCCIÓN ESTRICTA:
        En la raíz del diccionario retornado quedan ÚNICAMENTE las 9 columnas exactas de `real_contacts`:
          - contact_name
          - relationship_type
          - total_messages_analyzed
          - real_median_reply_minutes
          - user_initiates_pct
          - active_hours_distribution
          - real_lexical_profile (JSONB que contiene todas las métricas léxicas y de estilo)
          - extracted_psych_summary
          - last_interaction_at
        """
        median_contact_reply, median_user_reply, _ = self.calculate_reply_latencies(df)
        user_initiates_pct, total_sessions, user_sessions = self.calculate_initiation_percentage(df)
        active_hours = self.calculate_active_hours_distribution(df, for_contact_only=True)
        top_words, top_idioms = self.extract_top_words_and_idioms(df, top_n=25, for_contact_only=True)
        top_emojis = self.extract_top_emojis(df, top_n=10, for_contact_only=True)
        syntax_style, punctuation_traits = self.analyze_syntax_and_punctuation(df)

        contact_df = df[~df["is_user"]]
        user_df = df[df["is_user"]]

        first_ts = df["timestamp"].min() if not df.empty else None
        last_ts = df["timestamp"].max() if not df.empty else None

        # Normalizar relación a 'FAMILY', 'WORK', 'FRIEND', 'ROMANTIC' según DDL de Supabase
        rel_upper = relationship_type.upper()
        if rel_upper in {"FAMILY", "WORK", "FRIEND", "ROMANTIC"}:
            normalized_rel = rel_upper
        else:
            rel_map = {
                "pareja": "ROMANTIC", "novio": "ROMANTIC", "novia": "ROMANTIC", "esposo": "ROMANTIC", "esposa": "ROMANTIC",
                "amigo": "FRIEND", "amiga": "FRIEND", "otro": "FRIEND", "friend": "FRIEND",
                "colega": "WORK", "jefe": "WORK", "director_tesis": "WORK", "director": "WORK", "asesor": "WORK", "work": "WORK",
                "familiar": "FAMILY", "familia": "FAMILY", "mama": "FAMILY", "mamá": "FAMILY", "papa": "FAMILY", "papá": "FAMILY", "family": "FAMILY"
            }
            normalized_rel = rel_map.get(relationship_type.lower(), "FRIEND")

        avg_msg_len = float(np.mean([len(t.split()) for t in contact_df["text"].dropna()])) if not contact_df.empty else 0.0

        # Objeto integral real_lexical_profile (JSONB)
        real_lexical_profile = {
            "top_words": top_words,
            "top_emojis": top_emojis,
            "frequent_words": [w["word"] for w in top_words],
            "frequent_emojis": [e["emoji"] for e in top_emojis],
            "frequent_idioms": top_idioms,
            "user_median_reply_minutes": median_user_reply,
            "closeness_level": closeness_level,
            "contact_messages_count": len(contact_df),
            "user_messages_count": len(user_df),
            "total_conversation_sessions": total_sessions,
            "user_initiated_sessions": user_sessions,
            "syntax_style": syntax_style,
            "punctuation_traits": punctuation_traits,
            "first_interaction": first_ts.isoformat() if first_ts is not None else None,
            "last_interaction": last_ts.isoformat() if last_ts is not None else None,
            "median_response_minutes": median_contact_reply,
            "avg_words_per_message": round(avg_msg_len, 2),
            "tone": "expresivo_empático" if syntax_style != "monosilábico_conciso" else "conciso_directo"
        }

        # Retorno estricto: ÚNICAMENTE las 9 columnas exactas de la tabla real_contacts
        return {
            "contact_name": contact_name,
            "relationship_type": normalized_rel,
            "total_messages_analyzed": len(df),
            "real_median_reply_minutes": median_contact_reply,
            "user_initiates_pct": user_initiates_pct,
            "active_hours_distribution": active_hours,
            "real_lexical_profile": real_lexical_profile,
            "extracted_psych_summary": None,
            "last_interaction_at": last_ts.isoformat() if last_ts is not None else None,
        }
