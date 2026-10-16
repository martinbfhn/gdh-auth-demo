import traceback
import logging
from typing import Optional, Dict, Any
import httpx
from app.core.config import settings

logger = logging.getLogger("gdh.nexo_client")

async def report_exception_to_nexo(
    exc: Exception,
    endpoint: str = "/login",
    action: str = "submit_login",
    user_identifier: Optional[str] = None,
    context_data: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Despacha un evento de excepción a NEXO GD vía API REST."""
    url = f"{settings.NEXO_URL.rstrip('/')}/api/v1/events/error"
    payload = {
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "stack_trace": "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        "endpoint": endpoint,
        "action": action,
        "user": user_identifier,
        "terminal_id": "GS-SPS-AUTH-01",
        "module": "Autenticación",
        "environment": settings.ENVIRONMENT,
        "server_host": settings.SERVER_HOST,
        "container_name": settings.CONTAINER_NAME,
        "context": context_data or {},
    }

    headers = {
        "X-NEXO-API-KEY": settings.NEXO_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"[Nexo SDK] Incidente reportado exitosamente: {data.get('incident_code')}")
                return data
            else:
                logger.warning(f"[Nexo SDK] Error enviando a Nexo ({resp.status_code}): {resp.text[:200]}")
                return None
    except Exception as ex:
        logger.warning(f"[Nexo SDK] No se pudo conectar con NEXO GD ({url}): {ex}")
        return None
