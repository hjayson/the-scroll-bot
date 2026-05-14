#!/usr/bin/env python3
"""
The Scroll — Daily AI & Social Media Marketing Newsletter Bot
v4: Mobile-first responsive design, CSS gradient hero, full premium content
"""

import os
import sys
import json
import re
import requests
from datetime import datetime
from dotenv import load_dotenv
import anthropic

# ── Load config ────────────────────────────────────────────
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
SERPER_API_KEY    = os.getenv("SERPER_API_KEY", "")
GHL_API_KEY       = os.getenv("GHL_API_KEY", "")
GHL_LOCATION_ID   = os.getenv("GHL_LOCATION_ID", "")
GHL_USER_ID       = os.getenv("GHL_USER_ID", "")
FROM_NAME         = os.getenv("FROM_NAME", "Jayson | The Scroll")
FROM_EMAIL        = os.getenv("FROM_EMAIL", "jayson@salesfunnelmarketing.us")

CLAUDE_MODEL         = "claude-sonnet-4-6"
GHL_BASE             = "https://services.leadconnectorhq.com"
SUBSCRIBERS_FILE     = os.path.expanduser("~/the-scroll-bot/subscribers.json")
NEWSLETTER_FORM_ID   = os.getenv("NEWSLETTER_FORM_ID", "H3x8RB2QY1aofmWEVw00")


def check_config():
    issues = []
    if not ANTHROPIC_API_KEY: issues.append("  • ANTHROPIC_API_KEY missing")
    if not SERPER_API_KEY:    issues.append("  • SERPER_API_KEY missing")
    if not GHL_API_KEY:       issues.append("  • GHL_API_KEY missing")
    if not GHL_LOCATION_ID:   issues.append("  • GHL_LOCATION_ID missing")
    if not GHL_USER_ID:       issues.append("  • GHL_USER_ID missing")
    if issues:
        print("\n❌ Config issues found in .env:")
        for i in issues: print(i)
        sys.exit(1)


# ── News Fetching ───────────────────────────────────────────
def fetch_news():
    print("📰 Fetching today's news...")
    queries = [
        "AI marketing tools small business 2025",
        "Facebook Instagram algorithm update 2025",
        "social media marketing strategy tips",
        "AI automation business productivity",
        "ChatGPT Claude AI business use cases"
    ]
    articles = []
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    for query in queries:
        try:
            resp = requests.post(
                "https://google.serper.dev/news",
                headers=headers,
                json={"q": query, "num": 3},
                timeout=10
            )
            resp.raise_for_status()
            for item in resp.json().get("news", [])[:2]:
                articles.append({
                    "title":   item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "source":  item.get("source", ""),
                    "link":    item.get("link", "")
                })
        except Exception as e:
            print(f"  Warning fetching '{query}': {e}")
    print(f"  Found {len(articles)} news items")
    return articles


# ── Newsletter Generation ───────────────────────────────────
def generate_newsletter(articles):
    print("✍️  Writing newsletter with Claude...")
    news_text = "\n\n".join([
        f"- {a['title']} ({a['source']})\n  {a['snippet']}"
        for a in articles if a['title']
    ]) or "No live news today — write a powerful evergreen issue instead."

    today    = datetime.now().strftime("%A, %B %d, %Y")

    prompt = f"""You are the writer behind "The Scroll" — the most valuable daily newsletter
for small business owners and social media marketers. Your readers are busy, smart people
who want to know what's happening in AI and marketing AND exactly what to do about it.
Today is {today}.

Here are today's news stories to draw from:

{news_text}

Write a complete newsletter issue using EXACTLY the section markers below.
Each section starts on a new line immediately after its marker.
Do not add any text before ---SUBJECT1--- or after ---CLOSE---.

---SUBJECT1---
Subject line option 1: punchy, curiosity-driven, under 50 chars

---SUBJECT2---
Subject line option 2: benefit-led or number format, under 50 chars

---SUBJECT3---
Subject line option 3: bold or contrarian, under 50 chars

---PREVIEW_TEXT---
Preview text (inbox snippet after subject): 1 sentence, 80 chars max

---HOOK---
1-2 punchy sentences that grab attention immediately. Reference something timely or surprising. Make them feel like they NEED to keep reading.

---STORY_TITLE---
Bold punchy headline for the biggest story (max 12 words)

---STORY---
3-4 sentences. Give real context — not just what happened, but WHY it's a big deal in AI and marketing. Make it feel significant.

---STORY_MEANS---
2-3 sentences that directly connect this news to the reader's reality as a small business owner or marketer. Be specific and concrete — not generic advice.

---ACTION1---
Specific, doable this week. Start with a strong action verb. Name the exact tool/platform and what to do with it.

---ACTION2---
Different angle, equally specific. Another strong verb opener.

---ACTION3---
The third move. Could be a mindset shift OR a concrete next-level tactic.

---HIT1---
Quick Hit: news item + 1-line take on why it matters to marketers.

---HIT2---
Quick Hit: different news item + 1-line take.

---HIT3---
Quick Hit: different news item + 1-line take.

---WORKING_NOW---
One specific proven tactic getting real results for businesses on social media RIGHT NOW. Name the platform, the format, and the result. 2-3 sentences. Should feel like insider intel from someone in the trenches.

---STAT---
One powerful statistic about AI, social media, or marketing.
Format: The stat itself on line 1.
"Why it matters:" followed by a 1-line explanation on line 2.

---HOT_TAKE---
Jayson's bold personal opinion on something in AI/marketing. Slightly contrarian or counter-intuitive. 2-3 sentences. First person ("I think...", "My take:"). This is what builds a loyal audience.

---CONTENT_IDEA---
Line 1: The concept/angle — what the post is about (1 sentence)
Line 2: Platform + format (e.g., "Instagram Reel" or "Facebook carousel post")
Line 3: Caption opener they can steal — first 1-2 sentences of the actual caption (make it compelling and specific)

---AI_PROMPT---
Try this in ChatGPT or Claude:
"[write a specific, immediately useful prompt for a small business owner — name the context, the goal, and any constraints to make the output great]"

---PROMPT_EXAMPLE---
Here's what great output looks like:
[2-3 sentences showing a genuinely useful AI response to that prompt. Make it feel real and valuable.]

---AI_TOOL---
**[Tool Name]** — [one sentence: what it does and who it's for]
This week, try this: [one specific action they can take this week with this tool to save time or grow their business]

---REPLY_CTA---
1-2 warm, conversational sentences inviting a reply. Ask a genuine question about their experience with AI or social media this week. Human, not salesy.

---CLOSE---
2 sentences max. Warm personal sign-off from Jayson. Ends with: — Jayson

RULES:
- Write in second person ("you", "your business") except Hot Take (first person)
- No fluff. Every sentence earns its place.
- Sound like the smartest, most plugged-in friend they have
- Action steps must name the specific tool, platform, and move — no vague advice
- Write for someone reading on their phone between meetings"""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=3500,
        messages=[{"role": "user", "content": prompt}]
    )
    content = message.content[0].text
    print("  ✅ Newsletter written")
    return content


# ── Section Parser ──────────────────────────────────────────
def parse_sections(text):
    keys = [
        "SUBJECT1", "SUBJECT2", "SUBJECT3", "PREVIEW_TEXT",
        "HOOK", "STORY_TITLE", "STORY", "STORY_MEANS",
        "ACTION1", "ACTION2", "ACTION3",
        "HIT1", "HIT2", "HIT3",
        "WORKING_NOW", "STAT", "HOT_TAKE", "CONTENT_IDEA",
        "AI_PROMPT", "PROMPT_EXAMPLE", "AI_TOOL",
        "REPLY_CTA", "CLOSE"
    ]
    sections = {}
    for key in keys:
        m = re.search(
            rf"---{key}---\s*(.*?)(?=---[A-Z_0-9]+---|$)",
            text,
            re.DOTALL
        )
        sections[key] = m.group(1).strip() if m else ""
    return sections


def md_bold(text):
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

def nl2br(text):
    return text.replace("\n", "<br>")

def esc(text):
    """Basic HTML escape."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ── HTML Builder ────────────────────────────────────────────
def build_html(newsletter_text):
    today    = datetime.now().strftime("%B %d, %Y")
    dow      = datetime.now().strftime("%A").upper()
    issue_dt = datetime.now().strftime("%B %d, %Y").upper()
    s        = parse_sections(newsletter_text)

    # ── Quick Hits ──
    hits_html = ""
    for h in [s.get("HIT1",""), s.get("HIT2",""), s.get("HIT3","")]:
        if h:
            hits_html += f"""
          <tr><td class="hit-row" style="padding:0 0 16px 0;">
            <table cellpadding="0" cellspacing="0" width="100%"><tr>
              <td width="20" style="vertical-align:top;padding-top:3px;color:#f59e0b;font-size:18px;line-height:1;">&#8226;</td>
              <td class="body-text" style="color:#333;font-size:15px;line-height:1.7;padding-left:10px;">{h}</td>
            </tr></table>
          </td></tr>"""

    # ── Action Steps ──
    actions_html = ""
    for i, key in enumerate(["ACTION1","ACTION2","ACTION3"], 1):
        a = s.get(key,"")
        if a:
            actions_html += f"""
          <tr><td style="padding:0 0 14px 0;">
            <table cellpadding="0" cellspacing="0" width="100%"><tr>
              <td width="32" style="vertical-align:top;">
                <div style="width:24px;height:24px;background:#4ade80;border-radius:50%;text-align:center;line-height:24px;color:#0a0a0a;font-size:12px;font-weight:900;">{i}</div>
              </td>
              <td class="body-text" style="color:#1a2e1a;font-size:15px;line-height:1.7;padding-left:10px;">{a}</td>
            </tr></table>
          </td></tr>"""

    # ── Content Idea ──
    ci_lines         = s.get("CONTENT_IDEA","").split("\n")
    content_concept  = ci_lines[0].strip() if len(ci_lines) > 0 else ""
    content_platform = ci_lines[1].strip() if len(ci_lines) > 1 else ""
    content_caption  = ci_lines[2].strip() if len(ci_lines) > 2 else ""

    # ── Stat lines ──
    stat_lines  = s.get("STAT","").split("\n")
    stat_figure = stat_lines[0].strip() if len(stat_lines) > 0 else ""
    stat_why    = stat_lines[1].strip() if len(stat_lines) > 1 else ""

    # ── Other sections ──
    hook        = s.get("HOOK","")
    story_title = s.get("STORY_TITLE","Today's Big Story")
    story       = s.get("STORY","")
    story_means = s.get("STORY_MEANS","")
    working_now = s.get("WORKING_NOW","")
    hot_take    = s.get("HOT_TAKE","")
    ai_prompt   = nl2br(s.get("AI_PROMPT",""))
    pr_example  = s.get("PROMPT_EXAMPLE","")
    ai_tool     = md_bold(nl2br(s.get("AI_TOOL","")))
    reply_cta   = s.get("REPLY_CTA","")
    close_text  = s.get("CLOSE","Stay sharp out there. — Jayson")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>The Scroll &mdash; {today}</title>
  <style>
    /* ── Reset ── */
    body, table, td, p, a, li {{ -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }}
    table, td {{ mso-table-lspace:0; mso-table-rspace:0; }}
    img {{ -ms-interpolation-mode:bicubic; border:0; outline:none; text-decoration:none; display:block; }}
    body {{ margin:0 !important; padding:0 !important; background:#e2e2e2 !important; }}

    /* ── Mobile ── */
    @media only screen and (max-width: 620px) {{
      .email-wrapper  {{ padding: 0 !important; }}
      .email-container {{ border-radius: 0 !important; width: 100% !important; }}
      .header-pad  {{ padding: 28px 20px 24px !important; }}
      .content-pad {{ padding: 24px 20px !important; }}
      .hero-pad    {{ padding: 28px 20px 24px !important; }}
      .side-pad    {{ padding: 20px !important; }}
      .footer-pad  {{ padding: 20px !important; }}
      .hero-title  {{ font-size: 28px !important; letter-spacing: 2px !important; }}
      .hero-date   {{ font-size: 9px !important; }}
      .hook-text   {{ font-size: 17px !important; }}
      .story-h2    {{ font-size: 20px !important; }}
      .body-text   {{ font-size: 15px !important; }}
      .label-text  {{ font-size: 9px !important; }}
      .stat-text   {{ font-size: 15px !important; }}
      .prompt-text {{ font-size: 13px !important; }}
      .hit-row     {{ padding: 0 0 12px 0 !important; }}
      .dark-section {{ padding: 24px 20px !important; }}
      .tool-pad    {{ padding: 16px 18px !important; }}
      .cta-pad     {{ padding: 18px 20px !important; }}
    }}
  </style>
</head>
<body style="margin:0;padding:0;background:#e2e2e2;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#e2e2e2;">
<tr><td class="email-wrapper" align="center" style="padding:20px 16px 40px;">

  <table class="email-container" width="600" cellpadding="0" cellspacing="0"
    style="max-width:600px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 8px 48px rgba(0,0,0,0.16);">


    <!-- ══════════════════════════════════ -->
    <!-- HEADER                            -->
    <!-- ══════════════════════════════════ -->
    <tr><td class="header-pad" style="background:#0a0a0a;padding:40px 48px 36px;text-align:center;">
      <p class="label-text" style="margin:0 0 10px;color:#4ade80;font-size:10px;letter-spacing:5px;text-transform:uppercase;font-weight:700;">Daily Briefing &bull; AI &amp; Marketing</p>
      <h1 class="hero-title" style="margin:0;color:#ffffff;font-size:38px;font-weight:900;letter-spacing:3px;text-transform:uppercase;font-family:Georgia,'Times New Roman',serif;">The Scroll</h1>
      <div style="width:48px;height:2px;background:#4ade80;margin:14px auto 12px;"></div>
      <p class="hero-date" style="margin:0;color:#555;font-size:11px;letter-spacing:2px;text-transform:uppercase;">{issue_dt}</p>
    </td></tr>


    <!-- ══════════════════════════════════ -->
    <!-- CSS HERO BAND (replaces photo)    -->
    <!-- ══════════════════════════════════ -->
    <tr><td style="padding:0;line-height:0;background:linear-gradient(135deg,#0f172a 0%,#1e3a2f 40%,#0a0a0a 100%);">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td class="hero-pad" style="padding:36px 48px;text-align:center;">
          <p style="margin:0 0 8px;color:#4ade80;font-size:11px;letter-spacing:4px;text-transform:uppercase;font-weight:600;">&#127381; {dow}'S EDITION</p>
          <p style="margin:0;color:rgba(255,255,255,0.15);font-size:52px;font-weight:900;letter-spacing:12px;font-family:Georgia,serif;line-height:1;">&#9632;&#9632;&#9632;</p>
          <p style="margin:8px 0 0;color:rgba(74,222,128,0.6);font-size:10px;letter-spacing:6px;text-transform:uppercase;">AI &bull; SOCIAL &bull; STRATEGY</p>
        </td></tr>
      </table>
    </td></tr>


    <!-- ══════════════════════════════════ -->
    <!-- HOOK                              -->
    <!-- ══════════════════════════════════ -->
    <tr><td class="content-pad" style="padding:36px 48px 28px;border-bottom:1px solid #f0f0f0;">
      <p class="hook-text" style="margin:0;font-size:19px;line-height:1.7;color:#0a0a0a;font-style:italic;font-family:Georgia,'Times New Roman',serif;">{hook}</p>
    </td></tr>


    <!-- ══════════════════════════════════ -->
    <!-- BIG STORY                         -->
    <!-- ══════════════════════════════════ -->
    <tr><td class="content-pad" style="padding:32px 48px 28px;border-bottom:1px solid #f0f0f0;">
      <p class="label-text" style="margin:0 0 10px;color:#4ade80;font-size:10px;letter-spacing:4px;text-transform:uppercase;font-weight:700;">&#128240; Today's Big Story</p>
      <div style="width:44px;height:3px;background:#4ade80;margin:0 0 20px;border-radius:2px;"></div>
      <h2 class="story-h2" style="margin:0 0 16px;color:#0a0a0a;font-size:22px;font-weight:900;line-height:1.3;font-family:Georgia,'Times New Roman',serif;">{story_title}</h2>
      <p class="body-text" style="margin:0 0 22px;color:#333;font-size:15px;line-height:1.75;">{story}</p>

      <!-- What This Means callout -->
      <table cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:22px;">
        <tr><td class="side-pad" style="background:#f0fdf4;border-left:4px solid #4ade80;border-radius:0 8px 8px 0;padding:16px 20px;">
          <p class="label-text" style="margin:0 0 6px;color:#065f46;font-size:10px;letter-spacing:3px;text-transform:uppercase;font-weight:700;">What This Means For Your Business</p>
          <p class="body-text" style="margin:0;color:#064e3b;font-size:15px;line-height:1.7;">{story_means}</p>
        </td></tr>
      </table>

      <!-- Action Steps -->
      <p style="margin:0 0 14px;color:#0a0a0a;font-size:11px;letter-spacing:3px;text-transform:uppercase;font-weight:700;">Your 3-Step Action Plan</p>
      <table cellpadding="0" cellspacing="0" width="100%">
        {actions_html}
      </table>
    </td></tr>


    <!-- ══════════════════════════════════ -->
    <!-- QUICK HITS                        -->
    <!-- ══════════════════════════════════ -->
    <tr><td class="content-pad" style="padding:28px 48px 20px;border-bottom:1px solid #f0f0f0;">
      <p class="label-text" style="margin:0 0 10px;color:#f59e0b;font-size:10px;letter-spacing:4px;text-transform:uppercase;font-weight:700;">&#9889; Quick Hits</p>
      <div style="width:44px;height:3px;background:#f59e0b;margin:0 0 18px;border-radius:2px;"></div>
      <table cellpadding="0" cellspacing="0" width="100%">
        {hits_html}
      </table>
    </td></tr>


    <!-- ══════════════════════════════════ -->
    <!-- WHAT'S WORKING RIGHT NOW          -->
    <!-- ══════════════════════════════════ -->
    <tr><td class="dark-section" style="background:#0f172a;padding:28px 48px;border-bottom:1px solid #1e293b;">
      <p class="label-text" style="margin:0 0 10px;color:#38bdf8;font-size:10px;letter-spacing:4px;text-transform:uppercase;font-weight:700;">&#128293; What's Working Right Now</p>
      <div style="width:44px;height:3px;background:#38bdf8;margin:0 0 16px;border-radius:2px;"></div>
      <p class="body-text" style="margin:0;color:#e2e8f0;font-size:15px;line-height:1.75;">{working_now}</p>
    </td></tr>


    <!-- ══════════════════════════════════ -->
    <!-- STAT OF THE DAY                   -->
    <!-- ══════════════════════════════════ -->
    <tr><td class="content-pad" style="padding:28px 48px;border-bottom:1px solid #f0f0f0;text-align:center;">
      <p class="label-text" style="margin:0 0 16px;color:#6b7280;font-size:10px;letter-spacing:4px;text-transform:uppercase;font-weight:700;">&#128202; Stat of the Day</p>
      <table cellpadding="0" cellspacing="0" width="100%">
        <tr><td style="background:#f9fafb;border-radius:12px;border:1px solid #e5e7eb;padding:22px 24px;text-align:center;">
          <p class="stat-text" style="margin:0 0 10px;color:#0a0a0a;font-size:17px;line-height:1.6;font-style:italic;font-family:Georgia,serif;font-weight:700;">{stat_figure}</p>
          <p class="body-text" style="margin:0;color:#6b7280;font-size:14px;line-height:1.6;">{stat_why}</p>
        </td></tr>
      </table>
    </td></tr>


    <!-- ══════════════════════════════════ -->
    <!-- HOT TAKE                          -->
    <!-- ══════════════════════════════════ -->
    <tr><td class="side-pad" style="background:#fff7ed;border-left:4px solid #f97316;padding:24px 44px;border-bottom:1px solid #f0f0f0;">
      <p class="label-text" style="margin:0 0 8px;color:#c2410c;font-size:10px;letter-spacing:4px;text-transform:uppercase;font-weight:700;">&#128293; Jayson's Hot Take</p>
      <p class="body-text" style="margin:0;color:#431407;font-size:15px;line-height:1.75;font-style:italic;">{hot_take}</p>
    </td></tr>


    <!-- ══════════════════════════════════ -->
    <!-- CONTENT IDEA OF THE WEEK          -->
    <!-- ══════════════════════════════════ -->
    <tr><td class="content-pad" style="padding:28px 48px;border-bottom:1px solid #f0f0f0;">
      <p class="label-text" style="margin:0 0 10px;color:#6366f1;font-size:10px;letter-spacing:4px;text-transform:uppercase;font-weight:700;">&#128197; Content Idea of the Week</p>
      <div style="width:44px;height:3px;background:#6366f1;margin:0 0 18px;border-radius:2px;"></div>
      <table cellpadding="0" cellspacing="0" width="100%" style="border-radius:10px;overflow:hidden;border:1px solid #e0e7ff;">
        <tr><td style="background:#6366f1;padding:12px 18px;">
          <p class="body-text" style="margin:0;color:#fff;font-size:14px;font-weight:700;line-height:1.4;">{content_concept}</p>
        </td></tr>
        <tr><td class="tool-pad" style="background:#fafafe;padding:16px 18px;">
          <p class="label-text" style="margin:0 0 3px;color:#7c3aed;font-size:10px;letter-spacing:2px;text-transform:uppercase;font-weight:700;">Platform &amp; Format</p>
          <p class="body-text" style="margin:0 0 14px;color:#4c1d95;font-size:14px;">{content_platform}</p>
          <p class="label-text" style="margin:0 0 5px;color:#7c3aed;font-size:10px;letter-spacing:2px;text-transform:uppercase;font-weight:700;">Steal This Caption Opener</p>
          <p class="body-text" style="margin:0;color:#1e1b4b;font-size:14px;line-height:1.65;font-style:italic;">"{content_caption}"</p>
        </td></tr>
      </table>
    </td></tr>


    <!-- ══════════════════════════════════ -->
    <!-- AI PROMPT OF THE DAY             -->
    <!-- ══════════════════════════════════ -->
    <tr><td class="content-pad" style="padding:28px 48px;border-bottom:1px solid #f0f0f0;">
      <p class="label-text" style="margin:0 0 10px;color:#8b5cf6;font-size:10px;letter-spacing:4px;text-transform:uppercase;font-weight:700;">&#129302; AI Prompt of the Day</p>
      <div style="width:44px;height:3px;background:#8b5cf6;margin:0 0 18px;border-radius:2px;"></div>

      <!-- Dark prompt box -->
      <table cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:14px;">
        <tr><td style="background:#1e1b2e;border-radius:10px;padding:20px 22px;">
          <p class="label-text" style="margin:0 0 10px;color:#a78bfa;font-size:10px;letter-spacing:3px;text-transform:uppercase;font-weight:700;">Copy &amp; Paste &#8594; ChatGPT or Claude</p>
          <p class="prompt-text" style="margin:0;color:#e9d5ff;font-size:14px;line-height:1.75;font-family:'Courier New',Courier,monospace;">{ai_prompt}</p>
        </td></tr>
      </table>

      <!-- Example output -->
      <table cellpadding="0" cellspacing="0" width="100%">
        <tr><td style="background:#faf5ff;border-left:3px solid #8b5cf6;border-radius:0 8px 8px 0;padding:16px 20px;">
          <p class="body-text" style="margin:0;color:#6b21a8;font-size:14px;line-height:1.7;">{pr_example}</p>
        </td></tr>
      </table>
    </td></tr>


    <!-- ══════════════════════════════════ -->
    <!-- AI TOOL SPOTLIGHT                 -->
    <!-- ══════════════════════════════════ -->
    <tr><td class="content-pad" style="padding:0 48px 28px;">
      <table cellpadding="0" cellspacing="0" width="100%" style="border-radius:10px;overflow:hidden;border:1px solid #fcd34d;">
        <tr><td style="background:#f59e0b;padding:10px 18px;">
          <p class="label-text" style="margin:0;color:#fff;font-size:10px;letter-spacing:4px;text-transform:uppercase;font-weight:700;">&#128161; AI Tool Spotlight</p>
        </td></tr>
        <tr><td class="tool-pad" style="background:#fffbeb;padding:18px 20px;">
          <p class="body-text" style="margin:0;color:#78350f;font-size:15px;line-height:1.75;">{ai_tool}</p>
        </td></tr>
      </table>
    </td></tr>


    <!-- ══════════════════════════════════ -->
    <!-- REPLY CTA                         -->
    <!-- ══════════════════════════════════ -->
    <tr><td class="content-pad" style="padding:0 48px 28px;">
      <table cellpadding="0" cellspacing="0" width="100%" style="border-radius:10px;border:1px solid #e5e7eb;background:#f9fafb;">
        <tr><td class="cta-pad" style="padding:20px 22px;">
          <p style="margin:0 0 8px;font-size:22px;">&#128172;</p>
          <p class="body-text" style="margin:0;color:#374151;font-size:15px;line-height:1.7;">{reply_cta}</p>
        </td></tr>
      </table>
    </td></tr>


    <!-- ══════════════════════════════════ -->
    <!-- CLOSE                             -->
    <!-- ══════════════════════════════════ -->
    <tr><td class="content-pad" style="padding:4px 48px 32px;border-top:1px solid #f0f0f0;">
      <p class="body-text" style="margin:0;color:#555;font-size:15px;line-height:1.7;font-style:italic;">{close_text}</p>
    </td></tr>


    <!-- ══════════════════════════════════ -->
    <!-- FOOTER                            -->
    <!-- ══════════════════════════════════ -->
    <tr><td class="footer-pad" style="background:#0a0a0a;padding:24px 48px;border-radius:0 0 16px 16px;">
      <p style="margin:0 0 6px;color:#4ade80;font-size:11px;text-align:center;font-weight:700;letter-spacing:3px;text-transform:uppercase;">The Scroll</p>
      <p style="margin:0;color:#444;font-size:11px;text-align:center;line-height:1.9;">
        Sent by Jayson Hines &bull; Sales Funnel Marketing<br>
        <a href="mailto:jayson@salesfunnelmarketing.us" style="color:#4ade80;text-decoration:none;">jayson@salesfunnelmarketing.us</a>
      </p>
    </td></tr>


  </table>
</td></tr>
</table>
</body>
</html>"""


# ── Subscribers ─────────────────────────────────────────────
THE_SCROLL_TAG = "the-scroll"

def get_subscribers_from_ghl():
    """Pull all contacts tagged 'the-scroll' directly from GHL — fully automatic."""
    if not GHL_API_KEY or not GHL_LOCATION_ID:
        return []
    headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version":       "2021-07-28",
        "Content-Type":  "application/json"
    }
    subs    = []
    page    = 1
    limit   = 100
    while True:
        try:
            params = {
                "locationId": GHL_LOCATION_ID,
                "tags":       THE_SCROLL_TAG,
                "limit":      limit,
                "skip":       (page - 1) * limit
            }
            resp = requests.get(
                f"{GHL_BASE}/contacts/",
                headers=headers, params=params, timeout=15
            )
            if resp.status_code != 200:
                print(f"  Warning: GHL contacts query returned {resp.status_code}")
                break
            data     = resp.json()
            contacts = data.get("contacts", [])
            for c in contacts:
                emails = c.get("email", "") or ""
                name   = (c.get("firstName") or c.get("name") or "Subscriber").strip()
                cid    = c.get("id", "")
                if emails and cid:
                    subs.append({"name": name, "email": emails, "id": cid})
            if len(contacts) < limit:
                break
            page += 1
        except Exception as e:
            print(f"  Warning fetching GHL contacts: {e}")
            break
    return subs


def tag_contact_in_ghl(contact_id):
    """Add the-scroll tag to a GHL contact so they get future issues automatically."""
    headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version":       "2021-07-28",
        "Content-Type":  "application/json"
    }
    try:
        resp = requests.post(
            f"{GHL_BASE}/contacts/{contact_id}/tags",
            headers=headers,
            json={"tags": [THE_SCROLL_TAG]},
            timeout=10
        )
        if resp.status_code in (200, 201):
            print(f"  ✅ Tagged contact {contact_id} as '{THE_SCROLL_TAG}'")
            return True
        else:
            print(f"  Warning: Could not tag contact — {resp.status_code}: {resp.text[:100]}")
    except Exception as e:
        print(f"  Warning tagging contact: {e}")
    return False


def get_subscribers_from_form():
    """
    Pull new subscribers from the Newsletter form submissions directly.
    Tags each contact with 'the-scroll' automatically — no GHL workflow needed.
    Returns a list of subscriber dicts for anyone not already tagged.
    """
    if not GHL_API_KEY or not GHL_LOCATION_ID or not NEWSLETTER_FORM_ID:
        return []
    headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version":       "2021-07-28",
        "Content-Type":  "application/json"
    }
    new_subs = []
    page     = 1
    limit    = 100
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
                headers=headers, params=params, timeout=15
            )
            if resp.status_code != 200:
                print(f"  Warning: GHL form submissions returned {resp.status_code}")
                break
            data        = resp.json()
            submissions = data.get("submissions", [])
            for sub in submissions:
                contact_id = sub.get("contactId", "")
                # Name: try direct fields or fieldData array
                name  = (sub.get("name") or sub.get("firstName") or "").strip()
                email = (sub.get("email") or "").strip()
                # Some GHL versions nest data in fieldData
                if not email:
                    for field in sub.get("fieldData", []):
                        fn = (field.get("name") or field.get("id") or "").lower()
                        fv = str(field.get("value") or "").strip()
                        if "email" in fn and fv:
                            email = fv
                        elif fn in ("first_name", "firstname", "name") and fv and not name:
                            name = fv
                if not email or not contact_id:
                    continue
                if not name:
                    name = "Subscriber"
                # Auto-tag the contact so future tag-based queries find them
                tag_contact_in_ghl(contact_id)
                new_subs.append({"name": name, "email": email, "id": contact_id})
            meta = data.get("meta", {})
            if meta.get("nextPage") is None or len(submissions) < limit:
                break
            page += 1
        except Exception as e:
            print(f"  Warning fetching form submissions: {e}")
            break
    return new_subs


def get_subscribers():
    """
    Primary: fetch live from GHL by tag (fully automatic — all subscribers).
    Also syncs any new form submissions and tags them, so future runs find them via tag.
    Fallback: read from subscribers.json if GHL returns nothing.
    """
    print("  📋 Fetching subscribers from GHL (tag: 'the-scroll')...")
    subs = get_subscribers_from_ghl()

    # Also pull from Newsletter form — auto-tags each submitter going forward
    print("  📝 Checking Newsletter form submissions for new subscribers...")
    form_subs = get_subscribers_from_form()
    if form_subs:
        # Merge, deduplicate by email
        existing_emails = {s["email"].lower() for s in subs}
        new_count = 0
        for fs in form_subs:
            if fs["email"].lower() not in existing_emails:
                subs.append(fs)
                existing_emails.add(fs["email"].lower())
                new_count += 1
        if new_count:
            print(f"  ➕ Added {new_count} new subscriber(s) from form submissions")

    if subs:
        print(f"  Found {len(subs)} subscriber(s) in GHL")
        return subs

    # Fallback to local file
    print("  ⚠️  No GHL subscribers found — falling back to subscribers.json")
    if not os.path.exists(SUBSCRIBERS_FILE):
        print("  No subscribers.json found either.")
        print("  Add: python3 newsletter_bot.py add \"First\" \"Last\" \"email\" \"ghl_contact_id\"")
        return []
    with open(SUBSCRIBERS_FILE) as f:
        subs = json.load(f)
    print(f"  Found {len(subs)} subscriber(s) in local file")
    return subs


# ── Send ────────────────────────────────────────────────────
def send_newsletter(html_body, subscribers, subject):
    if not subscribers:
        print("No subscribers — nothing to send.")
        return 0

    email_from = f"{FROM_NAME} <{FROM_EMAIL}>"
    headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version":       "2021-07-28",
        "Content-Type":  "application/json"
    }

    sent = 0
    print(f"📤 Sending to {len(subscribers)} subscriber(s)...")
    print(f"   Subject: {subject}")

    for sub in subscribers:
        payload = {
            "contactId":                sub["id"],
            "subject":                  subject,
            "html":                     html_body,
            "emailFrom":                email_from,
            "userId":                   GHL_USER_ID,
            "attachments":              [],
            "type":                     "Email",
            "channel":                  "email",
            "locationId":               GHL_LOCATION_ID,
            "emailReplyMode":           "reply_all",
            "fromOneToOneConversation": True
        }
        try:
            resp = requests.post(
                f"{GHL_BASE}/conversations/messages",
                headers=headers,
                json=payload,
                timeout=15
            )
            if resp.status_code in (200, 201):
                print(f"  ✅ {sub['email']} — sent!")
                sent += 1
            else:
                print(f"  ❌ {sub['email']} — {resp.status_code}: {resp.text[:300]}")
        except Exception as e:
            print(f"  ❌ {sub['email']} — error: {e}")

    print(f"\n  Sent {sent}/{len(subscribers)}")
    return sent


def add_subscriber(first, last, email, contact_id):
    """Add subscriber to local JSON AND tag them in GHL for automatic future sends."""
    # Tag in GHL first
    tagged = tag_contact_in_ghl(contact_id)
    if not tagged:
        print("  ⚠️  Could not tag in GHL — adding to local file only")

    # Always keep local file as backup
    subs = []
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE) as f:
            subs = json.load(f)
    if any(s["email"] == email for s in subs):
        print(f"  {email} is already in subscribers.json")
    else:
        subs.append({"name": first, "email": email, "id": contact_id})
        with open(SUBSCRIBERS_FILE, "w") as f:
            json.dump(subs, f, indent=2)
    print(f"✅ Added {first} {last} ({email}) — tagged '{THE_SCROLL_TAG}' in GHL")


# ── Main ────────────────────────────────────────────────────
if __name__ == "__main__":

    if len(sys.argv) == 6 and sys.argv[1] == "add":
        check_config()
        add_subscriber(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        sys.exit(0)

    print("\n══════════════════════════════════════════════════")
    print("   THE SCROLL — Newsletter Bot v4 (Mobile-First)")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("══════════════════════════════════════════════════\n")

    check_config()

    articles   = fetch_news()
    newsletter = generate_newsletter(articles)
    sections   = parse_sections(newsletter)

    # Print all subject line options to console
    print("\n📬 Subject Line Options:")
    print(f"  1️⃣   {sections.get('SUBJECT1','')}")
    print(f"  2️⃣   {sections.get('SUBJECT2','')}")
    print(f"  3️⃣   {sections.get('SUBJECT3','')}")
    print(f"\n  ✉️  Preview text: {sections.get('PREVIEW_TEXT','')}\n")

    # Default to subject 1 for automation
    subject = sections.get("SUBJECT1") or f"The Scroll — {datetime.now().strftime('%B %d')}"

    html = build_html(newsletter)
    subs = get_subscribers()

    # Test mode: TEST_EMAIL=you@example.com filters send to just that one recipient
    test_email = os.getenv("TEST_EMAIL", "").strip().lower()
    if test_email:
        original_count = len(subs)
        subs = [s for s in subs if s.get("email", "").strip().lower() == test_email]
        if subs:
            print(f"\n🧪 TEST MODE: filtered {original_count} subscribers → 1 recipient ({test_email})\n")
        else:
            print(f"\n⚠️  TEST MODE: no subscriber found in GHL matching {test_email}")
            print(f"   Tag yourself as 'the-scroll' in GHL first, then re-run.\n")
            sys.exit(0)

    sent = send_newsletter(html, subs, subject)

    print(f"\n🎉 Done! The Scroll sent to {sent} subscriber(s).\n")
