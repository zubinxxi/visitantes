from datetime import datetime, timezone, timedelta

TIMEZONE_PANAMA = timezone(timedelta(hours=-5))


def now_panama() -> datetime:
    """Retorna datetime timezone-aware en zona horaria de Panamá (UTC-5).

    Útil para JWT donde se requiere tzinfo para cálculo correcto de expiración.
    """
    return datetime.now(TIMEZONE_PANAMA)


def today_start_panama() -> datetime:
    """Retorna el inicio del día de hoy en Panamá (timezone-aware)."""
    now = now_panama()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def now_panama_naive() -> datetime:
    """Retorna datetime naive en hora local de Panamá.

    Para almacenar en columnas MariaDB `datetime` que no soportan timezone.
    Para JWT usar `now_panama()` en su lugar.
    """
    return datetime.now(TIMEZONE_PANAMA).replace(tzinfo=None)