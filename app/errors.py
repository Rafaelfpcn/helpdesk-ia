class AppError(Exception):
    """Erro de negócio base. Cada subclasse define o status HTTP e um código legível."""

    status_code: int = 400
    code: str = "app_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class TicketNotFound(AppError):
    status_code = 404
    code = "ticket_not_found"


class InvalidStatusTransition(AppError):
    status_code = 409
    code = "invalid_status_transition"


class NoSuggestionAvailable(AppError):
    status_code = 409
    code = "no_suggestion"


class ReviewAlreadyDone(AppError):
    status_code = 409
    code = "review_already_done"


class InvalidReview(AppError):
    status_code = 422
    code = "invalid_review"
