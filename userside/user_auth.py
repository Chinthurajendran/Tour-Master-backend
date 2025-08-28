from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import exceptions, status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


class _BaseTokenAuth(JWTAuthentication):
    allow_refresh_token = False
    allow_access_token  = True

    def get_validated_token(self, raw_token):
        """
        Force SimpleJWT to validate against RefreshToken or AccessToken
        depending on subclass settings.
        """
        try:
            if self.allow_access_token and not self.allow_refresh_token:
                return AccessToken(raw_token)   # ✅ only access allowed
            elif self.allow_refresh_token and not self.allow_access_token:
                return RefreshToken(raw_token)  # ✅ only refresh allowed
            else:
                # fallback: try both
                try:
                    return AccessToken(raw_token)
                except Exception:
                    return RefreshToken(raw_token)
        except Exception as e:
            raise InvalidToken(f"Token validation failed: {str(e)}")

    def _token_kind_ok(self, validated_token):
        token_type = validated_token.get("token_type")
        return (
            (token_type == "access" and self.allow_access_token) or
            (token_type == "refresh" and self.allow_refresh_token)
        )

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

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

        if not self._token_kind_ok(validated_token):
            msg = (
                "Please provide a refresh token"
                if validated_token.get("token_type") == "access"
                else "Please provide an access token"
            )
            raise exceptions.AuthenticationFailed(detail=msg, code=status.HTTP_403_FORBIDDEN)

        user = self.get_user(validated_token)
        return (user, validated_token)


class AccessTokenAuth(_BaseTokenAuth):
    allow_refresh_token = False
    allow_access_token  = True


class RefreshTokenAuth(_BaseTokenAuth):
    allow_refresh_token = True
    allow_access_token  = False
