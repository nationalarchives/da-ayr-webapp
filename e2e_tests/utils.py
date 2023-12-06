def block_resource_requests(route, block_css=True):
    """
    Intercepts and blocks CSS resource requests if block_css is True.

    This function is used as a callback for Playwright's route method to intercept
    and block CSS resource requests when the block_css flag is set to True. When
    a CSS request is intercepted, it will print a message and abort the request,
    effectively blocking CSS resources.

    Parameters:
        route (Route): The intercepted route object.
        block_css (bool): Flag to control CSS blocking (default is True).

    Returns:
        Route: The route object after intercepting and possibly blocking the request.
    """
    try:
        if route is None:
            raise ValueError("Route object is None")

        if block_css and route.request.resource_type == "stylesheet":
            print(f"Blocking the CSS request to: {route.request.url}")
            return route.abort()
        return route.continue_()
    except Exception as e:
        print(f"Error in block_css_requests: {e}")
