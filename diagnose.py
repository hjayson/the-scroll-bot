#!/usr/bin/env python3
import os, sys, traceback

print("=" * 50)
print("DIAGNOSTIC RUN")
print("=" * 50)

# 1. Env vars
print("\n--- ENV VARS ---")
for k in ["ANTHROPIC_API_KEY","SERPER_API_KEY","GHL_API_KEY","GHL_LOCATION_ID","GHL_USER_ID"]:
    v = os.getenv(k, "")
    print(f"  {k}: {'SET (' + str(len(v)) + ' chars)' if v else 'MISSING'}")

# 2. Imports
print("\n--- IMPORTS ---")
try:
    import anthropic
    print(f"  anthropic: OK (v{anthropic.__version__})")
except Exception as e:
    print(f"  anthropic: FAILED - {e}")

try:
    import requests
    print(f"  requests: OK (v{requests.__version__})")
except Exception as e:
    print(f"  requests: FAILED - {e}")

# 3. Anthropic API
print("\n--- ANTHROPIC API ---")
try:
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=10,
        messages=[{"role": "user", "content": "Reply with just: OK"}]
    )
    print(f"  API call: OK - '{msg.content[0].text}'")
except Exception as e:
    print(f"  API call: FAILED")
    traceback.print_exc()

# 4. Serper API
print("\n--- SERPER API ---")
try:
    import requests
    r = requests.post("https://google.serper.dev/news",
        headers={"X-API-KEY": os.getenv("SERPER_API_KEY",""), "Content-Type": "application/json"},
        json={"q": "AI marketing", "num": 1}, timeout=10)
    print(f"  Status: {r.status_code} - {'OK' if r.status_code == 200 else r.text[:100]}")
except Exception as e:
    print(f"  FAILED: {e}")

# 5. GHL API
print("\n--- GHL API ---")
try:
    import requests
    r = requests.get("https://services.leadconnectorhq.com/contacts/",
        headers={"Authorization": f"Bearer {os.getenv('GHL_API_KEY','')}",
                 "Version": "2021-07-28"},
        params={"locationId": os.getenv("GHL_LOCATION_ID",""), "limit": 1},
        timeout=10)
    print(f"  Status: {r.status_code} - {'OK' if r.status_code == 200 else r.text[:100]}")
except Exception as e:
    print(f"  FAILED: {e}")

print("\n" + "=" * 50)
print("DIAGNOSTIC COMPLETE")
print("=" * 50)
