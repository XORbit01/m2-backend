"""
JWT authentication middleware for API endpoints.

Validates Bearer token on /api/ requests and sets request.user.
Skips public paths: login, token refresh, schema, docs.
"""

import logging

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

# Paths that do not require JWT (public endpoints)
JWT_SKIP_PATHS = (
    "/api/v1/auth/login/",
    "/api/v1/auth/token/refresh/",
    "/api/schema/",
    "/api/docs/",
)


def _should_skip_jwt(path: str) -> bool:
    """Return True if path should skip JWT validation."""
    path_normalized = path.rstrip("/") or "/"
    return any(
        path_normalized == p.rstrip("/") or path_normalized.startswith(p.rstrip("/") + "/")
        for p in JWT_SKIP_PATHS
    )


class JwtAuthenticationMiddleware(MiddlewareMixin):
    """
    Validates JWT Bearer token for /api/ requests and sets request.user.
    """

    def process_request(self, request):
        if not request.path.startswith("/api/"):
            return None

        if _should_skip_jwt(request.path):
            return None

        try:
            from rest_framework_simplejwt.authentication import \
                JWTAuthentication

            auth = JWTAuthentication()
            result = auth.authenticate(request)
            if result:
                request.user, request.auth = result
        except Exception as e:
            logger.debug("JWT auth failed: %s", e)
        return None
