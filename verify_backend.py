import sys
import os

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_dir)

from app.core.config import settings
from app.core.errors import NotFoundError, APIErrorBody

print(f"Project: {settings.PROJECT_NAME}")
print(f"Environment: {settings.ENVIRONMENT}")
print(f"Reasoning model: {settings.REASONING_MODEL}")
print(f"Embedding model: {settings.EMBEDDING_MODEL}")
print(f"Fast model: {settings.FAST_MODEL}")

err = NotFoundError("Repository", "repo_abc")
body = APIErrorBody(
    error_code=err.error_code,
    message=err.message,
    trace_id="req_test123",
)
print(f"Error shape: {body.model_dump_json(indent=2)}")
print("Backend verification passed.")
