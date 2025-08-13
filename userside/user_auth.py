# auth_backends.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import exceptions, status
from rest_framework.permissions import BasePermission


class _BaseTokenAuth(JWTAuthentication):
    """
    Shared logic: read header, validate token, check user role.
    Sub‑classes decide whether ACCESS or REFRESH is allowed.
    """

    allow_refresh_token = False          # overridden below
    allow_access_token  = True           # overridden below

    def _token_kind_ok(self, validated_token):
        token_type = validated_token.get("token_type")
        if token_type == "access" and self.allow_access_token:
            return True
        if token_type == "refresh" and self.allow_refresh_token:
            return True
        return False

    def authenticate(self, request):
        """
        Returns (user, token) on success, raises AuthenticationFailed otherwise.
        """
        header = self.get_header(request)
        if header is None:
            return None                   # let other auth backends try

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except (TokenError, InvalidToken):
            raise exceptions.AuthenticationFailed(
                detail="Invalid or expired token",
                code=status.HTTP_401_UNAUTHORIZED,
            )

        # ── Access vs Refresh check ─────────────────────────────
        if not self._token_kind_ok(validated_token):
            msg = (
                "Please provide a refresh token"
                if validated_token.get("token_type") == "access"
                else "Please provide an access token"
            )
            raise exceptions.AuthenticationFailed(
                detail=msg,
                code=status.HTTP_403_FORBIDDEN,
            )

        # ── Role check (inside payload) ─────────────────────────
        # user_role = validated_token.get("user", {}).get("user_role")
        # if user_role != "user":
        #     raise exceptions.PermissionDenied(
        #         detail="Access denied! Only users are allowed.",
        #         code=status.HTTP_403_FORBIDDEN,
        #     )

        # Optionally: JTI blacklist test goes here…

        user = self.get_user(validated_token)
        return (user, validated_token)


class AccessTokenAuth(_BaseTokenAuth):
    """Accept **access** tokens only (like your AccessTokenBearer)."""
    allow_refresh_token = False
    allow_access_token  = True


class RefreshTokenAuth(_BaseTokenAuth):
    """Accept **refresh** tokens only (like your RefreshTokenBearer)."""
    allow_refresh_token = True
    allow_access_token  = False
