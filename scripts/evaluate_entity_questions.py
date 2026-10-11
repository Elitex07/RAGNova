"""
Does a lexical admit, a who/what-is prompt rule, or both, fix name lookups without breaking anything else?

Written 2026-10-11, after "who is alex morgan?" was refused on the live page although the corpus holds Alex Morgan's
ID card. Two causes were found: the image gate dropped the card (CLIP 0.151 against a 0.2 floor, MiniLM agreement 0.16
against 0.30), and with the card in scope the shipped prompt still made the 3B model refuse "who is X" (3 of 5 such
questions) while answering "what is X's roll number". Both fixes exist and are OFF by default:
src/pipelines/rag/lexical.py (LEXICAL_ADMIT) and the prompt rule (PROMPT_WHO_WHAT_RULE). Whether either is ever
switched on is decided here, by a rule written before anything was run.

DECLARED BEFORE RUNNING (committed before the first run)

  Rows. The 23 entity rows of data/gold_set.json (section "entity": 13 positives, 10 negatives), committed
  before any retrieval or model was run on them (E4 is the question that failed; it was written after seeing the
  failure, the rest were not). Each is asked through answer_query(include_images=True), as the page asks it.

  A positive is CORRECT when its answer is not a refusal, contains at least one of its answer_keywords
  (case-insensitive), AND at least one of its expected sources is among the numbered citations.
  A negative is CORRECT when its answer is a refusal.   SCORE = correct positives + correct negatives (max 23).

  Variants: retrieval in {off, L2 = lexical distinctive max_df 2, L4 = lexical distinctive max_df 4,
  LA = lexical all-known-words max_df 2} times prompt in {P0 = shipped, P1 = with the who/what-is rule}: eight.
  V0 = (off, P0) is what ships today.

  STAGE 1 (this script, no flags). A variant is a CANDIDATE when SCORE >= V0's + 3 AND its correct negatives are
  at least V0's. The WINNER is the candidate with the highest SCORE; ties go to the variant with fewer components
  (V0, then one of the two, then both), then L2 before LA before L4. No candidate: nothing is adopted.

  STAGE 2 (--regression VARIANT). The earlier rows may only VETO, never recommend: text T1-T33 answered
  substantively (not refused, not a bare "[n]"), negatives N1-N20 refused, text-to-image I1-I28 answered while citing
  the expected image (the evaluate_answers.py definitions), for V0 and for the winner. The winner is VETOED when its
  total is 2 or more below V0's, or when it answers any earlier negative that V0 refused. A vetoed winner is
  recorded as "tested, not adopted", like table extraction and the OCR-text image channel (ADR-014).

  A candidate that is adopted still changes a shipped default, so it gets an ADR and the .env.example line is
  changed from "opt-in" to "default". The model is stochastic; a difference of one question is noise.

    $env:CHROMA_PERSIST_DIR = "<scratch copy of chroma_db without any personal file>"
    python scripts/evaluate_entity_questions.py                    # stage 1
    python scripts/evaluate_entity_questions.py --regression V4    # stage 2 for the winner stage 1 named
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.core.config import settings as BASE_SETTINGS
from src.core.gold import load_gold_set
from src.pipelines.rag import answer as answer_module
from src.pipelines.rag import retrieve as retrieve_module
from src.pipelines.rag.answer import NOT_ENOUGH_INFO, answer_query

_spec = importlib.util.spec_from_file_location("evaluate_answers", PROJECT_ROOT / "scripts" / "evaluate_answers.py")
evaluate_answers = importlib.util.module_from_spec(_spec)
sys.modules["evaluate_answers"] = evaluate_answers
_spec.loader.exec_module(evaluate_answers)

# name -> (LEXICAL_ADMIT, LEXICAL_MODE, LEXICAL_MAX_DF, PROMPT_WHO_WHAT_RULE)
RETRIEVAL = {"off": (False, "distinctive", 2), "L2": (True, "distinctive", 2), "L4": (True, "distinctive", 4), "LA": (True, "all", 2)}
VARIANTS = {}
for _i, (_r, _p) in enumerate([(r, p) for p in (False, True) for r in RETRIEVAL]):
    VARIANTS[f"V{_i}"] = (_r, _p)
# V0 = (off, P0)  V1 = (L2, P0)  V2 = (L4, P0)  V3 = (LA, P0)  V4 = (off, P1)  V5 = (L2, P1)  V6 = (L4, P1)  V7 = (LA, P1)

REQUIRED_GAIN = 3
REGRESSION_TOLERANCE = 2


def configure(variant: str) -> None:
    retrieval, rule = VARIANTS[variant]
    on, mode, max_df = RETRIEVAL[retrieval]
    new = dataclasses.replace(BASE_SETTINGS, LEXICAL_ADMIT=on, LEXICAL_MODE=mode, LEXICAL_MAX_DF=max_df, PROMPT_WHO_WHAT_RULE=rule)
    retrieve_module.settings = new
    answer_module.settings = new


def describe(variant: str) -> str:
    retrieval, rule = VARIANTS[variant]
    return f"{variant} (retrieval {retrieval}, prompt {'P1 who/what-is rule' if rule else 'P0 shipped'})"


def components(variant: str) -> int:
    retrieval, rule = VARIANTS[variant]
    return (retrieval != "off") + bool(rule)


def refused(result) -> bool:
    return evaluate_answers._refused(result)


def judge(row: dict, result) -> bool:
    if row["kind"] == "negative":
        return refused(result)
    cited = any(c.source in row["expected_sources"] for c in result.citations)
    said = any(k in result.answer.lower() for k in row["answer_keywords"])
    return not refused(result) and said and cited


def run_entity(variant: str, verbose: bool) -> dict:
    configure(variant)
    rows = load_gold_set()["entity"]
    out = {"variant": variant, "ok": {}, "retrieved": {}}
    for row in rows:
        result = answer_query(row["question"], include_images=True)
        out["ok"][row["id"]] = judge(row, result)
        if row["kind"] == "positive":
            out["retrieved"][row["id"]] = any(c.source in row["expected_sources"] for c in result.citations)
        if verbose:
            print(f"[{'ok ' if out['ok'][row['id']] else 'BAD'}] {row['id']:4} {row['kind']:8} {row['question']!r:46} -> {result.answer.strip()[:150]!r}"
                  f"  cites {[c.source.split('/')[-1] for c in result.citations][:3]}")
    out["pos"] = sum(out["ok"][r["id"]] for r in rows if r["kind"] == "positive")
    out["neg"] = sum(out["ok"][r["id"]] for r in rows if r["kind"] == "negative")
    out["score"] = out["pos"] + out["neg"]
    out["found"] = sum(out["retrieved"].values())
    return out


def stage1() -> int:
    gold = load_gold_set()["entity"]
    n_pos = sum(r["kind"] == "positive" for r in gold)
    n_neg = len(gold) - n_pos
    print(f"model {BASE_SETTINGS.OLLAMA_MODEL}, TOP_K {BASE_SETTINGS.TOP_K}; {n_pos} positives, {n_neg} negatives\n")
    results = {}
    for variant in VARIANTS:
        print(f"######## {describe(variant)}")
        results[variant] = run_entity(variant, verbose=True)
        r = results[variant]
        print(f"-> positives correct {r['pos']}/{n_pos} (expected source cited in {r['found']}/{n_pos}), negatives refused {r['neg']}/{n_neg}, SCORE {r['score']}/{len(gold)}\n")

    base = results["V0"]
    print("=" * 78)
    print(f"{'variant':44} {'pos':>5} {'neg':>5} {'score':>6}   vs V0")
    for variant, r in results.items():
        print(f"{describe(variant):44} {r['pos']:>2}/{n_pos} {r['neg']:>3}/{n_neg} {r['score']:>4}/{len(gold)}   {r['score'] - base['score']:+d}")
    candidates = [v for v, r in results.items() if v != "V0" and r["score"] >= base["score"] + REQUIRED_GAIN and r["neg"] >= base["neg"]]
    print(f"\ncandidates (SCORE >= V0 + {REQUIRED_GAIN} and negatives refused >= V0's {base['neg']}): {candidates or 'none'}")
    if not candidates:
        print("RESULT: no candidate. Nothing is adopted; both stay off.")
        return 0
    order = {"off": 0, "L2": 1, "LA": 2, "L4": 3}
    winner = sorted(candidates, key=lambda v: (-results[v]["score"], components(v), order[VARIANTS[v][0]]))[0]
    print(f"WINNER: {describe(winner)}. Run stage 2: python scripts/evaluate_entity_questions.py --regression {winner}")
    return 0


def regression_score(variant: str) -> dict:
    configure(variant)
    old_gold = evaluate_answers.GOLD_QUESTIONS
    positives = [q for q in old_gold if q["id"].startswith("T")]
    negatives = [q for q in old_gold if q["id"].startswith("N")]
    out = {"substantive": set(), "refused": set(), "images": set()}
    for q in positives:
        result = answer_query(q["question"])
        if not refused(result) and not evaluate_answers._bare(result):
            out["substantive"].add(q["id"])
    for q in negatives:
        if refused(answer_query(q["question"])):
            out["refused"].add(q["id"])
    for q in evaluate_answers.IMAGE_QUESTIONS:
        result = answer_query(q["question"], include_images=True)
        if not refused(result) and any(c.source in q["expected_images"] for c in result.citations):
            out["images"].add(q["id"])
    out["total"] = len(out["substantive"]) + len(out["refused"]) + len(out["images"])
    return out


def stage2(winner: str) -> int:
    print(f"model {BASE_SETTINGS.OLLAMA_MODEL}; older rows: T1-T33, N1-N20, I1-I28 (may only veto)\n")
    base, won = regression_score("V0"), regression_score(winner)
    for name, r in (("V0", base), (winner, won)):
        print(f"{name}: text substantive {len(r['substantive'])}, negatives refused {len(r['refused'])}, images answered and cited {len(r['images'])}, TOTAL {r['total']}")
    newly_answered = sorted(base["refused"] - won["refused"])
    lost = sorted((base["substantive"] - won["substantive"]) | (base["images"] - won["images"]))
    print(f"older negatives V0 refused that {winner} answers: {newly_answered or 'none'}")
    print(f"older positives V0 got that {winner} lost: {lost or 'none'}")
    vetoed = won["total"] <= base["total"] - REGRESSION_TOLERANCE or bool(newly_answered)
    print("RESULT:", f"VETOED. {winner} is tested, not adopted." if vetoed else f"not vetoed. {winner} may be adopted (ADR + .env.example default).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--regression", metavar="VARIANT", help="stage 2: run the older rows for V0 and this variant")
    args = parser.parse_args()
    if args.regression:
        if args.regression not in VARIANTS or args.regression == "V0":
            parser.error(f"VARIANT must be one of {[v for v in VARIANTS if v != 'V0']}")
        return stage2(args.regression)
    return stage1()


if __name__ == "__main__":
    sys.exit(main())
