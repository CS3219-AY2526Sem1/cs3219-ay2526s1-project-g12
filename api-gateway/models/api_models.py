from typing import Annotated

from openapi_spec_validator import validate
from openapi_spec_validator.validation.exceptions import OpenAPIValidationError
from pydantic import BaseModel, Field, field_validator


class RoutePayload(BaseModel):
    """Model representing a route payload for service registration.

    Attributes:
        path (str): The path pattern (e.g. /users/me).
        methods (Dict[str, list]): List of allowed HTTP methods and their roles.
    """
    path: Annotated[str, Field(description="The path pattern (e.g. /users/me)")]
    methods: Annotated[dict[str, list[str]], Field(description="List of allowed HTTP methods and their roles")]


class RegisterServicePayload(BaseModel):
    """Model representing the payload for registering a service.

    Attributes:
        service_name (str): Unique name of the service.
        instance_id (str): Identifier for this instance (e.g. host:port).
        address (str): Host:port the gateway should forward to.
        routes (list[RoutePayload]): Routes exposed by this service.
    """
    service_name: Annotated[str, Field(description="Unique name of the service")]
    instance_id: Annotated[str, Field(description="Identifier for this instance (e.g. host:port)")]
    address: Annotated[str, Field(description="Host:port the gateway should forward to")]
    routes: Annotated[list[RoutePayload], Field(description="Routes exposed by this service")]


class RegisterOpenApiPayload(BaseModel):
    """Model representing the payload for registering a service using its OpenAPI specification.

    The OpenAPI schema should be provided as a JSON object. The gateway will parse the
    `paths` section to derive a list of routes. Each path will have its HTTP methods
    extracted and converted to uppercase. If no custom role information is present,
    the roles list will be empty.

    Attributes:
        service_name (str): Unique name of the service.
        instance_id (str): Identifier for this instance (e.g. host:port).
        address (str): Host:port the gateway should forward to.
        openapi (dict): The OpenAPI specification as a JSON object.
    """
    service_name: Annotated[str, Field(description="Unique name of the service")]
    instance_id: Annotated[str, Field(description="Identifier for this instance (e.g. host:port)")]
    address: Annotated[str, Field(description="Host:port the gateway should forward to")]
    openapi: Annotated[
        dict, Field(description="The OpenAPI specification as a JSON object")
    ]

    @field_validator("openapi")
    @classmethod
    def validate_openapi_spec(cls, spec: dict) -> dict:
        """Validate that the provided OpenAPI specification is valid."""
        try:
            validate(spec)
        except OpenAPIValidationError as e:
            raise ValueError(f"Invalid OpenAPI specification: {e}")
        return spec


class ServiceInstancePayload(BaseModel):
    """Model representing a service instance identity.

    Attributes:
        service_name (str): Unique name of the service.
        instance_id (str): Identifier for this instance (e.g. host:port).
    """
    service_name: Annotated[str, Field(description="Unique name of the service")]
    instance_id: Annotated[str, Field(description="Identifier for this instance (e.g. host:port)")]
