import io
import os
import re
import sys
import time
import sqlite3
import tarfile
import requests
import xml.etree.ElementTree as ET

# Ensure project root is in python path to load config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import Config


papers = {
    "RAG": [
        "2005.11401",  # Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
        "2002.08909",  # REALM
        "2004.04906",  # Dense Passage Retrieval
        "2007.01282",  # Fusion-in-Decoder
        "2009.02252",  # KILT
        "2104.08663",  # BEIR
        "2004.12832",  # ColBERT
        "2007.00808",  # ANCE
        "2112.09118",  # Contriever
        "2208.03299",  # Atlas
        "2310.11511",  # Self-RAG
        "2401.15884",  # Corrective Retrieval Augmented Generation
        "2401.18059",  # RAPTOR
        "2404.16130",  # GraphRAG
        "2405.14831",  # HippoRAG
        "2408.08067",  # RAGChecker
        "2311.09476",  # ARES
        "2309.15217",  # RAGAS
        "2307.03172",  # Lost in the Middle
        "2303.07678",  # Query2doc
        "2112.08688",  # Evidentiality-guided Generation
        "2310.20158",  # GAR-meets-RAG
        "2312.10997",  # RAG for LLMs: A Survey
        "2402.19473",  # RAG for AI-Generated Content
        "2408.08921",  # Graph RAG: A Survey
    ],
    "AI/ML": [
        "1706.03762",  # Attention Is All You Need
        "1512.03385",  # Deep Residual Learning for Image Recognition
        "1404.5997",   # ImageNet Classification with Deep CNNs
        "1406.2661",   # Generative Adversarial Nets
        "1312.6114",   # Auto-Encoding Variational Bayes
        "1412.6980",   # Adam
        "1207.0580",   # Dropout
        "1502.03167",  # Batch Normalization
        "1603.02754",  # XGBoost
        "1106.6242",   # Random Forests
        "2009.06732",  # Efficient Transformers: A Survey
        "1804.07612",  # Deep Learning
        "1301.3781",   # Word2Vec
        "1506.02078",  # GloVe
        "1707.06347",  # Proximal Policy Optimization
        "1509.02971",  # Deep Deterministic Policy Gradient
        "1409.0473",   # Neural Machine Translation by Jointly Learning to Align
        "1409.3215",   # Sequence to Sequence Learning
        "1806.07366",  # Neural ODEs
        "1611.01578",  # Neural Architecture Search with RL
        "1807.11626",  # MnasNet
        "2103.00020",  # CLIP
        "2004.00580",  # Deep Learning for Scientific Discovery
        "1511.06581",  # Dueling Network Architectures
        "1312.5602",   # Playing Atari with Deep Reinforcement Learning
    ],
    "LLMs": [
        "1810.04805",  # BERT
        "2005.14165",  # GPT-3
        "1910.10683",  # T5
        "1906.08237",  # XLNet
        "1907.11692",  # RoBERTa
        "1909.11942",  # ALBERT
        "2003.10555",  # ELECTRA
        "2001.08361",  # Scaling Laws for Neural Language Models
        "2203.15556",  # Chinchilla
        "2112.11446",  # Gopher
        "2204.02311",  # PaLM
        "2205.01068",  # OPT
        "2211.05100",  # BLOOM
        "2302.13971",  # LLaMA
        "2307.09288",  # Llama 2
        "2310.06825",  # Mistral 7B
        "2401.04088",  # Mixtral
        "2407.21783",  # Llama 3
        "2311.16867",  # Falcon
        "2304.01373",  # Pythia
        "2203.02155",  # InstructGPT / RLHF
        "2212.08073",  # Constitutional AI
        "2109.01652",  # FLAN
        "1909.08593",  # Learning from Human Preferences
        "2304.13712",  # ChatGPT and Beyond survey
    ],
    "Prompt Engineering": [
        "2201.11903",  # Chain-of-Thought Prompting
        "2205.11916",  # Zero-Shot Reasoners
        "2203.11171",  # Self-Consistency
        "2205.10625",  # Least-to-Most Prompting
        "2210.03629",  # ReAct
        "2211.01910",  # Automatic Prompt Engineer
        "2210.03350",  # Self-Ask
        "2110.08387",  # Generated Knowledge Prompting
        "2302.12246",  # Active-Prompt
        "2305.04091",  # Plan-and-Solve
        "2211.12588",  # Program of Thoughts
        "2211.10435",  # PAL
        "2305.10601",  # Tree of Thoughts
        "2308.09687",  # Graph of Thoughts
        "2303.11366",  # Reflexion
        "2303.17651",  # Self-Refine
        "2305.11738",  # CRITIC
        "2203.06566",  # PromptChainer
        "2302.11382",  # Prompt Pattern Catalog
        "2310.01798",  # LLMs Cannot Self-Correct Reasoning Yet
        "2309.03409",  # OPRO
        "2308.12261",  # Prompt2Model
        "2310.03714",  # DSPy
        "2402.10200",  # Chain-of-Thought Without Prompting
        "2212.10560",  # Self-Instruct
    ]
}

ARXIV_API = "https://export.arxiv.org/api/query"
ARXIV_SOURCE = "https://export.arxiv.org/e-print"


def get_paper(arxiv_id):
    response = requests.get(
        ARXIV_API,
        params={"id_list": arxiv_id},
        timeout=30
    )
    response.raise_for_status()

    root = ET.fromstring(response.text)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    entry = root.find("atom:entry", namespace)

    if entry is None:
        raise ValueError(f"Paper not found: {arxiv_id}")

    title_element = entry.find("atom:title", namespace)
    title = title_element.text.strip() if title_element is not None else None

    published_element = entry.find("atom:published", namespace)
    published_date = None
    if published_element is not None:
        published_date = published_element.text.strip()[:10]

    response = requests.get(f"{ARXIV_SOURCE}/{arxiv_id}", timeout=60)
    response.raise_for_status()
    source = response.content

    files = extract_source_files(source)
    main_file = find_main_tex(files)

    if main_file is None:
        raise ValueError(f"Could not identify main LaTeX file for {arxiv_id}")

    latex = resolve_includes(main_file, files)
    sections = parse_sections(latex)

    return {
        "arxiv_id": arxiv_id,
        "title": title,
        "published_date": published_date,
        "url": f"https://arxiv.org/abs/{arxiv_id}",
        "sections": sections
    }


def extract_source_files(source):
    files = {}
    try:
        archive = tarfile.open(fileobj=io.BytesIO(source), mode="r:*")
        for member in archive.getmembers():
            if not member.isfile():
                continue
            file = archive.extractfile(member)
            if file is None:
                continue
            content = file.read().decode("utf-8", errors="ignore")
            path = member.name.replace("\\", "/")
            if path.startswith("./"):
                path = path[2:]
            files[path] = content
    except tarfile.ReadError:
        files["main.tex"] = source.decode("utf-8", errors="ignore")
    return files


def find_main_tex(files):
    for path in files:
        if os.path.basename(path).lower() == "main.tex":
            return path

    candidates = []
    for path, content in files.items():
        if not path.lower().endswith(".tex"):
            continue
        if re.search(r"\\documentclass(?:\[[^\]]*\])?\{", content):
            candidates.append(path)

    if candidates:
        candidates.sort(key=lambda p: (p.count("/"), len(p)))
        return candidates[0]

    tex_files = [path for path in files if path.lower().endswith(".tex")]
    if tex_files:
        tex_files.sort()
        return tex_files[0]

    return None


def resolve_includes(filename, files, visited=None):
    if visited is None:
        visited = set()

    if filename in visited:
        return ""

    visited.add(filename)
    content = files.get(filename)

    if content is None:
        return ""

    base_dir = os.path.dirname(filename)
    pattern = re.compile(r"\\(?:input|include)\{([^}]+)\}")

    def replace_include(match):
        included = match.group(1).strip()
        if not included.lower().endswith(".tex"):
            included += ".tex"

        if base_dir:
            included_path = os.path.normpath(os.path.join(base_dir, included))
        else:
            included_path = os.path.normpath(included)

        included_path = included_path.replace("\\", "/")

        if included_path not in files:
            if included in files:
                included_path = included
            else:
                return ""

        return resolve_includes(included_path, files, visited)

    return pattern.sub(replace_include, content)


def parse_sections(latex):
    latex = remove_latex_comments(latex)
    pattern = re.compile(
        r"\\section\*?\{([^}]*)\}"
        r"(.*?)"
        r"(?=\\section\*?\{|"
        r"\\end\{document\}|$)",
        re.DOTALL
    )

    sections = []
    for match in pattern.finditer(latex):
        title = clean_latex(match.group(1))
        text = clean_latex(match.group(2))

        if not title and not text:
            continue

        sections.append({
            "section_number": len(sections) + 1,
            "title": title,
            "text": text
        })

    return sections


def remove_latex_comments(text):
    return re.sub(r"(?<!\\)%.*", "", text)


def clean_latex(text):
    text = remove_latex_comments(text)
    text = re.sub(r"\\subsection\*?\{([^}]*)\}", r"\n\n\1\n\n", text)
    text = re.sub(r"\\subsubsection\*?\{([^}]*)\}", r"\n\n\1\n\n", text)
    text = re.sub(r"\\(?:textbf|textit|emph|underline)\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\cite[a-zA-Z]*\{[^}]*\}", "", text)
    text = re.sub(r"\\(?:label|ref|pageref)\{[^}]*\}", "", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?", " ", text)
    text = text.replace("{", "").replace("}", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def insert_paper(conn, paper, category):
    """
    Insert or update a paper and its sections into SQLite.
    """
    cursor = conn.cursor()

    # Enable foreign keys for ON DELETE CASCADE
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Insert or Replace the paper record
    cursor.execute(
        """
        INSERT INTO papers (
            arxiv_id,
            title,
            published_date,
            category,
            url,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(arxiv_id) DO UPDATE SET
            title = excluded.title,
            published_date = excluded.published_date,
            category = excluded.category,
            url = excluded.url,
            updated_at = CURRENT_TIMESTAMP;
        """,
        (
            paper["arxiv_id"],
            paper["title"],
            paper["published_date"],
            category,
            paper["url"],
        )
    )

    # 2. Fetch the paper ID
    cursor.execute("SELECT id FROM papers WHERE arxiv_id = ?;", (paper["arxiv_id"],))
    paper_id = cursor.fetchone()[0]

    # 3. Remove existing sections for re-ingestion safety
    cursor.execute("DELETE FROM paper_sections WHERE paper_id = ?;", (paper_id,))

    # 4. Insert paper sections
    section_rows = [
        (paper_id, section["section_number"], section["title"], section["text"])
        for section in paper["sections"]
    ]
    cursor.executemany(
        """
        INSERT INTO paper_sections (
            paper_id,
            section_number,
            title,
            text
        )
        VALUES (?, ?, ?, ?);
        """,
        section_rows
    )

    conn.commit()
    return paper_id


def ingest_all():
    total = sum(len(ids) for ids in papers.values())
    current = 0

    print(f"Starting ingestion of {total} papers into SQLite: {Config.DB_PATH}\n")

    conn = sqlite3.connect(Config.DB_PATH)

    try:
        for category, arxiv_ids in papers.items():
            print(f"=== {category} ===")

            for arxiv_id in arxiv_ids:
                current += 1
                print(f"[{current}/{total}] Downloading {arxiv_id}...")

                try:
                    paper = get_paper(arxiv_id)
                    paper_id = insert_paper(conn, paper, category)

                    print(f"    ✓ {paper['title']}")
                    print(f"      {len(paper['sections'])} sections")
                    print(f"      database id: {paper_id}")

                except Exception as e:
                    print(f"    ✗ Failed: {arxiv_id}")
                    print(f"      {type(e).__name__}: {e}")

                time.sleep(3)

            print()
    finally:
        conn.close()


if __name__ == "__main__":
    ingest_all()