def add_docs(docs):
    def wrapper(f):
        f.__doc__ = docs
        return f
    return wrapper
