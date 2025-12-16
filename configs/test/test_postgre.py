"""Test PostgreSQL connection"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from configs.db.postgresql import get_db
from sqlalchemy import text

try:
    for db in get_db():
        db.execute(text("SELECT 1"))
    print("PostgreSQL connection: SUCCESS")
except Exception as e:
    print(f"PostgreSQL connection: FAILED - {e}")
    sys.exit(1)

