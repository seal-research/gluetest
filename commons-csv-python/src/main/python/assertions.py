class Assertions:
    @staticmethod
    def not_null(parameter, parameter_name):
        if parameter == None:
            raise ValueError(f"Parameter '{parameter_name}' must not be None!")
