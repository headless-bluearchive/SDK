from __future__ import annotations


class HeadlessBAError(Exception):
    pass


class LoginError(HeadlessBAError):
    pass


class LoginRequiredError(LoginError):
    pass


class AuthenticationError(LoginError):
    pass


class GatewayError(LoginError):
    pass


class ProofTokenError(LoginError):
    pass


class ConfigurationError(HeadlessBAError):
    pass


class RuntimeProfileError(HeadlessBAError):
    pass


class NetworkError(HeadlessBAError):
    pass
