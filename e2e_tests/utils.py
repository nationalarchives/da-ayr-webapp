def block_resource_requests(route):
    """
    Intercepts and blocks CSS resource requests.

    This function is used as a callback for Playwright's route method to intercept
    and block CSS resource requests. When a CSS request is intercepted, it will
    print a message and abort the request, effectively blocking CSS resources.

    Parameters:
        route (Route): The intercepted route object.

    Returns:
        Route: The route object after intercepting and possibly blocking the request.
    """
    if route.request.resource_type == "stylesheet":
        print(f"Blocking the CSS request to: {route.request.url}")
        return route.abort()
    return route.continue_()
