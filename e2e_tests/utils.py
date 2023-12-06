import functools


def block_css_decorator(func):
    """
    Decorator to intercept and block CSS resource requests.

    This decorator is designed to be applied to functions that receive a 'page'
    object as their first argument. It will intercept and block stylesheet resource
    requests.

    Parameters:
        func (function): The function to be wrapped.

    Returns:
        function: The wrapped function.

    """

    @functools.wraps(func)
    def wrapper(page, *args, **kwargs):
        try:
            if page is None:
                raise ValueError("Page object is None")

            def route_intercept(route):
                if route.request.resource_type == "stylesheet":
                    return route.abort()
                return route.continue_()

            page.route("**/*", route_intercept)

            return func(page, *args, **kwargs)
        except Exception as e:
            print(f"Error in block_css_decorator: {e}")

    return wrapper
