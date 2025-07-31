from app import db
from sqlalchemy import text

with db.engine.connect() as conn:
    result = conn.execute(text("SHOW search_path")).fetchall()
    print("Search path:", result)
