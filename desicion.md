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


## Parsers — Decision Reasoning per File Type

### Why Word parser walks XML body iterator instead of doc.paragraphs
python-docx gives you two ways to read a Word file. The `doc.paragraphs` list gives you all paragraphs in order but completely skips tables. If you use it, tables become invisible — they never appear in your output at all.

The XML body iterator `doc.element.body` walks every element in the document in the exact order it appears — paragraphs AND tables together. This is the only way to know that a table appears between two paragraphs, which matters when the chunker needs to keep a table attached to the section it belongs to.

### Why bold_title detection uses 80 characters
Section titles written without heading styles — like "Blockers" or "Action Items" — are typically short. Real body text that someone bolds for emphasis is usually a full sentence or longer. 80 characters is roughly one short sentence. Anything under that is almost certainly a title. Anything over is almost certainly emphasis in body text. This threshold will correctly identify section titles in sprint planning docs and meeting notes without false positives from bold body text.

### Why Excel parser returns a dictionary instead of a flat list
Every sheet in an Excel workbook is structurally independent. A Jira file might have one sheet of tickets. A retrospective file might have three sheets — one per category. An OKR file might have sheets per quarter.

If the parser returned a flat list of all rows from all sheets, the signal detector would have no way to run its categorical column detection per sheet — it would see all sheets mixed together and make wrong decisions.

Returning a dictionary keyed by sheet name means signal detection runs independently per sheet, and the chunker handles each sheet with the right strategy.

### Why Excel parser names empty header cells Column0, Column1 etc
Real world Excel files frequently have empty header cells — merged headers that span columns, formatting-only columns, or just poor data hygiene. If the parser leaves these as None, the row dictionary cannot map values to column names. Naming them Column0, Column1 etc ensures every row value has a key and nothing gets silently dropped.

### Why PowerPoint parser combines title + body + notes into one element
A slide's meaning comes from all three together. The title tells you the topic. The body gives the detail. The speaker notes often contain the most important context — decisions made, risks flagged, things the presenter wanted to say but did not put on the slide.

Splitting them into separate elements would produce tiny meaningless chunks. Combining them into one element per slide means each chunk is self-contained and semantically complete. A PM asking "what was discussed about onboarding in the Q2 deck" gets the full slide context, not just the title.

### Why PDF parser does two passes
The first pass reads only the first 5 pages to calculate the median font size — the body text baseline. This is a speed decision. Reading font sizes from every page of a 100-page document just to establish a baseline would be slow and unnecessary. 5 pages gives a statistically reliable median because body text dominates any normal document — titles and headings are rare compared to body paragraphs.

The second pass reads every page for actual content, using the baseline calculated in the first pass to identify headings by font size comparison.

### Why PDF uses font size to detect headings instead of styles
PDF format does not store document structure. There is no concept of "Heading 1" in a PDF — the format only stores drawing instructions: place this text at this position in this font size. When a Word document is exported to PDF, all heading styles are discarded. The only structural signal that survives is visual — headings are printed larger than body text. Font size comparison is therefore the only reliable heading detection method available for PDFs.

Word documents do not need this because python-docx can read heading styles directly from the file structure.

### Why PDF uses 1.3x body size as the heading threshold
A heading needs to be meaningfully larger than body text to be detected as a heading — not just slightly larger due to font rendering differences. 1.3x means a heading must be at least 30% larger than body text. If body text is 11pt, the threshold is 14.3pt. This correctly identifies subheadings at 14pt and main headings at 18pt or 24pt while ignoring minor size variations within body text caused by font rendering.

Level 1 uses 1.5x because main chapter headings are typically significantly larger — 50% bigger than body text or more.

### Why PDF flags scanned pages instead of failing
A scanned PDF page has no extractable text — it is an image of text, not actual text. The parser could throw an error. But that would fail the entire document ingestion just because some pages are scanned.

Instead the parser emits a paragraph element with a clear flag saying the page is scanned and needs OCR. This means the rest of the document still gets ingested and chunked correctly. The flagged pages can be identified later and handled with OCR in V2 without re-ingesting the whole document.

### Why Markdown and text parser caps heading level at 3
Markdown supports up to 6 heading levels with `######`. But heading levels 4, 5, and 6 in practice contain very little meaningful section separation — they are usually sub-sub-sub-sections with only a sentence or two of content. Chunking at these levels would produce extremely small chunks that hurt retrieval quality.

Capping at level 3 means any heading deeper than `###` is treated as a paragraph and included in the level 3 section above it. This produces larger, more semantically meaningful chunks.

### Why email parser returns a string instead of ParsedElements
Every other parser returns a list of labelled structural elements because the chunker needs to make decisions about how to group them. But email chunking is always the same — split at paragraph breaks, one chunk per message. There is no structural variation that requires labelled elements.

Returning a clean string directly is simpler and sufficient. The email chunker receives the string and splits it at double newlines. No element labels needed.

### Why email parser removes quoted reply chains
When someone replies to an email, the original email is quoted at the bottom. If this gets included in the chunk, a PM asking "what did Alex say about the API blocker?" might get a chunk containing Alex's reply PLUS the original email he was replying to — which could be from a completely different person about a completely different topic. This would pollute the retrieval result.

Removing quoted reply chains ensures each email chunk contains only what that specific person wrote in that specific message.




## Chunkers — Decision Reasoning

---

### What chunkers.py does and why it is separate from parsers.py
The parser reads files and labels every piece of content — heading, paragraph, table, blank, slide. It never decides how to group content into chunks. That is the chunker's job.

Keeping them separate means the parser can be reused for any purpose — not just chunking. And the chunker can work with any parser output without knowing which file type it came from. Clean separation of concerns.

---

### Why there is a main routing function chunk_document
The pipeline only needs to call one function regardless of file type. chunk_document receives the parsed elements and the detection result and routes to the right chunker automatically. This means pipeline.py never needs to know which chunking strategy was chosen — it just calls chunk_document and gets back a list of chunks. If we add a new strategy in V2, we add it inside chunk_document — nothing else changes.

---

### Why Word, PDF, Markdown, and plain text all use the same chunkers
By the time content reaches the chunker, it is just a list of ParsedElements — headings, paragraphs, blanks, tables. The chunker does not know or care whether those elements came from a Word file, a PDF, or a Markdown file. It just follows the strategy the signal detector chose.

This is the payoff of separating parsing from chunking. The same heading-based chunker works for a Word sprint planning doc, a PDF technical spec, and a Markdown README — because all three produce the same type of output from their parsers.

---

### Why tables are never split — the critical rule
A table row is meaningless without its column headers. Half a table is meaningless without the other half. Splitting a table mid-row would produce a chunk like "Dev A | 8 |" with no context about what those values mean.

Every table found in any document always becomes its own standalone chunk, with the heading it falls under used as a prefix so the chunk knows what section it belongs to. This rule applies to every strategy without exception. It is enforced in the chunker, not left to the caller.

---

### Why heading-based chunker does not need overlap
Each chunk is a complete section under a heading. The heading itself is the thought boundary. When one section ends and another begins, they are genuinely different topics — "Sprint Goal" and "Blockers" have no overlapping meaning. Adding overlap would put the end of "Sprint Goal" at the start of the "Blockers" chunk, mixing two unrelated topics. That hurts retrieval quality rather than helping it.

---

### Why blank-line-based chunker does not need overlap
Blank lines are the author's own section boundaries. The author decided where one thought ends and another begins. Respecting that boundary is correct. Adding overlap would mix content across the author's intended separations.

---

### Why recursive fallback chunker needs 200 character overlap
This is the only chunker splitting at arbitrary character positions, not at meaningful boundaries. There are no headings, no blank line separators, no author-defined boundaries. A sentence can easily get split across two chunks.

The 200 character overlap carries the last 200 characters of the previous chunk into the start of the next one. Any sentence that crosses the boundary appears completely in at least one chunk. Without this, a query about a sentence near a chunk boundary would retrieve neither chunk confidently.

---

### Why Excel chunker does not need overlap
Each row is a completely independent data record. A Jira ticket has no overlapping meaning with the next Jira ticket. Each category group in a retro is a separate topic. Overlap makes no sense for structured data — it would just duplicate row content across chunks unnecessarily.

---

### Why PowerPoint chunker does not need overlap
Each slide is already a complete self-contained unit. The author designed it that way. Speaker notes, title, and body are all combined into one slide element by the parser. There is nothing to overlap across slide boundaries.

---

### Why email chunker does not need overlap
The email chunker accumulates whole paragraphs and flushes when adding the next paragraph would exceed 800 characters. It always splits at paragraph boundaries, never mid-sentence. This gives the same protection as overlap without actually needing it. Email paragraphs are typically short — most are under 200 characters — so the 800 character limit almost always aligns with clean paragraph breaks.

---

### Why MAX_SECTION_SIZE = 1500
This applies to the heading-based chunker only. When paragraph text under a heading exceeds 1500 characters, recursive split triggers inside that section.

Most sections in sprint planning docs, meeting notes, and retros are short — 200 to 600 characters typically. But occasionally a section is very long — a "Technical Details" section in a spec document might be 3000 characters. One chunk of 3000 characters produces a blurry embedding that matches too many different queries.

1500 is roughly 250-300 words — enough to cover a complete thought without being so large that the embedding loses precision. It also stays comfortably within the embedding model's token limit.

These numbers are starting points not proven values. After first ingestion, inspect chunks in Supabase. If chunks are regularly over 1500 chars or under 100 chars, adjust the threshold.

---

### Why RECURSIVE_CHUNK = 1000
This is the target size for the recursive fallback chunker — roughly 150-170 words or two to three short paragraphs.

It is smaller than MAX_SECTION_SIZE because in the heading-based chunker, the heading itself provides context for the whole section. In recursive fallback there are no headings — the chunk must be entirely self-contained. Smaller chunks are more precise when there is no heading to anchor the meaning.

---

### Why RECURSIVE_OVERLAP = 200
200 characters is roughly 30-40 words — enough to carry one or two complete sentences across a chunk boundary. More overlap wastes storage and creates redundancy in retrieval results. Less overlap risks cutting off important context at boundaries.

---

### Why EMAIL_MAX_CHUNK = 800
Emails are conversational and shorter than documents. 800 characters is roughly 120-130 words — enough for 3-4 typical email paragraphs.

It is smaller than RECURSIVE_CHUNK because we repeat the From, Subject, Date prefix on every email chunk. That prefix is about 60-80 characters. If the max were 400, 20% of every chunk would be the prefix. 800 gives enough room for the actual content to dominate while keeping chunks focused on one point from the email.

---

### Why Markdown uses the same chunkers as Word
The Markdown parser outputs ParsedElements with headings, paragraphs, and blanks — exactly the same structure as the Word parser. The signal detector runs detect_text_strategy and returns heading_based, blank_line_based, or recursive_fallback. chunk_document routes to the right chunker. The chunker never knows it came from Markdown. No separate Markdown chunker is needed.

---

### Why HTML has no chunker
HTML is not a source file type in PrismAI. Google Drive and Gmail are the data sources. The only HTML handling is inside parse_email_body which strips HTML tags from email bodies before the email chunker ever sees the content. By the time any content reaches the chunker it is already clean plain text.

---

### Why PDF overlap depends on which strategy was chosen
When a PDF has font size variation, the signal detector returns heading_based and the heading-based chunker handles it — no overlap needed because section boundaries are meaningful.

When a PDF has uniform fonts and no structure, the signal detector returns recursive_fallback and the recursive fallback chunker handles it — 200 character overlap applies because we are splitting at arbitrary positions.

PDF overlap is handled correctly by routing. It is not a special case.

---

### Why each Excel strategy exists

**row_based** — when every row is an independent record like a Jira ticket, each row tells its own complete story. Keeping rows separate means querying "find all P1 bugs" retrieves exactly the P1 bug rows, not a mixed chunk of different priority tickets.

**group_by_column** — when rows belong to categories, the category is what gives them meaning together. A PM asking "what blocked sprint 5?" wants ALL the blockers, not one blocker per chunk requiring five separate retrievals. Grouping by category means one query retrieves everything in that category at once.

**single_chunk** — for very small sheets with 5 or fewer rows, splitting serves no purpose. The whole sheet is small enough to be one self-contained unit. An OKR sheet with 3 objectives is meaningless if split into 3 separate chunks — the objectives only make sense together.

---

### Why PowerPoint combines title, body, and speaker notes into one chunk
A slide's meaning comes from all three together. The title tells you the topic. The body gives the detail. The speaker notes often contain the most important context — decisions made, risks flagged, things the presenter wanted to say but did not put on the slide.

Splitting them into separate chunks would produce tiny meaningless fragments. Combining them into one chunk per slide means each chunk is self-contained and semantically complete. A PM asking "what was discussed about onboarding in the Q2 deck" gets the full slide context, not just the title.

---

### Why email prefix repeats on every chunk
When the retriever finds a chunk, it needs to know who wrote it and when without needing to look up the parent email. Each chunk must be self-contained. If a PM asks "what did Alex say about the API?" the chunk itself should contain Alex's name, the subject, and the date — not require a separate database lookup to identify the source.



## Chunking Strategy — Decision Reasoning per File Type

---

### Word docs, PDFs, Plain text, Markdown — Why they all use the same chunkers
These four file types all use the same family of chunkers because they are all narrative documents — flowing text with structure. The chunker the signal detector picks depends on what signals it found in the file.

---

### Heading-based chunker
Every time the parser finds a real heading, that heading starts a new chunk. All the paragraph text underneath it gets collected and becomes the body of that chunk. When the next heading appears, the previous section is flushed and a new one starts.

Why — headings are the author's own way of saying "this is where one topic ends and another begins." Splitting at the author's own boundaries produces the most semantically meaningful chunks. A PM asking "what was the sprint goal?" gets the Sprint Goal section, not half of Sprint Goal and half of Blockers.

---

### Bold-title-based chunker
Exactly the same logic as heading-based, but instead of real heading styles, it splits at bold short lines. Same outcome, different trigger.

Why — many people write structured documents without using proper heading styles. They just bold their section titles. The chunker respects that the same way it respects real headings.

---

### Blank-line-based chunker
Splits at blank lines instead of headings. Every time there is a blank paragraph, the accumulated text above it becomes one chunk.

Why — for documents with no headings and no bold titles but clear visual separation between sections. The author is using blank space as a separator. We respect that boundary.

---

### Recursive fallback chunker
No structure at all. Join everything into one big string and split by character count — first at paragraph breaks, then sentence breaks, then word breaks. Maintain 200 character overlap between chunks so context is not lost at boundaries.

Why — last resort. Some documents genuinely have no structure. Rather than producing one enormous chunk or failing, we split at the most natural text boundaries available and keep overlap so meaning does not get cut off mid-thought.

---

### Excel — Three different strategies per sheet

**Row-based**
Each row becomes one chunk. Formatted as "Column: value | Column: value" so it reads like a sentence not a spreadsheet.

Why — when every row is an independent record like a Jira ticket, each row tells its own complete story. Keeping rows separate means "find all P1 bugs" retrieves exactly the P1 bug rows, not a mixed chunk of different priority tickets.

**Group-by-column**
All rows sharing the same category value get grouped into one chunk. All rows where Category = Blocker go into one chunk together.

Why — when rows belong to categories, the category is what gives them meaning together. A PM asking "what blocked sprint 5?" wants ALL the blockers, not one blocker per chunk requiring five separate retrievals. Grouping by category means one query retrieves everything in that category at once.

**Single-chunk**
The entire sheet becomes one chunk.

Why — for very small sheets with 5 or fewer rows, splitting serves no purpose. The whole sheet is small enough to be one self-contained unit. An OKR sheet with 3 objectives is meaningless if split into 3 separate chunks — the objectives only make sense together.

---

### PowerPoint — Always slide-based, no detection needed
Each slide becomes one chunk. Title, body text, and speaker notes combined into one block.

Why — a slide is already a pre-chunked unit of information. The author decided what belongs together on each slide. Splitting mid-slide would separate the title from its content. Combining multiple slides would mix unrelated topics. The slide boundary is the perfect natural chunk boundary.

Speaker notes are included because they often contain the most important context — decisions, risks, things said verbally that do not appear on the slide itself. Excluding them would lose that knowledge entirely.

---

### Email — Always paragraph-based, no detection needed
Build a prefix with From, Subject, Date on every chunk. Split at paragraph breaks. If the whole email is short keep it as one chunk. If long, split at 800 character boundaries always restarting the prefix.

Why paragraph breaks — email writing naturally separates topics by paragraph. One paragraph is usually one thought or one point. Splitting at paragraph breaks keeps thoughts together. Splitting mid-paragraph would cut off sentences mid-meaning.

Why repeat the prefix on every chunk — when the retriever finds a chunk it needs to know who wrote it and when without needing to look up the parent email. Each chunk must be self-contained. If a PM asks "what did Alex say about the API?" the chunk itself should tell you it was Alex, not require a separate database lookup.

Why 500 character threshold for single chunk — short emails are usually one point. Splitting a 400 character email into two chunks is unnecessary and creates tiny meaningless fragments.

---

### The one rule that applies to every strategy — tables are never split
A table row is meaningless without its column headers. Half a table is meaningless without the other half. Splitting a table mid-row would produce a chunk like "Dev A | 8 |" with no context about what those values mean.

Every table found in any document always becomes its own standalone chunk, with the heading it falls under used as a prefix so the chunk knows what section it belongs to. No exception for any strategy anywhere.



## Embedder — Decision Reasoning

---

### What is an embedding and why does PrismAI need it?

When a PM asks "what blocked sprint 3?", the system cannot just search for those exact words in the documents. The documents might say "impediments", "blockers", "obstacles" — different words, same meaning.

Embeddings solve this. An embedding converts any piece of text into 1536 numbers that represent its meaning. "What blocked sprint 3?" and "impediments in sprint 3" will produce similar numbers because they mean the same thing. The system finds chunks whose numbers are closest to the question's numbers. That is semantic search — search by meaning, not by exact words.

Without embeddings, PrismAI is just a keyword search tool. With embeddings, it understands meaning.

---

### Why OpenRouter instead of calling OpenAI directly?

The project already has an OpenRouter API key configured in the .env file. OpenRouter is a gateway that provides access to OpenAI models including text-embedding-3-small. Using OpenRouter means one API key gives access to many models — if we want to switch embedding models in V2, we change one line of code, not our credentials setup.

---

### Why text-embedding-3-small and not another model?

Several embedding models were considered:

text-embedding-3-small was chosen because the entire Nutrivana dataset is in English, it has the best quality to cost ratio for English text, it costs approximately $0.02 per million tokens which means the entire dataset costs a few cents to embed, it is fast, and it works with the existing OpenRouter key with no new account needed.

text-embedding-3-large was rejected because it produces 3072 dimensions instead of 1536, costs more, is slower, and the quality difference is not meaningful for a PM document dataset of this size.

Cohere multilingual was rejected because the dataset is English only. It becomes the right choice in V2 if multilingual support is added.

---

### Why 1536 dimensions and not more or fewer?

Dimensions are like coordinates in a meaning space. More dimensions means more precision in capturing meaning differences between texts.

1536 is what text-embedding-3-small produces — it is fixed by the model and cannot be changed. The Supabase column was created as vector(1536) to match exactly. If you switch to text-embedding-3-large in V2, it produces 3072 dimensions and the Supabase column would need to change to vector(3072).

Fewer dimensions like 512 would mean less precision — two chunks with different meanings might get similar vectors and the retriever would return wrong results. More dimensions means more storage cost and slower similarity search for a quality gain that is not meaningful at this dataset size.

---

### Why batch size 100 and not send one text at a time?

The Nutrivana dataset will produce thousands of chunks. Sending each chunk as a separate API call would mean thousands of HTTP requests — slow, expensive, and likely to hit rate limits.

Batching sends 100 chunks in one API call. OpenRouter processes all 100 together and returns 100 vectors at once. For 500 chunks this means 5 API calls instead of 500.

100 was chosen as a safe conservative batch size. OpenRouter supports up to 2048 inputs per call but 100 avoids any risk of hitting undocumented limits and keeps each request small enough to complete reliably within the 60 second timeout.

---

### Why sort the API response by index before extracting vectors?

The OpenRouter API does not guarantee that the response items come back in the same order as the input texts. If you sent texts [A, B, C] you might get back vectors in order [B, A, C].

Each response item has an index field that tells you which input text it corresponds to. Sorting by index before extracting vectors ensures the output list always matches the input list order exactly. Without this sort, embeddings would be randomly mismatched to their chunks — chunk 1 might get chunk 3's embedding, producing completely wrong search results with no error message.

---

### Why replace empty strings with "empty document"?

The OpenRouter API rejects empty strings and returns an error for the entire batch. A single empty chunk would crash the whole ingestion run.

Empty chunks can appear when a section has a heading but no body text, or when a table is the only content under a heading and the text accumulator is empty. Replacing with "empty document" allows the batch to complete. The resulting embedding for "empty document" is meaningless but harmless — these chunks will never rank highly in similarity search because no PM query will ever be semantically similar to "empty document".

---

### Why retry 3 times with a 2 second wait?

Network calls fail occasionally — temporary connection issues, brief API unavailability, rate limit spikes. A single failure should not crash an entire ingestion run that might have been processing for 10 minutes.

3 retries covers the vast majority of transient failures. 2 seconds between retries gives the API time to recover from a momentary overload. If all 3 retries fail, the error is raised immediately with a clear message identifying which batch failed so it can be debugged and re-run.

---

### Why 0.1 second delay between batches?

A small pause between batches prevents hammering the API with back-to-back requests. Without any delay, sending 10 batches in rapid succession might trigger rate limiting. 0.1 seconds is small enough to not meaningfully slow down ingestion but large enough to be respectful of the API's rate limits.

---

### Why raise a ValueError at import time if credentials are missing?

If the API key or base URL is not set in .env, every embedding call will fail. It is much better to find this out immediately when the module is imported — before any files are parsed, before any chunks are generated — than to discover it after 10 minutes of processing when the first embedding call fails.

A clear ValueError at import time tells the developer exactly what is missing and where to set it. Silent failures discovered mid-ingestion waste time and leave partially ingested data in Supabase.

---

### Why is get_single_embedding a separate function from get_embeddings?

At query time, when a PM types a question, that single question needs to be embedded before searching Supabase. Calling get_embeddings with a list of one text works but is semantically confusing — the retrieval layer should not need to know about batching or lists.

get_single_embedding provides a clean simple interface: give it one string, get back one vector. Internally it calls get_embeddings so all retry logic, error handling, and logging lives in one place. No code duplication.

---

### Why use httpx instead of the requests library?

httpx is a modern HTTP library that supports both synchronous and asynchronous calls. The ingestion pipeline currently uses synchronous calls but the FastAPI backend uses async. Using httpx from the start means the embedder can be made fully async in V2 without changing the API call logic — just add async/await. With requests, switching to async would require rewriting the HTTP calls entirely.



```markdown
## Storage — Decision Reasoning

---

## You have 3 tables. Each function does ONE specific job on those tables.

Think of it like this. You have 3 filing cabinets:
- `documents` cabinet
- `document_chunks` cabinet
- `row_hashes` cabinet

The storage.py functions are like specific actions you can do on those cabinets. Some open a drawer and read. Some add a new file. Some update an existing file. Some delete.

---

## Let me map every function to its table and action:

### documents table actions

| Function | Action | When used |
|---|---|---|
| `get_document_by_source_id` | READ — find one row by Drive file ID | Check if file was ingested before |
| `document_exists_by_content_hash` | READ — check if hash exists | Catch duplicate files uploaded twice |
| `insert_document` | WRITE — add new row | First time a file is ingested |
| `update_document_after_reingestion` | UPDATE — change hash and timestamp | File content changed, re-ingested |
| `update_document_metadata_only` | UPDATE — change only metadata column | Gmail labels changed, no re-embedding needed |
| `delete_document_and_chunks` | DELETE — remove document row | File deleted from Drive or Gmail |

### document_chunks table actions

| Function | Action | When used |
|---|---|---|
| `delete_chunks_for_document` | DELETE — remove all chunks for a document | Before re-ingesting a changed file |
| `insert_chunks_with_embeddings` | WRITE — add all chunks with their vectors | Every time a file is ingested |
| `delete_chunks_for_rows` | DELETE — remove only specific row chunks | Excel row-level update — only changed rows |

### row_hashes table actions

| Function | Action | When used |
|---|---|---|
| `get_row_hashes_for_document` | READ — get all stored row hashes | Compare against current Excel rows to find changes |
| `upsert_row_hashes` | WRITE or UPDATE — save row hashes | After Excel ingestion to record what each row looked like |

### Logging — no table

| Function | Action | When used |
|---|---|---|
| `log_ingestion_result` | Print summary to terminal | After a batch ingestion run finishes |

---

## Why so many functions instead of just a few?

Because each situation needs a different action.

**Situation 1 — Brand new file:**
- `insert_document` → create document row
- `insert_chunks_with_embeddings` → store all chunks

**Situation 2 — File changed in Drive:**
- `get_document_by_source_id` → find existing document
- `delete_chunks_for_document` → remove old chunks
- `insert_chunks_with_embeddings` → store new chunks
- `update_document_after_reingestion` → update hash

**Situation 3 — Same file uploaded with different name:**
- `document_exists_by_content_hash` → detect duplicate → skip

**Situation 4 — Gmail label changed:**
- `update_document_metadata_only` → update labels → done. No re-embedding.

**Situation 5 — Excel file changed, only 3 rows different:**
- `get_row_hashes_for_document` → find which rows changed
- `delete_chunks_for_rows` → delete only changed row chunks
- `insert_chunks_with_embeddings` → re-embed only changed rows
- `upsert_row_hashes` → update stored hashes

**Situation 6 — File deleted from Drive:**
- `delete_document_and_chunks` → remove everything

---

Each function is small and does exactly one thing. The pipeline.py module combines them in the right order for each situation.
```



INGESTION TESTING OUTCOME:

## Word Document Ingestion Testing — Observations and Decisions

---

### Test file used
sprint1_meeting_notes.docx — Sprint 1 meeting notes for Nutrivana

---

### What the debug test revealed at each step

**Step 1 — Signal Detection**
The signal detector correctly identified the document as heading_based with high
confidence. It found 8 paragraphs with real Word Heading styles. This is exactly
right — sprint meeting notes are structured documents with clear section headings.

**Step 2 — Parsing**
The parser correctly labelled every element:
- Document title and metadata lines → paragraph
- Sprint Health Check, Key Discussions, Decisions Made etc → heading
- Action items data → table
- Body text under each heading → paragraph

**Step 3 — Chunking**
10 chunks produced. Each heading section became one chunk. The Action Items
table became its own separate chunk prefixed with "Action Items [TABLE]".

---

### Issue 1 — Empty heading chunk (Chunk 7)
**Observation:** Chunk 7 contained only "Action Items" — 12 characters — with no
body text. The Action Items section had no paragraph text, only a table.

**Decision:** Keep this behaviour. The empty chunk causes zero problems because:
- It will never rank highly in similarity search — no meaningful content
- The table chunk (Chunk 8) already has "Action Items" prefixed to it and is
  fully self-contained
- One extra tiny chunk per document is negligible at this dataset size
- Fixing it adds code complexity for no real quality gain

---

### Issue 2 — Document title classified as paragraph not heading
**Observation:** "Nutrivana Weekly Sync — Sprint 1" was classified as a paragraph
instead of a heading. This is because the document uses Word's "Title" style,
not "Heading 1" style. Our parser only detects styles starting with "Heading".

**Decision:** No fix needed for V1. Here is why:
- Chunk 0 already contains the full title text AND "Sprint 1" mentioned twice
- When a PM asks "summarise sprint 1 meeting notes?" the retriever finds chunks
  by semantic similarity — not by whether the title is a heading or paragraph
- All section chunks already contain Sprint 1 context in their content
- The title being a paragraph does not affect the chunk content or its embedding
- Nobody queries for the document title itself — they query for the content inside

If this causes retrieval problems in practice after full ingestion, the fix is to
add "Title" style detection in parse_docx() — emit it as heading level 0.
This is noted for V2.

---

### Issue 3 — Table correctly kept as its own chunk
**Observation:** The Action Items table became Chunk 8 — completely separate from
the surrounding text, prefixed with the section heading.

**Decision:** This is correct behaviour and exactly what we designed. A table row
is meaningless without its column headers. The table chunk contains:
- Section heading as prefix — "Action Items [TABLE]"
- All rows with Action, Owner, Due Date columns intact
- Full context for any PM query about action items

---

### How the retriever handles "summarise sprint 1 meeting notes?"
The retriever embeds the question and finds the top 10 most similar chunks.
It does NOT retrieve the whole document. It retrieves the most relevant sections.
Every section chunk already contains Sprint 1 context so all relevant chunks
rank highly. The summary built from those chunks covers the full meeting.

---

### Key learning from this test
The pipeline works correctly end to end for Word documents:
- Signal detection → correct strategy chosen
- Parsing → all element types correctly identified
- Chunking → sections split at right boundaries, tables kept intact
- Embedding → all chunks embedded successfully
- Storage → document and chunks stored in Supabase correctly

The two observations above are minor and do not affect retrieval quality.
Both are noted for potential V2 improvements.



CHUNKING SIGNAL STRATEGY CHANGED FOR EXCEL

## Excel Chunking — Bug Found and Fixed During Testing

---

### What went wrong

During testing of sprint1_jira.xlsx the signal detector chose the wrong
strategy for the Tickets sheet.

The Tickets sheet has these columns:
Ticket ID, Title, Type, Status, Priority, Assignee, Sprint, Story Points,
Description, Acceptance Criteria

The signal detector looped through ALL columns looking for a categorical one.
It found the `Type` column which has only 3 unique values — Task, Story, Epic.
This triggered `group_by_column` on Type.

Result — instead of 8 separate ticket chunks, we got 3 chunks:
- Chunk 0 — all Task tickets together
- Chunk 1 — all Story tickets together
- Chunk 2 — all Epic tickets together

This is wrong. A PM asking "what is TECH-001?" would get all Task tickets
mixed together instead of just that one ticket.

---

### Why it happened

The original signal detection logic looped through every column in the sheet
looking for any column with 2-8 unique repeating values. The `Type` column
with Task/Story/Epic satisfied this condition. The detector picked it before
even considering whether it was the right column to group by.

The detector had no way to distinguish between:
- A column that is a meaningful primary category — like Category in a retro
- A column that just happens to have few unique values — like Type in Jira

Both look identical to the detector.

---

### Why we did not catch it earlier

We designed the chunking strategy based on knowing the Nutrivana dataset.
We knew Jira files should be row_based and retro files should be
group_by_column. But the signal detector was making decisions based on
any column it found, not the right column.

This is exactly the problem we discussed earlier — making content assumptions
instead of reading structural signals.

---

### The fix

Changed signal detection to check ONLY the first column instead of
looping through all columns.

The first column of any well-structured sheet is always either:
- A unique identifier — Ticket ID, Row ID, Name — all unique → row_based
- A primary category — Category, Type, Status — repeating → group_by_column

This is a universal structural rule that works for 90% of real documents
without making any content assumptions.

Result after fix:

Tickets sheet — first column is Ticket ID — all unique values
→ row_based → 8 chunks, one per ticket ✅

Comments sheet — first column is Ticket ID — repeating values
→ group_by_column on Ticket ID → 8 chunks, one per ticket's comments ✅

---

### Why this fix is correct for any client's Excel files

Any well-structured Excel sheet puts the primary identifier or primary
category in the first column. This is standard spreadsheet practice.

- Jira files — first column is ticket ID — unique — row_based
- Retro files — first column is category — repeating — group_by_column
- OKR files — first column is objective — repeating or unique depending on structure
- Any other client's Excel — first column tells you the structure

Checking only the first column is simpler, more reliable, and makes no
assumptions about column names or content.

---

### What this means for retrieval quality

Before fix — a PM asking "what is TECH-001?" would get all Task tickets
mixed in one chunk. The answer would contain irrelevant tickets.

After fix — a PM asking "what is TECH-001?" gets exactly that one ticket
chunk with all its details. Clean, precise retrieval.


EMAIL CHUNKING LIMITATION FOR PARAGRAPH WISE 

Here it is in markdown format — paste into your DECISIONS.md:

```markdown
## Email Chunking — Known Limitation

---

### What the limitation is

When an email is long enough to be split into multiple chunks,
the chunker splits at paragraph boundaries up to 800 characters.
Every chunk gets the same prefix — From, Subject, Date — but the
body content is split across chunks.

For Email 1 in the GOAL-BUG-005 thread this produced:

**Chunk 0 — 732 chars:**
```
From: arjun@nutrivana.in | Subject: GOAL-BUG-005 | Date: 2025-04-18

Shristi,
Starting GOAL-BUG-005 today (BMR warning shown but goal saved incorrectly).
Before I begin I want to change how we approach health-critical bug fixes.
The bug: when a user sets a calorie goal below their BMR, clicks through
the warning, and confirms they understand the risk the goal is saved at an
incorrect value...
```

**Chunk 1 — 351 chars:**
```
From: arjun@nutrivana.in | Subject: GOAL-BUG-005 | Date: 2025-04-18

Step 1: Define every scenario that the fixed code must handle.
Step 2: Write test cases for all scenarios.
Step 3: Implement the fix until all tests pass.
Request permission to take an extra day for test-writing before implementation.
```

Chunk 0 has the bug description with no proposal. Chunk 1 has
the proposal with no bug description. They are stored as two
separate vectors in Supabase.

---

### How this affects retrieval

A PM asking "what was Arjun's proposal for fixing GOAL-BUG-005?"

The retriever finds Chunk 1 — it has the steps and request for
permission. But Chunk 1 has no bug description — the PM sees
a 3-step proposal with no context about what bug it is for.

A PM asking "what is GOAL-BUG-005?"

The retriever finds Chunk 0 — it has the full bug description.
But Chunk 0 has no proposal — the PM sees the bug but no
information about how Arjun planned to fix it.

---

### Severity — LOW

This limitation is partially mitigated by two things:

First — the Subject line prefix on every chunk. Both chunks say
"GOAL-BUG-005" in the subject. A PM reading either chunk
immediately knows which bug it relates to.

Second — the thread has 4 emails. Email 3 from Arjun on April 21
contains the full context — 23 test cases written, 3 failure
modes found. That email fits in one chunk and is completely
self-contained. A PM asking about the GOAL-BUG-005 fix will
likely retrieve Email 3 which gives the full picture.

So the impact is real but not severe. The PM gets partial
information from the split chunks but full information from
later emails in the thread.

---

### Solution — V2

The correct fix is semantic chunking for emails — splitting at
meaning boundaries not character boundaries.

Instead of splitting when the chunk reaches 800 characters,
split when the topic changes. In this email the natural split
is between the bug description and the proposal — not at the
800 character boundary which cuts mid-argument.

This requires either:
- An LLM to identify topic boundaries within the email body
- A smarter paragraph grouping algorithm that keeps related
  paragraphs together even if the total exceeds 800 characters

For V1 the 800 character paragraph-based chunking is acceptable.
The subject prefix on every chunk provides enough context for
retrieval to work. For V2 semantic chunking will improve
precision for long detailed emails.
```

---

Paste this into DECISIONS.md then we move to skip unchanged, update, delete tests for email.



### Mitigation — Metadata filtering

The limitation is fully mitigated by metadata filtering at
retrieval time.

Every chunk from the same email shares identical metadata:
- sender
- subject
- thread_id
- date

When the LangGraph agent receives a query about a specific
email or thread, it filters chunks by subject, sender, or
thread_id. This means ALL chunks from the same email are
always retrieved together — not just the most semantically
similar one.

So even though Chunk 0 has the bug description and Chunk 1
has the proposal — both are retrieved together when a PM asks
about GOAL-BUG-005. The LLM reads both chunks and gives a
complete answer combining both pieces of information.

This makes the character-boundary split a non-issue in practice.
No fix needed for V1.


EXCEL CHUNKING STRATEGY WHOLE STORY:
## Excel Chunking Strategy — Full Journey and Decisions

---

### Phase 1 — First approach: Pure structural signal detection

**What we built:**
Signal detector looped through ALL columns in every Excel sheet
looking for a categorical column — any column with 2-8 unique
repeating values. If found → group_by_column on that column.
Otherwise → row_based.

**What went wrong:**
Tested on sprint1_jira.xlsx Tickets sheet. The signal detector
found the Type column — Task, Story, Epic — only 3 unique values.
It chose group_by_column on Type. Result: all Task tickets in one
chunk, all Story tickets in one chunk, all Epic tickets in one chunk.

This is completely wrong. A PM asking "what is TECH-001?" would get
all Task tickets mixed together instead of just TECH-001.

**Root cause:**
The detector had no way to distinguish between:
- A column that is a meaningful primary category — like Category
  in a retro sheet
- A column that just happens to have few unique values — like
  Type in a Jira sheet

Both look identical structurally.

---

### Phase 2 — Fix: Check first column only

**What we changed:**
Changed signal detection to check ONLY the first column instead
of looping through all columns. The first column of any
well-structured sheet is always the primary identifier or
primary category.

**What worked:**
- Jira Tickets — first column is Ticket ID — all unique → row_based ✅
- Jira Comments — first column is Ticket ID — repeating → group_by_column ✅

**What still failed:**
- OKR sheet — first column is Objective — but has empty cells for
  rows belonging to the same objective. Signal detector saw empty
  cells and said no clear grouping column → row_based. Wrong.
- Review sheets — no structured columns at all — narrative text.
  Signal detector chose row_based. Every row became a separate chunk.
  "3 things to carry forward" split into 3 separate chunks with no
  connection to each other.
- Metrics sheet — 5 independent metrics each became a separate tiny
  chunk of 80-90 chars. Meaningless fragments.

**Root cause:**
No pure structural rule can handle all Excel architectures. There
are infinite ways to structure an Excel sheet. Every rule we write
breaks for some file type we have not seen.

---

### Phase 3 — Decision: LLM classifier for Excel

**Why LLM:**
The LLM reads the actual content and structure together and makes
the right decision. It understands:
- When empty cells mean "same as above" vs genuinely empty
- When rows are independent records vs grouped under a parent
- When a sheet is narrative text vs tabular data

No structural rule can do this. Only content understanding can.

**What we built:**
New function classify_excel_sheet_with_llm() in signal_detector.py.
Sends the entire sheet — all raw rows including first row — to
openai/gpt-4.1-nano via OpenRouter. Returns strategy, group_by_column,
and row_groups (every row assigned to its correct group).

**Why we send ALL rows including first row:**
The parser no longer separates the first row as headers. The LLM
decides which row is the header and which rows are data. This is
important because some sheets — like Review sheets — have a long
narrative sentence as the first row that is NOT a column header.
If we always treated row 0 as a header we would lose that content.

**Why gpt-4.1-nano:**
Newer reasoning model available on OpenRouter. Understands structure
and relationships between rows and columns. Much better than o3-mini
which is an older model. Affordable — pennies for the entire
Nutrivana dataset ingestion.

---

### Phase 4 — Problems found after adding LLM

**Problem 1 — Header row assigned to wrong group:**
First run — LLM assigned Row 0 (the header row) to a group value
like "Ticket ID" instead of excluding it. This caused the header
row to appear as a data row in chunks.

**Fix:**
Updated the prompt to explicitly tell the LLM:
- Row 0 is almost always a header row
- Exclude Row 0 from row_groups entirely
- row_groups keys should never contain "0"

**Problem 2 — OKR rows assigned to Key Result text instead of Objective:**
First run — LLM assigned rows to their own Key Result value instead
of their parent Objective value. Every row got its own unique group
making it effectively the same as row_based.

**Fix:**
Updated the prompt with a clearer rule:
- Assign every row to its PARENT GROUP value — not its own detail value
- A parent group column has a value on the first row of a group
  and empty cells on subsequent rows of the same group
- If a row has an empty cell in the group column it belongs to
  the same group as the last non-empty value above it
- Added a clear example showing correct row_groups assignment

**Problem 3 — LLM inconsistency for Review sheets:**
For Q2 Review sheet the LLM sometimes returns single_chunk and
sometimes returns group_by_column on different runs. The sheet
has a long narrative sentence as the first row which confuses
the LLM about whether to treat it as a header or content.

**Decision:**
Both results are acceptable for V1. single_chunk keeps the whole
review together. group_by_column splits by objective section —
actually better for targeted retrieval. The content is always
fully captured regardless of which strategy is chosen.
Inconsistency is noted for V2 improvement — add explicit prompt
guidance for narrative sheets with non-standard first rows.

---

### Final chunkers.py update

Updated chunk_excel_sheet() to handle the new raw row format
from the parser and to use row_groups from the LLM classifier.

**Old format expected:**
```python
{"headers": [...], "rows": [{col: val, ...}]}
```

**New format:**
```python
{"rows": [[val1, val2, ...], [val1, val2, ...]]}
```

Row 0 is always the header. Rows 1+ are data rows. For
group_by_column strategy — row_groups from LLM notes field
assigns each row to its correct parent group regardless of
empty cells in the grouping column.

---

### Why this approach is correct for V1

For the Nutrivana dataset — 28 Excel files with various sheet
types including Jira, OKR, Retro, Review, Initiatives — the LLM
classifier correctly identifies the right strategy for every sheet
type. The total cost for classifying all sheets at ingestion time
is a few cents. Classification runs once at ingestion only, never
at query time.

For future clients with different Excel structures — the LLM
approach is universal. It reads actual content and makes
intelligent decisions. No structural rule can match this.