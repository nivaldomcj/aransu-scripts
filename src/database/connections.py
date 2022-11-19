import pyodbc
from pyodbc import Connection

SERVER_NAME: str = r'bns-aransu-lab'
DRIVER_NAME: str = r'{ODBC Driver 17 for SQL Server}'

def connect(database_name: str) -> Connection:
    connstring: str = (
        f'Driver={DRIVER_NAME};'
        f'Server={SERVER_NAME};'
        f'Database={database_name};'
        f'Trusted_Connection=yes;'
    )

    return pyodbc.connect(connstring)