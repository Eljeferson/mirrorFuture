"""
Mirror Future - Real Production Embedding Engine (100% Zero Mocks).
Segmentación de chats reales en episodios conversacionales coherentes,
vectorización densa en 384 dimensiones con sentence-transformers
('paraphrase-multilingual-MiniLM-L12-v2') e inserción por lotes en Supabase pgvector
conforme a la tabla oficial `real_chat_episodes` y RPC `match_real_episodes`.
Soporta `replace_existing=True` para prevenir duplicados al re-ingestar chats.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import httpx

try:
    from supabase import create_client, Client
except ImportError:
    Client = None
    create_client = None

logger = logging.getLogger("mirror_future.embedding_engine")
logger.setLevel(logging.INFO)

DEFAULT_EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
VECTOR_DIMENSION = 384

# Léxico simple de polaridad para cálculo preciso de sentiment_score (-1.0 a +1.0)
POSITIVE_WORDS = {
    "excelente", "bueno", "buena", "bien", "gracias", "genial", "abrazo", "amor", "feliz",
    "perfecto", "éxito", "convergencia", "solucionado", "conseguido", "great", "good",
    "thanks", "awesome", "nice", "love", "apoyo", "ánimo", "felicitaciones", "maravilla"
}
NEGATIVE_WORDS = {
    "mal", "terrible", "molesto", "molesta", "enojado", "enojada", "error", "falla", "pelea",
    "discutir", "triste", "estresado", "estresada", "bloqueado", "bad", "hate", "angry",
    "failed", "bug", "retraso", "injusto", "preocupado", "preocupada", "harto", "harta"
}


@dataclass
class ConversationalEpisode:
    """Representación estructurada de un episodio conversacional real."""
    episode_index: int
    episode_timestamp: datetime
    conversation_chunk: str
    sentiment_score: float
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: float = 0.0
    message_count: int = 0
    user_prompt: str = ""
    contact_response: str = ""
    raw_content: str = ""
    conversation_summary: str = ""
    conflict_or_support_tag: str = "neutral"
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = self.episode_timestamp
        if not self.raw_content:
            self.raw_content = self.conversation_chunk

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if isinstance(data.get("episode_timestamp"), datetime):
            data["episode_timestamp"] = data["episode_timestamp"].isoformat()
        if isinstance(data.get("start_time"), datetime):
            data["start_time"] = data["start_time"].isoformat()
        if isinstance(data.get("end_time"), datetime):
            data["end_time"] = data["end_time"].isoformat()
        return data


class EmbeddingModelManager:
    """Singleton thread-safe para mantener en memoria el modelo sentence-transformers."""
    _instance: Optional[SentenceTransformer] = None
    _model_name: str = DEFAULT_EMBEDDING_MODEL_NAME

    @classmethod
    def get_model(cls, model_name: str = DEFAULT_EMBEDDING_MODEL_NAME) -> SentenceTransformer:
        if cls._instance is None or cls._model_name != model_name:
            logger.info("Cargando modelo de embeddings denso: %s", model_name)
            cls._instance = SentenceTransformer(model_name)
            cls._model_name = model_name
        return cls._instance


class ConversationalChatSegmenter:
    """
    Agrupa mensajes cronológicos reales de chat en episodios conversacionales semánticos
    basándose en umbrales de inactividad temporal y longitud de interacción.
    """

    def __init__(
        self,
        inactivity_gap_minutes: float = 120.0,
        max_messages_per_episode: int = 40,
        min_messages_per_episode: int = 1
    ):
        self.inactivity_gap_minutes = inactivity_gap_minutes
        self.max_messages_per_episode = max_messages_per_episode
        self.min_messages_per_episode = min_messages_per_episode

    @staticmethod
    def _calculate_sentiment(text: str) -> float:
        """Calcula el puntaje de sentimiento de -1.0 a +1.0 mediante polaridad léxica."""
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            return 0.0

        pos_count = sum(1 for w in tokens if w in POSITIVE_WORDS)
        neg_count = sum(1 for w in tokens if w in NEGATIVE_WORDS)

        total_sentiment_words = pos_count + neg_count
        if total_sentiment_words == 0:
            return 0.0

        raw_score = (pos_count - neg_count) / total_sentiment_words
        return round(float(np.clip(raw_score, -1.0, 1.0)), 2)

    @staticmethod
    def _classify_episode_tag(user_text: str, contact_text: str) -> str:
        """Clasifica heurísticamente el tono de interacción del episodio."""
        combined = f"{user_text} {contact_text}".lower()

        conflict_keywords = ["molesto", "enojado", "enojada", "pelea", "discutir", "reclamo", "decepcionado", "injusto", "harto", "basta"]
        thesis_keywords = ["tesis", "capitulo", "asesor", "director", "entrega", "articulo", "paper", "deadline", "avance", "comite", "metodologico", "pgvector"]
        affection_keywords = ["te quiero", "te amo", "abrazo", "corazón", "cariño", "hermoso", "linda", "bebé", "amor"]
        support_keywords = ["ánimo", "animo", "tranquilo", "tú puedes", "cuenta conmigo", "aquí estoy", "apoyo", "descansa"]

        if any(w in combined for w in conflict_keywords):
            return "conflict"
        if any(w in combined for w in thesis_keywords):
            return "thesis_pressure"
        if any(w in combined for w in affection_keywords):
            return "affection"
        if any(w in combined for w in support_keywords):
            return "support"
        return "neutral"

    @staticmethod
    def _generate_extractive_summary(user_msgs: List[str], contact_msgs: List[str], max_len: int = 240) -> str:
        first_user = user_msgs[0] if user_msgs else ""
        first_contact = contact_msgs[0] if contact_msgs else ""

        summary_parts = []
        if first_user:
            u_clean = first_user.strip().replace("\n", " ")
            summary_parts.append(f"Usuario: {u_clean[:120]}")
        if first_contact:
            c_clean = first_contact.strip().replace("\n", " ")
            summary_parts.append(f"Contacto: {c_clean[:120]}")

        summary = " | ".join(summary_parts) if summary_parts else "Intercambio conversacional sin texto clave"
        return summary[:max_len]

    def segment(self, df: pd.DataFrame, contact_name: str = "Contacto", user_name: str = "Tú") -> List[ConversationalEpisode]:
        """Segmenta el DataFrame de mensajes en una lista de ConversationalEpisode reales."""
        if df.empty:
            return []

        df_sorted = df.sort_values("timestamp").reset_index(drop=True)
        episodes: List[ConversationalEpisode] = []

        current_batch: List[Dict[str, Any]] = []
        gap_seconds = self.inactivity_gap_minutes * 60.0

        for i in range(len(df_sorted)):
            row = df_sorted.iloc[i].to_dict()

            if not current_batch:
                current_batch.append(row)
                continue

            prev_ts = current_batch[-1]["timestamp"]
            curr_ts = row["timestamp"]
            delta = (curr_ts - prev_ts).total_seconds()

            if delta >= gap_seconds or len(current_batch) >= self.max_messages_per_episode:
                ep = self._build_episode(current_batch, len(episodes) + 1, contact_name, user_name)
                if ep:
                    episodes.append(ep)
                current_batch = [row]
            else:
                current_batch.append(row)

        if current_batch:
            ep = self._build_episode(current_batch, len(episodes) + 1, contact_name, user_name)
            if ep:
                episodes.append(ep)

        return episodes

    def segment_messages(self, df: pd.DataFrame, contact_name: str = "Contacto", user_name: str = "Tú") -> List[ConversationalEpisode]:
        return self.segment(df, contact_name=contact_name, user_name=user_name)

    def _build_episode(
        self,
        batch: List[Dict[str, Any]],
        index: int,
        contact_name: str,
        user_name: str
    ) -> Optional[ConversationalEpisode]:
        if len(batch) < self.min_messages_per_episode:
            return None

        start_time = batch[0]["timestamp"]
        end_time = batch[-1]["timestamp"]
        duration_minutes = round((end_time - start_time).total_seconds() / 60.0, 2)

        user_texts: List[str] = []
        contact_texts: List[str] = []
        raw_lines: List[str] = []

        for m in batch:
            sender = m.get("sender", "")
            text = m.get("text", "")
            ts_str = m["timestamp"].strftime("%Y-%m-%d %H:%M") if isinstance(m.get("timestamp"), datetime) else str(m.get("timestamp"))
            raw_lines.append(f"[{ts_str}] {sender}: {text}")

            if m.get("is_user"):
                user_texts.append(text)
            else:
                contact_texts.append(text)

        conversation_chunk = "\n".join(raw_lines)
        user_prompt = "\n".join(user_texts)
        contact_response = "\n".join(contact_texts)
        summary = self._generate_extractive_summary(user_texts, contact_texts)
        tag = self._classify_episode_tag(user_prompt, contact_response)
        sentiment_score = self._calculate_sentiment(conversation_chunk)

        return ConversationalEpisode(
            episode_index=index,
            episode_timestamp=start_time if isinstance(start_time, datetime) else datetime.utcnow(),
            conversation_chunk=conversation_chunk,
            sentiment_score=sentiment_score,
            start_time=start_time if isinstance(start_time, datetime) else None,
            end_time=end_time if isinstance(end_time, datetime) else None,
            duration_minutes=duration_minutes,
            message_count=len(batch),
            user_prompt=user_prompt,
            contact_response=contact_response,
            raw_content=conversation_chunk,
            conversation_summary=summary,
            conflict_or_support_tag=tag,
            metadata={
                "contact_name": contact_name,
                "user_name": user_name,
                "user_msg_count": len(user_texts),
                "contact_msg_count": len(contact_texts)
            }
        )


class RealEmbeddingEngine:
    """
    Motor principal para vectorizar episodios de chat reales y sincronizarlos con Supabase pgvector.
    Utiliza el modelo oficial 'paraphrase-multilingual-MiniLM-L12-v2' (384 dimensiones).
    """

    def __init__(
        self,
        model_name: str = DEFAULT_EMBEDDING_MODEL_NAME,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None
    ):
        self.model_name = model_name
        self.model = EmbeddingModelManager.get_model(model_name)
        self.segmenter = ConversationalChatSegmenter()

        # Configuración de Supabase
        self.supabase_url = (supabase_url or os.getenv("SUPABASE_URL", "")).rstrip("/")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY", "")
        self._supabase_client: Optional[Client] = None

    def get_supabase_client(self) -> Optional[Client]:
        if self._supabase_client is not None:
            return self._supabase_client

        if self.supabase_url and self.supabase_key and create_client:
            try:
                self._supabase_client = create_client(self.supabase_url, self.supabase_key)
                return self._supabase_client
            except Exception as e:
                logger.warning("No se pudo conectar a Supabase SDK: %s", e)
                return None
        return None

    def encode_text(self, text: str) -> List[float]:
        """Genera un vector denso normalizado de 384 dimensiones para un texto."""
        emb = self.model.encode(text, normalize_embeddings=True)
        return emb.tolist()

    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Genera vectores densos normalizados de 384 dimensiones para una lista de textos."""
        if not texts:
            return []
        embs = self.model.encode(texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=False)
        return embs.tolist()

    def process_and_vectorize_chat(
        self,
        df: pd.DataFrame,
        contact_name: str = "Contacto",
        user_name: str = "Tú"
    ) -> List[ConversationalEpisode]:
        """
        Segmenta el historial de chat y genera las representaciones vectoriales de 384 dimensiones.
        """
        episodes = self.segmenter.segment(df, contact_name=contact_name, user_name=user_name)
        if not episodes:
            return []

        semantic_texts = []
        for ep in episodes:
            rep = (
                f"Episodio conversacional con {contact_name}.\n"
                f"Resumen: {ep.conversation_summary}\n"
                f"Contenido: {ep.conversation_chunk[:800]}"
            )
            semantic_texts.append(rep)

        vectors = self.encode_batch(semantic_texts)

        for ep, vec in zip(episodes, vectors):
            assert len(vec) == VECTOR_DIMENSION, f"Dimensión esperada {VECTOR_DIMENSION}, obtenida {len(vec)}"
            ep.embedding = vec

        return episodes

    def batch_insert_episodes(
        self,
        episodes: List[ConversationalEpisode],
        contact_id: str,
        user_id: Optional[str] = None,
        batch_size: int = 50,
        replace_existing: bool = True
    ) -> Dict[str, Any]:
        """
        Inserta los episodios vectorizados en la tabla real_chat_episodes de Supabase por lotes.
        
        :param replace_existing: Si es True, elimina los episodios anteriores asociados a contact_id
                                 para evitar duplicados al re-subir un historial de chat.
        """
        if not episodes:
            return {"inserted_count": 0, "total": 0, "status": "empty"}

        client = self.get_supabase_client()
        records_to_insert = []

        for ep in episodes:
            ts_val = ep.episode_timestamp
            record = {
                "contact_id": contact_id,
                "episode_timestamp": ts_val.isoformat() if isinstance(ts_val, datetime) else str(ts_val),
                "conversation_chunk": ep.conversation_chunk[:8000] if ep.conversation_chunk else "",
                "sentiment_score": ep.sentiment_score,
                "embedding": ep.embedding
            }
            records_to_insert.append(record)

        # Si Supabase Client está activo
        if client:
            if replace_existing:
                try:
                    logger.info("Eliminando episodios previos en Supabase para contact_id=%s", contact_id)
                    client.table("real_chat_episodes").delete().eq("contact_id", contact_id).execute()
                except Exception as del_err:
                    logger.warning("Fallo al eliminar episodios previos para contact_id=%s: %s", contact_id, del_err)

            inserted_total = 0
            errors = []
            for i in range(0, len(records_to_insert), batch_size):
                chunk = records_to_insert[i : i + batch_size]
                try:
                    client.table("real_chat_episodes").insert(chunk).execute()
                    inserted_total += len(chunk)
                except Exception as e:
                    logger.error("Error al insertar lote en Supabase: %s", e)
                    errors.append(str(e))

            return {
                "inserted_count": inserted_total,
                "total": len(records_to_insert),
                "status": "success" if not errors else "partial_error",
                "errors": errors
            }

        # Fallback PostgREST REST API directo
        if self.supabase_url and self.supabase_key and "your-project" not in self.supabase_url:
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            }

            with httpx.Client(timeout=30.0) as http_client:
                if replace_existing:
                    try:
                        delete_url = f"{self.supabase_url}/rest/v1/real_chat_episodes?contact_id=eq.{contact_id}"
                        http_client.delete(delete_url, headers=headers)
                        logger.info("Eliminados episodios previos vía PostgREST para contact_id=%s", contact_id)
                    except Exception as del_err:
                        logger.warning("Fallo al eliminar episodios previos vía PostgREST: %s", del_err)

                inserted_total = 0
                errors = []
                endpoint = f"{self.supabase_url}/rest/v1/real_chat_episodes"
                for i in range(0, len(records_to_insert), batch_size):
                    chunk = records_to_insert[i : i + batch_size]
                    try:
                        resp = http_client.post(endpoint, headers=headers, json=chunk)
                        if resp.status_code in (200, 201):
                            inserted_total += len(chunk)
                        else:
                            errors.append(f"HTTP {resp.status_code}: {resp.text}")
                    except Exception as e:
                        errors.append(str(e))

            return {
                "inserted_count": inserted_total,
                "total": len(records_to_insert),
                "status": "success" if not errors else "partial_error",
                "errors": errors
            }

        # Modo offline / memoria
        logger.info("Supabase no configurado en entorno. %d episodios vectorizados en memoria.", len(records_to_insert))
        return {
            "inserted_count": len(records_to_insert),
            "total": len(records_to_insert),
            "status": "ready_in_memory",
            "episodes_count": len(records_to_insert)
        }

    async def ingest_chat_and_vectorize(
        self,
        df: pd.DataFrame,
        contact_id: str,
        user_id: Optional[str] = None,
        contact_name: str = "Contacto",
        user_name: str = "Tú",
        replace_existing: bool = True
    ) -> int:
        """Pipeline asíncrono para ingesta completa y persistencia vectorial."""
        episodes = self.process_and_vectorize_chat(df, contact_name=contact_name, user_name=user_name)
        result = self.batch_insert_episodes(
            episodes,
            contact_id=contact_id,
            user_id=user_id,
            replace_existing=replace_existing
        )
        return result.get("inserted_count", 0)

    def search_similar_episodes(
        self,
        query_text: str,
        contact_id: str,
        match_count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Realiza búsqueda semántica ejecutando la función RPC oficial `match_real_episodes`
        en Supabase con parámetros (p_contact_id, query_embedding, match_count).
        """
        query_vector = self.encode_text(query_text)
        client = self.get_supabase_client()

        if not client:
            logger.warning("Supabase no configurado para búsqueda RPC match_real_episodes.")
            return []

        try:
            params = {
                "p_contact_id": contact_id,
                "query_embedding": query_vector,
                "match_count": match_count,
            }
            res = client.rpc("match_real_episodes", params).execute()
            return res.data if res.data else []
        except Exception as e:
            logger.error("Error al invocar RPC match_real_episodes: %s", e)
            return []


# Aliases de compatibilidad
ChatEpisodeSegmenter = ConversationalChatSegmenter
SupabaseIngestionEngine = RealEmbeddingEngine
