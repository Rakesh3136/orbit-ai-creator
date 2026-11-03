import base64, hashlib, hmac, secrets, time
from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Response
from aimn_api.config import settings
from aimn_api.schemas import AuthLogin

SESSION_COOKIE = 'aimn_owner_session'
auth_router = APIRouter(prefix='/api/v1/auth', tags=['authentication'])

def password_matches(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt, expected = encoded.split('$', 3)
        if algorithm != 'pbkdf2_sha256' or int(rounds) < 100000 or int(rounds) > 2000000:
            return False
        digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), int(rounds))
        actual = base64.urlsafe_b64encode(digest).decode().rstrip('=')
        return secrets.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False

def _encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip('=')

def issue_session(email: str, signing_key: str, ttl: int) -> str:
    body = _encode((email.lower() + '|' + str(int(time.time()) + ttl)).encode())
    signature = _encode(hmac.new(signing_key.encode(), body.encode(), hashlib.sha256).digest())
    return body + '.' + signature

def session_email(token: str | None, signing_key: str | None) -> str | None:
    if not token or not signing_key or len(signing_key) < 32:
        return None
    try:
        body, signature = token.split('.', 1)
        expected = _encode(hmac.new(signing_key.encode(), body.encode(), hashlib.sha256).digest())
        if not secrets.compare_digest(signature, expected):
            return None
        decoded = base64.urlsafe_b64decode(body + '=' * (-len(body) % 4)).decode()
        email, expiry = decoded.rsplit('|', 1)
        return email if int(expiry) > int(time.time()) else None
    except (ValueError, UnicodeDecodeError):
        return None

def require_owner_or_api_key(x_aimn_api_key: str | None = Header(default=None), owner_session: str | None = Cookie(default=None, alias=SESSION_COOKIE)) -> None:
    api_key = getattr(settings, 'admin_api_key', None)
    if api_key and x_aimn_api_key and secrets.compare_digest(x_aimn_api_key, api_key):
        return
    email = session_email(owner_session, getattr(settings, 'session_secret', None))
    owner = getattr(settings, 'owner_email', None)
    if email and owner and secrets.compare_digest(email, owner.lower()):
        return
    if not api_key and not (owner and getattr(settings, 'owner_password_hash', None) and getattr(settings, 'session_secret', None)):
        raise HTTPException(status_code=503, detail='Management API is locked; configure owner sign-in or the machine API key.')
    raise HTTPException(status_code=401, detail='Owner sign-in or valid API key required.')

def require_owner_session(owner_session: str | None = Cookie(default=None, alias=SESSION_COOKIE)) -> str:
    email = session_email(owner_session, getattr(settings, 'session_secret', None))
    owner = getattr(settings, 'owner_email', None)
    if not email or not owner or not secrets.compare_digest(email, owner.lower()):
        raise HTTPException(status_code=401, detail='Owner sign-in required.')
    return email

@auth_router.post('/login')
def login(payload: AuthLogin, response: Response):
    owner = getattr(settings, 'owner_email', None)
    password_hash = getattr(settings, 'owner_password_hash', None)
    signing_key = getattr(settings, 'session_secret', None)
    if not owner or not password_hash or not signing_key or len(signing_key) < 32:
        raise HTTPException(status_code=503, detail='Owner sign-in is not configured.')
    if not secrets.compare_digest(payload.email.strip().lower(), owner.lower()) or not password_matches(payload.password, password_hash):
        raise HTTPException(status_code=401, detail='Invalid email or password.')
    ttl = getattr(settings, 'session_ttl_seconds', 43200)
    response.set_cookie(SESSION_COOKIE, issue_session(owner, signing_key, ttl), max_age=ttl, httponly=True, secure=getattr(settings, 'session_cookie_secure', True), samesite='strict', path='/')
    return {'authenticated': True, 'email': owner}

@auth_router.post('/logout')
def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE, path='/', httponly=True, secure=getattr(settings, 'session_cookie_secure', True), samesite='strict')
    return {'authenticated': False}

@auth_router.get('/me')
def current_owner(email: str = Depends(require_owner_session)):
    return {'authenticated': True, 'email': email}