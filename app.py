import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time

st.title("🛍️ Vinted Scanner")

urls_input = st.text_area("Colle tes liens Vinted ici (1 par ligne)")

def scrape(urls):

    headers = {"User-Agent": "Mozilla/5.0"}
    results = []

    for url in urls:

        status = "🔴 Disponible"
        price = None
        image = None

        try:
            r = requests.get(url, headers=headers, timeout=20)
            soup = BeautifulSoup(r.text, "html.parser")

            # STATUS
            status_tag = soup.select_one('[data-testid="item-status--content"]')

            if status_tag:
                raw = status_tag.get_text(strip=True).lower()
                if "vendu" in raw:
                    status = "✅ Vendu"
                elif "réservé" in raw:
                    status = "🟠 Réservé"
                else:
                    status = "🔴 Disponible"
            else:
                text = soup.get_text(" ", strip=True).lower()
                if "vendu" in text:
                    status = "✅ Vendu"
                elif "réservé" in text:
                    status = "🟠 Réservé"
                else:
                    status = "🔴 Disponible"

            # PRICE
            price_tag = soup.select_one('p.web_ui__Text__subtitle.web_ui__Text__left')
            if price_tag:
                price = price_tag.get_text(strip=True)
            else:
                for p in soup.find_all("p"):
                    if "€" in p.get_text():
                        price = p.get_text(strip=True)
                        break

            if price:
                price = price.replace("\xa0", " ").strip()

            # IMAGE
            img_tag = soup.select_one('img[data-testid="item-photo-1--img"]')
            if img_tag:
                image = img_tag.get("src")
            else:
                og = soup.select_one('meta[property="og:image"]')
                if og:
                    image = og.get("content")

            results.append([url, status, price, image])

        except:
            results.append([url, "❌ Erreur", None, None])

        time.sleep(random.randint(2, 4))

    return pd.DataFrame(results, columns=["URL", "Statut", "Prix", "Image"])


if st.button("Analyser"):
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    if len(urls) == 0:
        st.warning("Ajoute des liens")
    else:
        df = scrape(urls)

        st.dataframe(df)

        st.download_button(
            "📥 Télécharger CSV",
            df.to_csv(index=False),
            "vinted_resultats.csv",
            "text/csv"
        )
