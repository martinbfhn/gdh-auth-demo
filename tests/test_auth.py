import pytest
from app.services.auth import calculate_login_risk, authenticate_user

def test_calculate_risk_normal():
    # En condiciones normales con sesiones previas
    score = calculate_login_risk(failed_attempts=2, total_attempts=10)
    assert score == 20.0

def test_calculate_risk_zero_sessions():
    # Al arrancar el contenedor sin sesiones registradas debe retornar 0.0 sin fallar
    score = calculate_login_risk(failed_attempts=0, total_attempts=0)
    assert score == 0.0

def test_authenticate_user_success():
    res = authenticate_user("admin", "Digital@2025", total_sessions=5)
    assert res["success"] is True
