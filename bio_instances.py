from typing import List
import csv
import os

from models import Bio


def _to_int(v: str):
    if v is None:
        return None
    v = v.strip()
    if v == '':
        return None
    try:
        return int(v)
    except ValueError:
        return None


def load_bio_instances(csv_path: str | None = None) -> List[Bio]:
    """Load Bio instances from a CSV file and return a list of `Bio` objects.

    By default reads `bio.csv` in the repository root. Fields that are empty
    are converted to None and numeric fields are converted to int when possible.
    """
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(__file__), 'bio.csv')

    instances: List[Bio] = []
    with open(csv_path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            b = Bio(
                first_name=(row.get('first_name') or '').strip() or None,
                last_name=(row.get('last_name') or '').strip() or None,
                position=(row.get('position') or '').strip() or None,
                jersey_number=_to_int(row.get('jersey_number')),
                weight=_to_int(row.get('weight')),
                height=(row.get('height') or '').strip() or None,
                class_year=(row.get('class_year') or '').strip() or None,
                home_town=(row.get('home_town') or '').strip() or None,
                highschool=(row.get('highschool') or '').strip() or None,
            )
            instances.append(b)

    return instances


def get_bio_instances() -> List[Bio]:
    """Convenience wrapper that loads from the default `bio.csv`."""
    return load_bio_instances()


__all__ = ["load_bio_instances", "get_bio_instances"]
