import json
from flask import Response


def parse_and_validate_json_args(request, required_args=()):
    try:
        parsed = json.loads(request.data or '{}')
    except ValueError:
        return "Invalid JSON supplied", None

    if not isinstance(parsed, dict):
        return "Invalid JSON supplied", None

    for arg_name in required_args:
        if arg_name not in parsed:
            return 'Missing argument: "{}"'.format(arg_name), None

    return None, parsed


def error_json_response(message, status):
    return Response(content_type='application/json', response=json.dumps({'error': message}), status=status)


def success_json_response(data, status):
    return Response(content_type='application/json', response=json.dumps(data), status=status)
