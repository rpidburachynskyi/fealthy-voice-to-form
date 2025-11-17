import csv
from pathlib import Path
from typing import List, Dict, Tuple


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

    import io

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


def _parse_bool(value: str) -> bool:
    """Parse boolean value from CSV string."""
    return str(value).strip().lower() == "true"


def _parse_int(value: str) -> int:
    """Parse integer value from CSV string."""
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return 0


def calculate_accuracies(csv_path: Path) -> Dict[str, float]:
    """Calculate accuracies from eval.csv file."""
    header, rows = _read_csv_text(csv_path)
    if not header or not rows:
        raise ValueError(f"No data found in {csv_path}")

    # Get column indices
    idx_e_t_matched = _idx(header, "e_t_matched")
    idx_e_d_is_matched = _idx(header, "e_d_is_matched")
    idx_e_c_is_matched = _idx(header, "e_c_is_matched")
    idx_e_a_is_matched = _idx(header, "e_a_is_matched")
    idx_e_b_is_matched = _idx(header, "e_b_is_matched")
    idx_e_n_matches = _idx(header, "e_n_matches")
    idx_is_b_best_match = _idx(header, "is_b_best_match")

    total_rows = len(rows)

    # Simple accuracies: count True / total
    e_t_true = 0
    e_d_true = 0
    e_c_true = 0
    e_a_true = 0
    e_b_true = 0
    is_b_best_match_true = 0

    # Business precision metric: sum of (1/e_n_matches if matched) / total
    e_b_precision_sum = 0.0

    for row in rows:
        # Simple boolean accuracies
        if idx_e_t_matched < len(row):
            if _parse_bool(row[idx_e_t_matched]):
                e_t_true += 1

        if idx_e_d_is_matched < len(row):
            if _parse_bool(row[idx_e_d_is_matched]):
                e_d_true += 1

        if idx_e_c_is_matched < len(row):
            if _parse_bool(row[idx_e_c_is_matched]):
                e_c_true += 1

        if idx_e_a_is_matched < len(row):
            if _parse_bool(row[idx_e_a_is_matched]):
                e_a_true += 1

        # Business metrics
        if idx_e_b_is_matched < len(row):
            if _parse_bool(row[idx_e_b_is_matched]):
                e_b_true += 1
                # precision metric: 1/e_n_matches when matched
                if idx_e_n_matches < len(row):
                    n_matches = _parse_int(row[idx_e_n_matches])
                    if n_matches > 0:
                        e_b_precision_sum += 1.0 / n_matches
                    else:
                        # Edge case: matched but n_matches is 0 (shouldn't happen, but handle it)
                        e_b_precision_sum += 1.0

        # Best business match metric
        if idx_is_b_best_match < len(row):
            if _parse_bool(row[idx_is_b_best_match]):
                is_b_best_match_true += 1

    # Calculate final accuracies
    accuracies = {
        "e_t_accuracy": e_t_true / total_rows if total_rows > 0 else 0.0,
        "e_d_accuracy": e_d_true / total_rows if total_rows > 0 else 0.0,
        "e_c_accuracy": e_c_true / total_rows if total_rows > 0 else 0.0,
        "e_a_accuracy": e_a_true / total_rows if total_rows > 0 else 0.0,
        "e_b_accuracy": e_b_true / total_rows if total_rows > 0 else 0.0,
        "e_b_precision": (
            e_b_precision_sum / total_rows if total_rows > 0 else 0.0
        ),
        "is_b_best_match_accuracy": (
            is_b_best_match_true / total_rows if total_rows > 0 else 0.0
        ),
    }

    return accuracies


def main() -> None:
    """Main function to calculate and display metrics."""
    csv_path = Path(__file__).with_name("eval.csv")

    if not csv_path.exists():
        print(f"Error: {csv_path} not found")
        return

    accuracies = calculate_accuracies(csv_path)

    # Mapping from internal names to display names
    display_names = {
        "e_t_accuracy": "Time accuracy",
        "e_d_accuracy": "Description accuracy",
        "e_c_accuracy": "Currency accuracy",
        "e_a_accuracy": "Amount accuracy",
        "e_b_accuracy": "Business accuracy",
        "e_b_precision": "Business average precision",
        "is_b_best_match_accuracy": "LLL business match precision",
    }

    print("Metrics:")
    print("=" * 50)
    for metric_name, value in accuracies.items():
        display_name = display_names.get(metric_name, metric_name)
        print(f"{display_name}: {value:.4f} ({value*100:.2f}%)")
    print("=" * 50)


if __name__ == "__main__":
    main()
