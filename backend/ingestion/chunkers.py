"""Chunkers for PrismAI ingestion.

Takes parsed elements (from :mod:`ingestion.parsers`) and a detection
result (from :mod:`ingestion.signal_detector`) and produces ready-to-embed
:class:`Chunk` objects. This module never reads files — it operates only on
already-parsed structures.

Why this module exists for PrismAI:
    A PM asks "what blocked sprint 3?" and we need to return the exact Blockers
    section of the retro — not a random 500-character window that happens to
    contain the word "blocked". Chunking strategy decides whether retrieval
    surfaces the right paragraph, the right Jira row, or the right slide.
    parsers.py finds the structure, signal_detector.py picks the strategy,
    and this module turns that into the actual embeddable units.

Pipeline contract:
    * pipeline.py calls :func:`chunk_document` for Word, PDF, Markdown, plain
      text, and PowerPoint — those share the ParsedElement list contract.
    * Excel and email skip the router because their inputs do not look like
      a flat element list — pipeline.py calls :func:`chunk_excel_sheet` per
      sheet and :func:`chunk_email` per message directly.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ingestion.parsers import ParsedElement
from ingestion.signal_detector import DetectionResult, Strategy

# WHY THIS EXISTS IN PRISM AI:
# When a PM asks "what was the sprint goal for sprint 3?" we want the entire
# Sprint Goal section to come back as one chunk so the answer reads cleanly.
# A heading-based section that is at most ~1500 characters fits comfortably
# inside an embedding model's context and is short enough to be precise.
#
# WHAT THIS CONSTANT DOES:
# Upper limit (in characters) for emitting a heading section as ONE chunk.
# Anything bigger gets handed to the recursive splitter so embeddings stay
# meaningful instead of becoming a vague summary of a 5-page section.
#
# WHY THIS WAY:
# 1500 chars is roughly 250–300 words — about one screenful of prose, the
# size humans naturally recognise as "one section". Smaller would split
# Sprint Goals; larger would dilute Q2 OKR retrieval.
#
# WHAT BREAKS IF THIS IS WRONG:
# Too high → embeddings of huge sections lose specificity, retrieval pulls
# the wrong section. Too low → we'd over-fragment short headings and the PM
# would get half a Sprint Goal in one hit and the other half in another.
MAX_SECTION_SIZE = 1500

# WHY THIS EXISTS IN PRISM AI:
# When the document has no headings (a stream-of-consciousness email, a
# scanned PDF without font cues), we must still split it somehow. The
# recursive splitter cuts on paragraphs, then sentences, then words — but
# every level needs a target chunk size to aim for.
#
# WHAT THIS CONSTANT DOES:
# Maximum size of any single recursive-fallback chunk in characters.
#
# WHY THIS WAY:
# 1000 chars (~150–200 words) keeps chunks small enough that retrieval is
# precise but big enough that meaning is preserved across sentence breaks.
#
# WHAT BREAKS IF THIS IS WRONG:
# A retrospective with no headings would either become one giant chunk
# (wrong section returned) or 30 micro-chunks (no coherent context).
RECURSIVE_CHUNK = 1000

# WHY THIS EXISTS IN PRISM AI:
# Recursive splits at fixed boundaries can cut a sentence mid-thought —
# e.g. "Alex flagged the API was..." | "...rate-limited by Stripe." If
# retrieval picks only the second half, the PM never learns Alex flagged it.
#
# WHAT THIS CONSTANT DOES:
# Number of trailing characters from the previous chunk that get repeated
# at the start of the next chunk so context flows across the boundary.
#
# WHY THIS WAY:
# Overlap is ONLY applied in recursive_fallback. Heading and blank-line
# strategies already cut at semantic boundaries (a section, a paragraph
# break) so duplicating their text would waste embedding space and inflate
# storage with no recall gain.
#
# WHAT BREAKS IF THIS IS WRONG:
# Zero overlap → answers cite a chunk that says "...rate-limited by Stripe"
# without "Alex flagged the API". Too high → near-duplicate chunks dominate
# similarity search and crowd out the real answer.
RECURSIVE_OVERLAP = 200

# WHY THIS EXISTS IN PRISM AI:
# Emails are conversational. A long thread that reaches the embedding model
# as one giant blob loses the natural decision points ("we agreed X", "Sarah
# vetoed Y"). Splitting at paragraph boundaries with a moderate ceiling
# preserves those decisions while keeping each chunk searchable.
#
# WHAT THIS CONSTANT DOES:
# Soft cap (in characters) used by chunk_email when packing email paragraphs.
#
# WHY THIS WAY:
# Smaller than RECURSIVE_CHUNK (1000) because every email chunk also carries
# a sender/subject/date prefix that eats ~50–100 chars; 800 leaves room for
# the actual message without overshooting embedding context.
#
# WHAT BREAKS IF THIS IS WRONG:
# Too high → "what did Alex say about the API?" returns a 3-paragraph chunk
# burying Alex's quote. Too low → fragments break a single decision into
# two chunks and ranking misses the pair.
EMAIL_MAX_CHUNK = 800


@dataclass
class Chunk:
    """The smallest unit of text PrismAI embeds and stores in the vector DB.

    One-sentence summary: a self-contained piece of content with a stable
    position-in-document and a metadata bag describing where it came from.

    Why it exists for PrismAI:
        Every retrieval answer that surfaces in the chat — "blocked tickets
        in sprint 3", "Alex's API comment", "Q2 OKR drift" — comes from one
        of these objects. The fields decide whether the answer is precise
        (right ``content``), well-cited (right ``metadata``), and well-ordered
        on screen (right ``chunk_index``).

    Field roles (every decision spelled out):
        * ``content`` — the only thing that gets embedded. Headings,
          [TABLE] markers, and email prefixes are intentionally part of
          ``content`` so the embedding picks up "this paragraph is under
          Sprint Goal" semantically, not just structurally.
        * ``chunk_index`` — 0-based position inside the parent document.
          We keep it stable across re-runs so a citation like
          "Sprint 3 Retro · chunk 4" still points at the same paragraph
          tomorrow. Sorting by this in the UI shows results in
          document order, not embedding-similarity order.
        * ``metadata`` — uses ``field(default_factory=dict)`` because a
          plain ``= {}`` would share one dict between every Chunk instance
          and corrupt citations across unrelated documents (a classic
          mutable-default Python footgun).

    Returns: not applicable — this is a data carrier consumed by
    pipeline.py's embedder and Supabase writer.

    What breaks if this is wrong:
        If ``content`` is missing or empty, the vector DB silently rejects
        the row and the PM's question never matches that document. If
        ``metadata`` is shared across instances, citations cross-pollinate
        and the answer claims to come from the wrong PRD or sprint.
    """

    content: str
    chunk_index: int
    metadata: Dict[str, Any] = field(default_factory=dict)


def chunk_document(
    elements: List[ParsedElement],
    detection: DetectionResult,
    base_metadata: Dict[str, Any],
) -> List[Chunk]:
    """Send the parsed elements to whichever chunker matches the detection result.

    One-sentence summary: dispatches a single document's parsed structure into
    the right chunking algorithm based on what signal_detector saw.

    Why it exists for PrismAI:
        Different PM artefacts need different chunking. A sprint retro with
        Markdown headings (``## Blockers``, ``## Wins``) must be cut at
        section boundaries so "what blocked sprint 3?" returns the Blockers
        section. A wall of bullets with no headings must use blank lines as
        soft seams. A scanned PDF with no structure has to fall back to
        recursive splitting. PowerPoint must produce one chunk per slide so
        "what was on the Q2 OKR slide?" maps to the literal slide. This
        function is the single place that decision is enacted.

    Decisions made inside (every branch explained):
        1. ``Strategy.heading_based`` → :func:`_chunk_by_headings` with
           ``split_on="heading"``. Used when the document has explicit
           Heading 1/2/3 styles (Word) or ``#`` markdown. Headings are
           the cleanest semantic boundary a PM relies on.
        2. ``Strategy.bold_title_based`` → :func:`_chunk_by_headings` with
           ``split_on="bold_title"``. Same algorithm, different element
           type — used when authors faked headings by bolding a single
           line. Reusing the heading routine keeps section behaviour
           identical so retrieval feels consistent across docs.
        3. ``Strategy.blank_line_based`` → :func:`_chunk_by_blank_lines`.
           Used for stream-of-consciousness notes (meeting minutes typed
           live) where blank lines separate ideas.
        4. ``Strategy.slide_based`` → :func:`chunk_slide_elements`. One
           chunk per slide so "see slide 12" citations are exact.
        5. Anything else (most importantly ``recursive_fallback``) joins
           non-blank element content with double newlines and runs the
           recursive splitter. Joining first means we feed clean paragraph
           breaks to the splitter instead of feeding it 200 individual
           ParsedElements.
        6. ``label = strategy.value`` is captured once and passed to the
           inner chunkers so every chunk's metadata gets a consistent
           ``strategy_used`` value, making it possible to debug "why did
           this PRD chunk so weirdly" later.

    Why Excel and email are not here:
        Excel arrives as a per-sheet dict with headers + rows, not a flat
        ParsedElement list — pipeline.py iterates the sheets and calls
        :func:`chunk_excel_sheet` directly. Email is a single cleaned
        string with thread metadata (sender/subject/date) attached, which
        :func:`chunk_email` consumes directly. Forcing them through the
        same router would require fake "elements" wrappers and break the
        clean shape of each format.

    Returns:
        ``List[Chunk]`` ready for embedding. pipeline.py merges these with
        the document's base_metadata, embeds each ``content`` field, and
        writes the rows to Supabase pgvector.

    What breaks if this is wrong:
        Wrong dispatch = wrong chunk shape. A PM asking "what blocked
        sprint 3?" against a heading-based retro that fell into recursive
        fallback would get random 1000-char windows that overlap the
        Blockers and Wins sections — the answer would mix outcomes with
        problems and the PM would distrust PrismAI.
    """

    # WHY THIS EXISTS IN PRISM AI:
    # We pull the strategy and its string label up front so each branch
    # below stays a one-liner. The label travels into chunk metadata so
    # debugging "why did this OKR doc chunk like that?" is one query
    # away — every chunk literally records the strategy that built it.
    #
    # WHAT THIS BLOCK DOES:
    # Capture the chosen strategy enum and its string value once.
    #
    # WHY THIS WAY:
    # ``strategy.value`` is computed once instead of per branch — keeps
    # the inner chunker calls compact and avoids drift if the enum is
    # ever renamed (one place to update).
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # If we forgot ``strategy = detection.strategy`` and used
    # ``detection`` directly, every comparison below would fail because
    # DetectionResult is not equal to a Strategy enum value — every
    # document would silently fall through to recursive_fallback and
    # PMs would lose section-aware retrieval entirely.
    strategy = detection.strategy
    label = strategy.value

    # WHY THIS EXISTS IN PRISM AI:
    # Heading-based is the gold-standard route for PRDs, sprint planning
    # docs, and OKR write-ups where the author placed real Word "Heading"
    # styles or ``##`` markdown. A PM asking "what's the goal of sprint 4?"
    # gets back the Sprint Goal section verbatim because the chunker cut
    # at the heading boundary above and below it.
    #
    # WHAT THIS BLOCK DOES:
    # Route to the heading chunker, telling it to split on ParsedElement
    # whose ``element_type == "heading"``.
    #
    # WHY THIS WAY:
    # We hard-code ``"heading"`` here so the heading chunker stays
    # generic (it's reused for bold titles below). The strategy label is
    # threaded through so each emitted chunk records ``strategy_used``.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # If we passed ``"paragraph"`` here, the chunker would split on every
    # paragraph and produce one chunk per sentence — Sprint Goal would
    # be 12 micro-chunks and retrieval would lose the section concept.
    if strategy == Strategy.heading_based:
        return _chunk_by_headings(elements, "heading", base_metadata, label)

    # WHY THIS EXISTS IN PRISM AI:
    # Some PMs never use Word's Heading styles — they bold a line and call
    # it a section. signal_detector flags those as ``bold_title_based`` so
    # the same section-boundary chunking still happens. A PM asking "what
    # are our Q2 OKRs?" against a doc that bolded "Q2 OKRs:" instead of
    # styling it H2 still gets the same precise answer.
    #
    # WHAT THIS BLOCK DOES:
    # Route to the heading chunker with ``split_on="bold_title"`` so it
    # treats fully-bold short paragraphs as section breaks.
    #
    # WHY THIS WAY:
    # Reusing ``_chunk_by_headings`` instead of writing a parallel function
    # guarantees identical behaviour — headings and bold titles produce
    # chunks with the same metadata shape, so retrieval ranking is fair.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Falling through to recursive_fallback would lose the bolded section
    # markers and the PM would get blended chunks across "Q1 wins" and
    # "Q2 OKRs" mid-document.
    if strategy == Strategy.bold_title_based:
        return _chunk_by_headings(elements, "bold_title", base_metadata, label)

    # WHY THIS EXISTS IN PRISM AI:
    # Live-typed meeting notes and Slack-pasted retros usually have no
    # headings at all — they use blank lines to separate ideas. Splitting
    # on those preserves the structure the author actually used.
    #
    # WHAT THIS BLOCK DOES:
    # Hand the elements to the blank-line chunker.
    #
    # WHY THIS WAY:
    # The blank-line chunker uses the ``blank`` ParsedElement entries we
    # emit during parsing — without that strategy, those blanks would be
    # noise. This routes them into useful split points.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # The PM asks "what did Alex say in the standup?" and gets Alex's
    # comment glued to Sarah's update because the blank line between them
    # was ignored.
    if strategy == Strategy.blank_line_based:
        return _chunk_by_blank_lines(elements, base_metadata)

    # WHY THIS EXISTS IN PRISM AI:
    # PowerPoint decks must always chunk one slide at a time so citations
    # like "see slide 7" map to the actual slide content; mixing two
    # slides into a chunk breaks visual grounding the PM expects.
    #
    # WHAT THIS BLOCK DOES:
    # Route to the slide chunker which emits one Chunk per slide
    # ParsedElement.
    #
    # WHY THIS WAY:
    # Slide chunking is rule-based, not signal-based — every deck wants
    # this. Routing through the same dispatcher keeps the call site
    # uniform with Word/PDF.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # A PM asking about the "Q2 OKR slide" would get bullets from slide
    # 6 and slide 8 mixed together; slide_number citations would be wrong.
    if strategy == Strategy.slide_based:
        return chunk_slide_elements(elements, base_metadata)

    # WHY THIS EXISTS IN PRISM AI:
    # Recursive fallback is the safety net for documents with no usable
    # structure: scanned PDFs, raw text dumps, transcripts. We still need
    # SOMETHING embeddable, so we glue all real content together with
    # double newlines and let the recursive splitter cut at paragraph,
    # then sentence, then word boundaries.
    #
    # WHAT THIS BLOCK DOES:
    # Build one big string from every non-blank element with content,
    # joining with ``\n\n`` so paragraph breaks are visible to the
    # splitter; then send to ``_recursive_split``.
    #
    # WHY THIS WAY:
    # 1. We skip ``element_type == "blank"`` so emitted page-break or
    #    blank-line markers do not turn into ``\n\n\n\n`` runs that confuse
    #    the splitter.
    # 2. We skip elements with empty ``content`` so the join does not
    #    produce double-double-newlines (which would split on the wrong
    #    boundary and create artificially large chunks).
    # 3. We use ``\n\n`` as the join separator because the recursive
    #    splitter's first pass cuts on exactly that token — we are
    #    handing it pre-aligned natural paragraphs.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # If we joined with ``\n`` instead, the splitter would see one giant
    # paragraph and fall straight through to sentence-level splitting,
    # producing tiny fragments where paragraph context would have been
    # preserved — answers would lose nuance.
    joined = "\n\n".join(
        e.content for e in elements if e.element_type != "blank" and e.content
    )
    return _recursive_split(joined, base_metadata)


def _chunk_by_headings(
    elements: List[ParsedElement],
    split_on: str,
    base_metadata: Dict[str, Any],
    strategy_label: str,
) -> List[Chunk]:
    """Cut a document into one chunk per heading section, isolating tables.

    One-sentence summary: walks the elements top-to-bottom, treats each heading
    (or bold title) as a section boundary, emits the section's body as a chunk,
    and emits each table inside the section as its own chunk.

    Why it exists for PrismAI:
        This is the single most important chunker for PM workflows. PRDs,
        sprint planning docs, retrospectives, and OKR write-ups are all
        section-structured. When a PM asks "what blocked sprint 3?" we MUST
        return only the Blockers section, not Blockers tangled with Wins.
        This function is what makes that possible.

    Decisions made inside (every choice spelled out):
        1. State machine, not a list comprehension — we cannot know where a
           section ends until we hit the next heading, so we accumulate
           paragraphs and tables and "flush" them when the boundary appears.
        2. Heading text is repeated INSIDE the chunk content, not just in
           metadata — the embedding sees "Blockers\\n<body>" so similarity
           search has the section title as a strong signal.
        3. Tables are buffered separately (``current_tables``) and emitted
           AFTER the text body — they are never mixed into prose. A 50-row
           scope matrix in the middle of a paragraph would dominate the
           embedding and make narrative content unsearchable.
        4. Each table becomes its OWN chunk, prefixed with the section
           heading + "[TABLE]" — a PM asking "what's in the scope matrix
           for sprint 4?" gets that exact table back, with the section
           context attached for ranking.
        5. Sections at or under MAX_SECTION_SIZE emit as a single chunk so
           the answer reads as one coherent paragraph block. Oversized
           sections are recursively split, but the heading is RE-PREPENDED
           to each sub-chunk so every fragment still carries "Blockers" in
           its content — retrieval cannot lose track of the section.
        6. ``counter`` is a one-element list, not an int — the inner
           ``_flush`` closure mutates it. Python closures cannot rebind
           outer scalars without ``nonlocal``; the list trick keeps the
           closure tiny.
        7. Blank elements are deliberately skipped — they were structural
           hints for OTHER strategies (blank_line_based); inside a heading
           document they would just inflate the body with empty lines.
        8. Empty ``content`` paragraphs are filtered out at append time so
           ``_flush`` does not emit "\\n\\n\\n" as a "section".
        9. ``strategy_label`` is threaded through so heading_based and
           bold_title_based outputs are distinguishable in the DB even
           though they share this code path.

    Returns:
        ``List[Chunk]`` in document order. pipeline.py embeds each
        ``content`` and writes the row with the rich metadata
        (``section_heading``, ``heading_level``, ``strategy_used``).

    What breaks if this is wrong:
        * Wrong boundary → Blockers content shows up in the Wins chunk.
        * Heading not repeated inside content → the embedding loses
          section context and a query for "blockers" matches generic
          paragraphs across the whole doc.
        * Tables mixed into prose → the chunker emits one giant chunk
          dominated by a scope matrix; "what is the sprint goal?" returns
          a row from that table because the goal text is overwhelmed.
        * Heading not re-prepended on sub-chunks → long sections become
          orphaned fragments and the PM gets cited "chunk 4 of unnamed
          section" with no idea where it came from.
    """

    out: List[Chunk] = []
    # WHY THIS EXISTS IN PRISM AI:
    # Every emitted chunk needs a stable position-in-document. Citations
    # in answers say "Sprint 3 Retro · chunk 4" — that 4 must reflect
    # the order we emitted sections in, INCLUDING any sub-chunks from
    # over-long sections AND any standalone table chunks.
    #
    # WHAT THIS BLOCK DOES:
    # ``counter`` holds the next chunk_index. It's wrapped in a one-
    # element list because the inner ``_flush`` closure mutates it.
    #
    # WHY THIS WAY:
    # Python closures cannot rebind outer scalars without ``nonlocal``.
    # Using a list lets ``_flush`` do ``counter[0] += 1`` cleanly.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Two chunks share an index → Supabase upserts collide on the
    # composite key and one chunk silently overwrites the other; PMs
    # see partial answers from incomplete documents.
    counter = [0]

    # WHY THIS EXISTS IN PRISM AI:
    # We are running a state machine. Until we see the next heading we
    # have to remember (a) which heading we're under, (b) at what level
    # (H1/H2/H3 affects ranking), (c) the running list of body
    # paragraphs, and (d) any tables we've encountered. The flush only
    # happens when the boundary fires, so these four pieces of state
    # have to live across loop iterations.
    #
    # WHAT THIS BLOCK DOES:
    # Initialise the section accumulator state to "no current section".
    #
    # WHY THIS WAY:
    # ``current_heading = ""`` (not None) lets ``if current_heading:``
    # work as a clean truthiness check. ``current_heading_level = 0``
    # mirrors the ParsedElement convention for "not a heading".
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Initialising paragraphs/tables to None would make the first
    # element-append crash with AttributeError.
    current_heading: str = ""
    current_heading_level: int = 0
    current_paragraphs: List[str] = []
    current_tables: List[ParsedElement] = []

    def _flush() -> None:
        """Emit one or more chunks for whatever section state is currently buffered.

        One-sentence summary: turns the accumulated heading + paragraphs +
        tables into Chunk objects, with size-aware splitting.

        Why it exists for PrismAI:
            The outer loop knows WHEN a section ends but does not want to
            know HOW to package it. ``_flush`` is the packaging step that
            decides "small enough to be one chunk" vs "needs recursive
            split with heading re-prepended". Centralising this avoids
            duplicating the size + table emission logic three times.

        Decisions made inside:
            1. Heading is prepended to body text INSIDE content so the
               embedding gets the section title.
            2. Strip after concatenation so leading/trailing blanks from
               odd Word formatting don't become empty content.
            3. Branch on ``len(full_text) <= MAX_SECTION_SIZE``:
               - Short → one Chunk.
               - Long → recursive split, then re-prepend heading to each
                 sub-chunk and overwrite metadata so every sub-chunk
                 still belongs to this section.
            4. Tables flush AFTER text — they are appended to ``out``
               last so chunk order in the DB matches reading order
               (text first, then the table that visually follows).
            5. Each table chunk content uses ``"[TABLE]\\n"`` so the
               embedding can disambiguate table content from prose.
            6. Table metadata merges in the original ParsedElement
               metadata (row_count, col_count from parsers.py) so a
               retrieved table chunk can render with its dimensions
               in the citation UI.

        Returns:
            None — mutates ``out`` and ``counter`` in the enclosing scope.

        What breaks if this is wrong:
            * Skipping the heading prefix → embedding loses section signal.
            * Forgetting to re-prepend heading on sub-chunks → orphaned
              fragments with no section context.
            * Emitting tables before text → chunk order misrepresents
              document order in the UI.
        """

        # WHY THIS EXISTS IN PRISM AI:
        # Body paragraphs were appended one-by-one as we walked elements;
        # the embedding model wants them as one prose block, not as
        # disconnected lines.
        #
        # WHAT THIS BLOCK DOES:
        # Join the buffered paragraphs into a single string with ``\n``
        # between them.
        #
        # WHY THIS WAY:
        # Single newlines (not ``\n\n``) because the heading + body
        # already implies one logical section — extra newlines between
        # paragraphs would not change embedding meaning but would inflate
        # storage. The ``if p is not None`` guard is defensive against
        # any accidental None entries (shouldn't happen, but a future
        # bug elsewhere would corrupt every chunk silently otherwise).
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Joining with empty string would glue sentences end-to-end and
        # the embedding would treat them as one run-on paragraph.
        body_text = "\n".join(p for p in current_paragraphs if p is not None)

        # WHY THIS EXISTS IN PRISM AI:
        # Including the heading inside the chunk content turns
        # "Blockers" into a strong embedding signal. Without it, the
        # chunk would be just paragraphs and a query for "blockers"
        # would have to match purely on body wording.
        #
        # WHAT THIS BLOCK DOES:
        # If we have a heading, build "<heading>\n<body>"; otherwise use
        # body alone (for the prologue text before the first heading).
        #
        # WHY THIS WAY:
        # An ``if current_heading`` check skips the prefix when the
        # document starts with body text before any heading — re-emitting
        # an empty "" + "\n" + body would produce a leading blank line.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Always-prepending would yield "\n<body>" for prologues; the
        # leading newline confuses the recursive splitter's paragraph
        # detection.
        if current_heading:
            full_text = current_heading + "\n" + body_text
        else:
            full_text = body_text
        # WHY THIS EXISTS IN PRISM AI:
        # Word and PDF parsers occasionally produce paragraphs with
        # trailing whitespace or stray newlines. A chunk that starts
        # with "\n   \n" looks empty to a quick eye-check on the DB
        # rows.
        #
        # WHAT THIS BLOCK DOES:
        # Strip leading/trailing whitespace from the assembled text.
        #
        # WHY THIS WAY:
        # ``strip()`` is cheap and idempotent. We only strip the outer
        # whitespace; internal newlines that hold structure are preserved.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Empty-but-whitespace sections would slip past the next
        # ``if full_text:`` check and become embedded empty chunks.
        full_text = full_text.strip()

        # WHY THIS EXISTS IN PRISM AI:
        # Skipping flushes when there is genuinely no content protects
        # against a heading immediately followed by another heading
        # (rare but happens in template documents).
        #
        # WHAT THIS BLOCK DOES:
        # Only emit chunks if there is actual text to embed.
        #
        # WHY THIS WAY:
        # Embedding empty strings wastes API calls and produces zero
        # vectors that pollute similarity search.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Empty rows in Supabase fight for ranking with real chunks and
        # the PM occasionally gets a citation for a chunk with no text.
        if full_text:
            # WHY THIS EXISTS IN PRISM AI:
            # Most retro sections, OKR sections, and Sprint Goal blocks
            # come in well under 1500 characters. Keeping them as one
            # chunk means the PM sees the whole section as a clean
            # block in the answer instead of three half-overlapping
            # fragments.
            #
            # WHAT THIS BLOCK DOES:
            # If the section fits, build one Chunk with full metadata
            # and increment the index counter.
            #
            # WHY THIS WAY:
            # ``{**base_metadata, ...overrides}`` lets us start from the
            # document-level metadata pipeline.py supplied (file name,
            # source URL, owner) and layer the section-specific keys on
            # top. Section keys win on conflict, which is what we want.
            #
            # WHAT BREAKS IF THIS IS WRONG:
            # Skipping section_heading metadata would remove the field
            # the UI uses to label citations ("Sprint 3 Retro · Blockers").
            if len(full_text) <= MAX_SECTION_SIZE:
                meta = {
                    **base_metadata,
                    "section_heading": current_heading,
                    "heading_level": current_heading_level,
                    "strategy_used": strategy_label,
                }
                out.append(
                    Chunk(
                        content=full_text,
                        chunk_index=counter[0],
                        metadata=meta,
                    )
                )
                counter[0] += 1
            # WHY THIS EXISTS IN PRISM AI:
            # Big "Background" sections in PRDs or 5-page Blockers
            # appendices in retros do not fit in one chunk. We split
            # them recursively but keep them branded as the same
            # section so the PM sees "Sprint 3 Retro · Blockers · part 2"
            # in the citation, not orphan fragments.
            #
            # WHAT THIS BLOCK DOES:
            # Recursively split the body text, then re-prepend the
            # heading and stamp section metadata on every sub-chunk.
            # Re-number the chunk_index sequentially using the outer
            # counter so the document's chunk indices stay contiguous.
            #
            # WHY THIS WAY:
            # We pass ``body_text`` (without heading) to ``_recursive_split``
            # because we want the splitter to cut on real paragraphs.
            # Then we manually prepend the heading to each sub-chunk's
            # content so retrieval still gets the section signal.
            # Overwriting ``sub.metadata`` instead of merging is
            # intentional: the recursive splitter emits its own
            # ``strategy_used="recursive_fallback"`` which is true at
            # the splitter level but wrong at the document level —
            # this section is heading_based.
            #
            # WHAT BREAKS IF THIS IS WRONG:
            # If we left strategy_used="recursive_fallback" on long-section
            # sub-chunks, debugging would falsely flag those PRDs as
            # "fell back to recursion" when they actually came through
            # heading routing — masking real chunker problems elsewhere.
            else:
                sub_chunks = _recursive_split(body_text, base_metadata)
                for sub in sub_chunks:
                    if current_heading:
                        sub.content = current_heading + "\n" + sub.content
                    sub.metadata = {
                        **sub.metadata,
                        "section_heading": current_heading,
                        "heading_level": current_heading_level,
                        "strategy_used": strategy_label,
                    }
                    sub.chunk_index = counter[0]
                    counter[0] += 1
                    out.append(sub)

        # WHY THIS EXISTS IN PRISM AI:
        # Sprint planning docs and PRDs are full of tables — scope
        # matrices, RACI, dependency lists, ticket tables. A PM asking
        # "what's in the scope matrix for sprint 4?" must get that
        # exact table back, not a paragraph that mentions it.
        #
        # WHAT THIS BLOCK DOES:
        # Emit each buffered table as its own Chunk. Content is
        # "<heading> [TABLE]\n<table_body>" so the embedding sees both
        # the section context and an explicit table marker.
        #
        # WHY THIS WAY:
        # 1. One chunk per table keeps tables from being split mid-row
        #    (which would be unreadable). MAX_SECTION_SIZE does not
        #    apply here — table integrity beats size limits.
        # 2. The "[TABLE]" marker helps embeddings disambiguate table
        #    content from prose so similarity search ranks them when
        #    the query is tabular ("which tickets are blocked").
        # 3. We merge ``table_el.metadata`` (row_count, col_count) into
        #    the chunk metadata so the UI can render dimensions.
        # 4. Tables are emitted AFTER the body chunks so document
        #    ordering by chunk_index reads correctly: section text →
        #    section table.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Mixing tables inline with prose would let a 30-row table
        # dominate the embedding of a 200-character paragraph and the
        # PM's Sprint Goal query would return rows from the scope
        # matrix instead.
        for table_el in current_tables:
            if current_heading:
                content = current_heading + " [TABLE]\n" + table_el.content
            else:
                content = "[TABLE]\n" + table_el.content
            meta = {
                **base_metadata,
                **(table_el.metadata or {}),
                "section_heading": current_heading,
                "element_type": "table",
                "strategy_used": strategy_label,
            }
            out.append(
                Chunk(
                    content=content,
                    chunk_index=counter[0],
                    metadata=meta,
                )
            )
            counter[0] += 1

    # WHY THIS EXISTS IN PRISM AI:
    # We walk every parsed element exactly once, in document order, so
    # the section state machine sees boundaries in the right sequence.
    # Reordering or skipping any element would mis-attribute content
    # to the wrong section.
    #
    # WHAT THIS BLOCK DOES:
    # Iterate the parsed elements top-to-bottom and route each one
    # based on its element_type.
    #
    # WHY THIS WAY:
    # Single linear pass keeps the implementation simple and matches
    # the natural reading order of the document.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Iterating in reverse or sorting by something else would scramble
    # which paragraphs belong under which heading.
    for el in elements:
        # WHY THIS EXISTS IN PRISM AI:
        # When a PM asks "what blocked sprint 3?" we need to retrieve the
        # exact Blockers section. If we split randomly by character count,
        # blockers content would be mixed with "What Went Well" content in
        # the same chunk. The PM would get irrelevant information mixed
        # with relevant information.
        #
        # WHAT THIS BLOCK DOES:
        # Check if we have hit a new heading element. If yes, flush
        # everything accumulated so far as a chunk before starting the
        # new section.
        #
        # WHY THIS WAY:
        # We flush BEFORE updating current_heading so the previous
        # section's content gets the previous heading as its label,
        # not the new one.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # If we flush after updating current_heading, every section
        # would be labelled with the NEXT section's heading. Sprint
        # Goal content would be labelled as Blockers. Retrieval would
        # return completely wrong sections.
        if el.element_type == split_on:
            _flush()
            current_heading = el.content
            current_heading_level = el.level
            current_paragraphs = []
            current_tables = []
        # WHY THIS EXISTS IN PRISM AI:
        # Tables encountered between headings belong to the CURRENT
        # section (the one we're accumulating). Buffering them lets us
        # emit them as separate chunks during flush instead of merging
        # them into the prose body.
        #
        # WHAT THIS BLOCK DOES:
        # Stash the table element in the current section's table buffer.
        #
        # WHY THIS WAY:
        # Storing the whole ParsedElement (not just its content) keeps
        # row_count/col_count metadata available for the eventual chunk.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Appending ``table_el.content`` to current_paragraphs instead
        # would mix table rows into prose chunks, killing both
        # retrievability of the table and prose embedding quality.
        elif el.element_type == "table":
            current_tables.append(el)
        # WHY THIS EXISTS IN PRISM AI:
        # Blank elements were emitted by parsers as structural hints for
        # OTHER strategies (blank_line_based). Inside a heading-based
        # document they would inflate the body with empty lines that
        # break paragraph joins.
        #
        # WHAT THIS BLOCK DOES:
        # Skip blank elements entirely.
        #
        # WHY THIS WAY:
        # ``continue`` keeps the loop linear; we never accumulate blanks
        # so flush never has to handle them.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Appending blank content to current_paragraphs would put empty
        # strings into the body join, leaving "\n\n" gaps that the
        # recursive splitter would later interpret as paragraph breaks
        # in the wrong places.
        elif el.element_type == "blank":
            continue
        # WHY THIS EXISTS IN PRISM AI:
        # Everything else (paragraphs, bold_titles when split_on is
        # "heading", etc.) is treated as body content for the current
        # section.
        #
        # WHAT THIS BLOCK DOES:
        # Append the element's content to the running paragraph buffer
        # if it has any text.
        #
        # WHY THIS WAY:
        # The ``if el.content`` guard avoids appending empty strings
        # from edge-case ParsedElements that slipped through with
        # ``content=""``. Empty entries here would join into the body
        # as extra newlines.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # No filter → every empty paragraph adds a phantom "\n" to the
        # body, eventually triggering recursive split when the section
        # is otherwise small enough to stay whole.
        else:
            if el.content:
                current_paragraphs.append(el.content)

    # WHY THIS EXISTS IN PRISM AI:
    # The loop only flushes when it SEES a new heading. The very last
    # section never has a "next heading" to trigger the flush, so we
    # have to flush manually after the loop.
    #
    # WHAT THIS BLOCK DOES:
    # Emit the trailing section as the document's final chunk(s).
    #
    # WHY THIS WAY:
    # A separate explicit call is clearer than an awkward sentinel
    # heading at the end of the loop.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Forgetting this final flush would silently truncate every Word
    # doc — its last section (often Conclusions or Next Steps) would
    # never reach Supabase and the PM's queries against that section
    # would return nothing.
    _flush()
    return out


def _chunk_by_blank_lines(
    elements: List[ParsedElement],
    base_metadata: Dict[str, Any],
) -> List[Chunk]:
    """Cut a document into chunks every time a blank line separates paragraphs.

    One-sentence summary: walks the elements, accumulates paragraph content,
    and flushes the buffer as a chunk every time a blank element appears.

    Why it exists for PrismAI:
        Live-typed standup notes, meeting minutes, and Slack-pasted retros
        rarely have headings — instead the author hits Enter twice between
        ideas. A PM asking "what did Alex say in standup?" needs Alex's
        paragraph to be one chunk, separate from Sarah's update right above
        it. Blank-line splitting preserves those soft seams.

    Decisions made inside:
        1. State machine accumulating paragraphs, flushing on blanks —
           same shape as ``_chunk_by_headings`` but simpler because there
           is no heading hierarchy to track.
        2. Tables flush the paragraph buffer FIRST, then emit as their
           own standalone chunk — same isolation principle as the heading
           chunker (tables never mix with prose).
        3. Tables in this strategy do not carry a section heading
           because there is no heading concept here — but the
           ``element_type="table"`` metadata still tags them so the UI
           can render them as tables.
        4. Final flush after the loop catches the last paragraph block
           even if the document didn't end with a blank line.
        5. Empty content paragraphs are filtered at append time so two
           blank lines in a row don't emit empty chunks.
        6. ``counter`` is a plain int (not a list) because there is no
           inner closure here that mutates it across scopes — the inner
           ``_flush_paragraphs`` takes the index in and returns the new
           one, keeping the data flow explicit.

    Returns:
        ``List[Chunk]`` in document order, all tagged
        ``strategy_used="blank_line_based"``. pipeline.py embeds and
        stores them.

    What breaks if this is wrong:
        * Skipping the blank-flush logic → entire transcript becomes
          one chunk; "what did Alex say?" returns the whole standup.
        * Not flushing before a table → the table gets prepended to
          the previous paragraph and the embedding mixes prose with
          tabular data.
        * Forgetting the final flush → the last topic discussed in
          the meeting never makes it to retrieval.
    """

    out: List[Chunk] = []
    # WHY THIS EXISTS IN PRISM AI:
    # Every chunk needs a stable position-in-document for citations
    # like "Standup 12 May · chunk 3". The counter increments only
    # when a real chunk is appended.
    #
    # WHAT THIS BLOCK DOES:
    # Initialise the chunk-index counter to 0.
    #
    # WHY THIS WAY:
    # Plain int (not a list-trick) because the only mutator is
    # ``_flush_paragraphs``, which takes the index in as a parameter
    # and returns the updated value. No closure mutation needed.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Starting at 1 would shift every chunk index by one and break
    # any external system that joins on chunk_index.
    counter = 0
    # WHY THIS EXISTS IN PRISM AI:
    # We must remember the running paragraphs across iterations so a
    # blank line knows what to flush.
    #
    # WHAT THIS BLOCK DOES:
    # Initialise the paragraph accumulator.
    #
    # WHY THIS WAY:
    # Re-binding to a fresh list inside ``_flush_paragraphs`` (via
    # ``nonlocal``) keeps the code straightforward and avoids subtle
    # bugs from clearing an existing list while iterating.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Forgetting to reset after a flush → paragraphs from one chunk
    # leak into the next.
    current_paragraphs: List[str] = []

    def _flush_paragraphs(idx: int) -> int:
        """Emit the buffered paragraphs as a chunk if there is anything to emit.

        One-sentence summary: turns accumulated body lines into one Chunk and
        clears the buffer, returning the next chunk index.

        Why it exists for PrismAI:
            Both the blank handler and the table handler need to flush the
            running paragraph buffer to disk before doing their own thing.
            Putting the logic in one place makes the contract explicit:
            "flush always returns the next index to use".

        Decisions inside:
            1. Use ``nonlocal current_paragraphs`` to reset the buffer
               from inside the closure — the outer ``current_paragraphs``
               must point to a fresh empty list, not the same list with
               its contents popped.
            2. Strip the joined content so leading/trailing whitespace
               from quirky parsers does not produce blank chunks.
            3. Only emit + advance the counter when content is actually
               non-empty — multiple blank elements in a row should not
               create empty chunks.
            4. The function takes ``idx`` and returns the updated value
               instead of mutating an outer scope — explicit data flow,
               easy to reason about.

        Returns:
            Updated chunk index. Caller assigns it back to ``counter`` so
            the outer state stays in sync.

        What breaks if this is wrong:
            * Forgetting ``nonlocal`` → the outer ``current_paragraphs``
              never resets and every flush emits the entire document
              prefix.
            * Returning the wrong index → chunk numbering drifts and
              citations point at neighbours.
        """

        # WHY THIS EXISTS IN PRISM AI:
        # The closure needs to rebind ``current_paragraphs`` to a fresh
        # empty list after flushing. Without ``nonlocal`` the assignment
        # would create a NEW local variable and the outer scope's
        # paragraphs would never clear.
        #
        # WHAT THIS BLOCK DOES:
        # Tells Python this name refers to the enclosing scope's
        # ``current_paragraphs``.
        #
        # WHY THIS WAY:
        # Standard Python idiom for closures that need to rebind, not
        # just mutate, an outer variable.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Without nonlocal, ``current_paragraphs = []`` later in this
        # function shadows instead of resetting; outer scope keeps the
        # old list and every chunk after the first is wrong.
        nonlocal current_paragraphs
        if current_paragraphs:
            content = "\n".join(current_paragraphs).strip()
            # WHY THIS EXISTS IN PRISM AI:
            # Two blank lines in a row should not emit two empty
            # chunks. The double check (buffer non-empty AND joined
            # content non-empty after strip) prevents that.
            #
            # WHAT THIS BLOCK DOES:
            # Only build a Chunk if the assembled content has real text.
            #
            # WHY THIS WAY:
            # Cheap defensive check; no downside other than one extra
            # ``if``.
            #
            # WHAT BREAKS IF THIS IS WRONG:
            # Empty chunks pollute Supabase, embed to all-zero or
            # garbage vectors, and rank against real content for
            # similarity hits — PMs occasionally see an empty citation.
            if content:
                out.append(
                    Chunk(
                        content=content,
                        chunk_index=idx,
                        metadata={
                            **base_metadata,
                            "strategy_used": "blank_line_based",
                        },
                    )
                )
                idx += 1
            # WHY THIS EXISTS IN PRISM AI:
            # After flushing (or trying to flush) we must always reset
            # the buffer so the next paragraph block starts clean.
            #
            # WHAT THIS BLOCK DOES:
            # Reset the paragraph accumulator to an empty list.
            #
            # WHY THIS WAY:
            # Rebinding to a new list (instead of ``.clear()``) is
            # marginally safer if any external code held a reference
            # to the old list — that reference is left undisturbed.
            #
            # WHAT BREAKS IF THIS IS WRONG:
            # No reset → next "flush" would include all previous
            # paragraphs again and chunks would explode in size.
            current_paragraphs = []
        return idx

    for el in elements:
        # WHY THIS EXISTS IN PRISM AI:
        # When a PM dumps standup notes into a doc, they hit Enter
        # twice between speakers. We use those blank lines as the
        # natural cut points. A blank means "the previous topic ended,
        # start a new chunk".
        #
        # WHAT THIS BLOCK DOES:
        # On a blank element, flush whatever paragraphs are buffered
        # so each speaker's turn becomes its own chunk.
        #
        # WHY THIS WAY:
        # Reassigning ``counter = _flush_paragraphs(counter)`` keeps
        # the chunk index synced because flush returns the new value.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # If we ignored blanks, the entire standup would be one giant
        # chunk and Alex's update would be embedded with Sarah's,
        # destroying retrieval precision.
        if el.element_type == "blank":
            counter = _flush_paragraphs(counter)
        # WHY THIS EXISTS IN PRISM AI:
        # If a table appears mid-document we still want it isolated
        # from prose. First we close out any pending paragraphs (so
        # the table doesn't tag onto them), then we emit the table as
        # its own chunk so a PM asking "show me the dependency table"
        # gets the table, not surrounding prose.
        #
        # WHAT THIS BLOCK DOES:
        # 1. Flush running paragraphs first.
        # 2. Build a "[TABLE]\n<body>" chunk and emit it.
        # 3. Increment the counter manually because tables don't go
        #    through ``_flush_paragraphs``.
        #
        # WHY THIS WAY:
        # Same separation principle as ``_chunk_by_headings``: tables
        # are never mixed with prose. The "[TABLE]" prefix gives the
        # embedding model a strong "this is tabular" signal.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Forgetting the flush before emitting the table would glue
        # the previous paragraphs onto the table chunk; forgetting to
        # increment the counter would collide chunk indices.
        elif el.element_type == "table":
            counter = _flush_paragraphs(counter)
            content = "[TABLE]\n" + el.content
            out.append(
                Chunk(
                    content=content,
                    chunk_index=counter,
                    metadata={
                        **base_metadata,
                        **(el.metadata or {}),
                        "element_type": "table",
                        "strategy_used": "blank_line_based",
                    },
                )
            )
            counter += 1
        # WHY THIS EXISTS IN PRISM AI:
        # Anything that's not a blank or a table is body content —
        # actual standup updates, meeting comments, retro thoughts.
        # We accumulate them until the next blank or table appears.
        #
        # WHAT THIS BLOCK DOES:
        # Append the element's content to the running paragraph buffer
        # if it has any text.
        #
        # WHY THIS WAY:
        # The ``if el.content`` guard rejects edge-case empty
        # paragraphs.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # No filter would let empty content slip in as phantom "\n"
        # in the join, distorting chunk size estimates.
        else:
            if el.content:
                current_paragraphs.append(el.content)

    # WHY THIS EXISTS IN PRISM AI:
    # The last topic in a meeting often has no trailing blank line.
    # Without this final flush, the PM's last discussion point would
    # never be embedded.
    #
    # WHAT THIS BLOCK DOES:
    # Flush whatever's left in the paragraph buffer as a final chunk.
    #
    # WHY THIS WAY:
    # Explicit single call after the loop is the clearest pattern; an
    # alternative sentinel-blank-at-end approach would muddle the loop.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # The last paragraph(s) never reach Supabase, leaving a silent
    # data hole — answers about the closing minutes of the standup
    # would always be empty.
    counter = _flush_paragraphs(counter)
    return out


def _pack_with_overlap(
    pieces: List[str],
    join_sep: str,
    sub_splitter: Optional[Any],
) -> List[str]:
    """Greedily pack a list of text pieces into chunks at most ``RECURSIVE_CHUNK`` wide.

    One-sentence summary: assembles pieces into chunks, descends into any piece
    that is itself too big, and copies the last ``RECURSIVE_OVERLAP`` characters
    forward into the next chunk so context flows across the boundary.

    Why it exists for PrismAI:
        When neither headings nor blank lines are usable (think raw transcripts,
        legal PDFs, scanned reports), we still need chunks small enough to embed
        precisely. This function is the reusable engine that powers paragraph,
        sentence, and word-level splitting; the higher-level ``_split_*`` helpers
        just feed it different splits and a different sub-splitter.

    Decisions made inside (every choice spelled out):
        1. Greedy packing — accumulate pieces in ``current`` until adding the
           next piece would exceed ``RECURSIVE_CHUNK``. Greedy keeps chunks
           full so we minimise total chunk count and storage.
        2. Drop ``None`` and skip leading-empty pieces — defensive against
           upstream regex splits that occasionally produce empty entries.
        3. If a single piece is bigger than the budget AND a sub_splitter is
           provided, flush the current buffer and DESCEND. The piece's own
           sub-splits become the new chunks, with the last sub-piece kept
           as ``current`` so the next iteration can still pack things behind it.
        4. ``current[-RECURSIVE_OVERLAP:]`` is prepended to the next piece on
           flush so context bridges the cut. This is the ONLY place overlap is
           applied — heading and blank-line strategies skip it because they
           split at semantic boundaries.
        5. ``join_sep`` is the separator for the natural unit (``\\n\\n`` for
           paragraphs, ``" "`` for sentences/words) so packed chunks read
           correctly when displayed.
        6. The final ``if current`` flush at the end captures whatever was
           buffered when the loop ended.
        7. ``sub_splitter is None`` (word-level) — single overlong words are
           kept as-is; we cannot split a 2000-character URL further without
           breaking it.

    Returns:
        ``List[str]`` — raw chunks; the caller wraps them in :class:`Chunk`
        objects with metadata.

    What breaks if this is wrong:
        * No overlap → answers cite a chunk that says "rate-limited by Stripe"
          without knowing Alex flagged it; PMs see decontextualised quotes.
        * Greedy packing turned eager → chunks exceed RECURSIVE_CHUNK and
          embedding API truncates them silently, losing tail content.
        * Wrong descent → splitter gets stuck at paragraph level for an
          over-long paragraph and emits a 5000-char chunk that ranks badly.
    """

    chunks: List[str] = []
    # WHY THIS EXISTS IN PRISM AI:
    # ``current`` is the in-progress chunk we're greedily filling. We hold
    # it across iterations because a chunk usually spans multiple input
    # pieces (multiple paragraphs, sentences, or words).
    #
    # WHAT THIS BLOCK DOES:
    # Initialise the running buffer to empty.
    #
    # WHY THIS WAY:
    # Empty string is a clean truthiness signal — ``if current:`` later
    # tells us whether to flush.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Initialising to None or a list would force isinstance checks
    # everywhere; an empty string is the simplest sentinel.
    current = ""

    for piece in pieces:
        # WHY THIS EXISTS IN PRISM AI:
        # Upstream splits (regex, str.split) occasionally produce None or
        # empty entries — sentence splitting on "Hello!! " for example.
        # We refuse to embed empty content.
        #
        # WHAT THIS BLOCK DOES:
        # Skip None pieces outright. Skip empty pieces if we have nothing
        # buffered (otherwise we'd pad the buffer with separators).
        #
        # WHY THIS WAY:
        # The two-condition check ``if not piece and not current`` means
        # we only skip empty pieces at the very start; once we have
        # buffered text, we keep going so the loop terminates cleanly.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # No None guard → ``len(None)`` crashes. No empty guard → we
        # emit chunks that contain only the separator like "\n\n".
        if piece is None:
            continue
        if not piece and not current:
            continue

        # WHY THIS EXISTS IN PRISM AI:
        # Sometimes a single "paragraph" is actually a wall of text with
        # no double newlines — e.g. an entire chat-pasted message. That
        # piece alone exceeds RECURSIVE_CHUNK. We must descend into the
        # sub-splitter (sentences, then words) to break it down further.
        #
        # WHAT THIS BLOCK DOES:
        # 1. If we have anything buffered, flush it as a chunk.
        # 2. Hand the over-long piece to the sub-splitter (e.g. sentence
        #    splitter receives an over-long paragraph).
        # 3. Take all but the last sub-result as completed chunks.
        # 4. Keep the last sub-result as ``current`` so the next outer
        #    piece can pack onto it (and benefit from its overlap).
        #
        # WHY THIS WAY:
        # Flushing first preserves chunk order. Keeping the LAST sub-piece
        # as current lets us continue packing — otherwise an over-long
        # piece would always start a new chunk and we'd lose efficiency
        # on the next paragraph.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Skipping the descent → emit a 5000-char chunk; embedding API
        # truncates it silently. Discarding the last sub-piece → lose
        # the tail content of the over-long piece entirely.
        if len(piece) > RECURSIVE_CHUNK and sub_splitter is not None:
            if current:
                chunks.append(current)
                current = ""
            sub = sub_splitter(piece)
            if sub:
                chunks.extend(sub[:-1])
                current = sub[-1]
            continue

        # WHY THIS EXISTS IN PRISM AI:
        # We try to pack the next piece into the running buffer. If it
        # fits, great — bigger chunks mean fewer storage rows and
        # better context. If not, we flush the buffer and start a new
        # one with overlap.
        #
        # WHAT THIS BLOCK DOES:
        # Build a candidate "current + sep + piece" string and check
        # whether it stays under the budget.
        #
        # WHY THIS WAY:
        # The ``if current else piece`` ternary avoids a leading
        # separator when the buffer was empty (otherwise we'd start
        # the chunk with "\n\n" or " ").
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Always concatenating with separator → chunks start with
        # "\n\n", which the recursive splitter on a re-pass would
        # interpret as a paragraph break in the wrong place.
        candidate = (current + join_sep + piece) if current else piece
        if len(candidate) <= RECURSIVE_CHUNK:
            current = candidate
        else:
            # WHY THIS EXISTS IN PRISM AI:
            # The piece would push us over budget. Flush the current
            # buffer, then start a new buffer that begins with the
            # tail of the previous chunk — that's the overlap that
            # lets retrieval surface "Alex flagged the API was..."
            # alongside "...rate-limited by Stripe" instead of one
            # without the other.
            #
            # WHAT THIS BLOCK DOES:
            # 1. Append ``current`` as a finished chunk.
            # 2. Take the trailing RECURSIVE_OVERLAP chars of ``current``.
            # 3. Start the new ``current`` with that overlap + "\n" +
            #    the piece.
            #
            # WHY THIS WAY:
            # We use "\n" between overlap and piece instead of
            # ``join_sep`` because the overlap ends mid-paragraph; a
            # double newline would imply a false paragraph break.
            # The ``if len(current) > RECURSIVE_OVERLAP`` guard avoids
            # IndexError on tiny chunks where current itself is shorter
            # than the overlap.
            #
            # WHAT BREAKS IF THIS IS WRONG:
            # No overlap → cited chunks lose context, PM gets the
            # second half of a sentence with no subject. Wrong
            # separator → false paragraph break confuses any
            # downstream re-parsing.
            if current:
                chunks.append(current)
                overlap = (
                    current[-RECURSIVE_OVERLAP:]
                    if len(current) > RECURSIVE_OVERLAP
                    else current
                )
                current = overlap + "\n" + piece
            # WHY THIS EXISTS IN PRISM AI:
            # If ``current`` was empty AND the candidate exceeds budget,
            # this piece itself is too big and there's nothing to flush.
            # We accept it as a single oversized chunk because we've
            # already exhausted descent (sub_splitter was None or
            # already used).
            #
            # WHAT THIS BLOCK DOES:
            # Take the over-long piece as the new ``current`` so the
            # loop continues to behave sensibly.
            #
            # WHY THIS WAY:
            # Refusing to emit it would lose data; truncating would
            # corrupt content. A slightly oversized chunk is the
            # least-bad option at the deepest split level.
            #
            # WHAT BREAKS IF THIS IS WRONG:
            # Dropping the piece → silent data loss. Aborting → entire
            # function fails on one bad URL or token.
            else:
                current = piece

    # WHY THIS EXISTS IN PRISM AI:
    # The loop only flushes when adding the NEXT piece would exceed the
    # budget. After the last piece, we still have to flush whatever's
    # in the buffer.
    #
    # WHAT THIS BLOCK DOES:
    # Emit the final ``current`` buffer if it has content.
    #
    # WHY THIS WAY:
    # Single explicit final flush mirrors the same pattern in the
    # heading and blank-line chunkers.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Forgetting this → the trailing chunk vanishes; a transcript's
    # closing remarks (often the most important conclusions) never
    # make it to retrieval.
    if current:
        chunks.append(current)
    return chunks


def _split_words(text: str) -> List[str]:
    """Word-level fallback splitter used as the deepest level of recursion.

    One-sentence summary: splits on single spaces and packs words back into
    chunks no bigger than ``RECURSIVE_CHUNK``.

    Why it exists for PrismAI:
        When even sentence-level splitting fails (a 2000-character
        sentence — usually a long URL list or a code snippet), we fall
        back to splitting on words. This is the deepest recursion level;
        nothing splits further than this.

    Decisions inside:
        1. Split on a single space — fast, language-agnostic enough for
           the PM corpus we ingest.
        2. ``sub_splitter=None`` — no further descent. A single word
           longer than RECURSIVE_CHUNK (a giant URL) becomes one
           oversized chunk; we accept that as a known edge case rather
           than break the URL with a synthetic split.
        3. Reuses ``_pack_with_overlap`` so overlap behaviour matches
           every other recursive level.

    Returns:
        ``List[str]`` of raw word-packed chunks. Used internally by
        ``_split_sentences`` only.

    What breaks if this is wrong:
        Long URLs lose characters; embeddings of URL-heavy retros or
        engineering memos get malformed.
    """
    return _pack_with_overlap(text.split(" "), " ", None)


def _split_sentences(text: str) -> List[str]:
    """Sentence-level splitter used by the recursive fallback's middle level.

    One-sentence summary: splits on sentence-ending punctuation followed by
    a space, packs sentences into chunks, descends to word splitting if a
    sentence itself exceeds the budget.

    Why it exists for PrismAI:
        When a paragraph is bigger than RECURSIVE_CHUNK and we can't keep
        it whole, sentence boundaries are the next-best cut. A PM asking
        "what did Alex say about API rate limits?" is far more likely to
        get a clean answer if the chunk ends at a real sentence than if
        it ends mid-thought.

    Decisions inside:
        1. Regex ``(?<=[.?!]) `` — lookbehind for ., ?, or ! followed by
           a literal space. Lookbehind preserves the punctuation INSIDE
           the sentence so chunks read correctly.
        2. We do not split on newlines — that's the paragraph layer's job.
           Splitting on newlines here would double-split and confuse
           pack_with_overlap's separator logic.
        3. sub_splitter is ``_split_words`` — anything that's still too
           big after sentence splitting falls down to word level.

    Returns:
        ``List[str]`` of raw sentence-packed chunks. Used by
        ``_split_paragraphs``.

    What breaks if this is wrong:
        * Splitting on every period would shred decimals like "v1.2"
          and abbreviations like "i.e."; the lookbehind+space rule
          requires a space after, which mostly avoids that.
        * No sub_splitter → over-long sentences emit oversized chunks
          and embeddings truncate.
    """
    sentences = re.split(r"(?<=[.?!]) ", text)
    return _pack_with_overlap(sentences, " ", _split_words)


def _split_paragraphs(text: str) -> List[str]:
    """Paragraph-level splitter — the top of the recursive fallback hierarchy.

    One-sentence summary: splits on double newlines, packs paragraphs into
    chunks, descends to sentence splitting if a paragraph itself overflows.

    Why it exists for PrismAI:
        ``_recursive_split`` calls this first. Paragraphs are the cleanest
        natural cut for prose — keeping them whole means a PM's answer
        about a Sprint 3 retro point reads as a complete thought.

    Decisions inside:
        1. ``text.split("\\n\\n")`` — caller already joined upstream
           elements with double newlines so this aligns with that join.
        2. Separator passed to pack is ``"\\n\\n"`` so reassembled chunks
           re-read like the original document.
        3. sub_splitter is ``_split_sentences`` for the cascade.

    Returns:
        ``List[str]`` of raw paragraph-packed chunks. Consumed by
        ``_recursive_split``.

    What breaks if this is wrong:
        * Splitting on single ``\\n`` would treat every soft-wrapped line
          in a Word doc as a paragraph and over-fragment the chunks.
        * No descent → 5000-char paragraphs in legal PDFs become one
          giant chunk and retrieval loses precision.
    """
    paragraphs = text.split("\n\n")
    return _pack_with_overlap(paragraphs, "\n\n", _split_sentences)


def _recursive_split(
    text: str,
    base_metadata: Dict[str, Any],
) -> List[Chunk]:
    """Last-resort chunker that splits unstructured text into ``Chunk`` objects.

    One-sentence summary: when no headings, blank lines, or slides are
    available, this splits raw text recursively (paragraphs → sentences →
    words) and wraps each piece as a Chunk with overlap between adjacent ones.

    Why it exists for PrismAI:
        Some PM artefacts have no usable structure: scanned PDFs without
        font cues, raw chat transcripts, automated email digests. We still
        need them in retrieval — a PM might ask "did anyone mention OKR-3
        in last week's transcript?" and the answer must come from
        somewhere. This function is that somewhere.

    Decisions made inside:
        1. Strip leading/trailing whitespace BEFORE the size check —
           otherwise a "tiny" all-whitespace input would pass the
           length check and emit a Chunk of empty content.
        2. Empty after strip → return ``[]`` so pipeline.py emits zero
           chunks for a doc with no extractable content (better than
           an empty chunk polluting the DB).
        3. Short enough to fit in one chunk → return one Chunk with
           chunk_index=0. We do not split prematurely; preserving the
           whole text keeps embedding precision high for short docs.
        4. Otherwise → call the cascading paragraph→sentence→word
           splitter via ``_split_paragraphs`` and wrap each resulting
           string as a Chunk with sequential chunk_index from 0.
        5. NO heading prefixes are added here — that is intentionally
           the caller's job. ``_chunk_by_headings`` re-prepends the
           heading on each sub-chunk; raw recursive callers (the dispatch
           in ``chunk_document``) have no heading to prepend.
        6. ``strategy_used="recursive_fallback"`` on every chunk so debug
           queries can surface "which docs are falling back?" easily.
        7. ``base_metadata`` is merged in via ``{**base_metadata, ...}``
           so document-level keys (file name, source) propagate.

    Returns:
        ``List[Chunk]``. pipeline.py embeds each chunk and stores it.
        Empty list if input was empty.

    What breaks if this is wrong:
        * Skipping the empty-after-strip return → empty chunks in DB
          rank against real content and the PM occasionally cites a
          blank source.
        * Forgetting to wrap in Chunk → returning raw strings would
          break the pipeline contract; the embedder expects Chunks.
        * Wrong strategy_used label → makes debugging silent (a
          recursively-split section would not show as recursion in
          metrics).
    """

    # WHY THIS EXISTS IN PRISM AI:
    # Strip BEFORE the empty/length checks so all-whitespace inputs
    # short-circuit out instead of producing whitespace chunks.
    #
    # WHAT THIS BLOCK DOES:
    # Remove leading/trailing whitespace.
    #
    # WHY THIS WAY:
    # Idempotent and cheap. Internal whitespace (paragraph breaks) is
    # preserved because ``strip()`` only touches the ends.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # All-whitespace input would slip through and become a chunk of
    # spaces — embedded as a near-zero vector that pollutes ranking.
    text = text.strip()
    # WHY THIS EXISTS IN PRISM AI:
    # An empty input means the document had nothing extractable (e.g.
    # an image-only PDF that fell through OCR). We must not emit any
    # chunks for it.
    #
    # WHAT THIS BLOCK DOES:
    # Return an empty list immediately on empty input.
    #
    # WHY THIS WAY:
    # Returning ``[]`` is the explicit "no chunks" signal; pipeline.py
    # treats an empty list as "this document contributes nothing" and
    # logs accordingly without writing rows.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Continuing past this point would split "" into [""] and emit a
    # blank Chunk. PMs would occasionally see citations to empty docs.
    if not text:
        return []

    # WHY THIS EXISTS IN PRISM AI:
    # If the entire document fits in one chunk, splitting it would
    # only fragment a coherent answer. A short standup transcript or
    # a one-page memo should embed as a single dense vector.
    #
    # WHAT THIS BLOCK DOES:
    # Return one Chunk containing the whole text, indexed at 0.
    #
    # WHY THIS WAY:
    # Single-chunk path skips all the splitter machinery; cheaper and
    # the result is a perfect representation of the doc.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Always splitting → short docs become 5 micro-chunks that compete
    # for ranking against each other.
    if len(text) <= RECURSIVE_CHUNK:
        return [
            Chunk(
                content=text,
                chunk_index=0,
                metadata={
                    **base_metadata,
                    "strategy_used": "recursive_fallback",
                },
            )
        ]

    # WHY THIS EXISTS IN PRISM AI:
    # Long unstructured input (a 50-page legal PDF without headings)
    # needs to be cascaded down: paragraphs first, then sentences,
    # then words for the few stragglers.
    #
    # WHAT THIS BLOCK DOES:
    # Run the paragraph splitter (which itself descends into sentences
    # and words for over-long pieces).
    #
    # WHY THIS WAY:
    # Keeping the cascade in dedicated helpers (``_split_paragraphs``,
    # ``_split_sentences``, ``_split_words``) makes each level testable
    # in isolation.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Skipping straight to words would shred the document into tiny
    # fragments and destroy retrieval coherence.
    pieces = _split_paragraphs(text)
    chunks: List[Chunk] = []
    # WHY THIS EXISTS IN PRISM AI:
    # Each piece becomes one Chunk with a sequential 0-based index so
    # citations like "page 3, chunk 12" stay stable.
    #
    # WHAT THIS BLOCK DOES:
    # Wrap every text piece in a Chunk with metadata.
    #
    # WHY THIS WAY:
    # ``enumerate`` gives a clean ascending index without manual
    # counters; the wrapper merges base_metadata + strategy_used.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Reusing the same chunk_index across pieces would collide on
    # Supabase's composite key and one piece would silently overwrite
    # another.
    for idx, piece in enumerate(pieces):
        chunks.append(
            Chunk(
                content=piece,
                chunk_index=idx,
                metadata={
                    **base_metadata,
                    "strategy_used": "recursive_fallback",
                },
            )
        )
    return chunks


def chunk_excel_sheet(
    sheet_name: str,
    sheet_data: Dict[str, Any],
    detection: DetectionResult,
    base_metadata: Dict[str, Any],
) -> List[Chunk]:
    """Turn one parsed Excel sheet into Chunks using the chosen tabular strategy.

    One-sentence summary: dispatches to single_chunk, group_by_column, or
    row_based packaging based on the detection strategy chosen by
    :func:`signal_detector.detect_excel_strategy`.

    Why it exists for PrismAI:
        PMs live in spreadsheets — sprint backlogs, Jira exports, OKR rollups,
        dependency matrices, capacity plans. The right chunking depends on the
        sheet's shape:
            * A small status board (≤ 5 rows): one chunk so the PM gets the
              full board back when they ask "what's on the status board?"
            * An epic-keyed backlog (many tickets per epic): one chunk per
              epic so "what's in epic Login Refresh?" returns all tickets
              for that epic together.
            * A long flat list (capacity per person): one chunk per row so
              "what is Alex's capacity?" gets that exact row.

    Decisions made inside (each branch and every formatting choice):
        1. Empty rows → return ``[]`` immediately. An empty sheet contributes
           nothing to retrieval; emitting a single empty chunk would pollute
           the DB with citations to nothing.
        2. ``Strategy.single_chunk`` — emit ALL rows as one chunk prefixed
           with ``[<sheet_name>]``. The square-bracketed sheet name is a
           strong embedding signal for "this is the X sheet" queries.
        3. ``Strategy.group_by_column`` — bucket rows by the detected
           grouping column, preserve first-seen order so the chunk sequence
           matches the original sheet, then format each bucket as one chunk
           with header ``[<sheet>] <col>: <value>``. Tickets for the same
           epic stay together so a single retrieval surfaces the whole
           epic. The grouping column is REMOVED from each row's ``"Col: val"``
           formatting because it would just repeat ``epic: Login Refresh``
           on every line; the header row already carries it.
        4. Default row-based — one chunk per non-empty row, prefixed with
           ``[<sheet_name>]`` and formatted as ``"Col: val | Col: val"``.
        5. ``" | "`` between fields — pipes almost never appear in Excel
           values so they parse cleanly downstream and survive embedding.
        6. ``f"{h}: {v}"`` — column-name + value preserved together so the
           embedding sees both context and data; "Status: Blocked" is a far
           stronger retrieval cue than just "Blocked".
        7. ``if row.get(h)`` filter — drop empty cells from the formatted
           line so chunks don't contain ``"Owner: "`` for unfilled columns.
        8. Row-based skips rows that are fully empty after stringification
           — same reasoning as parsers' empty-row filter, applied here as
           well so a chunker called directly by a test still behaves.
        9. Per-strategy ``strategy_used`` metadata makes downstream debug
           queries trivial ("how many chunks were group_by_column today?").
        10. ``sheet_name`` always lands in metadata so retrieval can filter
            "only show me Sprint 24 backlog rows".

    Returns:
        ``List[Chunk]``. pipeline.py iterates the workbook and calls this
        per sheet, then merges all returned chunks for the file.

    What breaks if this is wrong:
        * Wrong strategy dispatch → epic-keyed backlogs flatten to one row
          per chunk and "what's in Login Refresh?" returns one ticket
          instead of the whole epic.
        * Missing sheet_name in metadata → retrieval cannot filter by
          sheet; the PM gets backlog rows mixed with capacity rows.
        * Group column not removed from per-row formatting → every line
          repeats the epic name, embeddings tilt heavily on that token,
          recall drops.
    """

    # WHY THIS EXISTS IN PRISM AI:
    # parsers.parse_excel returns ``{"headers": [...], "rows": [...]}``.
    # We pull both with safe defaults so missing keys don't crash; an
    # empty sheet still returns a usable structure further down.
    #
    # WHAT THIS BLOCK DOES:
    # Extract headers and rows from the sheet payload.
    #
    # WHY THIS WAY:
    # ``or []`` after ``.get(...)`` defends against ``None`` values — a
    # sheet with a single None entry would crash a list iteration.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Calling ``.get(...)`` without the ``or []`` fallback and getting
    # None back would cause iteration to crash, taking down the entire
    # ingestion of any workbook with one quirky sheet.
    headers: List[str] = sheet_data.get("headers", []) or []
    rows: List[Dict[str, Any]] = sheet_data.get("rows", []) or []

    # WHY THIS EXISTS IN PRISM AI:
    # An empty sheet should contribute zero chunks. Emitting a single
    # empty chunk would clutter the DB and produce empty citations.
    #
    # WHAT THIS BLOCK DOES:
    # Short-circuit return on no data rows.
    #
    # WHY THIS WAY:
    # Empty list signals "nothing to embed" to pipeline.py.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Falling through would emit a chunk containing only ``[<sheet>]``
    # which embeds as the sheet name alone — false positives whenever
    # someone queries the sheet's name.
    if not rows:
        return []

    out: List[Chunk] = []

    # WHY THIS EXISTS IN PRISM AI:
    # Tiny sheets (status boards, summary dashboards) make sense as a
    # single chunk so a PM asking "what's on the dashboard?" gets the
    # whole thing back as one coherent answer.
    #
    # WHAT THIS BLOCK DOES:
    # Format every row as "Col: val | Col: val", join with newlines,
    # prefix with the sheet name, emit one Chunk.
    #
    # WHY THIS WAY:
    # 1. ``[<sheet_name>]`` prefix gives the embedding a strong
    #    document-identity signal — ranking improves for sheet-named
    #    queries.
    # 2. ``" | "`` between fields is a low-collision separator (pipes
    #    rarely appear in PM cell values).
    # 3. ``if row.get(h)`` skips empty cells so the chunk is not full
    #    of "Owner: | Status:" placeholders.
    # 4. ``chunk_index=0`` because this strategy always emits exactly
    #    one chunk per sheet.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Skipping the prefix → embedding can't disambiguate which sheet
    # a row came from. Failing to filter empty cells → embedding is
    # dominated by repeated empty placeholders.
    if detection.strategy == Strategy.single_chunk:
        row_lines = [
            " | ".join(
                f"{h}: {row.get(h, '')}" for h in headers if row.get(h)
            )
            for row in rows
        ]
        body = "\n".join(line for line in row_lines if line)
        content = f"[{sheet_name}]\n" + body
        out.append(
            Chunk(
                content=content,
                chunk_index=0,
                metadata={
                    **base_metadata,
                    "sheet_name": sheet_name,
                    "strategy_used": "single_chunk",
                },
            )
        )
        return out

    # WHY THIS EXISTS IN PRISM AI:
    # The most common PM question against a backlog is "what's in epic X?"
    # or "show me all sprint 4 tickets". Grouping rows by a low-cardinality
    # column (epic, sprint, status, owner) means the answer is one chunk,
    # not five.
    #
    # WHAT THIS BLOCK DOES:
    # Bucket rows by their value in detection.group_by_column,
    # preserving first-seen order, then emit one Chunk per bucket
    # with a header line and per-row "Col: val" lines (excluding the
    # group column from per-row formatting).
    #
    # WHY THIS WAY:
    # 1. ``order`` preserves insertion order — Python 3.7+ dicts also
    #    preserve insertion order so this could rely on that, but the
    #    explicit list is clearer about intent.
    # 2. ``group_col`` defaults to "" if detection didn't set it, so we
    #    fail soft (one giant bucket keyed on "") instead of crashing.
    # 3. The group value goes into metadata as ``group_value`` so
    #    retrieval can filter "only show Login Refresh epic chunks".
    # 4. We exclude ``group_col`` from each row's formatted line because
    #    it's already in the header — repeating it would inflate every
    #    row line and bias the embedding toward that one column.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Not preserving order → chunks for the same epic appear in random
    # positions; UI ordering by chunk_index no longer matches sheet
    # order. Including the group_col in row lines → every row repeats
    # ``epic: Login Refresh``, embeddings over-rank that token.
    if detection.strategy == Strategy.group_by_column:
        group_col = detection.group_by_column or ""
        groups: Dict[str, List[Dict[str, Any]]] = {}
        order: List[str] = []
        for row in rows:
            gv_raw = row.get(group_col, "") if group_col else ""
            gv = "" if gv_raw is None else str(gv_raw)
            if gv not in groups:
                groups[gv] = []
                order.append(gv)
            groups[gv].append(row)

        idx = 0
        for gv in order:
            rows_in_group = groups[gv]
            row_lines = [
                " | ".join(
                    f"{h}: {row.get(h, '')}"
                    for h in headers
                    if row.get(h) and h != group_col
                )
                for row in rows_in_group
            ]
            body = "\n".join(line for line in row_lines if line)
            content = f"[{sheet_name}] {group_col}: {gv}\n" + body
            out.append(
                Chunk(
                    content=content,
                    chunk_index=idx,
                    metadata={
                        **base_metadata,
                        "sheet_name": sheet_name,
                        "group_by": group_col,
                        "group_value": gv,
                        "strategy_used": "group_by_column",
                    },
                )
            )
            idx += 1
        return out

    # WHY THIS EXISTS IN PRISM AI:
    # Default row-based — one chunk per row. Used when the sheet is a
    # flat list (capacity per person, dependencies per ticket) and we
    # want each entry retrievable on its own.
    #
    # WHAT THIS BLOCK DOES:
    # Walk every row, skip fully empty ones, format as
    # "Col: val | Col: val", prefix with sheet name, emit a Chunk
    # carrying the row's index for citation.
    #
    # WHY THIS WAY:
    # 1. ``row_index=row_index`` (the original Excel row index) goes
    #    into metadata so the UI can deep-link "row 14 of capacity sheet".
    # 2. The empty-row guard re-checks even though parsers also drops
    #    empty rows — defence-in-depth in case this function is ever
    #    called with hand-built test data.
    # 3. ``f"{h}: {v}"`` keeps column context with the value, same as
    #    other branches.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Including empty rows → empty chunks. Losing row_index → citations
    # cannot point at a specific row, just "somewhere in the sheet".
    idx = 0
    for row_index, row in enumerate(rows):
        if not any(
            (v is not None) and str(v).strip() != "" for v in row.values()
        ):
            continue
        formatted = " | ".join(f"{h}: {v}" for h, v in row.items() if v)
        content = f"[{sheet_name}]\n" + formatted
        out.append(
            Chunk(
                content=content,
                chunk_index=idx,
                metadata={
                    **base_metadata,
                    "sheet_name": sheet_name,
                    "row_index": row_index,
                    "strategy_used": "row_based",
                },
            )
        )
        idx += 1
    return out


def chunk_slide_elements(
    elements: List[ParsedElement],
    base_metadata: Dict[str, Any],
) -> List[Chunk]:
    """Emit exactly one chunk per slide so deck citations stay slide-accurate.

    One-sentence summary: walks the slide ParsedElements and turns each one
    into a Chunk whose metadata carries the original slide_number.

    Why it exists for PrismAI:
        PMs cite decks by slide ("see slide 12"). When they ask "what was
        on the Q2 OKR slide?" or "what did the launch deck say about
        risk?", we must return the literal slide content, not slide N
        glued to slide N+1. One ParsedElement per slide → one Chunk per
        slide is the most reliable mapping.

    Decisions made inside:
        1. Skip non-slide elements — defensive, in case ``elements`` was
           built by a future parser that interleaves other types.
        2. Sequential ``chunk_index`` from 0 — keeps DB ordering aligned
           with deck order so the UI can sort citations naturally.
        3. ``slide_number`` is only set in metadata when the parsed
           element has it. PowerPoint always provides it; defensive
           branch protects against future formats (Google Slides export,
           etc.) that might omit it.
        4. ``strategy_used="slide_based"`` on every chunk — consistent
           with other strategies for debug querying.
        5. We do NOT split or merge slide content — the parser already
           merged title + body + notes into one string per slide.
           Splitting again would break "see slide 12" precision.

    Returns:
        ``List[Chunk]``. pipeline.py embeds and stores them.

    What breaks if this is wrong:
        * Splitting slides → cited slide numbers no longer match what
          the PM sees in the deck.
        * Missing slide_number metadata → citations show "Q2 Roadmap
          deck · chunk 6" instead of "slide 7", confusing reviewers.
        * Skipping slides that have empty content → slide indices
          drift and "slide 7" cites "slide 8" instead.
    """

    out: List[Chunk] = []
    # WHY THIS EXISTS IN PRISM AI:
    # Each emitted Chunk needs a stable position-in-document index
    # used by the UI to sort citations.
    #
    # WHAT THIS BLOCK DOES:
    # Initialise the chunk index counter to 0.
    #
    # WHY THIS WAY:
    # Plain int — no closures here that need a list-trick.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Starting at a non-zero number would shift all chunk indices and
    # break any external system that joins on chunk_index.
    idx = 0
    for el in elements:
        # WHY THIS EXISTS IN PRISM AI:
        # Future parser changes might mix other element types into a
        # PowerPoint output; we defensively only chunk what we expect.
        #
        # WHAT THIS BLOCK DOES:
        # Skip any element that isn't a slide.
        #
        # WHY THIS WAY:
        # Single-line guard, no surprises.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Treating a non-slide element as a slide would produce a
        # chunk with no slide_number and a confusing content type.
        if el.element_type != "slide":
            continue

        # WHY THIS EXISTS IN PRISM AI:
        # We start every chunk's metadata from the document-level
        # base_metadata pipeline.py supplied (file path, source, etc.)
        # then layer slide-specific keys on top.
        #
        # WHAT THIS BLOCK DOES:
        # Initialise this chunk's metadata dict.
        #
        # WHY THIS WAY:
        # ``{**base_metadata, ...}`` creates a fresh dict so we don't
        # mutate base_metadata across iterations (the ParsedElement
        # default-factory pattern fixed this for parsers; we keep the
        # discipline here too).
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Mutating base_metadata directly would carry slide_number
        # forward into the next slide's metadata.
        meta: Dict[str, Any] = {
            **base_metadata,
            "strategy_used": "slide_based",
        }
        # WHY THIS EXISTS IN PRISM AI:
        # The "Q2 OKR slide" question only works if the chunk metadata
        # records WHICH slide it came from. parsers.parse_pptx writes
        # slide_number into the ParsedElement's metadata; we copy it
        # straight into the Chunk metadata.
        #
        # WHAT THIS BLOCK DOES:
        # Conditionally set ``slide_number`` on the chunk metadata.
        #
        # WHY THIS WAY:
        # Defensive ``if el.metadata and "slide_number" in el.metadata`` —
        # ParsedElement.metadata could in principle be None or missing
        # the key in future formats; we set it only when available.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # No slide number → citations look like "deck · chunk 5" with
        # no slide reference; users have to count slides manually.
        if el.metadata and "slide_number" in el.metadata:
            meta["slide_number"] = el.metadata["slide_number"]
        out.append(
            Chunk(
                content=el.content,
                chunk_index=idx,
                metadata=meta,
            )
        )
        idx += 1
    return out


def chunk_email(
    clean_body: str,
    email_metadata: Dict[str, Any],
) -> List[Chunk]:
    """Turn a cleaned email body into Chunks, repeating sender/subject/date on each.

    One-sentence summary: prefixes every chunk with a fixed
    "From / Subject / Date" header so each retrieved chunk carries enough
    context to be useful on its own; short emails stay as one chunk, long
    emails get paragraph-packed under :data:`EMAIL_MAX_CHUNK`.

    Why it exists for PrismAI:
        Email is the most context-dependent format we ingest. A PM asking
        "what did Alex say about the API?" needs a chunk that contains both
        Alex's name (sender) and the API quote — without the From/Subject
        header repeated on every chunk, retrieval would surface body text
        with no idea who said it. Repeating the prefix is intentional: a
        small storage cost in exchange for self-contained citations.

    Decisions made inside (each one explained):
        1. Pull sender/subject/date with safe defaults — missing fields
           don't crash the pipeline; the prefix just shows blanks for
           those slots.
        2. Build a single ``prefix`` string used for the whole-email
           single-chunk path AND as the seed of every long-email chunk.
        3. ``len(full_text) <= 500`` short-circuit — the vast majority of
           PM emails (status pings, decision confirmations) fit easily.
           One chunk preserves the conversation as a single embeddable
           unit and avoids over-fragmentation.
        4. The 500-char ceiling is deliberately tighter than RECURSIVE_CHUNK.
           Email is conversational; we want to split sooner so each chunk
           focuses on one topic, not three.
        5. Long-email path splits on ``\\n\\n`` (paragraphs as the
           parser left them) and PACKS them up to ``EMAIL_MAX_CHUNK``.
           Packing — instead of one paragraph per chunk — keeps related
           paragraphs together (e.g. an intro + the actual decision).
        6. ``current = prefix + para`` on overflow — every new chunk
           starts with the prefix, restating "From: Alex | Subject: ..."
           so retrieval citations look uniform.
        7. ``current.strip() != prefix.strip()`` guard before flushing —
           never emit a chunk that's literally just the prefix; it would
           contain no body content.
        8. Final flush after the loop so the trailing buffer reaches
           Supabase even if the email didn't end on a paragraph boundary.
        9. ``if not out`` last-resort emit of ``full_text`` — if every
           paragraph was empty (rare but possible with weird HTML
           cleanups), still emit something so the email isn't lost.
        10. ``strategy_used="paragraph_based"`` on every chunk — labels
            this strategy distinctly from the document-level ones.

    Why repeating the prefix on every chunk:
        Without the repeat, retrieving the second chunk of a long email
        would yield body text disconnected from "who said this when".
        The PM would have to manually look up the citation each time.
        The repeated prefix is what makes "what did Alex say about the
        API?" return a self-contained answer in one query.

    Returns:
        ``List[Chunk]``. pipeline.py embeds and stores them.

    What breaks if this is wrong:
        * Skipping the prefix repeat → "what did Alex say?" returns body
          text with no name attached; the answer is unattributable.
        * Wrong size cap (too high) → conversational emails become one
          chunk that mixes three topics and ranks for none.
        * Wrong size cap (too low) → every paragraph splits, decisions
          get separated from their setup, retrieval pulls half-context.
        * Forgetting the trailing flush → the closing paragraph
          (often "Approved" or "Let's ship") never reaches the DB.
    """

    # WHY THIS EXISTS IN PRISM AI:
    # email_metadata may be missing fields (parser failed to extract
    # subject, message had no date, etc.). Defaults of "" let the
    # prefix render with empty slots instead of crashing.
    #
    # WHAT THIS BLOCK DOES:
    # Pull sender, subject, date with safe string defaults.
    #
    # WHY THIS WAY:
    # The double-default pattern ``email_metadata.get(k, "") or ""``
    # protects against both missing keys AND keys whose value is None.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # No fallback → ``KeyError`` on the format string crashes the
    # entire ingestion pipeline for any email with even one missing
    # header field.
    sender = email_metadata.get("sender", "") or ""
    subject = email_metadata.get("subject", "") or ""
    date = email_metadata.get("date", "") or ""

    # WHY THIS EXISTS IN PRISM AI:
    # The prefix is the "envelope" we want at the top of every email
    # chunk. By keeping it as a single string we can prepend it
    # uniformly in both the short-email and long-email paths.
    #
    # WHAT THIS BLOCK DOES:
    # Build the envelope prefix and assemble the full text used for
    # the size-check path.
    #
    # WHY THIS WAY:
    # ``\n\n`` after the prefix gives the body a clean paragraph
    # break — when the recursive splitter or any consumer looks at
    # the chunk, the first paragraph is the envelope, the rest is
    # the message.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Single newline after the prefix → embedding treats envelope and
    # body as one continuous paragraph and ranking weights them
    # awkwardly. Wrong field order → citation UIs that assume
    # "From | Subject | Date" mis-display fields.
    prefix = f"From: {sender} | Subject: {subject} | Date: {date}\n\n"
    full_text = prefix + (clean_body or "")

    # WHY THIS EXISTS IN PRISM AI:
    # We capture the email metadata + strategy label once so every
    # emitted chunk gets a consistent metadata bag. Every email field
    # (sender, subject, date, thread_id, etc.) survives onto every
    # chunk for citations and filtering.
    #
    # WHAT THIS BLOCK DOES:
    # Build the shared metadata template.
    #
    # WHY THIS WAY:
    # Storing it once and ``dict(base_meta)``-cloning per emission
    # avoids accidental cross-mutation between chunks.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Reusing the same dict across chunks → mutating one mutates all;
    # subtle bugs where every chunk thinks it's the LAST chunk in
    # the thread.
    base_meta = {**email_metadata, "strategy_used": "paragraph_based"}

    # WHY THIS EXISTS IN PRISM AI:
    # Most PM emails are short — a status ping, a decision, an
    # acknowledgement. Splitting them is overkill and would dilute
    # the embedding. We use 500 chars (tighter than RECURSIVE_CHUNK)
    # because email is conversational — short cohesion matters more
    # than long packing.
    #
    # WHAT THIS BLOCK DOES:
    # If prefix + body fits under 500 chars, emit one Chunk and
    # return immediately.
    #
    # WHY THIS WAY:
    # The single-chunk path is a fast exit; everything below assumes
    # we're in the long-email mode.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Cap too high → emails with 3 distinct topics ride together in
    # one chunk and rank weakly for any single topic. Cap too low →
    # short emails get split mid-thought.
    if len(full_text) <= 500:
        return [
            Chunk(
                content=full_text.strip(),
                chunk_index=0,
                metadata=dict(base_meta),
            )
        ]

    # WHY THIS EXISTS IN PRISM AI:
    # Long emails are split on paragraph boundaries — the natural
    # author cut. parse_email_body already collapsed odd whitespace
    # so ``\n\n`` here is a reliable paragraph signal.
    #
    # WHAT THIS BLOCK DOES:
    # Split the body into paragraphs.
    #
    # WHY THIS WAY:
    # Paragraphs preserve the author's logical units (intro,
    # decision, follow-up, sign-off). Splitting on single newlines
    # would over-fragment by treating soft-wrapped lines as
    # separate paragraphs.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Splitting on ``\n`` → a wrapped paragraph becomes 4 chunks of
    # half-sentences and retrieval has nothing coherent to surface.
    paragraphs = (clean_body or "").split("\n\n")
    out: List[Chunk] = []
    idx = 0
    # WHY THIS EXISTS IN PRISM AI:
    # ``current`` is the in-progress chunk. We seed it with the
    # prefix so even the first emitted chunk carries the envelope.
    #
    # WHAT THIS BLOCK DOES:
    # Initialise the running buffer to the envelope.
    #
    # WHY THIS WAY:
    # Pre-seeding with prefix ensures every chunk starts with
    # "From | Subject | Date". The same seed is used after each
    # flush below to restate the envelope.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Starting empty → first chunk has no envelope and the citation
    # for the first chunk loses sender attribution.
    current = prefix

    for para in paragraphs:
        # WHY THIS EXISTS IN PRISM AI:
        # ``split("\n\n")`` can produce empty strings around runs of
        # blank lines. We skip those instead of letting them push the
        # buffer over budget with extra "\n\n" separators.
        #
        # WHAT THIS BLOCK DOES:
        # Skip empty paragraphs.
        #
        # WHY THIS WAY:
        # Cheap guard, no downside.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Including empty paragraphs would inflate ``current`` with
        # whitespace and trigger early flushes.
        if not para:
            continue
        # WHY THIS EXISTS IN PRISM AI:
        # We test whether adding the next paragraph would push the
        # buffer over EMAIL_MAX_CHUNK. If it stays under, keep
        # packing; if it overflows, flush and restart with prefix.
        #
        # WHAT THIS BLOCK DOES:
        # Build a candidate "current + (paragraph break) + para" so
        # we can measure its length.
        #
        # WHY THIS WAY:
        # The ``current.endswith("\n\n")`` check avoids inserting an
        # extra "\n\n" right after the prefix (which itself ends in
        # "\n\n"). Without this we'd see "prefix\n\n\n\nbody" with
        # an extra blank line that confuses re-parsing.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Always inserting "\n\n" → leading body text starts with an
        # awkward blank line. Never inserting → paragraphs run
        # together with no break and the embedding loses paragraph
        # structure.
        candidate = current + para if current.endswith("\n\n") else current + "\n\n" + para
        if len(candidate) > EMAIL_MAX_CHUNK:
            # WHY THIS EXISTS IN PRISM AI:
            # We're flushing because adding ``para`` would overflow.
            # We only flush a chunk that contains real body content,
            # not just the bare prefix — a chunk that's only the
            # envelope provides no answer.
            #
            # WHAT THIS BLOCK DOES:
            # 1. If ``current`` has more than just the prefix, emit
            #    it as a Chunk.
            # 2. Reset ``current`` to ``prefix + para`` so the next
            #    chunk starts with the envelope plus this paragraph.
            #
            # WHY THIS WAY:
            # Comparing stripped strings handles trailing newlines on
            # the prefix vs current; ``dict(base_meta)`` clones the
            # metadata so independent chunks don't share references.
            #
            # WHAT BREAKS IF THIS IS WRONG:
            # Skipping the strip-equality check could emit envelope-
            # only chunks (no answer). Reassigning ``current = para``
            # without prefix → subsequent chunks lose the envelope.
            if current.strip() != prefix.strip():
                out.append(
                    Chunk(
                        content=current.strip(),
                        chunk_index=idx,
                        metadata=dict(base_meta),
                    )
                )
                idx += 1
            current = prefix + para
        else:
            # WHY THIS EXISTS IN PRISM AI:
            # The candidate fits — keep packing. Bigger chunks
            # (within EMAIL_MAX_CHUNK) preserve more conversational
            # context per retrieval.
            #
            # WHAT THIS BLOCK DOES:
            # Accept the candidate as the new buffer.
            #
            # WHY THIS WAY:
            # Greedy packing minimises chunk count.
            #
            # WHAT BREAKS IF THIS IS WRONG:
            # Forgetting to update ``current`` would replay the same
            # paragraph forever / skip it entirely depending on the
            # variant.
            current = candidate

    # WHY THIS EXISTS IN PRISM AI:
    # The loop only flushes when overflow happens. The final
    # paragraph(s) sit in the buffer at the end and need an explicit
    # flush — same as in every other chunker in this file.
    #
    # WHAT THIS BLOCK DOES:
    # If the buffer holds real body content (not just prefix), emit
    # it as the final chunk.
    #
    # WHY THIS WAY:
    # Same strip-equality safeguard as inside the loop, applied once
    # at the tail.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # No final flush → the closing paragraph of the email (often the
    # actual decision: "Approved" / "Let's ship") never reaches
    # Supabase and "what did Alex decide?" returns nothing.
    if current.strip() and current.strip() != prefix.strip():
        out.append(
            Chunk(
                content=current.strip(),
                chunk_index=idx,
                metadata=dict(base_meta),
            )
        )
        idx += 1

    # WHY THIS EXISTS IN PRISM AI:
    # Edge case: a long email whose body, after parser cleanup, is
    # entirely empty paragraphs. ``out`` would be empty after the
    # loop, leaving the email unindexed. We emit one fallback chunk
    # with the full text (envelope + whatever body remained) so
    # the email is still discoverable.
    #
    # WHAT THIS BLOCK DOES:
    # If nothing was emitted, emit the entire ``full_text`` as a
    # single chunk.
    #
    # WHY THIS WAY:
    # Fallback to the originally-built ``full_text`` rather than
    # synthesising — guarantees the chunk has at least the envelope
    # plus any non-empty content.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # No fallback → an empty-body email becomes invisible to
    # retrieval; PMs can never find it even though it was processed.
    if not out:
        out.append(
            Chunk(
                content=full_text.strip(),
                chunk_index=0,
                metadata=dict(base_meta),
            )
        )

    return out
