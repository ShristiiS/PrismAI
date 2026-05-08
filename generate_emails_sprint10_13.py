from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

DATASET_DIR = Path(__file__).resolve().parent
load_dotenv(DATASET_DIR / ".env")

MODEL = os.getenv("NUTRIVANA_OPENAI_MODEL", "openai/gpt-4o-mini")

BLUEPRINT_PATH = DATASET_DIR / "Sprint_10-13_Gmail_Thread.md"
OUT_DIR = DATASET_DIR / "generated" / "emails"

THREAD_20_OUT = OUT_DIR / "thread_20_pregnant_women_data.txt"
THREAD_21_OUT = OUT_DIR / "thread_21_nps_results_34.txt"
THREAD_22_OUT = OUT_DIR / "thread_22_38_percent_dropoff.txt"
THREAD_23_OUT = OUT_DIR / "thread_23_icmr_vs_who.txt"
THREAD_24_OUT = OUT_DIR / "thread_24_ab_test_results.txt"
THREAD_25_OUT = OUT_DIR / "thread_25_bug014_prenatal_units.txt"
THREAD_26_OUT = OUT_DIR / "thread_26_q2_okr_review.txt"
THREAD_27_OUT = OUT_DIR / "thread_27_custom_food_847.txt"

SYSTEM_PROMPT = """ROLE: You are generating realistic workplace emails for Nutrivana team members who have worked together for 6 months and communicate directly and honestly.

CONTEXT: Team is Shristi (shristi@nutrivana.in), Arjun (arjun@nutrivana.in), Priya (priya@nutrivana.in), Kabir (kabir@nutrivana.in), Ananya (ananya@nutrivana.in). Investor is Ravi Kapoor (ravi.kapoor@seedfund.in). Internal emails are direct and first-name only. No pleasantries.

INSTRUCTION: Read each thread blueprint carefully and write complete realistic emails. Use the blueprint as the source of truth for what each email must contain. Do not summarise — write the full email content as a real person would write it.

PERFORMANCE:
- Internal emails are short and direct — no Dear, no Thanks, no pleasantries
- Each email adds new information not in the previous email
- Technical emails include specific details — numbers, column names, code
- Investor emails are professional but warm
- Every email ends naturally when the content ends"""


class GenerationError(RuntimeError):
    pass


def _client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
    if not key or key == "sk-or-v1-your-key-here":
        raise GenerationError(
            "OpenAI API key missing. Set OPENAI_API_KEY in nutrivana-dataset/.env (use python-dotenv)."
        )
    kwargs: dict[str, Any] = {"api_key": key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def _extract_thread_block(full_md: str, thread_number: int) -> str:
    start_tag = f"## THREAD {thread_number}"
    start = full_md.find(start_tag)
    if start == -1:
        raise GenerationError(f"Could not find {start_tag!r} in {BLUEPRINT_PATH.name}")
    end_tag = f"## THREAD {thread_number + 1}"
    end = full_md.find(end_tag, start)
    if end == -1:
        end = len(full_md)
    return full_md[start:end].strip()


_EMAIL_HEADER_RE = re.compile(
    r"(?m)^Date:\s+.+\nFrom:\s+.+\nTo:\s+.+\nSubject:\s+.+\n",
)


def _validate_thread_text(text: str) -> None:
    t = text.strip()
    if not t:
        raise ValueError("thread_text is empty")

    # Must contain at least 2 emails in a thread.
    headers = list(_EMAIL_HEADER_RE.finditer(t))
    if len(headers) < 2:
        raise ValueError(f"Expected at least 2 emails (Date/From/To/Subject blocks). Found {len(headers)}")

    # Basic field presence + ordering within each email is ensured by regex.
    # Ensure each email has some body text after Subject line.
    for i, m in enumerate(headers):
        body_start = m.end()
        body_end = headers[i + 1].start() if i + 1 < len(headers) else len(t)
        body = t[body_start:body_end].strip()
        if len(body) < 20:
            raise ValueError(f"Email {i+1} body too short / missing")


def _call_thread_text(client: OpenAI, *, blueprint_block: str, thread_label: str) -> str:
    user = (
        f"Generate the full plain-text Gmail thread for {thread_label}.\n\n"
        "Output format rules (must match exactly):\n"
        "For each email in the thread, include exactly these header lines then a blank line, then the body:\n"
        "Date: [date] [time]\n"
        "From: [email]\n"
        "To: [email]\n"
        "Subject: [subject]\n"
        "[email body]\n\n"
        "Do not add any extra labels, IDs, or markdown.\n\n"
        "Return JSON with exactly one key: thread_text.\n\n"
        "Blueprint (source of truth):\n-----\n"
        f"{blueprint_block}\n"
        "-----\n"
    )

    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]

    max_attempts = 5  # 1 initial + 4 retries
    last_err: Exception | None = None
    for attempt in range(max_attempts):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.35,
                # Avoid provider defaulting to a too-high max_tokens vs remaining credits.
                max_tokens=10000,
                response_format={"type": "json_object"},
            )
            text = (resp.choices[0].message.content or "").strip()
            data = json.loads(text)
            thread_text = str(data.get("thread_text", "")).strip()
            _validate_thread_text(thread_text)
            return thread_text
        except Exception as e:  # noqa: BLE001
            last_err = e
            if attempt == max_attempts - 1:
                break
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Your previous output failed validation. Return ONLY valid JSON.\n"
                        "Fix: ensure the output is a chain of emails, each with Date/From/To/Subject lines and a real body.\n"
                        f"Validation error: {e}"
                    ),
                }
            )
            time.sleep(min(2.0, 0.5 * (attempt + 1)))
    raise GenerationError(f"Failed after retries: {last_err}")


def _write_text_atomic(text: str, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(".tmp.txt")
    tmp.write_text(text.rstrip() + "\n", encoding="utf-8")
    try:
        os.replace(tmp, out_path)
        return out_path
    except PermissionError:
        fb = out_path.with_name(out_path.stem + "_ready.txt")
        shutil.move(str(tmp), str(fb))
        return fb


def generate_thread_20() -> Path:
    full_md = BLUEPRINT_PATH.read_text(encoding="utf-8")
    # In this blueprint, "THREAD 1" corresponds to output filename "thread_20_*".
    blueprint_block = _extract_thread_block(full_md, 1)

    print(f"Model: {MODEL}")
    print("Calling API for thread_20_pregnant_women_data...")
    client = _client()
    thread_text = _call_thread_text(client, blueprint_block=blueprint_block, thread_label="thread_20_pregnant_women_data")
    saved = _write_text_atomic(thread_text, THREAD_20_OUT)
    if saved != THREAD_20_OUT:
        print(
            f"Saved to {saved} (could not overwrite {THREAD_20_OUT} — file may be open in another program). "
            "Close it and rename/copy, or rerun."
        )
    else:
        print(f"Wrote {saved}")
    return saved


def generate_thread_21() -> Path:
    full_md = BLUEPRINT_PATH.read_text(encoding="utf-8")
    # In this blueprint, "THREAD 2" corresponds to output filename "thread_21_*".
    blueprint_block = _extract_thread_block(full_md, 2)

    print(f"Model: {MODEL}")
    print("Calling API for thread_21_nps_results_34...")
    client = _client()
    thread_text = _call_thread_text(
        client,
        blueprint_block=blueprint_block,
        thread_label="thread_21_nps_results_34",
    )
    saved = _write_text_atomic(thread_text, THREAD_21_OUT)
    if saved != THREAD_21_OUT:
        print(
            f"Saved to {saved} (could not overwrite {THREAD_21_OUT} — file may be open in another program). "
            "Close it and rename/copy, or rerun."
        )
    else:
        print(f"Wrote {saved}")
    return saved


def generate_thread_22() -> Path:
    full_md = BLUEPRINT_PATH.read_text(encoding="utf-8")
    # In this blueprint, "THREAD 3" corresponds to output filename "thread_22_*".
    blueprint_block = _extract_thread_block(full_md, 3)

    print(f"Model: {MODEL}")
    print("Calling API for thread_22_38_percent_dropoff...")
    client = _client()
    thread_text = _call_thread_text(
        client,
        blueprint_block=blueprint_block,
        thread_label="thread_22_38_percent_dropoff",
    )
    saved = _write_text_atomic(thread_text, THREAD_22_OUT)
    if saved != THREAD_22_OUT:
        print(
            f"Saved to {saved} (could not overwrite {THREAD_22_OUT} — file may be open in another program). "
            "Close it and rename/copy, or rerun."
        )
    else:
        print(f"Wrote {saved}")
    return saved


def generate_thread_23() -> Path:
    full_md = BLUEPRINT_PATH.read_text(encoding="utf-8")
    # In this blueprint, "THREAD 4" corresponds to output filename "thread_23_*".
    blueprint_block = _extract_thread_block(full_md, 4)

    print(f"Model: {MODEL}")
    print("Calling API for thread_23_icmr_vs_who...")
    client = _client()
    thread_text = _call_thread_text(
        client,
        blueprint_block=blueprint_block,
        thread_label="thread_23_icmr_vs_who",
    )
    saved = _write_text_atomic(thread_text, THREAD_23_OUT)
    if saved != THREAD_23_OUT:
        print(
            f"Saved to {saved} (could not overwrite {THREAD_23_OUT} — file may be open in another program). "
            "Close it and rename/copy, or rerun."
        )
    else:
        print(f"Wrote {saved}")
    return saved


def generate_thread_24() -> Path:
    full_md = BLUEPRINT_PATH.read_text(encoding="utf-8")
    # In this blueprint, "THREAD 5" corresponds to output filename "thread_24_*".
    blueprint_block = _extract_thread_block(full_md, 5)

    print(f"Model: {MODEL}")
    print("Calling API for thread_24_ab_test_results...")
    client = _client()
    thread_text = _call_thread_text(
        client,
        blueprint_block=blueprint_block,
        thread_label="thread_24_ab_test_results",
    )
    saved = _write_text_atomic(thread_text, THREAD_24_OUT)
    if saved != THREAD_24_OUT:
        print(
            f"Saved to {saved} (could not overwrite {THREAD_24_OUT} — file may be open in another program). "
            "Close it and rename/copy, or rerun."
        )
    else:
        print(f"Wrote {saved}")
    return saved


def generate_thread_25() -> Path:
    full_md = BLUEPRINT_PATH.read_text(encoding="utf-8")
    # In this blueprint, "THREAD 6" corresponds to output filename "thread_25_*".
    blueprint_block = _extract_thread_block(full_md, 6)

    print(f"Model: {MODEL}")
    print("Calling API for thread_25_bug014_prenatal_units...")
    client = _client()
    thread_text = _call_thread_text(
        client,
        blueprint_block=blueprint_block,
        thread_label="thread_25_bug014_prenatal_units",
    )
    saved = _write_text_atomic(thread_text, THREAD_25_OUT)
    if saved != THREAD_25_OUT:
        print(
            f"Saved to {saved} (could not overwrite {THREAD_25_OUT} — file may be open in another program). "
            "Close it and rename/copy, or rerun."
        )
    else:
        print(f"Wrote {saved}")
    return saved


def generate_thread_26() -> Path:
    full_md = BLUEPRINT_PATH.read_text(encoding="utf-8")
    # In this blueprint, "THREAD 7" corresponds to output filename "thread_26_*".
    blueprint_block = _extract_thread_block(full_md, 7)

    print(f"Model: {MODEL}")
    print("Calling API for thread_26_q2_okr_review...")
    client = _client()
    thread_text = _call_thread_text(
        client,
        blueprint_block=blueprint_block,
        thread_label="thread_26_q2_okr_review",
    )
    saved = _write_text_atomic(thread_text, THREAD_26_OUT)
    if saved != THREAD_26_OUT:
        print(
            f"Saved to {saved} (could not overwrite {THREAD_26_OUT} — file may be open in another program). "
            "Close it and rename/copy, or rerun."
        )
    else:
        print(f"Wrote {saved}")
    return saved


def generate_thread_27() -> Path:
    full_md = BLUEPRINT_PATH.read_text(encoding="utf-8")
    # In this blueprint, "THREAD 8" corresponds to output filename "thread_27_*".
    blueprint_block = _extract_thread_block(full_md, 8)

    print(f"Model: {MODEL}")
    print("Calling API for thread_27_custom_food_847...")
    client = _client()
    thread_text = _call_thread_text(
        client,
        blueprint_block=blueprint_block,
        thread_label="thread_27_custom_food_847",
    )
    saved = _write_text_atomic(thread_text, THREAD_27_OUT)
    if saved != THREAD_27_OUT:
        print(
            f"Saved to {saved} (could not overwrite {THREAD_27_OUT} — file may be open in another program). "
            "Close it and rename/copy, or rerun."
        )
    else:
        print(f"Wrote {saved}")
    return saved


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Sprint 10-13 email threads from blueprint.")
    parser.add_argument(
        "--thread20",
        action="store_true",
        help="Generate only thread_20_pregnant_women_data.txt (test run).",
    )
    parser.add_argument(
        "--thread21",
        action="store_true",
        help="Generate only thread_21_nps_results_34.txt.",
    )
    parser.add_argument(
        "--thread22",
        action="store_true",
        help="Generate only thread_22_38_percent_dropoff.txt.",
    )
    parser.add_argument(
        "--thread23",
        action="store_true",
        help="Generate only thread_23_icmr_vs_who.txt.",
    )
    parser.add_argument(
        "--thread24",
        action="store_true",
        help="Generate only thread_24_ab_test_results.txt.",
    )
    parser.add_argument(
        "--thread25",
        action="store_true",
        help="Generate only thread_25_bug014_prenatal_units.txt.",
    )
    parser.add_argument(
        "--thread26",
        action="store_true",
        help="Generate only thread_26_q2_okr_review.txt.",
    )
    parser.add_argument(
        "--thread27",
        action="store_true",
        help="Generate only thread_27_custom_food_847.txt.",
    )
    args = parser.parse_args()

    if args.thread20:
        generate_thread_20()
        return 0
    if args.thread21:
        generate_thread_21()
        return 0
    if args.thread22:
        generate_thread_22()
        return 0
    if args.thread23:
        generate_thread_23()
        return 0
    if args.thread24:
        generate_thread_24()
        return 0
    if args.thread25:
        generate_thread_25()
        return 0
    if args.thread26:
        generate_thread_26()
        return 0
    if args.thread27:
        generate_thread_27()
        return 0

    # Default to the requested test: thread 20 only.
    generate_thread_20()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except GenerationError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(1)

