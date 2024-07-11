import pandas as pd
from google_sheet import read_google_sheet
from database import init_db, add_project
import os
from dotenv import load_dotenv

load_dotenv()

SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
RANGE_NAME = os.getenv('GOOGLE_SHEET_RANGE')

def load_initial_data():
    values = read_google_sheet(SHEET_ID, RANGE_NAME)
    df = pd.DataFrame(values[1:], columns=values[0])
    return df

def sync_data_to_db():
    df = load_initial_data()
    for index, row in df.iterrows():
        add_project(row['프로젝트명'], float(row['배정금액']))

if __name__ == '__main__':
    if not os.path.exists('../data/database.db'):
        init_db()
    sync_data_to_db()