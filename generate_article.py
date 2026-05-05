import os
import random
from datetime import datetime
from slugify import slugify
from groq import Groq

# -----------------------------
# CONFIGURATION
# -----------------------------

CATEGORIES = {
    "hardware": [
        "HP ProDesk 400 G1 DM",
        "Dell OptiPlex 3050 Micro",
        "Lenovo Tiny M720q",
        "Minisforum UM790 Pro",
        "Beelink SER5"
    ],
    "setups": [
        "€150 Proxmox Starter Lab",
        "Silent Proxmox Lab",
        "Low-Power Proxmox Lab",
        "Proxmox + Home Assistant Setup"
    ],
    "tutorials": [
        "How to Install Proxmox (Beginner-Friendly)",
        "Proxmox Backups Explained Simply",
        "USB Passthrough in Proxmox",
        "LXC vs VM — Simple Explanation"
    ],
    "troubleshooting": [
        "Fixing No Network After Installing Proxmox",
        "USB Passthrough Not Working",
        "ZFS Using Too Much RAM",
        "VM Performance Issues"
    ]
}

# Groq model fallback order
MODEL_FALLBACKS = [
    "llama3-8b-8192",
    "llama3-70b-8192",
    "mixtral-8x7b-32768"
]

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# -----------------------------
# SELECT TOPIC
# -----------------------------

category = random.choice(list(CATEGORIES.keys()))
topic = random.choice(CATEGORIES[category])

date = datetime.utcnow().strftime("%Y-%m-%d")
slug = slugify(topic)
filename = f"content/{category}/{date}-{slug}.md"

# Prevent duplicates
if os.path.exists(filename):
    print(f"Skipping: {filename} already exists.")
    exit(0)

os.makedirs(f"content/{category}", exist_ok=True)

# -----------------------------
# PROMPT
# -----------------------------

prompt = f"""
Write a beginner-friendly article for a Proxmox home lab website.

Topic: {topic}
Tone: friendly, warm, encouraging, simple explanations.

Include:
- a short intro
- what the user needs
- step-by-step instructions
- common mistakes
- a friendly conclusion
"""

# -----------------------------
# MODEL FALLBACK LOGIC
# -----------------------------

article = None

for model in MODEL_FALLBACKS:
    try:
        print(f"Trying model: {model}")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        article = response.choices[0].message.content
        print(f"Success with model: {model}")
        break
    except Exception as e:
        print(f"Model {model} failed: {e}")

if article is None:
    print("All models failed. Exiting.")
    exit(1)

# -----------------------------
# WRITE ARTICLE
# -----------------------------

with open(filename, "w") as f:
    f.write(f"---\ntitle: \"{topic}\"\ndate: {date}\ndraft: false\n---\n\n")
    f.write(article)

print(f"Generated article: {filename}")

