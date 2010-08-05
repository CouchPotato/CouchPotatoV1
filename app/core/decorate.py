from app.core.environment import Environment

def before(before_func, *args_before, **kwargs_before):
    """
    Execute a custom function with the specified arguments
    followed by the orignal call's arguments.
    before the original function has been called. 
    
    Return the original function's return value.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            #merge arguments
            merged_args = args_before.copy().extend(args)
            merged_kwargs = kwargs_before.copy().update(kwargs)
            before_func(*merged_args, **merged_kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def beforestatic(before_func, *args_before, **kwargs_before):
    """
    Execute a custom function with the specified arguments
    before the original function has been called. 
    
    Return the original function's return value.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            before_func(*args_before, **args_before)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def after(after_func, *args_after, **kwargs_after):
    """
    Execute a custom function with the specified arguments
    followed by the orignal call's arguments.
    before the original function has been called. 
    
    Return the original function's return value.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            #merge arguments
            merged_args = args_after.copy().extend(args)
            merged_kwargs = kwargs_after.copy().update(kwargs)
            after_func(*merged_args, **merged_kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def afterstatic(after_func, *args_after, **kwargs_after):
    """
    Execute a custom function with the specified arguments
    after the original function has been called. 
    
    Return the original function's return value.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            after_func(*args_after, **args_after)
            return result
        return wrapper
    return decorator

def debugonly(func):
    """
    Execute the function to be decorated only if the debug
    status is set to True returns the original function's
    return value.
    Else return None.
    """

    def wrapper(*args, **kwargs):
        if True:
            return func(*args, **kwargs)
        else:
            print 'skipped', func.__name__
    return wrapper

def conditional(conditional_decorator, condition, *condargs, **condkwargs):
    """
    Choose at runtime, depending on the condition whether to
    call the decorated or the plain function.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            decorated = conditional_decorator(func)
            if condition(*condargs, **condkwargs):
                return decorated(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator

def debugonlydecorator(decorator):
    """
    Decorate a function and call either the
    decorated or the plain, depending on whether the
    debug status is set at that particular moment.
    """
    return conditional(decorator, Environment.get, 'debug')
