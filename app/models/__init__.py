# Importar todos os modelos aqui garante que o SQLAlchemy os "conheça"
# antes de criar as tabelas (create_all).
from app.models.ai_suggestion import AISuggestion
from app.models.audit_log import AuditLog
from app.models.ticket import Ticket

__all__ = ["Ticket", "AISuggestion", "AuditLog"]
