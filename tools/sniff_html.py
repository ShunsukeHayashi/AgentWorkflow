import re

with open("page.html", "r", encoding="utf-8") as f:
    content = f.read()

# Look for script tags with json type
scripts = re.findall(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', content, re.DOTALL)
print(f"Found {len(scripts)} json scripts.")
for i, s in enumerate(scripts):
    print(f"--- Script {i} ---")
    print(s[:200] + "...")

# Look for window.__INITIAL_STATE__ or similar
assignments = re.findall(r'window\.__[A-Z_]+__\s*=\s*({.*?});', content, re.DOTALL)
print(f"Found {len(assignments)} global assignments.")
for i, a in enumerate(assignments):
    print(f"--- Assignment {i} ---")
    print(a[:200] + "...")
