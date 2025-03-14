from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """Base configuration class."""

    model_config = SettingsConfigDict(
        # Treat environment variables names as case-insensitive
        case_sensitive=False,
        # Use this prefix for all environment variables
        env_prefix="MANTIS__",
        # Load environment variables from this file if it exists
        env_file=".env",
        # Don't ignore empty environment variables
        env_ignore_empty=False,
        # Use this delimiter to separate nested models
        env_nested_delimiter="__",
        # Treat empty strings as None
        env_parse_none_str="",
        # Ignore extra fields
        extra="ignore",
        # Make the instance immutable
        frozen=True,
        # Disallow arbitrary types that Pydantic can't handle
        arbitrary_types_allowed=False,
        # Disallow non-serializable float values
        allow_inf_nan=False,
        # Allow type coercion
        strict=False,
        # Validate default values
        validate_default=True,
        # Make fields with default values required in serialization schemas
        json_schema_serialization_defaults_required=True,
        # Allow coercion of numbers to strings
        coerce_numbers_to_str=True,
        # Use field docstrings as descriptions
        use_attribute_docstrings=True,
    )
