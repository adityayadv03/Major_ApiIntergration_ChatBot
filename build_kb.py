import os
import json
import re

# 1. Improved Metadata Extraction
def extract_metadata(filename):
    # Remove extension, replace underscores with spaces, normalize to lowercase
    plant_name = filename.replace('.txt', '').replace('_', ' ').lower().strip()
    return {"plant": plant_name, "filename": filename}

def semantic_chunk(text, max_sentences=3):
    # Split by standard headers (capitalized words followed by colon)
    # OR just treat double newlines as section breaks
    sections = re.split(r'\n\n', text)
    
    chunks = []
    for sec in sections:
        # Split into sentences
        sents = re.split(r'(?<=[.!?])\s+', sec.strip())
        cur = []
        for s in sents:
            if s.strip():
                cur.append(s)
                # Chunk every 'max_sentences'
                if len(cur) >= max_sentences:
                    chunks.append(" ".join(cur))
                    cur = []
        if cur:
            chunks.append(" ".join(cur))
            
    return chunks if chunks else [text]

out = []
folder = "./data/kb_raw"

# Ensure output directory exists
os.makedirs("./data", exist_ok=True)

if not os.path.exists(folder):
    print(f"Error: Folder '{folder}' does not exist. Please create it and add .txt files.")
else:
    for filename in os.listdir(folder):
        if not filename.endswith(".txt"): continue
        
        path = os.path.join(folder, filename)
        with open(path, "r", encoding="utf8") as f:
            text = f.read()
        
        meta = extract_metadata(filename)
        chunks = semantic_chunk(text)
        
        for i, chunk in enumerate(chunks):
            out.append({
                "id": f"{filename}_{i}",
                "text": chunk,
                # Add plant name to text for better search hits
                "search_text": f"{meta['plant']} {chunk}", 
                **meta
            })

    with open("./data/kb_chunks.jsonl", "w", encoding="utf8") as f:
        for item in out:
            f.write(json.dumps(item) + "\n")

    print(f"Success! Processed {len(out)} chunks.")