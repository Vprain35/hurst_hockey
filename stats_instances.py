from typing import List
import csv
import os
import re

from models import Stats


def _to_int(v: str):
	if v is None:
		return None
	v = str(v).strip()
	if v == '':
		return None
	# remove surrounding quotes
	if v.startswith('"') and v.endswith('"'):
		v = v[1:-1]
	try:
		return int(v)
	except Exception:
		# sometimes values are like '-tm' or non-integer; return None
		return None


def _to_float(v: str):
	if v is None:
		return None
	s = str(v).strip()
	if s == '':
		return None
	# remove surrounding quotes
	if s.startswith('"') and s.endswith('"'):
		s = s[1:-1]
	# handle leading dot like .125
	if s.startswith('.'):
		s = '0' + s
	try:
		return float(s)
	except Exception:
		return None


def load_stats_instances(csv_path: str | None = None) -> List[Stats]:
	"""Load Stats instances from a CSV file and return a list of `Stats` objects.

	By default reads `stats.csv` in the repository root. Non-parsable numeric
	fields are converted to None. The header may contain hyphens which are
	mapped to underscores for attribute lookup (e.g. PN-PIM -> PN_PIM).
	"""
	if csv_path is None:
		csv_path = os.path.join(os.path.dirname(__file__), 'stats.csv')

	instances: List[Stats] = []
	with open(csv_path, newline='', encoding='utf-8') as fh:
		reader = csv.DictReader(fh)
		for row in reader:
			# normalize header keys: replace '-' with '_'
			r = {k.replace('-', '_'): v for k, v in row.items()}

			s = Stats(
				jersey_number=_to_int(r.get('jersey_number')),
				first_name=(r.get('first_name') or '').strip() or None,
				last_name=(r.get('last_name') or '').strip() or None,
				G=_to_int(r.get('G')),
				GP=_to_int(r.get('GP')),
				A=_to_int(r.get('A')),
				PTS=_to_int(r.get('PTS')),
				SH=_to_int(r.get('SH')),
				SH_PCT=_to_float(r.get('SH_PCT')),
				Plus_Minus=_to_int(r.get('Plus_Minus')),
				PPG=_to_int(r.get('PPG')),
				SHG=_to_int(r.get('SHG')),
				FG=_to_int(r.get('FG')),
				GWG=_to_int(r.get('GWG')),
				GTG=_to_int(r.get('GTG')),
				OTG=_to_int(r.get('OTG')),
				HTG=_to_int(r.get('HTG')),
				UAG=_to_int(r.get('UAG')),
				PN_PIM=(r.get('PN_PIM') or '').strip() or None,
				MIN=_to_int(r.get('MIN')),
				MAJ=_to_int(r.get('MAJ')),
				OTH=_to_int(r.get('OTH')),
				BLK=_to_int(r.get('BLK')),
			)
			instances.append(s)

	return instances


def get_stats_instances() -> List[Stats]:
	"""Convenience wrapper that loads from the default `stats.csv`."""
	return load_stats_instances()


__all__ = ["load_stats_instances", "get_stats_instances"]

