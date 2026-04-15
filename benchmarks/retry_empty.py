#!/usr/bin/env python3
"""Retry empty/failed responses in existing benchmark results."""

import asyncio
import json
import re
import os
import sys
from pathlib import Path
import aiohttp
from tqdm.asyncio import tqdm_asyncio

BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.gpt.mws.ru/v1/chat/completions")
API_KEY = os.environ.get("LLM_API_KEY", "sk-ewgiaPC3A6pPDYHwR8siVA")
CONCURRENT_REQUESTS = 10
TIMEOUT = 300


async def call_api(session: aiohttp.ClientSession, model: str, messages: list) -> str | None:
    """Call chat completions API."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0
    }

    try:
        async with session.post(BASE_URL, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as resp:
            if resp.status == 200:
                data = await resp.json()
                msg = data["choices"][0]["message"]
                content = msg.get("content") or msg.get("reasoning_content")
                return content
            else:
                text = await resp.text()
                print(f"API Error {resp.status}: {text[:200]}", file=sys.stderr)
                return None
    except asyncio.TimeoutError:
        print(f"Timeout after {TIMEOUT}s for {model}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Exception: {type(e).__name__}: {e}", file=sys.stderr)
        return None


def parse_mc_answer(response: str) -> str | None:
    """Parse multiple choice answer (A/B/C/D) from response."""
    if not response:
        return None

    response_clean = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)
    response_clean = response_clean.strip()

    if not response_clean:
        response_clean = response

    match = re.search(r"(?:answer|ответ|выбор)[:\s]*\(?([A-Da-d])\)?", response_clean, re.IGNORECASE)
    if match:
        return match.group(1).upper()

    last_letter = None
    for char in reversed(response_clean):
        if char.upper() in "ABCD":
            last_letter = char.upper()
            break

    if last_letter:
        return last_letter

    match = re.search(r"(?:answer|ответ)[:\s]*\(?([A-Da-d])\)?", response, re.IGNORECASE)
    if match:
        return match.group(1).upper()

    if response and response[0] in "ABCD":
        return response[0]

    return None


def format_mmlu_question(q: dict) -> str:
    """Format MMLU question."""
    choices = q.get("choices", [])
    if not choices and "A" in q:
        choices = [q.get("A", ""), q.get("B", ""), q.get("C", ""), q.get("D", "")]

    choices_text = "\n".join([f"{chr(ord('A') + i)}. {c}" for i, c in enumerate(choices)])

    return f"""Answer the following multiple choice question. Reply with only the letter (A, B, C, or D).

Question: {q.get("question", "")}

{choices_text}

Answer:"""


def format_mmlu_ru_question(q: dict) -> str:
    """Format Russian MMLU question."""
    choices = q.get("choices", [])
    if not choices and "A" in q:
        choices = [q.get("A", ""), q.get("B", ""), q.get("C", ""), q.get("D", "")]

    choices_text = "\n".join([f"{chr(ord('A') + i)}. {c}" for i, c in enumerate(choices)])

    return f"""Ответь на вопрос с несколькими вариантами ответа. Напиши только букву (A, B, C или D).

Вопрос: {q.get("question", "")}

{choices_text}

Ответ:"""


def format_hellaswag_question(q: dict) -> str:
    """Format HellaSwag question."""
    context = q.get("context", "")
    endings = q.get("endings", [])
    choices_text = "\n".join([f"{chr(ord('A') + i)}. {e}" for i, e in enumerate(endings)])

    return f"""Complete the sentence with the most logical continuation. Reply with only the letter (A, B, C, or D).

Context: {context}

{choices_text}

Answer:"""


async def retry_hellaswag(model: str, samples_path: Path, questions_path: Path):
    """Retry empty responses for HellaSwag benchmark."""

    with open(samples_path) as f:
        samples = json.load(f)

    with open(questions_path) as f:
        questions = json.load(f)

    # Find indices with empty responses
    empty_indices = []
    for i, s in enumerate(samples):
        raw = s.get("raw_response") or ""
        if not raw:
            empty_indices.append(i)

    print(f"Found {len(empty_indices)} empty responses out of {len(samples)}")

    if not empty_indices:
        print("Nothing to retry!")
        return

    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async def retry_question(idx: int):
        async with semaphore:
            q = questions[idx]
            prompt = format_hellaswag_question(q)
            messages = [{"role": "user", "content": prompt}]

            async with aiohttp.ClientSession() as session:
                response = await call_api(session, model, messages)

            parsed = parse_mc_answer(response)
            correct_idx = q.get("answer", 0)
            correct = chr(ord("A") + correct_idx)
            is_correct = parsed == correct if parsed else False

            return idx, {
                "question": q.get("context", "")[:100],
                "correct_answer": correct,
                "model_answer": parsed,
                "is_correct": is_correct,
                "raw_response": response
            }

    async with aiohttp.ClientSession() as session:
        tasks = [retry_question(idx) for idx in empty_indices]
        results = await tqdm_asyncio.gather(*tasks, desc="Retrying hellaswag")

    # Update samples
    updated = 0
    still_empty = 0
    for idx, new_sample in results:
        if new_sample["raw_response"]:
            samples[idx] = new_sample
            updated += 1
        else:
            still_empty += 1

    correct = sum(1 for s in samples if s.get("is_correct"))
    total = len(samples)

    print(f"\nRetry complete:")
    print(f"  Updated: {updated}")
    print(f"  Still empty: {still_empty}")
    print(f"  New accuracy: {correct}/{total} = {correct/total*100:.2f}%")

    with open(samples_path, "w") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)

    print(f"Saved to {samples_path}")


async def retry_mmlu(model: str, benchmark: str, samples_path: Path, questions_path: Path):
    """Retry empty responses for MMLU benchmark."""

    # Load existing samples
    with open(samples_path) as f:
        samples = json.load(f)

    # Load questions
    with open(questions_path) as f:
        questions = json.load(f)

    # Find indices with empty responses
    empty_indices = []
    for i, s in enumerate(samples):
        raw = s.get("raw_response") or ""
        if not raw:
            empty_indices.append(i)

    print(f"Found {len(empty_indices)} empty responses out of {len(samples)}")

    if not empty_indices:
        print("Nothing to retry!")
        return

    # Format function
    if "ru" in benchmark.lower():
        format_fn = format_mmlu_ru_question
    else:
        format_fn = format_mmlu_question

    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async def retry_question(idx: int):
        async with semaphore:
            q = questions[idx]
            prompt = format_fn(q)
            messages = [{"role": "user", "content": prompt}]

            async with aiohttp.ClientSession() as session:
                response = await call_api(session, model, messages)

            parsed = parse_mc_answer(response)

            if "answer_index" in q:
                correct_idx = q["answer_index"]
                correct = chr(ord("A") + correct_idx)
            elif "answer" in q and isinstance(q["answer"], str):
                correct = q["answer"].upper()
            elif "answer" in q and isinstance(q["answer"], int):
                correct = chr(ord("A") + q["answer"])
            else:
                correct = None

            is_correct = parsed == correct if parsed and correct else False

            return idx, {
                "question": q.get("question", q.get("context", ""))[:100],
                "correct_answer": correct,
                "model_answer": parsed,
                "is_correct": is_correct,
                "raw_response": response
            }

    # Run retries
    async with aiohttp.ClientSession() as session:
        tasks = [retry_question(idx) for idx in empty_indices]
        results = await tqdm_asyncio.gather(*tasks, desc=f"Retrying {benchmark}")

    # Update samples
    updated = 0
    still_empty = 0
    for idx, new_sample in results:
        if new_sample["raw_response"]:
            samples[idx] = new_sample
            updated += 1
        else:
            still_empty += 1

    # Recalculate stats
    correct = sum(1 for s in samples if s.get("is_correct"))
    total = len(samples)

    print(f"\nRetry complete:")
    print(f"  Updated: {updated}")
    print(f"  Still empty: {still_empty}")
    print(f"  New accuracy: {correct}/{total} = {correct/total*100:.2f}%")

    # Save updated samples
    with open(samples_path, "w") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)

    print(f"Saved to {samples_path}")


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Retry empty benchmark responses")
    parser.add_argument("--model", required=True, help="Model name")
    parser.add_argument("--benchmark", required=True, choices=["mmlu", "global_mmlu_full_ru", "hellaswag"], help="Benchmark name")
    args = parser.parse_args()

    results_dir = Path("local_results") / args.model
    samples_path = results_dir / f"{args.benchmark}_samples.json"

    questions_path = Path("parsed_data") / args.benchmark / "questions.json"

    if not samples_path.exists():
        print(f"Samples not found: {samples_path}")
        sys.exit(1)

    if not questions_path.exists():
        print(f"Questions not found: {questions_path}")
        sys.exit(1)

    if args.benchmark == "hellaswag":
        await retry_hellaswag(args.model, samples_path, questions_path)
    else:
        await retry_mmlu(args.model, args.benchmark, samples_path, questions_path)


if __name__ == "__main__":
    asyncio.run(main())
