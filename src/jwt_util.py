from datetime import datetime, timezone
import json
import sys
from typing import List, Optional, Tuple

import click
import jwt
from jwt import PyJWKClient

# Keys that we will render in a more human-friendly way
TIME_KEYS = ("iat", "exp", "nbf", "auth_time")


def format_timestamp_fields(payload: dict) -> dict:
    """Convert common epoch fields to include ISO time alongside raw epoch."""
    formatted = {}
    for key, value in payload.items():
        if key in TIME_KEYS:
            try:
                ts = int(value)
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                iso = dt.isoformat()
                formatted[key] = {
                    "raw": value,
                    "iso": iso,
                }
            except Exception:
                formatted[key] = value
        else:
            formatted[key] = value
    return formatted


def decode_no_verify(token: str) -> Tuple[dict, dict]:
    """Decode header and payload without verifying the signature (for inspection)."""
    header = jwt.get_unverified_header(token)
    algorithms = [header["alg"]] if "alg" in header else None
    payload = jwt.decode(
        token,
        algorithms=algorithms,
        options={"verify_signature": False, "verify_aud": False},
    )
    return header, payload


def verify_with_jwks(
    token: str,
    jwks_url: str,
    audience: Optional[str] = None,
    issuer: Optional[List[str]] = None,
) -> Tuple[dict, dict]:
    """Verify token using a JWKS URL; returns (header, payload)."""
    header = jwt.get_unverified_header(token)
    key = PyJWKClient(jwks_url).get_signing_key_from_jwt(token).key
    payload = jwt.decode(
        token,
        key=key,
        algorithms=[
            "RS256",
            "RS384",
            "RS512",
            "ES256",
            "ES384",
            "ES512",
            "PS256",
            "PS384",
            "PS512",
        ],
        audience=audience,
        issuer=issuer,
    )
    return header, payload


def pretty_print_jwt(header: dict, payload: dict) -> None:
    print("=== Header ===")
    print(json.dumps(header, indent=2, sort_keys=True, ensure_ascii=False))
    print()
    print("=== Payload ===")
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def _read_token_from_inputs(token: Optional[str], token_file: Optional[click.File]) -> str:
    if token:
        return token.strip()
    if token_file:
        return token_file.read().strip()
    if not sys.stdin.isatty():
        data = sys.stdin.read().strip()
        if data:
            return data
    raise click.UsageError("TOKEN argument, --file, or stdin input is required")


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("token", required=False)
@click.option(
    "--file",
    "token_file",
    type=click.File("r"),
    help="Read token from file instead of argument or stdin",
)
@click.option(
    "--verify/--no-verify",
    default=False,
    help="Verify the token using JWKS (off by default).",
)
@click.option("--jwks", help="JWKS URL to use when --verify is enabled")
@click.option("--aud", help="Expected audience (aud)")
@click.option(
    "--iss",
    multiple=True,
    help="Expected issuer(s). Repeat flag to provide multiple values.",
)
@click.option(
    "--raw/--pretty-time",
    default=False,
    help="Print raw timestamps (raw) or include ISO times (pretty-time)",
)
def cli(
    token: Optional[str],
    token_file: Optional[click.File],
    verify: bool,
    jwks: Optional[str],
    aud: Optional[str],
    iss: Tuple[str, ...],
    raw: bool,
) -> None:
    """Decode a JSON Web Token.

    TOKEN may be provided as an argument, via --file, or via stdin.
    By default, signature verification is disabled (inspection mode).
    Enable --verify with --jwks to verify using a JWKS endpoint.
    """
    try:
        tok = _read_token_from_inputs(token, token_file)

        if verify:
            if not jwks:
                raise click.UsageError("--jwks is required when using --verify")
            header, payload = verify_with_jwks(tok, jwks, aud, list(iss) or None)
        else:
            header, payload = decode_no_verify(tok)

        if not raw:
            payload = format_timestamp_fields(payload)

        pretty_print_jwt(header, payload)
    except click.UsageError:
        raise
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()