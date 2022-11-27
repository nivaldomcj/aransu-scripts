"""
Export tables from SQL Server to DBML format,
attempting to unite all foreign key candidates.

Creates Table objects and Refs objects complying with DBML format.
"""
import pyodbc

CONN_STR = """
    Driver=ODBC Driver 18 for SQL Server;
    Server=localhost; 
    port=1433; 
    Database={};
    uid=sa; 
    pwd=Mudar@123;
    Network Library=DBMSSOCN; 
    TrustServerCertificate=yes;
"""


class Column:
    def __init__(self, column_name, data_type, is_pk):
        self.column_name = column_name
        self.data_type = data_type
        self.is_pk = is_pk

    def __str__(self):
        return self.column_name

    def __repr__(self):
        return self.__str__()

    def is_fk(self):
        return not self.is_pk and self.column_name.lower().endswith('id')

    def get_dbml(self):
        if self.is_pk:
            return '{} {} [pk]'.format(self.column_name, self.data_type)
        return '{} {}'.format(self.column_name, self.data_type)


class Table:
    def __init__(self, database_name, table_name, columns):
        self.database_name = database_name
        self.table_name = table_name
        self.columns = columns

    def __str__(self):
        return self.table_name

    def __repr__(self):
        return self.__str__()

    def get_primary_columns(self):
        return list(filter(lambda x: x.is_pk, self.columns))

    def get_special_columns(self):
        return list(filter(lambda x: x.is_pk or x.is_fk(), self.columns))

    def get_dbml(self):
        title = 'Table {}.{}'.format(self.database_name, self.table_name)
        columns = '\n'.join(['  %s' % (column.get_dbml())
                            for column in self.columns])
        return '%s {\n%s\n}\n' % (title, columns)


class Ref:
    def __init__(self, database_name, table_name, column_name):
        self.database_name = database_name
        self.table_name = table_name
        self.column_name = column_name
        self.collected_refs = []

    def __str__(self):
        return '%s.%s.%s' % (
            self.database_name, self.table_name, self.column_name)

    def __repr__(self):
        return self.__str__()

    def add(self, database_name, table_name, column_name):
        if table_name != self.table_name:
            ref = Ref(database_name, table_name, column_name)
            self.collected_refs.append(ref)

    def get_dbml(self):
        if not len(self.collected_refs):
            return ''
        return ''.join([
            'Ref: %s - %s\n' % (self, other_ref)
            for other_ref in self.collected_refs
        ])


class TablesExtractor:
    def __get_databases(self):
        get_databases_query = """
            SELECT
                name
            FROM
                master.sys.databases 
            WHERE 
                name NOT IN ('master', 'tempdb', 'model', 'msdb')
        """
        with pyodbc.connect(CONN_STR.format('master')) as connection:
            with connection.cursor() as cursor:
                cursor.execute(get_databases_query)
                return [r[0] for r in cursor.fetchall()]

    def __get_table_columns(self, database_name, table_name):
        get_table_columns_query = """
            SELECT DISTINCT
                sys.columns.name AS ColumnName,
                sys.types.name AS TypeName,
                (   SELECT 
                        COUNT(column_name)
                    FROM 
                        INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE 
                    WHERE
                        TABLE_NAME = sys.tables.name AND
                        CONSTRAINT_NAME = (
                            SELECT TOP 1
                                constraint_name
                            FROM 
                                INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                            WHERE
                                TABLE_NAME = sys.tables.name AND
                                constraint_type = 'PRIMARY KEY' AND
                                COLUMN_NAME = sys.columns.name
                        )
                ) AS IsPrimaryKey
            FROM 
                sys.columns, sys.types, sys.tables 
            WHERE
                sys.tables.object_id = sys.columns.object_id AND
                sys.types.system_type_id = sys.columns.system_type_id AND
                sys.types.user_type_id = sys.columns.user_type_id AND
                sys.tables.name = ?
            ORDER BY 
                IsPrimaryKey DESC, ColumnName ASC
        """
        with pyodbc.connect(CONN_STR.format(database_name)) as connection:
            with connection.cursor() as cursor:
                cursor.execute(get_table_columns_query, table_name)
                return [Column(r[0], r[1], r[2]) for r in cursor.fetchall()]

    def get_table_definitions(self):
        tables = []

        for database_name in self.__get_databases():
            with pyodbc.connect(CONN_STR.format(database_name)) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT DISTINCT name FROM sys.Tables")
                    for row in cursor.fetchall():
                        tables.append(Table(
                            database_name=database_name,
                            table_name=row[0],
                            columns=self.__get_table_columns(
                                database_name, row[0])
                        ))

        return tables

    def get_table_references(self, tables):
        references = {}

        # 1st scan, to find and set initial references
        for table in tables:
            for column in table.get_special_columns():
                key = column.column_name.lower()
                if key in references and not column.is_pk:
                    continue
                references[key] = Ref(
                    table.database_name, table.table_name, column.column_name)

        # 2nd scan, to link initial references with secondary ones
        for table in tables:
            for column in table.get_special_columns():
                key = column.column_name.lower()
                references[key].add(
                    table.database_name, table.table_name, column.column_name)

        return references.values()


class DbmlExporter:
    def __init__(self, tables, references):
        self.tables = tables
        self.references = references

    def __export_table_defs(self, file, tables):
        for table in tables:
            file.write('%s\n' % table.get_dbml())

    def __export_table_refs(self, file, references):
        for reference in references:
            file.write('%s' % reference.get_dbml())

    def export(self, file_name):
        with open(file_name, 'w') as file:
            self.__export_table_defs(file, self.tables)
            file.write('\n')
            self.__export_table_refs(file, self.references)
            file.write('\n')


def main():
    e = TablesExtractor()
    t = e.get_table_definitions()
    r = e.get_table_references(t)

    d = DbmlExporter(t, r)
    d.export('output.txt')


if __name__ == '__main__':
    main()
