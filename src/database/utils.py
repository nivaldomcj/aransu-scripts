from pyodbc import Cursor

from database.models import TableColumnsInfo


def get_databases(cursor: Cursor) -> list[str]:
    query: str = """
        SELECT	name
        FROM	master.sys.databases
        WHERE	name NOT IN ('master', 'tempdb', 'model', 'msdb')
    """

    cursor.execute(query)
    return [e[0] for e in cursor.fetchall()] if cursor.rowcount else []


def get_tables(cursor: Cursor) -> list[str]:
    query: str = "SELECT name FROM sys.Tables"

    cursor.execute(query)
    return [e[0] for e in cursor.fetchall()] if cursor.rowcount else []


def get_columns(cursor: Cursor, table_name: str) -> list[TableColumnsInfo]:
    query: str = """
        SELECT
            C.ORDINAL_POSITION						AS id,
            C.COLUMN_NAME							AS column_name,
            C.DATA_TYPE								AS data_type,
            CASE
                WHEN K.COLUMN_NAME = C.COLUMN_NAME 
                THEN CAST(1 AS BIT) 
                ELSE CAST(0 AS BIT)
            END										AS is_pk
        FROM INFORMATION_SCHEMA.COLUMNS AS C
            INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS K
                ON C.TABLE_NAME = K.TABLE_NAME
        WHERE
            C.TABLE_NAME = '{0}'
        ORDER BY 
            C.ORDINAL_POSITION ASC
    """.format(table_name)

    cursor.execute(query)
    return [
        TableColumnsInfo(e[1], e[2], e[3])
        for e in cursor.fetchall()
    ] if cursor.rowcount else []
