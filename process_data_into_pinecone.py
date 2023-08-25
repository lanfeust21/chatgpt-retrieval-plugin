import os
import uuid
import json
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import requests
from requests.adapters import HTTPAdapter, Retry
from tqdm.auto import tqdm
from datetime import datetime
from dotenv import load_dotenv

def adapt_path_for_filename(path):
    # Replace / with _
    adapted_path = path.replace("/", "_")
    # Replace \ with _
    adapted_path = adapted_path.replace("\\", "_")
    # Replace : with _
    adapted_path = adapted_path.replace(":", "_")
    # Replace spaces with _
    adapted_path = adapted_path.replace(" ", "_")
    return adapted_path

def publish_documents(documents):
    BEARER_TOKEN = os.environ.get("BEARER_TOKEN") or "BEARER_TOKEN_HERE"
    print(f"BEARER_TOKEN '{BEARER_TOKEN}'")
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }

    batch_size = 100
    endpoint_url = "http://localhost:8080"
    s = requests.Session()

    # we setup a retry strategy to retry on 5xx errors
    retries = Retry(
        total=5,  # number of retries before raising error
        backoff_factor=0.1,
        status_forcelist=[500, 502, 503, 504]
    )
    s.mount('http://', HTTPAdapter(max_retries=retries))

    for i in tqdm(range(0, len(documents), batch_size)):
        i_end = min(len(documents), i+batch_size)
        # make post request that allows up to 5 retries
        res = s.post(
            f"{endpoint_url}/upsert",
            headers=headers,
            json={
                "documents": documents[i:i_end]
            }
        )
        res.raise_for_status() 

def split_text(text, length=3000, overlap=200):
    chunks = []
    if length <= overlap:
        return [text]
    
    start = 0
    while start < len(text):
        end = min(start + length, len(text))
        chunks.append(text[start:end])
        if end == len(text):  
            break
        start = end - overlap

    return chunks

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    ext = file_path.split('.')[-1]
    if file_path.endswith('.html'):
        soup = BeautifulSoup(content, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        content = md(soup.get_text())
   
    base_id = str(uuid.uuid4())
    chunks = split_text(content)
    iresults = []

    for idx, chunk in enumerate(chunks):
        item_id = f"{base_id}-{idx+1}"
        iresults.append({
            "id": item_id,
            "text": chunk,
            "source": "file",
            "ext": ext,
            "type": "text",
            "source_id": file_path,
            "created_at": "2021-01-01T12:00:00Z"
        })

    return iresults

def main(folder_path):
    allowed_extensions = ["svelte", "js", "ts", "html", "json", "md", "txt"]
    results = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if any(file.endswith(ext) for ext in allowed_extensions):
                file_path = os.path.join(root, file)
                results.extend(process_file(file_path))


    if len(results) == 0:
          print(f"No files read from '{folder_path}'  :(")
          return

    # Print the source_id and len(text) for each result from the current file
    for res in results:
        print(f"source_id: {res['source_id']}, len(text): {len(res['text'])}")

    with open(f"data/{adapt_path_for_filename(folder_path)}_output.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)


    publish_documents(results)

if __name__ == "__main__":
    load_dotenv()
    folder_path = input("Enter the folder path: ")
    main(folder_path)
