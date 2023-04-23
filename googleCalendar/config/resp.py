import datetime

def api_response(status, code, message, data, metadata=None, links=None, documentation=None):
    """
    Generates an API response as a dictionary.

    Args:
        status (str): Status of the API response (e.g., "success", "error").
        code (int): HTTP status code.
        message (str): Message describing the outcome of the API request.
        data (dict): Data payload of the API response.
        metadata (dict, optional): Metadata about the API response. Defaults to None.
        links (list, optional): List of hypermedia links. Defaults to None.
        documentation (str, optional): Link to API documentation. Defaults to None.

    Returns:
        dict: Dictionary representing the API response.
    """
    api_response = {
        "status": status,
        "code": code,
        "message": message,
        "data": data
    }

    if metadata is not None:
        api_response["metadata"] = metadata

    if links is not None:
        api_response["links"] = links

    if documentation is not None:
        api_response["documentation"] = documentation

    return api_response


# Example usage
# user_data = {
#     "id": 12345,
#     "name": "John Doe",
#     "age": 30,
#     "email": "johndoe@example.com"
# }

# metadata = {
#     "timestamp": datetime.datetime.utcnow().isoformat(),
#     "version": "1.0"
# }

# links = [
#     {"rel": "self", "href": "https://api.example.com/users/12345"},
#     {"rel": "profile", "href": "https://api.example.com/profiles/johndoe"}
# ]

# documentation = "https://api.example.com/docs"

