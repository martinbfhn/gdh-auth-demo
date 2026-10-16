import logging
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.services.auth import authenticate_user
from app.core.nexo_client import report_exception_to_nexo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gdh_auth_demo")

app = FastAPI(title=settings.APP_NAME)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        name="login.html",
        context={
            "request": request,
            "server_host": settings.SERVER_HOST,
            "container_name": settings.CONTAINER_NAME,
        },
    )

@app.post("/login", response_class=HTMLResponse)
async def process_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    try:
        # En producción arranca sin sesiones acumuladas (total_sessions=0)
        # Esto dispara ZeroDivisionError intencional en calculate_login_risk
        auth_result = authenticate_user(username, password, total_sessions=0)

        if auth_result["success"]:
            return f"""
            <div class="p-4 mb-4 rounded-xl bg-emerald-950/40 border border-emerald-500/50 text-emerald-300 text-sm flex items-center gap-2">
                <i class="fas fa-circle-check text-emerald-400"></i>
                <span>¡Bienvenido, <strong>{auth_result['user']}</strong>! Acceso concedido (Riesgo: {auth_result['risk_score']}%).</span>
            </div>
            """
        else:
            return f"""
            <div class="p-4 mb-4 rounded-xl bg-rose-950/40 border border-rose-500/50 text-rose-300 text-sm flex items-center gap-2">
                <i class="fas fa-circle-xmark text-rose-400"></i>
                <span>{auth_result.get('error', 'Error de autenticación')}</span>
            </div>
            """

    except Exception as exc:
        logger.error(f"[Auth Error] Excepción en login: {exc}", exc_info=True)
        # Reportar automáticamente la excepción a NEXO GD
        nexo_resp = await report_exception_to_nexo(
            exc=exc,
            endpoint="/login",
            action="submit_login",
            user_identifier=username,
            context_data={"total_sessions": 0},
        )

        code_badge = f"<code class='text-amber-300 font-mono font-bold'>{nexo_resp['incident_code']}</code>" if nexo_resp and nexo_resp.get("incident_code") else ""

        return f"""
        <div class="p-4 mb-4 rounded-xl bg-rose-950/60 border border-rose-500 text-rose-200 text-xs space-y-2">
            <div class="flex items-center gap-2 font-bold text-rose-300 text-sm">
                <i class="fas fa-triangle-exclamation text-rose-400"></i>
                <span>Error 500: Fallo no controlado en producción</span>
            </div>
            <p class="font-mono text-[11px] text-rose-200">{type(exc).__name__}: {str(exc)}</p>
            <div class="pt-2 border-t border-rose-800/60 text-[11px] text-slate-300">
                🚀 Incidente despachado a <strong>NEXO GD</strong>: {code_badge}
                <br>Revisa tu Telegram para autorizar el <strong>AutoFix</strong>.
            </div>
        </div>
        """
