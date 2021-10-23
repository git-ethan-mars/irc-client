wrapper_args = None
return_value = None


def decorator_function(func):
    def wrapper():
        return func(*wrapper_args)

    return wrapper
