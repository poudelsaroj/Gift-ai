"""Gmail connector tests."""

from __future__ import annotations

import base64

import httpx

from app.connectors.base.types import FetchRequest
from app.connectors.gmail.connector import GmailConnector
from app.core.config import get_settings


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def gmail_config() -> dict:
    return {
        "api_base_url": "https://gmail.googleapis.com/gmail/v1",
        "access_token": "gmail-token",
        "refresh_token": "refresh-token",
        "client_id": "client-id",
        "client_secret": "client-secret",
        "token_url": "https://oauth2.googleapis.com/token",
        "query": "label:gifts",
        "page_size": 10,
        "max_messages_per_sync": 10,
    }


class MockClient:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def __enter__(self) -> MockClient:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def request(self, method: str, url: str, headers=None, params=None, json=None):
        request = httpx.Request(method, url, headers=headers, params=params, json=json)
        if request.url.path.endswith("/users/me/profile"):
            return httpx.Response(
                200,
                json={
                    "emailAddress": "giving@example.org",
                    "messagesTotal": 25,
                    "threadsTotal": 10,
                    "historyId": "500",
                },
                request=request,
            )
        if request.url.path.endswith("/users/me/messages"):
            assert request.url.params.get("maxResults") in {"10", "3", "1"}
            return httpx.Response(
                200,
                json={"messages": [{"id": "msg-3"}, {"id": "msg-2"}, {"id": "msg-1"}], "resultSizeEstimate": 3},
                request=request,
            )
        if request.url.path.endswith("/users/me/messages/msg-3"):
            body_text = _b64url(
                b"Donation notification\n"
                b"Donor: Newest Donor\n"
                b"Email: newest@example.org\n"
                b"Amount: $200.00\n"
                b"Date: 2026-04-06\n"
            )
            return httpx.Response(
                200,
                json={
                    "id": "msg-3",
                    "threadId": "thread-3",
                    "historyId": "503",
                    "internalDate": "1775520000000",
                    "labelIds": ["INBOX", "Label_gifts"],
                    "snippet": "Newest donation notification",
                    "payload": {
                        "headers": [
                            {"name": "Subject", "value": "Donation receipt"},
                            {"name": "From", "value": "Giving Team <giving@example.org>"},
                            {"name": "To", "value": "ops@example.org"},
                        ],
                        "mimeType": "multipart/mixed",
                        "parts": [
                            {
                                "partId": "0",
                                "mimeType": "text/plain",
                                "filename": "",
                                "body": {"size": 120, "data": body_text},
                            }
                        ],
                    },
                },
                request=request,
            )
        if request.url.path.endswith("/users/me/messages/msg-2"):
            body_text = _b64url(
                b"Donation notification\n"
                b"Donor: Middle Donor\n"
                b"Email: middle@example.org\n"
                b"Amount: $150.00\n"
                b"Date: 2026-04-05\n"
            )
            return httpx.Response(
                200,
                json={
                    "id": "msg-2",
                    "threadId": "thread-2",
                    "historyId": "502",
                    "internalDate": "1775433600001",
                    "labelIds": ["INBOX", "Label_gifts"],
                    "snippet": "Middle donation notification",
                    "payload": {
                        "headers": [
                            {"name": "Subject", "value": "Donation receipt"},
                            {"name": "From", "value": "Giving Team <giving@example.org>"},
                            {"name": "To", "value": "ops@example.org"},
                        ],
                        "mimeType": "multipart/mixed",
                        "parts": [
                            {
                                "partId": "0",
                                "mimeType": "text/plain",
                                "filename": "",
                                "body": {"size": 120, "data": body_text},
                            }
                        ],
                    },
                },
                request=request,
            )
        if request.url.path.endswith("/users/me/messages/msg-1"):
            body_text = _b64url(
                b"Donation notification\n"
                b"Donor: Jane Donor\n"
                b"Email: jane@example.org\n"
                b"Amount: $125.00\n"
                b"Date: 2026-04-05\n"
            )
            return httpx.Response(
                200,
                json={
                    "id": "msg-1",
                    "threadId": "thread-1",
                    "historyId": "501",
                    "internalDate": "1775433600000",
                    "labelIds": ["INBOX", "Label_gifts"],
                    "snippet": "Donation notification",
                    "payload": {
                        "headers": [
                            {"name": "Subject", "value": "Donation receipt"},
                            {"name": "From", "value": "Giving Team <giving@example.org>"},
                            {"name": "To", "value": "ops@example.org"},
                        ],
                        "mimeType": "multipart/mixed",
                        "parts": [
                            {
                                "partId": "0",
                                "mimeType": "text/plain",
                                "filename": "",
                                "body": {"size": 120, "data": body_text},
                            },
                            {
                                "partId": "1",
                                "mimeType": "text/csv",
                                "filename": "gift-report.csv",
                                "body": {"size": 140, "attachmentId": "att-1"},
                            },
                        ],
                    },
                },
                request=request,
            )
        if request.url.path.endswith("/users/me/messages/msg-1/attachments/att-1"):
            attachment_body = _b64url(
                b"Donor Name,Donor Email,Donation Amount,Donation Date,Receipt Number\n"
                b"Jane Donor,jane@example.org,125.00,2026-04-05,rcpt-1\n"
            )
            return httpx.Response(200, json={"data": attachment_body}, request=request)
        raise AssertionError(f"Unhandled request: {request.url}")

    def post(self, url: str, data=None, **kwargs):
        request = httpx.Request("POST", url, data=data)
        if url.endswith("/token"):
            return httpx.Response(200, json={"access_token": "gmail-token"}, request=request)
        raise AssertionError(f"Unhandled POST request: {url}")


class RefreshingMockClient(MockClient):
    def request(self, method: str, url: str, headers=None, params=None, json=None):
        request = httpx.Request(method, url, headers=headers, params=params, json=json)
        auth_header = (headers or {}).get("Authorization", "")
        if request.url.path.endswith("/users/me/profile") and auth_header == "Bearer gmail-token":
            return httpx.Response(401, json={"error": {"message": "Invalid Credentials"}}, request=request)
        return super().request(method, url, headers=headers, params=params, json=json)

    def post(self, url: str, data=None, **kwargs):
        request = httpx.Request("POST", url, data=data)
        if url.endswith("/token"):
            return httpx.Response(200, json={"access_token": "fresh-token"}, request=request)
        raise AssertionError(f"Unhandled POST request: {url}")


def test_gmail_test_connection(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setattr("app.connectors.gmail.client.httpx.Client", MockClient)

    connector = GmailConnector(gmail_config())
    response = connector.test_connection()

    assert response["ok"] is True
    assert response["email_address"] == "giving@example.org"


def test_gmail_fetch_emits_message_attachment_and_gift(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "openai-test-key")
    get_settings.cache_clear()
    monkeypatch.setattr("app.connectors.gmail.client.httpx.Client", MockClient)
    monkeypatch.setattr(
        "app.services.openai_email_extraction_service.OpenAIEmailExtractionService.extract",
        lambda self, *, email, source_system: {
            "is_gift_email": True,
            "extraction_summary": "Detected one gift from email.",
            "unsupported_attachments": [],
            "gifts": [
                {
                    "recordType": "gift",
                    "sourceRecordId": f"gift-{email.message_id}",
                    "sourceParentId": email.message_id,
                    "giftId": f"gift-{email.message_id}",
                    "sourceFileId": None,
                    "primaryName": (
                        "Newest Donor" if email.message_id == "msg-3"
                        else "Middle Donor" if email.message_id == "msg-2"
                        else "Jane Donor"
                    ),
                    "primaryEmail": (
                        "newest@example.org" if email.message_id == "msg-3"
                        else "middle@example.org" if email.message_id == "msg-2"
                        else "jane@example.org"
                    ),
                    "donorName": (
                        "Newest Donor" if email.message_id == "msg-3"
                        else "Middle Donor" if email.message_id == "msg-2"
                        else "Jane Donor"
                    ),
                    "donorEmail": (
                        "newest@example.org" if email.message_id == "msg-3"
                        else "middle@example.org" if email.message_id == "msg-2"
                        else "jane@example.org"
                    ),
                    "companyName": None,
                    "amount": "200.00" if email.message_id == "msg-3" else "150.00",
                    "currency": "USD",
                    "recordDate": "2026-04-06" if email.message_id == "msg-3" else "2026-04-05",
                    "giftDate": "2026-04-06" if email.message_id == "msg-3" else "2026-04-05",
                    "paymentType": "email_body",
                    "giftType": "donation",
                    "campaignId": None,
                    "campaignName": "Spring Appeal",
                    "relatedEntityId": email.message_id,
                    "relatedEntityName": "email_body",
                    "receiptNumber": None,
                    "memo": "Imported by OpenAI",
                    "confidenceScore": 0.94,
                    "sourceMedium": "email_body",
                    "sourceFilename": None,
                    "sourceAttachmentId": None,
                    "messageId": email.message_id,
                }
            ],
        },
    )

    connector = GmailConnector(gmail_config())
    connector.typed_config.max_messages_per_sync = 1
    result = connector.fetch(
        FetchRequest(
            run_type="incremental",
            trigger_type="manual",
            cursor_state={"gmail": {"last_internal_date_ms": 1775433600000}},
        )
    )

    object_types = [item.object_type for item in result.items]
    assert "email_message" in object_types
    assert "gift_extract" in object_types
    assert object_types.count("email_message") == 1
    gift_items = [item for item in result.items if item.object_type == "gift_extract"]
    assert {item.payload["primaryEmail"] for item in gift_items} == {"newest@example.org"}
    assert result.cursor_state["gmail"]["last_internal_date_ms"] == 1775520000000
    assert result.metadata["messages_processed"] == 1
    assert result.metadata["processing_scope"] == "incremental_since_last_fetch"


def test_gmail_refreshes_access_token_after_unauthorized(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setattr("app.connectors.gmail.client.httpx.Client", RefreshingMockClient)

    connector = GmailConnector(gmail_config())
    response = connector.test_connection()

    assert response["ok"] is True
    assert connector.runtime_config_updates() == {"access_token": "fresh-token"}


def test_gmail_dedupes_same_gift_between_email_body_and_attachment(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "openai-test-key")
    get_settings.cache_clear()
    monkeypatch.setattr("app.connectors.gmail.client.httpx.Client", MockClient)
    monkeypatch.setattr(
        "app.services.openai_email_extraction_service.OpenAIEmailExtractionService.extract",
        lambda self, *, email, source_system: {
            "is_gift_email": True,
            "extraction_summary": "Detected duplicate gift in body and attachment.",
            "unsupported_attachments": [],
            "gifts": [
                {
                    "recordType": "gift",
                    "sourceRecordId": "gift-body-1",
                    "sourceParentId": email.message_id,
                    "giftId": "gift-body-1",
                    "sourceFileId": None,
                    "primaryName": "Olivia Martinez",
                    "primaryEmail": "olivia@example.org",
                    "donorName": "Olivia Martinez",
                    "donorEmail": "olivia@example.org",
                    "companyName": None,
                    "amount": "8500.00",
                    "currency": "USD",
                    "recordDate": "2026-04-07",
                    "giftDate": "2026-04-07",
                    "paymentType": "email",
                    "giftType": "donation",
                    "campaignId": None,
                    "campaignName": "Gift",
                    "relatedEntityId": email.message_id,
                    "relatedEntityName": "email_body",
                    "receiptNumber": None,
                    "memo": "Body version",
                    "confidenceScore": 0.80,
                    "sourceMedium": "email_body",
                    "sourceFilename": None,
                    "sourceAttachmentId": None,
                    "messageId": email.message_id,
                },
                {
                    "recordType": "gift",
                    "sourceRecordId": "gift-attachment-1",
                    "sourceParentId": email.message_id,
                    "giftId": "gift-attachment-1",
                    "sourceFileId": "gift-report.csv",
                    "primaryName": "Olivia Martinez",
                    "primaryEmail": "olivia@example.org",
                    "donorName": "Olivia Martinez",
                    "donorEmail": "olivia@example.org",
                    "companyName": None,
                    "amount": "8500.00",
                    "currency": "USD",
                    "recordDate": "2026-04-07",
                    "giftDate": "2026-04-07",
                    "paymentType": "email_attachment",
                    "giftType": "donation",
                    "campaignId": None,
                    "campaignName": "Gift",
                    "relatedEntityId": email.message_id,
                    "relatedEntityName": "attachment_csv",
                    "receiptNumber": None,
                    "memo": "Attachment version",
                    "confidenceScore": 0.92,
                    "sourceMedium": "attachment_csv",
                    "sourceFilename": "gift-report.csv",
                    "sourceAttachmentId": "att-1",
                    "messageId": email.message_id,
                },
            ],
        },
    )
    connector = GmailConnector(gmail_config())
    connector.typed_config.max_messages_per_sync = 1
    result = connector.fetch(
        FetchRequest(
            run_type="incremental",
            trigger_type="manual",
            cursor_state={"gmail": {"last_internal_date_ms": 1775433600000}},
        )
    )

    gift_items = [item for item in result.items if item.object_type == "gift_extract"]
    assert len(gift_items) == 1
    assert gift_items[0].payload["sourceMedium"] == "attachment_csv"
    assert gift_items[0].payload["primaryEmail"] == "olivia@example.org"
