import pandas as pd
from database.mysqlam import MySQLAM

with MySQLAM() as mam:
    vals = mam.mysunpower_hourly_data_read()

print()