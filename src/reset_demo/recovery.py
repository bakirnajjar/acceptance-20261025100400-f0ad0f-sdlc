"""Private reset-link issuance; no public route or external delivery."""

import re
from datetime import datetime
from hashlib import sha256

from reset_demo.foundation import Account, AppResources, Notification, ResetToken


class IssuanceError(Exception):
    """A generic, account-independent private issuance failure."""


class RecoveryService:
    """Issue links for synthetic accounts without disclosing eligibility."""

    def __init__(self, resources: AppResources) -> None:
        self._resources = resources

    def request_link(self, identifier: str) -> None:
        """Accept a known account's request if fewer than five are in the last hour.

        Unknown and capped identifiers have the same outward result as an issue.
        The raw bearer link is retained only in the private notification sink.
        """
        normalized = identifier.strip().lower()

        try:

            def create_issue(
                account: Account, now: datetime
            ) -> tuple[ResetToken, Notification]:
                raw_token = self._resources.token_factory()
                if not isinstance(raw_token, str) or not re.fullmatch(
                    r"[A-Za-z0-9_-]+", raw_token
                ):
                    raise ValueError("Invalid reset token")
                digest = sha256(raw_token.encode("ascii")).hexdigest()
                return (
                    ResetToken(digest, account.id, now),
                    Notification(
                        account.synthetic_owner,
                        "reset_link",
                        now,
                        f"/reset/{raw_token}",
                    ),
                )

            self._resources.store.issue_if_eligible(
                normalized, self._resources.now, create_issue, self._resources.sink
            )
        except (RuntimeError, ValueError, TypeError, OSError):
            raise IssuanceError("Reset request could not be processed") from None
