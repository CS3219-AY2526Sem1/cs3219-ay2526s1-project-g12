import json
from dataclasses import asdict, dataclass
from typing import List


@dataclass
class RouteDefinition:
    """Representation of a single API route in the registry.

    Attributes:
        path: The URL path pattern (e.g. "/users/me", "/users/{id}").
        methods: A list of allowed HTTP methods for this route (e.g.
            ["GET", "POST"]).  Method names should be uppercase.
        roles: A list of allowed roles for this route.  If empty, no
            role restriction is applied.
    """
    path: str
    methods: List[str]
    roles: List[str]

    def to_json(self) -> str:
        """Serialize the route definition to a JSON string."""
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(data: str) -> "RouteDefinition":
        """Deserialize a JSON string back into a RouteDefinition."""
        obj = json.loads(data)
        return RouteDefinition(path=obj["path"], methods=obj["methods"], roles=obj["roles"])
