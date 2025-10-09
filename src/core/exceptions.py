class DomainError(Exception):
    """Base class for domain-level errors."""
    pass

class InvalidIATAError(DomainError):
    """Raised when an airport code isn't a 3-letter IATA code."""
    pass

class ValidationError(DomainError):
    """Raised when input values don't pass simple domain rules."""
    pass