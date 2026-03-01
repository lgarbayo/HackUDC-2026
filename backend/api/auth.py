"""
api/auth.py — EL GUARDIÁN DEL SISTEMA (Seguridad).
------------------------------------------------
Este módulo es el responsable de preguntar: "¿Quién eres?" y "¿Tienes permiso?".
Usamos un sistema de Control de Acceso Basado en Roles (RBAC) para proteger 
el conocimiento de la empresa.

¿CÓMO FUNCIONA EL FLUJO DE SEGURIDAD?
1. LOGIN: El usuario envía sus credenciales. Si son correctas, le damos un "Pasaporte" (JWT).
2. PETICIÓN: En cada acción, el usuario enseña su Pasaporte.
3. VALIDACIÓN: Este módulo comprueba si el pasaporte es real y si aún es válido.
4. PERMISOS: Si la acción requiere ser 'admin', y el usuario es 'lector', le denegamos el acceso.

PARA EL DESARROLLADOR:
Si creas un nuevo endpoint sensible, asegúrate de añadir `Depends(require_admin)` 
como parámetro para que nadie sin permiso pueda ejecutarlo.
"""

import jwt
import datetime
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

# Contexto criptográfico para el hashing de contraseñas.
# "bcrypt" es un algoritmo de hashing lento y probado que es resistente
# a ataques de fuerza bruta.
# deprecated="auto" permite la migración fluida si se adopta un esquema mejor.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Clave secreta para firmar y verificar tokens JWT.
# CRÍTICO: Para un despliegue real, mueva esto a una variable de entorno.
SECRET_KEY = "super_secreto_hackathon"

# El esquema estándar HTTP Bearer espera la cabecera 'Authorization: Bearer <token>'.
security = HTTPBearer()

# ── Base de Datos de Usuarios Virtual ─────────────────────────────
# Para propósitos de demostración y hackathons, usamos un diccionario estático.
# En un proyecto OSS, esto facilita una configuración rápida sin requerir una BD.
#
# Roles:
#   - admin: acceso total a la configuración del sistema y gestión de datos.
#   - editor: puede subir documentos y realizar búsquedas.
#   - lector: solo puede realizar búsquedas y ver resultados.
#
# NOTA: Las contraseñas están pre-hasheadas aquí para disponibilidad inmediata.
USERS = {
    "admin":   {"password": pwd_context.hash("admin123"),   "role": "admin"},
    "editor":  {"password": pwd_context.hash("editor123"),  "role": "editor"},
    "lector":  {"password": pwd_context.hash("lector123"),  "role": "lector"},
    # Alias legado para asegurar la compatibilidad con versiones anteriores.
    "empleado": {"password": pwd_context.hash("normal123"), "role": "lector"},
}

def create_token(username: str, role: str):
    """
    Genera un JWT firmado criptográficamente para un usuario autenticado.

    Los reclamos (claims) del token incluyen:
        - sub (subject): El identificador único del usuario (username).
        - role: El rol del usuario, usado por las dependencias del backend para RBAC.
        - exp (expiration): Timestamp Unix que marca cuándo el token deja de ser válido.

    Args:
        username (str): El nombre de usuario de la persona autenticada.
        role (str): El rol asignado (admin, editor, lector).

    Returns:
        str: Una cadena JWT codificada.
    """
    # Una ventana de expiración de 4 horas proporciona un equilibrio entre seguridad y conveniencia.
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=4)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    EL CONTROL DE PASAPORTES (get_current_user).
    -------------------------------------------
    Esta es la función que se ejecuta cada vez que alguien intenta entrar a un área protegida.
    
    ¿Qué hace?
    1. Mira el token que viene en la cabecera 'Authorization'.
    2. Usa la SECRET_KEY para descifrarlo.
    3. Si todo está bien, devuelve la información del usuario (Nombre, Rol).
    4. Si el token es mentira o ha caducado, lanza un error 401 (No autorizado).
    """
    try:
        # Decodifica y valida el token. PyJWT gestiona la comprobación de 'exp' automáticamente.
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload 
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        # Mensaje de error genérico para evitar la fuga de detalles internos.
        raise HTTPException(status_code=401, detail="Token de autenticación inválido o expirado")


def require_admin(current_user: dict = Security(get_current_user)):
    """
    Dependencia RBAC que requiere privilegios de 'admin'.

    Use esto para acciones de alto impacto como configuración del sistema
    o eliminación masiva de datos.

    Args:
        current_user (dict): Payload del usuario validado por get_current_user.

    Returns:
        dict: El payload del usuario si el rol coincide.

    Raises:
        HTTPException (403): Si el usuario no tiene el rol de admin.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Se requieren privilegios de administrador")
    return current_user


def require_admin_or_editor(current_user: dict = Security(get_current_user)):
    """
    Dependencia RBAC que requiere al menos privilegios de 'editor'.

    Generalmente se usa para acciones que alteran datos pero no involucran
    ajustes de todo el sistema (ej., subir nuevos documentos).

    Args:
        current_user (dict): Payload del usuario validado por get_current_user.

    Returns:
        dict: El payload del usuario si el rol es admin o editor.

    Raises:
        HTTPException (403): Si el usuario es un lector o no tiene rol.
    """
    if current_user.get("role") not in ("admin", "editor"):
        raise HTTPException(status_code=403, detail="Se requiere rol de editor o administrador")
    return current_user
