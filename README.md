# dev-utils
Developer Utility scripts and tools

## JWT decoder (CLI)
Inspect JWTs quickly from the terminal.

- Install with pipx (from Git):
  ```bash
  pipx install --python "$(uv python find 3.13)" "git+https://github.com/codespider/dev-utils.git@main"
  ```

- Usage:
  ```bash
  jwt-decode "<jwt>"
  jwt-decode --file token.jwt
  # verify (optional)
  jwt-decode --verify --jwks https://www.googleapis.com/oauth2/v3/certs --aud <aud> --iss https://accounts.google.com
  ```

Note: pretty timestamps are shown by default. Use `--raw` to print raw epoch values.
