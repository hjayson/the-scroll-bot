#!/usr/bin/env python3
"""
The Scroll — Welcome Bot
Runs every 15 minutes. Detects new subscribers from the GHL Newsletter form,
sends them a welcome email with the 30 AI Prompts PDF, and tags them in GHL.
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# ── Load config ─────────────────────────────────────────────
load_dotenv()

GHL_API_KEY        = os.getenv("GHL_API_KEY", "")
GHL_LOCATION_ID    = os.getenv("GHL_LOCATION_ID", "")
FROM_NAME          = os.getenv("FROM_NAME", "Jayson | The Scroll")
FROM_EMAIL         = os.getenv("FROM_EMAIL", "jayson@salesfunnelmarketing.us")
NEWSLETTER_FORM_ID = os.getenv("NEWSLETTER_FORM_ID", "H3x8RB2QY1aofmWEVw00")

GHL_BASE          = "https://services.leadconnectorhq.com"
GHL_USER_ID       = os.getenv("GHL_USER_ID", "")
THE_SCROLL_TAG    = "the-scroll"
WELCOMED_TAG      = "scroll-welcomed"
PDF_URL           = "https://bit.ly/scroll-prompts"
LANDING_PAGE_URL  = "https://www.salesfunnelmarketing.us/post/the-scroll-free-daily-ai-marketing-newsletter-for-small-business-owners"


def ghl_headers():
    return {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version":       "2021-07-28",
        "Content-Type":  "application/json"
    }


# ── Find new subscribers who haven't been welcomed yet ──────
def get_unwelcomed_subscribers():
    """
    Query GHL form submissions for Newsletter form.
    Return contacts that have 'the-scroll' tag but NOT 'scroll-welcomed'.
    """
    subs = []
    page = 1
    limit = 100

    while True:
        try:
            params = {
                "locationId": GHL_LOCATION_ID,
                "formId":     NEWSLETTER_FORM_ID,
                "limit":      limit,
                "page":       page
            }
            resp = requests.get(
                f"{GHL_BASE}/forms/submissions",
                headers=ghl_headers(), params=params, timeout=15
            )
            if resp.status_code != 200:
                print(f"  Warning: GHL form submissions returned {resp.status_code}")
                break

            data        = resp.json()
            submissions = data.get("submissions", [])

            for sub in submissions:
                contact_id = sub.get("contactId", "")
                name       = (sub.get("name") or sub.get("firstName") or "").strip()
                email      = (sub.get("email") or "").strip()

                # Try fieldData if top-level fields are empty
                if not email or not name:
                    for field in sub.get("fieldData", []):
                        fn = (field.get("name") or field.get("id") or "").lower()
                        fv = str(field.get("value") or "").strip()
                        if "email" in fn and fv and not email:
                            email = fv
                        elif fn in ("first_name", "firstname", "name") and fv and not name:
                            name = fv

                if not email or not contact_id:
                    continue
                if not name:
                    name = "Friend"

                # Check if already welcomed by fetching contact tags
                contact_resp = requests.get(
                    f"{GHL_BASE}/contacts/{contact_id}",
                    headers=ghl_headers(), timeout=10
                )
                if contact_resp.status_code == 200:
                    contact = contact_resp.json().get("contact", {})
                    tags    = contact.get("tags", [])
                    if WELCOMED_TAG not in tags:
                        subs.append({"name": name, "email": email, "id": contact_id})

            meta = data.get("meta", {})
            if meta.get("nextPage") is None or len(submissions) < limit:
                break
            page += 1

        except Exception as e:
            print(f"  Warning fetching form submissions: {e}")
            break

    return subs


# ── Tag a contact ────────────────────────────────────────────
def add_tag(contact_id, tag):
    try:
        resp = requests.post(
            f"{GHL_BASE}/contacts/{contact_id}/tags",
            headers=ghl_headers(),
            json={"tags": [tag]},
            timeout=10
        )
        return resp.status_code in (200, 201)
    except Exception as e:
        print(f"  Warning tagging contact {contact_id}: {e}")
        return False


# ── Welcome email HTML ───────────────────────────────────────
def build_welcome_email(name):
    first = name.split()[0] if name else "Friend"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Welcome to The Scroll</title>
</head>
<body style="margin:0;padding:0;background:#f5f5f0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
<table cellpadding="0" cellspacing="0" width="100%" style="background:#f5f5f0;padding:32px 16px;">
  <tr><td align="center">
    <table cellpadding="0" cellspacing="0" width="600" style="max-width:600px;width:100%;">

      <!-- Header -->
      <tr><td style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);border-radius:12px 12px 0 0;padding:36px 40px;text-align:center;">
        <p style="margin:0 0 4px 0;color:#f59e0b;font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;">YOU'RE IN</p>
        <h1 style="margin:0;color:#ffffff;font-size:32px;font-weight:800;letter-spacing:-0.5px;">THE SCROLL</h1>
        <p style="margin:8px 0 0 0;color:#94a3b8;font-size:13px;">AI &amp; Marketing Intelligence · Weekdays</p>
      </td></tr>

      <!-- Body -->
      <tr><td style="background:#ffffff;padding:40px 40px 32px 40px;">

        <p style="margin:0 0 20px 0;color:#1e293b;font-size:17px;line-height:1.6;">Hey {first},</p>

        <p style="margin:0 0 20px 0;color:#334155;font-size:15px;line-height:1.7;">
          Welcome to <strong>The Scroll</strong> — you just made one of the smartest moves for your business this year.
        </p>

        <p style="margin:0 0 20px 0;color:#334155;font-size:15px;line-height:1.7;">
          Starting tomorrow morning, you'll get a sharp, punchy daily email covering the AI tools and social media tactics that are actually working right now — not hype, not theory, just what small business owners need to know.
        </p>

        <!-- PDF CTA Box -->
        <table cellpadding="0" cellspacing="0" width="100%" style="margin:28px 0;">
          <tr><td style="background:linear-gradient(135deg,#fef3c7,#fde68a);border-radius:12px;padding:28px 32px;text-align:center;">
            <p style="margin:0 0 6px 0;color:#92400e;font-size:12px;font-weight:700;letter-spacing:2px;text-transform:uppercase;">🎁 Your Free Gift Is Ready</p>
            <h2 style="margin:0 0 12px 0;color:#1e293b;font-size:22px;font-weight:800;line-height:1.3;">30 AI Prompts for Small Business Owners</h2>
            <p style="margin:0 0 20px 0;color:#374151;font-size:14px;line-height:1.6;">Copy-paste prompts for social media, email, customer service, sales, and more. Plug in your business details — get pro-quality output in seconds.</p>
            <a href="{LANDNG_PAGE_URL}" style="display:inline-block;background:#f59e0b;color:#1a1a2e;font-size:15px;font-weight:800;text-decoration:none;padding:14px 32px;border-radius:8px;letter-spacing:0.3px;">
              ⬇️ Get Your Free PDF
            </a>
          </td></tr>
        </table>

        <p style="margin:0 0 16px 0;color:#334155;font-size:15px;line-height:1.7;"><strong>Here's what lands in your inbox every weekday:</strong></p>

        <table cellpadding="0" cellspacing="0" width="100%">
          {''.join([f'<tr><td style="padding:6px 0;color:#334155;font-size:14px;line-height:1.6;">{"✅"} {item}</td></tr>' for item in [
            "Today's Big Story — explained with a 3-step action plan",
            "Quick Hits — 3 things worth knowing this week",
            "What's Working Right Now — real tactics, real results",
            "AI Prompt of the Day — copy-paste ready for ChatGPT or Claude",
            "AI Tool Spotlight — one tool, one specific way to use it this week",
            "Jayson's Hot Take — bold, honest opinions on AI and marketing"
          ]])}
        </table>

        <p style="margin:28px 0 20px 0;color:#334155;font-size:15px;line-height:1.7;">
          If you ever have a question or want to share what's working in your business, just reply to any issue. I read every email.
        </p>

        <p style="margin:0 0 4px 0;color:#334155;font-size:15px;line-height:1.7;">Talk tomorrow,</p>
        <p style="margin:0;color:#1e293b;font-size:15px;font-weight:700;">— Jayson</p>
        <p style="margin:4px 0 0 0;color:#64748b;font-size:13px;">Founder, Sales Funnel Marketing</p>

      </td></tr>

      <!-- Footer -->
      <tr><td style="background:#1e293b;border-radius:0 0 12px 12px;padding:24px 40px;text-align:center;">
        <p style="margin:0 0 8px 0;color:#94a3b8;font-size:12px;line-height:1.6;">
          You subscribed at <a href="{LANDING_PAGE_URL}" style="color:#f59e0b;text-decoration:none;">The Scroll landing page</a>.
        </p>
        <p style="margin:0;color:#64748b;font-size:11px;">Sales Funnel Marketing · Perrysburg, OH</p>
      </td></tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""


# ── Send welcome email via GHL ───────────────────────────────
def send_welcome_email(contact):
    name  = contact["name"]
    email = contact["email"]
    cid   = contact["id"]
    first = name.split()[0] if name else "Friend"

    subject  = f"🎉 You're in, {first}! Your 30 AI Prompts are ready to download"
    html     = build_welcome_email(name)

    payload = {
        "type":                     "Email",
        "channel":                  "email",
        "contactId":                cid,
        "subject":                  subject,
        "html":                     html,
        "emailFrom":                f"{FROM_NAME} <{FROM_EMAIL}>",
        "userId":                   GHL_USER_ID,
        "locationId":               GHL_LOCATION_ID,
        "attachments":              [],
        "emailReplyMode":           "reply_all",
        "fromOneToOneConversation": True
    }

    try:
        resp = requests.post(
            f"{GHL_BASE}/conversations/messages",
            headers=ghl_headers(),
            json=payload,
            timeout=20
        )
        if resp.status_code in (200, 201):
            print(f"  ✅ Welcome email sent to {name} <{email}>")
            return True
        else:
            print(f"  ❌ Failed to send to {email}: {resp.status_code} {resp.text[:150]}")
            return False
    except Exception as e:
        print(f"  ❌ Error sending to {email}: {e}")
        return False


# ── Main ──────────────────────────────────────────────────
def main():
    print(f"\n📬 The Scroll Welcome Bot — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("─" * 50)

    if not GHL_API_KEY or not GHL_LOCATION_ID:
        print("❌ Missing GHL_API_KEY or GHL_LOCATION_ID in .env")
        return

    print("🔍 Checking for new subscribers to welcome...")
    new_subs = get_unwelcomed_subscribers()

    if not new_subs:
        print("  ✨ No new subscribers to welcome right now.")
        return

    print(f"  Found {len(new_subs)} subscriber(s) to welcome:")

    sent = 0
    for sub in new_subs:
        print(f"\n  → {sub['name']} <{sub['email']}>")

        # Send welcome email
        if send_welcome_email(sub):
            sent += 1
            # Tag as welcomed so we don't send again
            add_tag(sub["id"], WELCOMED_TAG)
            add_tag(sub["id"], THE_SCROLL_TAG)

    print(f"\n{'─' * 50}")
    print(f"✅ Done — welcomed {sent}/{len(new_subs)} new subscriber(s).")


if __name__ == "__main__":
    main()
