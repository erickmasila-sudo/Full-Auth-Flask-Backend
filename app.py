"""
API entry point (scaffold).

Route registration is added incrementally in later commits.
"""
from config import app, db
from models import User, Note  # noqa: F401  (imported so migrations can detect tables)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
