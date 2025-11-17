import os
import csv
import io
import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime

import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from src.gpt import process_text, CHAT_SETTINGS
from src.main import (
    get_main_json_data,
    get_business_json_data,
    get_datetime_json_data,
)

from logging_config import logging

CURRENT_TIME_ISO = "2025-10-01T14:32:10Z"
CURRENT_TIME_DT = datetime.fromisoformat(
    CURRENT_TIME_ISO.replace("Z", "+00:00")
)


def _read_csv_text(csv_path: Path) -> Tuple[List[str], List[List[str]]]:
    """Read CSV file with encoding fallback."""
    raw_bytes = csv_path.read_bytes()
    try:
        decoded_text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            decoded_text = raw_bytes.decode("cp1251")
        except UnicodeDecodeError:
            decoded_text = raw_bytes.decode("utf-8", errors="replace")

    with io.StringIO(decoded_text) as buf:
        reader = csv.reader(buf)
        rows = list(reader)
    if not rows:
        return [], []
    header, data = rows[0], rows[1:]
    return header, data


def _idx(header: List[str], name: str) -> int:
    """Find column index by name (case-insensitive)."""
    lowered = [h.strip().lower() for h in header]
    return lowered.index(name.strip().lower())


def _safe_json_extract_description(text_response: str) -> str:
    """Safely extract description field from JSON response."""
    try:
        obj = json.loads(text_response)
        value = obj.get("description", "")
        return value if isinstance(value, str) else ""
    except Exception:
        return ""


def _safe_json_extract_amount(text_response: Union[str, dict]) -> str:
    """Safely extract amount field from JSON response."""
    try:
        if isinstance(text_response, dict):
            obj = text_response
        else:
            obj = json.loads(text_response)
        value = obj.get("amount", "")
        if value is None or value == "":
            return ""
        # Convert to string, handling both string and numeric values
        return str(value).strip()
    except Exception:
        return ""


def _safe_json_extract_currency(text_response: Union[str, dict]) -> str:
    """Safely extract currency field from JSON response."""
    try:
        if isinstance(text_response, dict):
            obj = text_response
        else:
            obj = json.loads(text_response)
        value = obj.get("currency", "")
        return value if isinstance(value, str) else ""
    except Exception:
        return ""


def _values_match(a: str, b: str) -> bool:
    """Check if two values match, including both empty."""
    a_clean = (a or "").strip()
    b_clean = (b or "").strip()

    # Both empty - match
    if not a_clean and not b_clean:
        return True

    # One empty, one not - no match
    if not a_clean or not b_clean:
        return False

    # Try numeric comparison for amounts
    try:
        a_num = float(a_clean)
        b_num = float(b_clean)
        return a_num == b_num
    except (ValueError, TypeError):
        # If not numeric, compare as strings
        return a_clean == b_clean


def _business_metrics(
    gt_name: str, matches: Optional[List[Dict[str, Any]]]
) -> Tuple[bool, int, Optional[float], Optional[int], List[str]]:
    """Calculate business matching metrics from ground truth and matches."""
    if not matches:
        # If GT is empty and we have no matches, consider it matched by definition
        is_empty_gt = (gt_name or "").strip() == ""
        return is_empty_gt, 0, None, None, []

    # Sort by score desc, stable
    sorted_matches = sorted(
        matches, key=lambda m: m.get("score") or 0.0, reverse=True
    )
    gt = (gt_name or "").strip().lower()
    found_index = None
    found_score = None
    for i, m in enumerate(sorted_matches):
        name = str(m.get("name", "")).strip().lower()
        if name == gt and found_index is None:
            found_index = i
            found_score = m.get("score")
            break

    is_matched = found_index is not None
    n_matches = len(sorted_matches)
    position = (found_index + 1) if found_index is not None else None
    names_list = [str(m.get("name", "")).strip() for m in sorted_matches]
    return (
        is_matched,
        n_matches,
        (float(found_score) if found_score is not None else None),
        position,
        names_list,
    )


def _datetimes_equal(a: Optional[str], b: Optional[str]) -> bool:
    """Check if two datetime strings are equal."""
    if not a or not b:
        return False
    try:
        da = datetime.fromisoformat(a.replace("Z", "+00:00"))
        db = datetime.fromisoformat(b.replace("Z", "+00:00"))
        return da == db
    except Exception:
        return False


async def _judge_description(
    api_key: str, gt_description: str, pred_description: str
) -> bool:
    """Use LLM to judge if two descriptions match in context."""
    system_prompt = (
        """
###Ти експерт з оцінки якості та відповідності описів транзакцій. Твоя роль - точно визначати чи відповідають два описи покупки одному й тому ж контексту.###

###Користувач надасть тобі два описи покупки українською мовою.
Твоє завдання - порівняти ground_truth та predicted описи та визначити чи збігається їх контекст.###

###Правила оцінки:###
- Вони не мають бути однаковими слово в слово, але повинні бути про одне й теж
- Навіть частковий збіг контексту вважається відповідністю
- Якщо вони про різний контекст - поверни false
- Визначай відповідність за змістом (подумай чи опис відповідає контексту)
- Ігноруй незначні варіації формулювань
- Числа важливі - якщо числа різні, це може вказувати на різний контекст

###Формат відповіді:###
Поверни ВИКЛЮЧНО JSON:
{"match": true|false}

###Повертай ВИКЛЮЧНО json файл у визначеному форматі і нічого більше (це важливо)!###
"""
    ).strip()
    user_prompt = json.dumps(
        {
            "ground_truth": gt_description or "",
            "predicted": pred_description or "",
        },
        ensure_ascii=False,
    )
    try:
        response = await process_text(
            api_key,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=CHAT_SETTINGS["judge_model"],
        )
        data = json.loads(response)
        return bool(data.get("match"))
    except Exception:
        return False


async def _get_best_business_match(
    api_key: str, input_text: str, business_list: List[Dict[str, Any]]
) -> str:
    """Get the best business match from a list using LLM."""
    if not business_list:
        return ""

    system_prompt = (
        """
###Ти експерт з визначення найкращого збігу назв бізнесів.
# Твоя роль - точно ідентифікувати найбільш відповідну назву бізнесу з наданого
# списку для вхідного тексту.###

###Користувач надасть тобі вхідний текст та список бізнесів.
Твоє завдання - визначити найкращий збіг бізнесу (часто вказується як "у" чи
"в" назва бізнесу) зі списку business_list для input_text.###

###Важливо:###
- Це вже відфільтрований список бізнесів - тут список найімовірніших збігів
- Аналізуй і звучання назв бізнесів теж
- Вхідний текст - жива мова, назва бізнесу може виглядати по-різному
- Порівнюй за змістом, звучанням та контекстом

###Формат відповіді:###
Поверни ВИКЛЮЧНО JSON:
{"best_match": "назва бізнесу"|""}

###Правила:###
- Якщо є найкращий збіг серед наданих варіантів - поверни його назву
- Якщо немає підходящого збігу - поверни порожній рядок ""

###Повертай ВИКЛЮЧНО json файл у визначеному форматі і нічого більше (це важливо)!###
"""
    ).strip()

    business_names = [str(m.get("name", "")).strip() for m in business_list]
    user_prompt = json.dumps(
        {
            "input_text": input_text,
            "business_list": business_names,
        },
        ensure_ascii=False,
    )

    try:
        response = await process_text(
            api_key,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=CHAT_SETTINGS["judge_model"],
        )
        data = json.loads(response)
        best_match = data.get("best_match", "")
        return best_match if isinstance(best_match, str) else ""
    except Exception:
        return ""


async def _eval_one_row(
    api_key: str,
    input_text: str,
    gt_business: str,
    gt_datetime: str,
    gt_description: str,
    gt_amount: str,
    gt_currency: str,
) -> Dict[str, Any]:
    """Evaluate a single row of test data against the model."""
    # Run primary model calls concurrently
    main_task = asyncio.create_task(get_main_json_data(api_key, input_text))
    dt_task = asyncio.create_task(
        get_datetime_json_data(
            api_key, input_text, current_time=CURRENT_TIME_DT
        )
    )
    biz_task = asyncio.create_task(get_business_json_data(api_key, input_text))

    main_resp, dt_resp, biz_resp = await asyncio.gather(
        main_task, dt_task, biz_task, return_exceptions=True
    )

    # Description extraction
    e_description = ""
    if isinstance(main_resp, Exception):
        e_description = ""
    else:
        e_description = _safe_json_extract_description(str(main_resp))

    # Amount extraction
    e_amount = ""
    if isinstance(main_resp, Exception):
        e_amount = ""
    else:
        e_amount = _safe_json_extract_amount(main_resp)

    # Currency extraction
    e_currency = ""
    if isinstance(main_resp, Exception):
        e_currency = ""
    else:
        e_currency = _safe_json_extract_currency(main_resp)

    # Datetime extraction
    e_datetime = None
    if isinstance(dt_resp, Exception):
        e_datetime = None
    else:
        try:
            e_datetime = dt_resp.get("datetime")
        except Exception:
            e_datetime = None

    # Fallback to current_time if datetime is None
    if e_datetime is None:
        e_datetime = CURRENT_TIME_ISO

    # Business matches
    matches_list: Optional[List[Dict[str, Any]]] = None
    if not isinstance(biz_resp, Exception):
        if isinstance(biz_resp, dict) and "businesses" in biz_resp:
            matches_list = biz_resp.get("businesses") or []
        else:
            matches_list = []

    e_b_is_matched, e_n_matches, e_score, e_n_position, e_b_names = (
        _business_metrics(gt_business, matches_list)
    )

    # Best business match
    e_best_b_match = ""
    if matches_list:
        e_best_b_match = await _get_best_business_match(
            api_key, input_text, matches_list
        )
    e_is_b_best_match = (gt_business or "").strip().lower() == (
        e_best_b_match or ""
    ).strip().lower()

    # Description judge
    e_d_is_matched = await _judge_description(
        api_key, gt_description, e_description
    )

    # Amount and currency matching
    # If ground truth is empty, consider it matched (no expectation)
    if not (gt_amount or "").strip():
        e_a_is_matched = True
    else:
        e_a_is_matched = _values_match(gt_amount, e_amount)

    if not (gt_currency or "").strip():
        e_c_is_matched = True
    else:
        e_c_is_matched = _values_match(gt_currency, e_currency)

    return {
        "o_input_text": input_text,
        "o_business": gt_business,
        "e_b_is_matched": e_b_is_matched,
        "e_b_list": json.dumps(e_b_names, ensure_ascii=False),
        "e_n_matches": e_n_matches,
        "e_score": e_score,
        "e_n_position": e_n_position,
        "best_b_match": e_best_b_match,
        "is_b_best_match": e_is_b_best_match,
        "o_datetime": gt_datetime,
        "e_datetime": e_datetime,
        "e_t_matched": _datetimes_equal(gt_datetime, e_datetime),
        "o_description": gt_description,
        "e_description": e_description,
        "e_d_is_matched": e_d_is_matched,
        "o_amount": gt_amount,
        "e_amount": e_amount,
        "e_a_is_matched": e_a_is_matched,
        "o_currency": gt_currency,
        "e_currency": e_currency,
        "e_c_is_matched": e_c_is_matched,
    }


async def _run_eval(
    rows: List[List[str]], header: List[str]
) -> List[Dict[str, Any]]:
    """Run evaluation on all rows with concurrency control."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    i_input = _idx(header, "Input text")
    i_business = _idx(header, "Business")
    i_datetime = _idx(header, "Datetime")
    i_description = _idx(header, "Description")
    i_amount = _idx(header, "Amount")
    i_currency = _idx(header, "Currency")

    semaphore = asyncio.Semaphore(5)

    async def guard_call(row: List[str]) -> Dict[str, Any]:
        """Guard concurrent calls with semaphore."""
        async with semaphore:
            input_text = row[i_input] if i_input < len(row) else ""
            gt_business = row[i_business] if i_business < len(row) else ""
            gt_datetime = row[i_datetime] if i_datetime < len(row) else ""
            gt_description = (
                row[i_description] if i_description < len(row) else ""
            )
            gt_amount = row[i_amount] if i_amount < len(row) else ""
            gt_currency = row[i_currency] if i_currency < len(row) else ""
            return await _eval_one_row(
                api_key,
                input_text,
                gt_business,
                gt_datetime,
                gt_description,
                gt_amount,
                gt_currency,
            )

    tasks = [asyncio.create_task(guard_call(r)) for r in rows]
    return await asyncio.gather(*tasks)


def _write_eval_csv(out_path: Path, data: List[Dict[str, Any]]) -> None:
    """Write evaluation results to CSV file."""
    cols = [
        "o_input_text",
        "o_business",
        "e_b_is_matched",
        "e_b_list",
        "e_n_matches",
        "e_score",
        "e_n_position",
        "best_b_match",
        "is_b_best_match",
        "o_datetime",
        "e_datetime",
        "e_t_matched",
        "o_description",
        "e_description",
        "e_d_is_matched",
        "o_amount",
        "e_amount",
        "e_a_is_matched",
        "o_currency",
        "e_currency",
        "e_c_is_matched",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        for row in data:
            writer.writerow({k: row.get(k) for k in cols})


def main() -> None:
    """Main function to run evaluation and save results."""
    data_path = Path(__file__).with_name("eval_data.csv")
    out_path = Path(__file__).with_name("eval.csv")

    header, rows = _read_csv_text(data_path)
    if not header or not rows:
        logging.error("No data found in eval/data.csv")
        return

    results = asyncio.run(_run_eval(rows, header))
    _write_eval_csv(out_path, results)
    logging.info(f"Saved {len(results)} rows to {out_path}")


if __name__ == "__main__":
    main()
