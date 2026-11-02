"""
Actuator: Production Asynchronous Client for Meta WhatsApp Cloud API.
Dispatches executive notifications, burnout risk reports, and schedule prescriptions
directly to WhatsApp via the official Meta Graph API (v21.0).
"""

import re
import logging
from typing import Dict, Any, Optional, List
import httpx
from app.config import get_settings
from app.models.schemas import WhatsAppSendResult

logger = logging.getLogger("MirrorFuture.WhatsAppSender")


class WhatsAppCloudClient:
    """
    Client for the official Meta WhatsApp Cloud API.
    Supports rich text messages, interactive quick-action buttons, and document/calendar distribution.
    """

    def __init__(
        self,
        api_token: Optional[str] = None,
        phone_number_id: Optional[str] = None,
        api_version: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        settings = get_settings()
        self.api_token = api_token or settings.whatsapp_api_token
        self.phone_number_id = phone_number_id or settings.whatsapp_phone_number_id
        self.api_version = api_version or settings.whatsapp_api_version
        self.base_url = (base_url or settings.whatsapp_base_url).rstrip("/")

    def _sanitize_phone(self, phone: str) -> str:
        """
        Sanitizes and validates international E.164 phone format (digits only).
        E.g.: '+57 300 123-4567' -> '573001234567'
        """
        cleaned = re.sub(r"[^\d]", "", phone)
        if not cleaned:
            raise ValueError(f"Invalid phone number format: '{phone}'")
        return cleaned

    def _get_headers(self) -> Dict[str, str]:
        if not self.api_token:
            logger.warning("Missing WHATSAPP_API_TOKEN in environment configuration.")
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _get_endpoint_url(self) -> str:
        return f"{self.base_url}/{self.api_version}/{self.phone_number_id}/messages"

    async def send_text_message(
        self,
        to_phone: str,
        message_text: str,
        preview_url: bool = True,
    ) -> WhatsAppSendResult:
        """
        Sends a plain text message with newline support and optional link previews.
        """
        sanitized_to = self._sanitize_phone(to_phone)
        url = self._get_endpoint_url()

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": sanitized_to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": message_text
            }
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(url, headers=self._get_headers(), json=payload)
                data = response.json()

                if response.status_code in (200, 201):
                    msg_id = data.get("messages", [{}])[0].get("id")
                    logger.info(f"WhatsApp message dispatched successfully to {sanitized_to}. Message ID: {msg_id}")
                    return WhatsAppSendResult(
                        success=True,
                        status_code=response.status_code,
                        message_id=msg_id,
                        recipient_phone=sanitized_to,
                    )
                else:
                    err_info = data.get("error", {}).get("message", response.text)
                    logger.error(f"WhatsApp Cloud API failure (HTTP {response.status_code}): {err_info}")
                    return WhatsAppSendResult(
                        success=False,
                        status_code=response.status_code,
                        recipient_phone=sanitized_to,
                        error_message=f"Error {response.status_code}: {err_info}"
                    )
            except Exception as exc:
                logger.error(f"WhatsApp dispatch exception: {exc}")
                return WhatsAppSendResult(
                    success=False,
                    status_code=500,
                    recipient_phone=sanitized_to,
                    error_message=str(exc)
                )

    async def send_document_message(
        self,
        to_phone: str,
        document_url: str,
        filename: str = "optimal_schedule_mirror_future.ics",
        caption: Optional[str] = None,
    ) -> WhatsAppSendResult:
        """
        Sends a downloadable document (such as the generated .ics file or a PDF summary).
        """
        sanitized_to = self._sanitize_phone(to_phone)
        url = self._get_endpoint_url()

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": sanitized_to,
            "type": "document",
            "document": {
                "link": document_url,
                "caption": caption or "Optimized Schedule Blocks by Mirror Future",
                "filename": filename
            }
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.post(url, headers=self._get_headers(), json=payload)
                data = response.json()

                if response.status_code in (200, 201):
                    msg_id = data.get("messages", [{}])[0].get("id")
                    return WhatsAppSendResult(
                        success=True,
                        status_code=response.status_code,
                        message_id=msg_id,
                        recipient_phone=sanitized_to,
                    )
                else:
                    err_info = data.get("error", {}).get("message", response.text)
                    return WhatsAppSendResult(
                        success=False,
                        status_code=response.status_code,
                        recipient_phone=sanitized_to,
                        error_message=err_info
                    )
            except Exception as exc:
                return WhatsAppSendResult(
                    success=False,
                    status_code=500,
                    recipient_phone=sanitized_to,
                    error_message=str(exc)
                )

    async def send_interactive_decision_buttons(
        self,
        to_phone: str,
        body_text: str,
        buttons: List[Dict[str, str]],
    ) -> WhatsAppSendResult:
        """
        Sends an interactive message with quick-action reply buttons.
        Example buttons:
        [
          {"id": "BTN_APPLY_CALENDAR", "title": "Sync .ICS"},
          {"id": "BTN_RECALCULATE", "title": "Adjust Hours"}
        ]
        """
        sanitized_to = self._sanitize_phone(to_phone)
        url = self._get_endpoint_url()

        formatted_buttons = []
        for btn in buttons[:3]:  # WhatsApp allows up to 3 interactive reply buttons
            formatted_buttons.append({
                "type": "reply",
                "reply": {
                    "id": btn["id"],
                    "title": btn["title"][:20]  # Maximum 20 characters per button title
                }
            })

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": sanitized_to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {"buttons": formatted_buttons}
            }
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(url, headers=self._get_headers(), json=payload)
                data = response.json()

                if response.status_code in (200, 201):
                    msg_id = data.get("messages", [{}])[0].get("id")
                    return WhatsAppSendResult(
                        success=True,
                        status_code=response.status_code,
                        message_id=msg_id,
                        recipient_phone=sanitized_to,
                    )
                else:
                    err_info = data.get("error", {}).get("message", response.text)
                    return WhatsAppSendResult(
                        success=False,
                        status_code=response.status_code,
                        recipient_phone=sanitized_to,
                        error_message=err_info
                    )
            except Exception as exc:
                return WhatsAppSendResult(
                    success=False,
                    status_code=500,
                    recipient_phone=sanitized_to,
                    error_message=str(exc)
                )


# Default singleton instance
whatsapp_actuator = WhatsAppCloudClient()
