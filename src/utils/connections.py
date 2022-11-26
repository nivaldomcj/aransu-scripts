from pyodbc import Connection, connect

DRIVER_NAME: str = 'ODBC Driver 17 for SQL Server'


def connect_winauth(server_name: str,
                    database_name: str,
                    driver_name: str = DRIVER_NAME) -> Connection:
    connstring: str = (
        f'Driver={driver_name};'
        f'Server={server_name};'
        f'Database={database_name};'
        f'Trusted_Connection=yes;'
    )
    return connect(connstring)


def connect_sqlauth(server_ip: str,
                    server_port: str,
                    username: str,
                    password: str,
                    database_name: str,
                    driver_name: str = DRIVER_NAME) -> Connection:
    connstring: str = (
        f'Driver={driver_name};'
        f'Server={server_ip};'
        f'port={server_port};'
        f'Network Library=DBMSSOCN;'
        f'Database={database_name};'
        f'uid={username};'
        f'pwd={password};'
        f'TrustServerCertificate=yes;'
    )
    return connect(connstring)
