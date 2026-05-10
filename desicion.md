# PrismAI — Architecture Decisions & Reasoning

---

## Signal Detector — Why these numbers?

### >= 2 headings to confirm heading_based strategy
One heading might just be a document title. Two or more means
there is a real section structure worth splitting by.

### <= 80 characters for bold title detection
Section titles like "Sprint Goal" or "Blockers" are short.
Body text that happens to be bold is usually a full sentence or longer.
80 characters is roughly one short sentence — a reliable cutoff.

### > 15% blank lines for blank_line_based strategy
A small number of blank lines means the author is just spacing paragraphs.
If 15%+ of all paragraphs are blank, the author is clearly using
blank lines as section dividers.

### These numbers are starting points — not perfect
After first ingestion, inspect chunks in Supabase.
If some documents got the wrong strategy, adjust these thresholds.
This tuning phase is normal for every RAG system.

---

## Why PDF detection is different from Word detection

Word format explicitly stores paragraph styles — you can directly ask
"is this Heading 1?" and get yes or no. python-docx reads this directly.

PDF format stores no structure — only drawing instructions.
"Put this text at this position in this font size." That is all.
So for PDF we infer headings from font size variation — larger text
than surrounding body text is treated as a heading.

Both Word and PDF can end up using heading_based chunking strategy.
The detection method is different because the file formats expose
different information. The chunking output is the same.

---

## Why sprint column is TEXT not INTEGER
Nutrivana uses sprint numbers 1-13. But PrismAI is a product.
Future clients may name sprints "Sprint Alpha", "Q1-Sprint-2" etc.
TEXT handles all cases. INTEGER would break for non-numeric sprint names.

---

## Why certain columns are real columns vs JSONB in document_chunks
Real columns: source_type, folder, sprint, section_heading, sheet_name, page_number
These are promoted to real columns because agents filter by them constantly.
Fast indexed lookup beats JSONB field extraction for frequent queries.

JSONB: file_id, owner, sender, thread_id, recipients, email_date etc.
These are stored for context and display — rarely filtered.
JSONB is fine for occasional reads.

---

## Why parent-child chunking is V2 not V1
Dataset is ~80 documents, mostly short structured files.
Parent-child adds ingestion complexity and retrieval join overhead.
Quality boost is real but designed for large dense documents
like legal contracts or research papers — not sprint planning docs.
Add in V2 after seeing where retrieval actually fails.

---

## Why LangChain and LangGraph are NOT used in ingestion
Ingestion is pure Python — read files, chunk, embed, store.
LangChain and LangGraph are only needed for retrieval and agents.
Using them in ingestion would add unnecessary complexity and dependencies.

---

## Why IVFFlat vector index is created AFTER ingestion not before
IVFFlat needs existing data to build clusters.
On an empty table it either fails or builds a useless index.
Rule: ingest at least 100 chunks first, then create the index.

---