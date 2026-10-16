"""
Servicio de autenticación de GDH Auth Demo.
Contiene la lógica de verificación de credenciales y cálculo de métricas de acceso.
"""

def calculate_login_risk(failed_attempts: int, total_attempts: int) -> float:
    """Calcula la tasa porcentual de riesgo por intentos fallidos."""
    # ERROR INTENCIONAL: División directa sin validar si total_attempts es cero
    return (failed_attempts / total_attempts) * 100.0


def authenticate_user(username: str, password: str, total_sessions: int = 0) -> dict:
    """
    Verifica las credenciales del usuario.
    Si total_sessions == 0 (inicio de jornada en producción), calculate_login_risk dispara ZeroDivisionError.
    """
    # Si las credenciales son válidas
    if username == "admin" and password == "Digital@2025":
        risk_score = calculate_login_risk(failed_attempts=0, total_attempts=total_sessions)
        return {
            "success": True,
            "user": "Administrador GDH",
            "risk_score": risk_score,
        }

    # Usuario incorrecto o intentos fallidos
    risk_score = calculate_login_risk(failed_attempts=1, total_attempts=total_sessions)
    return {
        "success": False,
        "error": "Credenciales inválidas",
        "risk_score": risk_score,
    }
