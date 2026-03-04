# app/models/__init__.py

# Import all models here so they can be easily accessed
# Example: from app.models import User, Document, Conversation

from app.models.user import User
from app.models.document import Document, Conversation

__all__ = ["User", "Document", "Conversation"]