
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

PAGE_ID = os.environ["FACEBOOK_PAGE_ID"]
PAGE_TOKEN = os.environ["FACEBOOK_PAGE_TOKEN"]
GEMINI_KEY = os.environ["GEMINI_API_KEY"]

GRAPH_VERSION = "v26.0"
GEMINI_MODEL = "gemini-3.8-flash"


def get_facebook_posts():
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PAGE_ID}/posts"
    params = {
        "fields": "id,message,created_time,permalink_url",
        "limit": 25,
        "access_token": PAGE_TOKEN,
    }

    response = requests.get(url, params=params, timeout=30)
    if not response.ok:
        raise RuntimeError(
            f"Erreur Facebook : HTTP {response.status_code}"
        )

    return response.json().get("data", [])


def ask_gemini(posts):
    instructions = """
Tu es responsable éditorial de l'association française
Ô Bonheur des Nanouts, qui aide les chats.

Analyse les publications Facebook fournies.

Sélectionne uniquement les publications qui peuvent devenir
une actualité utile sur le site :
- sauvetage ou prise en charge d'un chat ;
- adoption ou recherche de famille d'accueil ;
- nouvelles importantes sur un chat ;
- collecte, dons, événements ou actions de l'association ;
- partenariat ou information utile aux visiteurs.

Ignore les simples commentaires, mentions de fans,
remerciements sans information utile et doublons.

N'invente jamais de faits, de dates, de lieux ou de détails.
Ne publie aucune donnée personnelle inutile.
Ne transforme pas un projet en action déjà réalisée.

Retourne uniquement un JSON valide sous cette forme :
{
  "articles": [
    {
      "post_id": "identifiant Facebook exact",
      "keep": true,
      "reason": "Pourquoi cette publication est utile",
      "title": "Titre court",
      "category": "Sauvetages, Adoptions, Actualités ou Actions",
      "content": "Texte d'actualité rédigé en français, fidèle à la publication"
    }
  ]
}

Si aucune publication ne mérite un article, retourne :
{"articles": []}
"""

    payload = {
        "contents": [{
            "parts": [{
                "text": instructions + "\n\nPUBLICATIONS :\n" +
                json.dumps(posts, ensure_ascii=False)
            }]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{GEMINI_MODEL}:generateContent"
    )

    response = requests.post(
        url,
        headers={"x-goog-api-key": GEMINI_KEY},
        json=payload,
        timeout=90,
    )

    if not response.ok:
        raise RuntimeError(
            f"Erreur Gemini : HTTP {response.status_code}"
        )

    result = response.json()
    text = result["candidates"][0]["content"]["parts"][0]["text"]
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())

    return json.loads(text)


def main():
    posts = get_facebook_posts()

    if not posts:
        print("Aucune publication Facebook trouvée.")
        return

    result = ask_gemini(posts)
    articles = result.get("articles", [])

    selected = [
        article for article in articles
        if article.get("keep") is True
        and article.get("post_id")
        and article.get("title")
        and article.get("content")
    ]

    if not selected:
        print("Gemini n'a sélectionné aucune actualité.")
        return

    output_dir = Path("propositions")
    output_dir.mkdir(exist_ok=True)

    for article in selected:
        post = next(
            (p for p in posts if p["id"] == article["post_id"]),
            None
        )

        if not post:
            continue

        safe_id = re.sub(r"[^a-zA-Z0-9_-]", "-", article["post_id"])
        date = post.get("created_time", "")[:10]
        filename = output_dir / f"{date}-{safe_id}.md"

        content = f"""---
title: "{article['title'].replace('"', "'")}"
date: "{date}"
category: "{article.get('category', 'Actualités')}"
source: "{post.get('permalink_url', '')}"
status: "à-valider"
---

{article['content']}

---

**Pourquoi cette publication a été sélectionnée :**
{article.get('reason', 'Information utile pour le site.')}
"""

        filename.write_text(content, encoding="utf-8")
        print(f"Proposition préparée : {filename.name}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Automatisation interrompue : {error}")
        sys.exit(1)
