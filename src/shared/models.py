class TableColumnsInfo:
    def __init__(self, column_name: str, data_type: str, pk: bool):
        self.column_name: str = column_name
        self.data_type: str = data_type
        self.pk: bool = pk

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.column_name

class ProcedureParamsInfo:
    def __init__(self, parameter_name: str, data_type: str):
        self.parameter_name: str = parameter_name
        self.data_type: str = data_type

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.parameter_name
