#!/usr/bin/env python3

"""Utilities module."""

from typing import Any, Tuple, Union

from flask import request


def _check_form_data_field_existence(*, expected_fields: set):
    """Verify that the expected fields are found in the request body."""
    if not request.form:
        raise ValueError({"expected_fields": list(expected_fields)})
    for field in expected_fields:
        if not request.form.get(field):
            raise ValueError(f"{field} missing")


def request_body_provided(
    *, expected_fields: set
) -> Union[Tuple[bool, Any], Tuple[bool, None]]:
    """Validate that all fields required for request body is provided.

    This validates that all `expected_fields` are present in the request body.
    In the event where any of the fields are not provided, `False` is
    returned with an error message stating why.

    If all the fields are present in the request body, the error message is
    set to `None` and success is to `True`.

    Args:
        expected_fields (set): The field(s) expected to be in the request body.

    Returns:
        `False` and an error message if an error occurred. Otherwise,
        `True` with error message set to `None`.
    """
    try:
        _check_form_data_field_existence(expected_fields=expected_fields)
    except ValueError as err:
        return False, err.args[0]

    return True, None
