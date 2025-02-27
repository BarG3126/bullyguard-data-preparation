def validate_config_parameter_is_in(
    allow_parameter_values: set[str], current_parameter_value: str, parameter_name: str
) -> None:
    if current_parameter_value not in allow_parameter_values:
        raise ValueError(
            f"Parameter {parameter_name} has value {current_parameter_value}, but it should be one of {allow_parameter_values}"
        )
