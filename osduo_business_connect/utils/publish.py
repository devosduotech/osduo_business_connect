# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Shared lifecycle helpers for public-facing documents.

Business, Digital Card, Showcase Product and Showcase Service are all
submittable, but each has a separate ``status`` field that defaults to
``Draft``. A submitted record left in ``Draft`` is invisible on every public
page, which is a confusing state for the person who just created it.

Submitting is the publish action. These helpers promote a draft to published
at submit time while preserving an explicit ``Suspended``/``Archived``/
``Unpublished`` choice.
"""


def publish_on_submit(doc, draft_status="Draft", published_status="Published"):
    """Promote ``doc`` to published when it is being submitted.

    Called from ``validate`` so the promoted status is visible to later
    validation (for example "a published business needs a contact method").
    """
    if getattr(doc, "_action", None) == "submit" and doc.status == draft_status:
        doc.status = published_status
    return doc.status
