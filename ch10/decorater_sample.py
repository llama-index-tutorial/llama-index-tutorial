def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"Calling function: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_call
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
