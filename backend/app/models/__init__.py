"""Import all models so that ``Base.metadata`` sees every table.

Alembic and any code that calls ``Base.metadata.create_all()`` must
import this module first.
"""

from app.db.base import Base  # noqa: F401

from app.models.user import User, OAuthAccount, RefreshToken  # noqa: F401
from app.models.workspace import Workspace, WorkspaceMember  # noqa: F401
from app.models.repository import (  # noqa: F401
    Repository,
    RepositoryFile,
    CodeSymbol,
    CodeChunk,
    ChunkEmbedding,
)
from app.models.incident import (  # noqa: F401
    Incident,
    AgentRun,
    AgentStep,
    RetrievalResult,
    PatchSet,
    PatchFile,
    SandboxRun,
)
from app.models.audit import AuditEvent  # noqa: F401
