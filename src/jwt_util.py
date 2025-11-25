from datetime import datetime, timezone
import json

import jwt

TIME_KEYS = ("iat", "exp", "nbf", "auth_time")


def format_timestamp_fields(payload):
    formatted = {}
    for key, value in payload.items():
        if key in TIME_KEYS:
            ts = int(value)
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            iso = dt.isoformat()
            formatted[key] = {
                'raw': value,
                'iso': iso
            }
        else:
            formatted[key]=value
    return formatted


def decode_jwt_token(token:str):
    headers = jwt.get_unverified_header(token)
    algorithms = [headers['alg']] if 'alg' in headers else None
    payload = jwt.decode(token, algorithms=algorithms, options = {'verify_signature': False})

    formatted = format_timestamp_fields(payload)

    pretty_print_jwt(headers, formatted)

def pretty_print_jwt(header: dict, payload: dict):
    print("=== Header ===")
    print(json.dumps(header, indent=2, sort_keys=True, ensure_ascii=False))
    print()
    print("=== Payload ===")
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))

if __name__ == '__main__':
    decode_jwt_token("eyJhbGciOiJSUzI1NiIsImtpZCI6Ijc4YjRjZjIzNjU2ZGMzOTUzNjRmMWI2YzAyOTA3NjkxZjJjZGZmZTEifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwic3ViIjoiMTEwNTAyMjUxMTU4OTIwMTQ3NzMyIiwiYXpwIjoiODI1MjQ5ODM1NjU5LXRlOHFnbDcwMWtnb25ub21ucDRzcXY3ZXJodTEyMTFzLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiZW1haWwiOiJwcmFiYXRoQHdzbzIuY29tIiwiYXRfaGFzaCI6InpmODZ2TnVsc0xCOGdGYXFSd2R6WWciLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXVkIjoiODI1MjQ5ODM1NjU5LXRlOHFnbDcwMWtnb25ub21ucDRzcXY3ZXJodTEyMTFzLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiaGQiOiJ3c28yLmNvbSIsImlhdCI6MTQwMTkwODI3MSwiZXhwIjoxNDAxOTEyMTcxfQ.TVKv-pdyvk2gW8sGsCbsnkqsrS0T-H00xnY6ETkIfgIxfotvFn5IwKm3xyBMpy0FFe0Rb5Ht8AEJV6PdWyxz8rMgX2HROWqSo_RfEfUpBb4iOsq4W28KftW5H0IA44VmNZ6zU4YTqPSt4TPhyFC9fP2D_Hg7JQozpQRUfbWTJI")