class BaseConstants:
    @classmethod
    def iterate_constants(cls):
        """
        Iterates over all constants.
        """
        for key, value in cls.__dict__.items():
            if not key.startswith("__") and not callable(value):
                yield key, value

    @classmethod
    def is_valid_constant(cls, value):
        """
        Checks if the provided value is valid within the constants.
        """
        return value in cls.__dict__.values()

    @classmethod
    def get_constant(cls, key):
        """
        Returns the value of the constant key.
        """
        return cls.__dict__.get(key)

    @classmethod
    def query_by_substring(cls, substring):
        """
        Queries the constants for keys/values containing the provided substring.
        """
        result = {}
        for key, value in cls.__dict__.items():
            if not key.startswith("__") and not callable(value):
                if substring.lower() in key.lower() or substring.lower() in value.lower():
                    result[key] = value
        return result
