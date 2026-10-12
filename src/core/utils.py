def normalize_path(path: str) -> str:
    """ Garants that path parameter starts with / and doesn't ends with /

        Parameters:
        path (str): Endpoint's path (URL)

        Return:
        path (str): Endpoint's normalized path 
    """
    if not path.startswith("/"):
        path = "/" + path
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    return path
