"""
Resend email service.
Sends the weekly CloudGuard digest to users who opted in.
"""

import os
import httpx
from typing import Optional

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_FROM    = os.getenv("RESEND_FROM", "CloudGuard <reports@cloudguard.app>")
FRONTEND_URL   = os.getenv("FRONTEND_URL", "https://cloudguard.app")

GRADE_LABEL = {
    "A": ("Great shape", "#22d3ee"),
    "B": ("Good, with room to improve", "#06b6d4"),
    "C": ("Several issues need attention", "#facc15"),
    "D": ("High-risk findings present", "#f97316"),
    "F": ("Critical — act now", "#ef4444"),
}


def send_weekly_digest(
    to_email: str,
    grade: str,
    score: int,
    findings_summary: list[dict],
    scan_id: str,
) -> bool:
    """
    Send a weekly digest email via Resend.
    Returns True on success, False on any error (never raises).

    findings_summary: list of up to 3 dicts with keys: title, severity
    """
    if not RESEND_API_KEY:
        return False

    label, color = GRADE_LABEL.get(grade, ("Unknown", "#64748b"))
    scan_url = f"{FRONTEND_URL}/scan/{scan_id}"

    top_findings_html = ""
    for f in findings_summary[:3]:
        sev_color = {
            "critical": "#ef4444",
            "high":     "#f97316",
            "medium":   "#facc15",
            "low":      "#94a3b8",
        }.get(f["severity"], "#94a3b8")

        top_findings_html += f"""
        <tr>
          <td style="padding:8px 0;border-bottom:1px solid #1e293b;">
            <span style="display:inline-block;width:8px;height:8px;border-radius:50%;
                         background:{sev_color};margin-right:8px;"></span>
            <span style="color:#e2e8f0;font-size:14px;">{f['title']}</span>
          </td>
        </tr>"""

    html_body = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#0f172a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td align="center" style="padding:40px 20px;">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#1e293b;border-radius:16px;overflow:hidden;max-width:600px;">

        <!-- Header -->
        <tr>
          <td style="padding:32px 40px;background:linear-gradient(135deg,#0f172a,#1e293b);
                     border-bottom:1px solid #334155;">
            <p style="margin:0;font-size:20px;font-weight:700;color:#fff;">
              🛡️ CloudGuard Weekly Report
            </p>
            <p style="margin:6px 0 0;font-size:14px;color:#94a3b8;">
              Here's your AWS security summary for this week
            </p>
          </td>
        </tr>

        <!-- Score card -->
        <tr>
          <td style="padding:32px 40px;text-align:center;">
            <p style="margin:0;font-size:96px;font-weight:900;line-height:1;color:{color};">
              {grade}
            </p>
            <p style="margin:8px 0 0;font-size:18px;color:#fff;">{score}/100</p>
            <p style="margin:6px 0 0;font-size:14px;color:#94a3b8;">{label}</p>
          </td>
        </tr>

        <!-- Top findings -->
        {"" if not top_findings_html else f'''
        <tr>
          <td style="padding:0 40px 24px;">
            <p style="margin:0 0 12px;font-size:14px;font-weight:600;
                      text-transform:uppercase;letter-spacing:.08em;color:#64748b;">
              Top Findings
            </p>
            <table width="100%" cellpadding="0" cellspacing="0">
              {top_findings_html}
            </table>
          </td>
        </tr>'''}

        <!-- CTA -->
        <tr>
          <td style="padding:24px 40px 40px;text-align:center;">
            <a href="{scan_url}"
               style="display:inline-block;padding:14px 32px;background:#22d3ee;
                      color:#0f172a;font-weight:700;font-size:15px;border-radius:10px;
                      text-decoration:none;">
              View Full Report →
            </a>
            <p style="margin:20px 0 0;font-size:12px;color:#475569;">
              You're receiving this because you opted into weekly CloudGuard reports.<br>
              <a href="{FRONTEND_URL}/dashboard" style="color:#475569;">Manage preferences</a>
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

    try:
        resp = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type":  "application/json",
            },
            json={
                "from":    RESEND_FROM,
                "to":      [to_email],
                "subject": f"Your CloudGuard weekly report — you're a {grade} this week",
                "html":    html_body,
            },
            timeout=10,
        )
        return resp.status_code == 200
    except Exception:
        return False
