"""
AI Remediation Service — Claude-powered fix instructions.

Global cache strategy:
  Before calling Claude, we check the DB for any OTHER finding with the same
  (resource_type, title) that already has remediation_cached set.
  This means the 14 unique finding types in the scanner are each only ever
  called once across ALL users — cost approaches $0 at scale.
"""

import os
import json
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)

_client: Anthropic | None = None

def _get_client() -> Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set.")
        _client = Anthropic(api_key=api_key)
    return _client


SYSTEM_PROMPT = """\
You are a cloud security expert specializing in AWS remediation.
Return ONLY a valid JSON object — no markdown, no explanation outside the JSON.
The JSON must have exactly these four fields:
- explanation: 2-3 sentences explaining why this finding is dangerous in plain English
- cli_command: the single most effective AWS CLI command to fix this finding (or "N/A" if not applicable via CLI)
- console_steps: array of 3-6 concise step-by-step instructions for fixing via AWS Console
- risk_level: one of "low", "medium", or "high" — the risk of applying the fix (not the risk of the finding)"""


def call_claude(finding) -> dict:
    """
    Call Claude Sonnet to generate remediation for a finding.
    Uses prompt caching on the system prompt to reduce costs on repeated calls.
    """
    client = _get_client()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Generate a remediation guide for this AWS security finding:\n\n"
                    f"Title: {finding.title}\n"
                    f"Resource Type: {finding.resource_type}\n"
                    f"Resource ID: {finding.resource_id}\n"
                    f"Region: {finding.region or 'global'}\n"
                    f"Description: {finding.description}\n\n"
                    f"Return the JSON object now."
                ),
            }
        ],
    )

    raw = response.content[0].text.strip()
    # Strip markdown code fences if Claude wraps the JSON anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)


def get_remediation(finding, db) -> dict:
    """
    Return remediation for a finding.
    1. Return finding.remediation_cached if already set.
    2. Check DB for another finding with same (resource_type, title) that has a cache.
    3. Call Claude, cache the result on this finding (and it becomes available for step 2 for future callers).
    """
    from ..models import Finding  # avoid circular import

    # Step 1 — this specific finding already has a cached result
    if finding.remediation_cached:
        return finding.remediation_cached

    # Step 2 — look for a global cache hit (same finding type, different instance/user)
    cached = (
        db.query(Finding)
        .filter(
            Finding.resource_type      == finding.resource_type,
            Finding.title              == finding.title,
            Finding.remediation_cached != None,
            Finding.id                 != finding.id,
        )
        .first()
    )
    if cached:
        result = cached.remediation_cached
        finding.remediation_cached = result
        db.commit()
        logger.info("Remediation cache hit (global) for: %s", finding.title)
        return result

    # Step 3 — call Claude
    logger.info("Calling Claude for remediation: %s", finding.title)
    result = call_claude(finding)
    finding.remediation_cached = result
    db.commit()
    return result
