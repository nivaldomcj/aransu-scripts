from database.connections import connect
from database.utils import get_columns




def main():
    connection = connect('LimitDb')
    cursor = connection.cursor()
    cols = get_columns(cursor, 'LimitExceptions')
    print(cols)


if __name__ == '__main__':
    main()
