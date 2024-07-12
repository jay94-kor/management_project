# utils/db_utils.py

import os
from db.database import initialize_db

def setup_database():
    if not os.path.exists('project_management.db'):
        initialize_db()
