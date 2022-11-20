from pyodbc import Connection, connect

DRIVER_NAME: str = r'{ODBC Driver 17 for SQL Server}'


def connect_winauth(server_name: str, 
                    database_name: str) -> Connection:
    connstring: str = (
        f'Driver={DRIVER_NAME};'
        f'Server={server_name};'
        f'Database={database_name};'
        f'Trusted_Connection=yes;'
    )
    return connect(connstring)


def connect_sqlauth(server_ip: str,
                    server_port: str,
                    username: str,
                    password: str,
                    database_name: str) -> Connection:
    connstring: str = (
        f'Driver={DRIVER_NAME};'
        f'Server={server_ip};'
        f'port={server_port};'
        f'Network Library=DBMSSOCN;'
        f'Database={database_name};'
        f'uid={username};'
        f'pwd={password};'
    )
    return connect(connstring)
