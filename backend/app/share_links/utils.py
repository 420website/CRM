from datetime import datetime, timedelta
import datetime as dt
from jose import JWTError, jwt
from app.config import settings
from typing import Optional


# JWT Handling
def generate_jwt(mime_type: str, patient_id: int, file_name: str) -> str:
    # attachment_id: int) -> str:

    expiry = datetime.now(dt.timezone.utc) + timedelta(
        minutes=settings.share_link_expire_minutes
    )

    payload = {
        "patient_id": patient_id,
        "file_name": file_name,
        "mime_type": mime_type,
        "exp": int(expiry.timestamp()),
        "iat": int(datetime.now(dt.timezone.utc).timestamp()),
    }

    return jwt.encode(
        payload,
        settings.jwt_access_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_jwt(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_access_secret,
            algorithms=settings.jwt_algorithm,
        )
        return payload
    except JWTError:
        return None
