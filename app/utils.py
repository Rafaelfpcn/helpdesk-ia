from datetime import datetime, timezone


def utcnow() -> datetime:
    """Data/hora atual em UTC, sem fuso (naive).

    O SQLite não guarda fuso horário nativamente. Padronizar tudo em UTC naive
    evita erros ao comparar datas lidas do banco com datas atuais.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
