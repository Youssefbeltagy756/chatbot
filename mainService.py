import requests
import json
from bs4 import BeautifulSoup, Tag
import re
from urllib.parse import urljoin



url = "https://ocelot.readthedocs.io/en/latest/index.html"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

searchArray = set()

for a in soup.find_all("a", href=True):
    href = a["href"]

    if href.startswith("features/"):
        name = href.split("features/")[1]
        name = name.split("#")[0]      # remove anchors
        name = name.replace(".html", "")  # remove .html

        if name:  # avoid empty
            searchArray.add(name)

# لو عايزه list بدل set
searchArray = sorted(searchArray)

print(searchArray)



# -------------------
# Base URL
# -------------------
BASE_URL = "https://ocelot.readthedocs.io/en/latest/features/"

# -------------------
# Feature pages array
# -------------------
feature_pages = searchArray
# -------------------
# Fetch & clean helpers
# -------------------
def clean_soup(soup):
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    for a in soup.find_all("a", href=True):
        if a["href"].startswith("http"):
            a.decompose()
    return soup

def get_text_preserve_structure(element):
    if element.name in ["pre", "code", "table"]:
        return element.get_text(separator=" ", strip=True) + "\n"
    else:
        return element.get_text(separator=" ", strip=True) + "\n"

def get_clean_text_for_summary(text):
    text = re.sub(r'`[^`]*`', '', text)            # remove inline code
    text = re.sub(r'https?://\S+', '', text)       # remove URLs
    text = re.sub(r'\n+', ' ', text)               # collapse newlines
    text = re.sub(r'\s+', ' ', text)               # collapse spaces
    return text.strip()

# -------------------
# Fetch and chunk function
# -------------------
def fetch_and_chunk(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    soup = clean_soup(soup)

    content = soup.find("div", {"role": "main"}) or soup

    context_chunks = []
    pre_summary_chunks = []

    current_chunk = ""
    current_title = "intro"

    for element in content.descendants:
        if not isinstance(element, Tag):
            continue

        if element.name in ["h1", "h2", "h3"]:
            if current_chunk.strip():
                context_chunks.append(current_chunk.strip())
                pre_summary_chunks.append(get_clean_text_for_summary(current_chunk.strip()))
            current_title = element.get_text(strip=True)
            current_chunk = current_title + "\n"

        elif element.name in ["p", "pre", "code", "table", "ul", "ol"]:
            text = get_text_preserve_structure(element)
            if text.strip():
                current_chunk += text + "\n"

    if current_chunk.strip():
        context_chunks.append(current_chunk.strip())
        pre_summary_chunks.append(get_clean_text_for_summary(current_chunk.strip()))

    return context_chunks, pre_summary_chunks

# -------------------
# Fetch all feature pages
# -------------------
all_context_chunks = []
all_pre_summary_chunks = []

for page_name in feature_pages:
    url = urljoin(BASE_URL, page_name + ".html")
    print(f"Fetching: {url}")
    context_chunks, pre_summary_chunks = fetch_and_chunk(url)
    all_context_chunks.extend(context_chunks)
    all_pre_summary_chunks.extend(pre_summary_chunks)

# -------------------
# Print results
# -------------------

print("\n=== Context Chunks ===")
for i, chunk in enumerate(all_context_chunks):
    print(f"\n--- Chunk {i} ---\n{chunk}\n")

print("\n=== Pre-Summary Chunks ===")
for i, chunk in enumerate(all_pre_summary_chunks):
    print(f"\n--- Chunk {i} ---\n{chunk}\n")