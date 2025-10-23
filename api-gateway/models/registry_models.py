import json
from dataclasses import asdict, dataclass


@dataclass
class RouteDefinition:
    """Representation of a single API route in the registry.

    Attributes:
        path: The URL path pattern (e.g. "/users/me", "/users/{id}").
        methods: A dictionary where each key is an HTTP method
            (e.g. "GET", "POST") and the value is a list of roles
            authorized to access that method. (An empty list means
            the method is public.)
    """
    path: str
    methods: dict[str, list[str]]

    def to_json(self) -> str:
        """Serialize the route definition to a JSON string."""
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(data: str) -> "RouteDefinition":
        """Deserialize a JSON string back into a RouteDefinition."""
        obj = json.loads(data)
        return RouteDefinition(path=obj["path"], methods=obj["methods"])
