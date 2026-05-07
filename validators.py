"""Funciones de validación de formato reutilizables para toda la aplicación.

Las funciones lanzan ``ValueError`` con un mensaje descriptivo cuando el valor
no cumple el formato esperado, de modo que los controladores y la capa de UI
pueden capturar la excepción y mostrarla al usuario sin lógica adicional.
"""

import re

# ── Patrones compilados (rendimiento: se compilan una sola vez) ─────────────

_CEDULA_RE    = re.compile(r'^\d{10}$')
_PHONE_RE     = re.compile(r'^\d{9,10}$')
_EMAIL_RE     = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
_RUC_RE       = re.compile(r'^\d{13}$')          # RUC ecuatoriano: 13 dígitos


# ── Validadores públicos ────────────────────────────────────────────────────

def validate_cedula(cedula: str) -> None:
    """Valida que la cédula tenga exactamente 10 dígitos numéricos.

    Args:
        cedula: Cadena a validar (ya saneada con .strip()).

    Raises:
        ValueError: Si el formato es incorrecto.
    """
    if not _CEDULA_RE.match(cedula):
        raise ValueError("La cédula debe tener exactamente 10 dígitos numéricos.")


def validate_phone(phone: str) -> None:
    """Valida que el teléfono tenga entre 9 y 10 dígitos numéricos.

    El campo es opcional; pasar cadena vacía omite la validación.

    Args:
        phone: Cadena a validar (ya saneada con .strip()).

    Raises:
        ValueError: Si el formato es incorrecto.
    """
    if phone and not _PHONE_RE.match(phone):
        raise ValueError("El teléfono debe tener entre 9 y 10 dígitos numéricos.")


def validate_email(email: str) -> None:
    """Valida que el correo electrónico tenga un formato básico válido.

    El campo es opcional; pasar cadena vacía omite la validación.

    Args:
        email: Cadena a validar (ya saneada con .strip()).

    Raises:
        ValueError: Si el formato es incorrecto.
    """
    if email and not _EMAIL_RE.match(email):
        raise ValueError("El formato del correo electrónico es inválido.")


def validate_ruc(ruc: str) -> None:
    """Valida que el RUC tenga exactamente 13 dígitos numéricos (Ecuador).

    El campo es opcional; pasar cadena vacía omite la validación.

    Args:
        ruc: Cadena a validar (ya saneada con .strip()).

    Raises:
        ValueError: Si el formato es incorrecto.
    """
    if ruc and not _RUC_RE.match(ruc):
        raise ValueError("El RUC debe tener exactamente 13 dígitos numéricos.")
