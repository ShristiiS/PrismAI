"""Embedding client for PrismAI ingestion and retrieval.

Turns a list of text strings into a list of 1536-dimension float vectors using
the OpenRouter-proxied ``openai/text-embedding-3-small`` model. This module
never opens files — its only inputs are strings handed to it by ingestion or
the query path. Credentials are read from environment variables at import time
via ``python-dotenv`` and the module fails loudly if either is missing.

Why this module exists for PrismAI:
    Every chunk that ingestion produces has to become a vector before it can
    live in Supabase pgvector. Every PM question has to become a vector
    before we can search. This is the single, narrow piece of code that
    converts text → vector. Keeping it tiny and well-tested means the rest
    of the pipeline never has to think about HTTP, retries, or token limits.
"""

from __future__ import annotations

# WHY THIS EXISTS IN PRISM AI:
# ``os`` is how we read environment variables (the API key, the base URL).
# ``time`` powers the small sleep between batches so we never hammer the
# API. ``logging`` gives us batch-level progress logs so a 30-minute
# ingest is observable from the terminal. ``List`` is the public type
# contract for inputs and outputs. ``httpx`` is our HTTP client (modern,
# supports timeouts cleanly). ``load_dotenv`` makes the local backend/.env
# file usable without exporting variables manually.
#
# WHAT THIS BLOCK DOES:
# Pull in every dependency the module needs — stdlib first, then external.
#
# WHY THIS WAY:
# Standard library imports first, then third-party. Keeps imports
# auditable; if any of these go missing we want a clear ImportError at
# module load instead of a cryptic NameError mid-batch.
#
# WHAT BREAKS IF THIS IS WRONG:
# Missing httpx → embedder cannot make API calls; ingestion silently
# embeds nothing. Missing dotenv → credentials never load and every call
# fails 401 mid-batch.
import logging
import os
import time
from typing import List

import httpx
from dotenv import load_dotenv


# WHY THIS EXISTS IN PRISM AI:
# pipeline.py imports this module exactly once at startup. Calling
# ``load_dotenv()`` at module load time means env vars from
# backend/.env are available before any constant below is read. Doing
# this lazily inside each function would invite a "first call fails,
# second call works" debugging headache.
#
# WHAT THIS BLOCK DOES:
# Loads ``backend/.env`` into ``os.environ`` if not already present.
#
# WHY THIS WAY:
# ``load_dotenv`` is a no-op if the file is missing or values are
# already set, so it's safe in production where vars come from the
# real environment.
#
# WHAT BREAKS IF THIS IS WRONG:
# Without this call, running ``uvicorn`` from a fresh shell would not
# see the keys in backend/.env and the embedder would fail on the
# very first PM upload.
load_dotenv()


# WHY THIS EXISTS IN PRISM AI:
# Every function in this file logs progress so a long ingestion is
# observable. A module-level logger keyed on ``__name__`` lets the
# pipeline's logging configuration (in main.py) attach the right
# handlers and level without each function having to know.
#
# WHAT THIS BLOCK DOES:
# Creates the embedder's logger.
#
# WHY THIS WAY:
# ``logging.getLogger(__name__)`` is the canonical Python pattern;
# the logger inherits root-level config so handlers added in the
# FastAPI startup get respected here automatically.
#
# WHAT BREAKS IF THIS IS WRONG:
# A bare ``print(...)`` would not respect logging levels and would
# spam stdout in production. ``logging.getLogger()`` (no name) would
# attach to the root logger and pollute logs from unrelated modules.
logger = logging.getLogger(__name__)


# WHY THIS EXISTS IN PRISM AI:
# Constants captured once at module load make the rest of the file
# trivially readable. Hard-coded literals scattered through API calls
# are the easiest way to ship a "wrong dimension count" bug into prod.
#
# WHAT THIS BLOCK DOES:
# Pull credentials from env. Hardcode model identity and tuning knobs
# that should not change at runtime.
#
# WHY THIS WAY:
# 1. ``OPENAI_API_KEY`` / ``OPENAI_BASE_URL`` come from env so we never
#    commit secrets and so the same code works locally, in staging,
#    and in production with different keys.
# 2. ``EMBEDDING_MODEL = "text-embedding-3-small"`` — OpenRouter
#    routes the OpenAI prefix to the actual OpenAI embedding model.
#    1536-dim is OpenAI's default for this model and what the Supabase
#    pgvector column is sized for. Changing this without changing the
#    DB schema would silently corrupt similarity search.
# 3. ``BATCH_SIZE = 100`` — text-embedding-3-small accepts up to a few
#    thousand inputs per call, but 100 is a sweet spot: small enough
#    that one bad text doesn't poison a huge batch, big enough to keep
#    HTTP overhead negligible (~10 calls per 1000 chunks).
# 4. ``DELAY_BETWEEN_BATCHES = 0.1`` — gentle pause keeps us under
#    OpenRouter's per-second limits during a large 5,000-chunk ingest.
#    Aggregate cost is 5 seconds extra per 1000 chunks; a price worth
#    paying to avoid 429s mid-run.
# 5. ``MAX_RETRIES = 3`` and ``RETRY_WAIT = 2.0`` — three attempts is
#    enough to ride out a transient blip without delaying ingestion
#    forever. Two seconds matches typical 429-cooldowns.
#
# WHAT BREAKS IF THIS IS WRONG:
# Wrong dimensions → vectors don't fit the Supabase column and inserts
# 500. Wrong model name → OpenRouter returns 400 and ingestion stops.
# Batch too big → one weird character chunk fails and 500 chunks fail
# with it. Batch too small → ingestion of a 10k-chunk corpus takes
# hours instead of minutes.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
BATCH_SIZE = 100
DELAY_BETWEEN_BATCHES = 0.1
MAX_RETRIES = 3
RETRY_WAIT = 2.0


# WHY THIS EXISTS IN PRISM AI:
# The first time a developer pulls the repo and forgets to populate
# backend/.env, every call would 401 mid-ingest with a confusing
# OpenRouter error. We'd rather fail at import — before any work
# happens — with a message that says exactly what's missing.
#
# WHAT THIS BLOCK DOES:
# Validate that both credentials are present and non-empty.
#
# WHY THIS WAY:
# Module-level checks fire on the very first ``import ingestion.embedder``
# and crash uvicorn at startup with a clear ValueError. That's far
# better UX than a 5-minute ingest that fails on chunk 1.
#
# WHAT BREAKS IF THIS IS WRONG:
# No validation → developer wastes time chasing 401s deep in HTTP
# tracebacks. Wrong-typed validation (e.g. a generic ImportError)
# would mask the actual cause.
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY environment variable is not set. "
        "Add it to backend/.env before importing ingestion.embedder."
    )
if not OPENAI_BASE_URL:
    raise ValueError(
        "OPENAI_BASE_URL environment variable is not set. "
        "Add it to backend/.env before importing ingestion.embedder."
    )


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Embed a list of text strings into a list of 1536-dimension vectors.

    One-sentence summary: cleans empty inputs, batches to 100, calls the
    embedding API with retries, and returns vectors in the exact same order
    as the input list.

    Why it exists for PrismAI:
        Ingestion produces hundreds-to-thousands of Chunk objects per
        document; each must become a vector before Supabase can store it.
        This function is the single, narrow place that conversion happens.
        At query time the same function (via :func:`get_single_embedding`)
        also embeds the PM's question — using the same model on both sides
        is what makes similarity search work.

    Decisions made inside (every choice spelled out):
        1. Empty-list short circuit — pipeline.py occasionally hands us
           an empty list (a doc with no extractable text). Returning ``[]``
           immediately avoids a wasted HTTP round-trip.
        2. "empty document" sentinel for blank inputs — the OpenRouter
           embedding endpoint 400s on empty strings. Replacing them with
           a placeholder keeps the batch alive and preserves index order
           so the result list still aligns 1-to-1 with the input.
        3. Batch size 100 — see module-level constant comment. Small
           enough to localise failures, big enough to keep HTTP overhead
           negligible for a 5,000-chunk ingest.
        4. Retry up to 3 times per batch with a 2-second wait — typical
           transient 429/503 cooldowns clear in under 5 seconds. After
           3 attempts we re-raise so the caller knows ingestion failed
           and can resume from the last successful batch.
        5. 0.1s sleep between batches — keeps us politely below
           OpenRouter's burst limits on long ingestions.
        6. Sort responses by ``index`` inside ``_embed_batch`` —
           OpenRouter does not guarantee response order matches input
           order. If we skipped this, the vector for chunk 5 might be
           saved as chunk 7 and retrieval would return wrong content.
        7. Logging at INFO level for batch progress — observability for
           any 30-minute ingest run; debug-level would hide it.

    Returns:
        ``List[List[float]]`` of length ``len(texts)``, each inner list
        having exactly :data:`EMBEDDING_DIMENSIONS` floats. pipeline.py
        zips this back with the original ``Chunk`` objects and writes
        ``(chunk_id, embedding, content, metadata)`` rows to Supabase.

    What breaks if this is wrong:
        * Wrong order → Supabase rows get mismatched embeddings;
          retrieval returns sprint-3 retro text under a Q2-OKR query.
        * Empty inputs not cleaned → OpenRouter 400s, the whole batch
          dies, ingest crashes mid-document.
        * No retries → a transient blip (rare 429) terminates a
          long-running ingest and the PM has to re-upload everything.
        * Wrong dimensions in response → Supabase pgvector insert
          fails and the chunk silently does not exist for retrieval.

    Raises:
        RuntimeError: If a batch still fails after ``MAX_RETRIES`` attempts.
            Caller (pipeline.py) is expected to catch this and surface a
            clear message in the FastAPI response.
    """

    # WHY THIS EXISTS IN PRISM AI:
    # An empty input list happens for documents that yielded zero
    # chunks (image-only PDF, parser failure). We must NOT call the
    # API with an empty list — OpenRouter rejects it.
    #
    # WHAT THIS BLOCK DOES:
    # Return ``[]`` immediately on empty input.
    #
    # WHY THIS WAY:
    # Cheap guard, no surprises.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Falling through to the loop would call the API with no batches
    # (harmless) but would still log "Done — 0 embeddings generated"
    # spam. The early return keeps logs clean.
    if not texts:
        return []

    # WHY THIS EXISTS IN PRISM AI:
    # Empty or whitespace-only chunk text is rare but real — a Word
    # paragraph that contained only formatting marks, or a slide whose
    # only shape was a chart. We replace those with a sentinel so the
    # batch survives. The placeholder embedding is meaningless for
    # retrieval but at least keeps the index alignment intact between
    # input texts and output vectors.
    #
    # WHAT THIS BLOCK DOES:
    # Build a cleaned list of texts — original text where non-empty,
    # "empty document" sentinel where empty/whitespace.
    #
    # WHY THIS WAY:
    # ``t.strip()`` is the cheapest "is there real content here?" check.
    # We do NOT mutate the caller's list — list comprehension creates
    # a new list so the caller still sees their originals.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Mutating the caller's list → callers that re-use ``texts``
    # downstream see surprise placeholder values. Skipping empties
    # entirely → output length no longer matches input length and
    # the pipeline's zip-with-chunks goes off by one.
    cleaned = [
        t if (t and t.strip()) else "empty document"
        for t in texts
    ]

    # WHY THIS EXISTS IN PRISM AI:
    # Embedding 5,000 chunks in one HTTP call is too big (request
    # body and provider limits both balk). Splitting into batches of
    # 100 keeps each call small, fast, and recoverable.
    #
    # WHAT THIS BLOCK DOES:
    # Pre-compute total batches for log messages, prepare an output
    # accumulator that will collect embeddings in input order.
    #
    # WHY THIS WAY:
    # ``(len + BATCH_SIZE - 1) // BATCH_SIZE`` is the standard
    # ceiling-divide pattern; cleaner than ``math.ceil(len/BATCH)``.
    # An accumulator list is preferred over yielding because callers
    # need a concrete list (Supabase insert expects a flat list).
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Off-by-one in total → log messages say "batch 4/3"; harmless
    # but confusing. Wrong accumulator type → caller blows up on
    # zip/index mismatches.
    total_batches = (len(cleaned) + BATCH_SIZE - 1) // BATCH_SIZE
    all_embeddings: List[List[float]] = []

    # WHY THIS EXISTS IN PRISM AI:
    # We slide a window across ``cleaned`` of size BATCH_SIZE. Each
    # iteration is one API call. Sequential (not concurrent) because
    # OpenRouter's per-key concurrency limits make parallelism risky
    # for marginal speedup; sequential is also easier to reason about
    # for retries.
    #
    # WHAT THIS BLOCK DOES:
    # Iterate batches of cleaned texts.
    #
    # WHY THIS WAY:
    # ``range(0, len, BATCH_SIZE)`` over the list with slicing is the
    # clearest pythonic way; ``itertools.batched`` exists in 3.12+ but
    # we stay backward compatible.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Wrong stride → batches overlap (duplicate embeddings in output)
    # or skip texts (missing embeddings).
    for batch_idx, start in enumerate(range(0, len(cleaned), BATCH_SIZE)):
        batch = cleaned[start : start + BATCH_SIZE]
        batch_num = batch_idx + 1

        # WHY THIS EXISTS IN PRISM AI:
        # Visible progress is critical during a 30-minute ingest.
        # Without per-batch logs, an operator has no idea whether the
        # process is healthy or hung.
        #
        # WHAT THIS BLOCK DOES:
        # Emit an INFO log line with current batch progress.
        #
        # WHY THIS WAY:
        # Logging at INFO so the default uvicorn config shows it; DEBUG
        # would hide progress in production.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Silent ingestion → "is it stuck?" Slack pings during every run.
        logger.info(
            "Embedding batch %d/%d (%d texts)...",
            batch_num,
            total_batches,
            len(batch),
        )

        # WHY THIS EXISTS IN PRISM AI:
        # OpenRouter is reliable, but transient 429s and 503s do
        # happen during peak hours. We retry up to MAX_RETRIES times
        # before giving up — three attempts is enough to ride out a
        # blip without making the user wait forever on a hard failure.
        #
        # WHAT THIS BLOCK DOES:
        # Try ``_embed_batch`` up to MAX_RETRIES times. On each
        # failure, log a warning, sleep RETRY_WAIT seconds, and try
        # again. After the last failure, raise a clear RuntimeError
        # naming the batch.
        #
        # WHY THIS WAY:
        # Capturing ``last_error`` lets us mention the original cause
        # in the final RuntimeError so the operator doesn't have to
        # dig through logs to find it. We chain via ``from`` so the
        # original traceback is preserved.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # No retries → one bad second kills a 30-minute ingest. Too
        # many retries (or no cap) → a permanent 401 (bad key) loops
        # forever instead of failing fast.
        last_error: Exception | None = None
        batch_embeddings: List[List[float]] | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                batch_embeddings = _embed_batch(batch)
                break
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Batch %d/%d attempt %d/%d failed: %s",
                    batch_num,
                    total_batches,
                    attempt,
                    MAX_RETRIES,
                    exc,
                )
                # WHY THIS EXISTS IN PRISM AI:
                # Sleeping only between attempts (not after the last
                # one) saves RETRY_WAIT seconds in the failure path.
                #
                # WHAT THIS BLOCK DOES:
                # Sleep before the next attempt, but skip the sleep
                # if this was the final attempt.
                #
                # WHY THIS WAY:
                # ``attempt < MAX_RETRIES`` is clearer than computing
                # whether we'll loop again from the loop bounds.
                #
                # WHAT BREAKS IF THIS IS WRONG:
                # Sleeping after the last attempt → an extra 2s of
                # latency before the user sees the failure message.
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_WAIT)

        # WHY THIS EXISTS IN PRISM AI:
        # If every attempt failed, ``batch_embeddings`` stays None.
        # We must NOT silently skip the batch — that would leave
        # hundreds of chunks unembedded and unsearchable.
        #
        # WHAT THIS BLOCK DOES:
        # If the batch never succeeded, raise a RuntimeError naming
        # the batch and chaining the underlying error.
        #
        # WHY THIS WAY:
        # ``raise RuntimeError(...) from last_error`` preserves the
        # original httpx exception in the chain so debugging the
        # network/API issue is still easy.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # Skipping → silent data loss. Raising a generic Exception
        # → loses the chained context.
        if batch_embeddings is None:
            raise RuntimeError(
                f"Failed to embed batch {batch_num}/{total_batches} "
                f"after {MAX_RETRIES} attempts: {last_error}"
            ) from last_error

        # WHY THIS EXISTS IN PRISM AI:
        # We accumulate the batch's vectors into the flat output list.
        # Order is preserved because we appended in batch order AND
        # _embed_batch sorted by index inside the batch.
        #
        # WHAT THIS BLOCK DOES:
        # Append the batch's embeddings to the running output.
        #
        # WHY THIS WAY:
        # ``extend`` is the clean idiom for appending an iterable.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # ``append`` instead of ``extend`` → output is a list-of-lists
        # nested one level too deep; downstream Supabase insert
        # crashes.
        all_embeddings.extend(batch_embeddings)

        # WHY THIS EXISTS IN PRISM AI:
        # Politeness sleep. Skipped after the final batch because
        # there's no next call to be polite to.
        #
        # WHAT THIS BLOCK DOES:
        # Wait DELAY_BETWEEN_BATCHES seconds before the next batch
        # unless this was the last one.
        #
        # WHY THIS WAY:
        # The check ``batch_num < total_batches`` is explicit and
        # avoids an unnecessary sleep at the end of long ingests.
        #
        # WHAT BREAKS IF THIS IS WRONG:
        # No throttle → bursty traffic risks 429s. Always sleeping
        # → 0.1s wasted at the end of every ingest, harmless but
        # untidy.
        if batch_num < total_batches:
            time.sleep(DELAY_BETWEEN_BATCHES)

    # WHY THIS EXISTS IN PRISM AI:
    # Final summary log so the operator can confirm everything
    # finished and matches the input count.
    #
    # WHAT THIS BLOCK DOES:
    # Log the total number of embeddings produced.
    #
    # WHY THIS WAY:
    # INFO level + matches the format spec the rest of the file uses.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Missing log → operator can't verify completion at a glance.
    logger.info("Done — %d embeddings generated", len(all_embeddings))

    return all_embeddings


def get_single_embedding(text: str) -> List[float]:
    """Embed a single string and return its 1536-dimension vector.

    One-sentence summary: convenience wrapper around :func:`get_embeddings`
    for the common single-text path used at PM query time.

    Why it exists for PrismAI:
        When a PM types "what blocked sprint 3?" we have to embed that
        question with the SAME model used for ingestion before searching
        Supabase. Wrapping the batch path in a single-text helper keeps
        the query path readable: ``vec = get_single_embedding(query)``.

    Decisions made inside:
        1. Empty/whitespace input → "empty document" sentinel — same
           reasoning as in ``get_embeddings``: never send empty text to
           the embedding API.
        2. Delegate to ``get_embeddings`` so all retry, batching, and
           ordering logic stays in one place. No duplication.
        3. Defensive empty-list check on the result — ``get_embeddings``
           returns ``[]`` for empty input, but this single-text wrapper
           always passes one item, so this guard mainly protects against
           a future regression in the underlying function.

    Returns:
        ``List[float]`` of length :data:`EMBEDDING_DIMENSIONS`. Empty
        list only if something has gone unexpectedly wrong upstream —
        callers should treat empty as "embedding failed".

    What breaks if this is wrong:
        * Different model in this path vs ingestion → query vectors
          live in a different latent space than stored chunks; cosine
          similarity returns gibberish and the PM gets random hits.
        * Skipping the empty-string clean → empty queries crash the
          chat endpoint instead of returning "no results".
    """

    # WHY THIS EXISTS IN PRISM AI:
    # PMs occasionally hit Send on an empty input box. We replace
    # empty with the same "empty document" sentinel get_embeddings
    # uses so behaviour is consistent across paths.
    #
    # WHAT THIS BLOCK DOES:
    # Substitute "empty document" if the input has no real text.
    #
    # WHY THIS WAY:
    # Single ternary expression for clarity; mirrors the
    # comprehension inside get_embeddings.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Empty input → API 400 → 500 to the chat endpoint instead of a
    # graceful empty-results UI.
    safe_text = text if (text and text.strip()) else "empty document"

    # WHY THIS EXISTS IN PRISM AI:
    # Reuse the batch path so retries, logging, and ordering stay
    # consistent. We pass a one-element list and pull the first
    # vector out.
    #
    # WHAT THIS BLOCK DOES:
    # Call get_embeddings with [safe_text] and return the first
    # result; defensively return [] if somehow nothing came back.
    #
    # WHY THIS WAY:
    # Single source of truth for HTTP/retry logic. The defensive
    # empty check guards against a future bug in get_embeddings
    # rather than any current behaviour.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Direct API call here would duplicate retry logic and drift
    # over time. Skipping the [] check would IndexError if the
    # function ever returned empty unexpectedly.
    result = get_embeddings([safe_text])
    if not result:
        return []
    return result[0]


def _embed_batch(texts: List[str]) -> List[List[float]]:
    """Make a single embedding API call for one batch of texts.

    One-sentence summary: posts the batch to OpenRouter's ``/embeddings``
    endpoint and returns the resulting vectors in input order.

    Why it exists for PrismAI:
        Isolating the raw HTTP call lets ``get_embeddings`` focus on
        batching/retry while this function focuses on talking to the
        provider. If we ever swap providers (Cohere, local TEI server),
        only this function changes.

    Decisions made inside (every choice spelled out):
        1. URL is built from ``OPENAI_BASE_URL`` + ``/embeddings`` — same
           pattern OpenAI clients use. We never hardcode the host so
           swapping providers requires only a .env change.
        2. ``Authorization: Bearer ...`` — standard OpenAI-style auth
           that OpenRouter accepts.
        3. ``HTTP-Referer`` and ``X-Title`` headers — OpenRouter uses
           these for attribution and analytics on their dashboard.
           Setting them tells the provider this traffic is PrismAI.
        4. JSON body has ``model``, ``input``, and ``dimensions`` —
           the dimensions field forces a 1536-dim output (matches our
           Supabase column) even though text-embedding-3-small would
           default there anyway. Being explicit means a future model
           switch won't silently drift dimension count.
        5. ``timeout=60.0`` — generous enough for a 100-text batch
           even when the provider is slow, tight enough that a hung
           connection doesn't stall the whole ingest forever.
        6. ``response.raise_for_status()`` — turns any 4xx/5xx into
           an httpx exception that the outer retry loop catches.
        7. **Sort response data by ``index``** — the OpenAI/OpenRouter
           contract does not guarantee response order matches input
           order. Skipping the sort would silently misalign vectors
           with the wrong source text, corrupting retrieval.

    Returns:
        ``List[List[float]]`` with one inner list per input text, in
        input order. Each inner list has :data:`EMBEDDING_DIMENSIONS`
        floats.

    What breaks if this is wrong:
        * No sort by ``index`` → chunk vectors land under the wrong
          source text; a PM searching for sprint 3 retro might match
          a Q2 OKR chunk semantically because the vectors are mixed up.
        * Wrong base URL or model name → 404/400 from the provider;
          retry loop exhausts and ingestion stops.
        * Headers missing → the call still works on most providers
          but OpenRouter analytics lose attribution.

    Raises:
        httpx.HTTPStatusError: For any non-2xx response (caught and
            retried by ``get_embeddings``).
        httpx.RequestError: Network-level failures (connection refused,
            timeout) — also caught upstream.
    """

    # WHY THIS EXISTS IN PRISM AI:
    # The endpoint is just the base URL + "/embeddings". We compute it
    # fresh here so any future change to OPENAI_BASE_URL is picked up
    # without a code change.
    #
    # WHAT THIS BLOCK DOES:
    # Build the request URL.
    #
    # WHY THIS WAY:
    # ``rstrip("/")`` defensively trims a trailing slash from the env
    # var so we never construct ``//embeddings``.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Trailing slash bug → 404 from provider; whole ingest fails.
    url = f"{OPENAI_BASE_URL.rstrip('/')}/embeddings"

    # WHY THIS EXISTS IN PRISM AI:
    # Headers tell the provider WHO is calling AND WHO they are. Auth
    # is non-negotiable; HTTP-Referer / X-Title give OpenRouter the
    # attribution data their dashboard needs.
    #
    # WHAT THIS BLOCK DOES:
    # Build the request headers dict.
    #
    # WHY THIS WAY:
    # Plain dict literal; httpx serialises it to wire format.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Missing/wrong Authorization → 401. Wrong Content-Type → some
    # gateways reject the body. Missing referer/title → still works
    # but hurts our OpenRouter analytics and rate-limit tier.
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/ShristiiS/PrismAI",
        "X-Title": "PrismAI",
    }

    # WHY THIS EXISTS IN PRISM AI:
    # The body tells the provider what model to use, what to embed,
    # and what dimension count we want.
    #
    # WHAT THIS BLOCK DOES:
    # Build the JSON body for the request.
    #
    # WHY THIS WAY:
    # ``dimensions=1536`` is explicit so a future switch to a model
    # with a different default cannot silently corrupt our DB schema.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # Wrong ``model`` → 400. Missing ``input`` → 400. Wrong
    # ``dimensions`` → vectors don't match Supabase column shape and
    # inserts fail.
    payload = {
        "model": EMBEDDING_MODEL,
        "input": texts,
        "dimensions": EMBEDDING_DIMENSIONS,
    }

    # WHY THIS EXISTS IN PRISM AI:
    # The actual HTTP call. ``httpx.post`` is preferred over
    # ``requests`` because it has a clean timeout API and is the
    # async-friendly modern choice (same library can be used in
    # both sync and async paths).
    #
    # WHAT THIS BLOCK DOES:
    # POST the payload to the embeddings endpoint with a 60-second
    # timeout; raise on any non-2xx status.
    #
    # WHY THIS WAY:
    # 60 seconds is generous enough for a slow batch but short
    # enough that a stuck connection doesn't hang ingestion. The
    # ``raise_for_status()`` immediately turns errors into exceptions
    # so the outer retry loop sees them.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # No timeout → a single hung connection stops ingestion forever.
    # No raise_for_status → 4xx responses look like "success" with
    # an error JSON body, the JSON parse below crashes on
    # ``data["data"]`` lookup.
    response = httpx.post(url, headers=headers, json=payload, timeout=60.0)
    response.raise_for_status()

    # WHY THIS EXISTS IN PRISM AI:
    # OpenAI's contract — and OpenRouter's compatible relay — does
    # not promise the response ``data`` array is in the same order as
    # the input. We MUST sort by the per-element ``index`` field
    # before extracting embeddings, or vectors will land under the
    # wrong source text.
    #
    # WHAT THIS BLOCK DOES:
    # Parse the JSON, pull ``data``, sort it by ``index``, then
    # build a flat list of just the ``embedding`` values.
    #
    # WHY THIS WAY:
    # ``sorted(..., key=lambda d: d["index"])`` is explicit and easy
    # to read. ``response.json()`` is the standard httpx accessor.
    #
    # WHAT BREAKS IF THIS IS WRONG:
    # No sort → silent vector/text misalignment. Retrieval would
    # answer "what blocked sprint 3?" with a Q2 OKR chunk because
    # the embedding for chunk index 4 is sitting under chunk 7.
    data = response.json()
    items = sorted(data["data"], key=lambda d: d["index"])
    return [item["embedding"] for item in items]
