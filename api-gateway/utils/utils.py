import os
import re

from dotenv import load_dotenv


def get_envvar(var_name: str) -> str:
    load_dotenv()
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is not set.")
    return value

def path_variants(path: str) -> set[str]:
    """Return both the slash and non-slash variants of a route path."""
    if path == "/":
        return {"/"} # root path only has one valid form
    if path.endswith("/"):
        return {path, path[:-1]}
    else:
        return {path, path + "/"}

def build_route_path(service_name: str, path: str) -> str:
    """Return a globally unique route path with the service name prefix."""
    # ensure path starts with "/" but doesn’t double-slash
    if not path.startswith("/"):
        path = "/" + path
    if not service_name.startswith("/"):
        service_name = "/" + service_name
    # avoid double slashes like /users//login
    return re.sub(r"//+", "/", f"{service_name}{path}")
