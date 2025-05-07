import os
import shutil
import json
import requests
import pdfkit
from bs4 import BeautifulSoup
import mwparserfromhell
from dotenv import load_dotenv

def save_pdf(title, output_dir):
    pdf_output_path = os.path.join(output_dir, f"{title}.pdf")
    url = f"https://en.wikipedia.org/wiki/{title}"
    pdfkit.from_url(url, pdf_output_path)
    return

def save_wikitext(title, output_dir):
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&titles={title}"
    res = requests.get(url).json()
    wikitext_raw = next(iter(res["query"]["pages"].values()))["revisions"][0]["*"]
    with open(os.path.join(output_dir, "wikitext.txt"), "w", encoding="utf-8") as f:
        f.write(wikitext_raw)
    return 


def save_json(title, output_dir):
    """"
    Save JSON from html
    """
    url = f"https://en.wikipedia.org/w/api.php?action=parse&format=json&page={title}"
    html = requests.get(url).json()['parse']['text']['*']
    soup = BeautifulSoup(html, 'html.parser')

    html_sections = []
    current = {"title": "Lead", "content": []}
    for tag in soup.find_all(['h2', 'p']):
        if tag.name == 'h2':
            if current["content"]:
                html_sections.append(current)
            current = {"title": tag.get_text(strip=True), "content": []}
        elif tag.name == 'p':
            text = tag.get_text(strip=True)
            if text:
                current["content"].append(text)
    html_sections.append(current)
    with open(os.path.join(output_dir, "html_sections.json"), "w", encoding="utf-8") as f:
        json.dump(html_sections, f, indent=2, ensure_ascii=False)
    return

def main(title, output_dir):
    save_pdf(title, output_dir)
    save_wikitext(title, output_dir)
    save_json(title, output_dir)
    return


if __name__ == "__main__":

    load_dotenv()

    title = os.getenv("WIKIPEDIA_TITLE")
    output_dir = os.path.join("../output", title)

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    main(title, output_dir)

