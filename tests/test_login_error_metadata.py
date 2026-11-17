from core.error import GatewayError


def test_gateway_error_retains_safe_metadata_only():
    error = GatewayError.from_response(
        "Account_CheckNexon returned Error",
        {
            "parsed": {"Protocol": -1, "ErrorCode": 5, "NpToken": "secret-token", "Message": "secret-body"},
            "http": {"status_code": 200, "url": "https://example.invalid/?token=secret-query"},
        },
        stage="Account_CheckNexon",
        client_version="1.96.474931",
    )
    assert error.error_code == 5
    assert error.error_name == "InternalServerError"
    assert error.protocol == -1
    assert error.http_status == 200
    assert error.stage == "Account_CheckNexon"
    assert error.client_version == "1.96.474931"
    assert "ErrorCode=5" in str(error)
    assert "secret" not in str(error) + repr(vars(error))


def test_gateway_error_preserves_legacy_constructor():
    error = GatewayError("original message")
    assert str(error) == "original message"
    assert error.error_code is None


def test_gateway_error_handles_missing_or_malformed_metadata():
    error = GatewayError.from_response(
        "failed", {"parsed": {"ErrorCode": "not-a-number"}, "http": None}, stage="Account_CheckNexon"
    )
    assert error.error_code is None
    assert error.http_status is None
    assert str(error) == "failed"
