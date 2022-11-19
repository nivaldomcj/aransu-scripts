from database.connections import connect
from database.utils import get_procedure_params




def main():
    connection = connect('LimitDb')
    cursor = connection.cursor()
    x = get_procedure_params(cursor, 'p_GetPurchaseStatisticsByUserIdAndPaymentTypeCore')
    print(x)


if __name__ == '__main__':
    main()
