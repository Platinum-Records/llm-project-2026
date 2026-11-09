"""Clean raw JSONL fragments while retaining provenance and review status.

Run from repository root:
    python src/clean.py
    python src/clean.py                       # Week 7 provisional sample (default)
    python src/clean.py --approved-only       # approved records only
"""
import argparse
import json
import re
import unicodedata
from pathlib import Path

DIACRITICS = str.maketrans({'ş': 'ș', 'Ş': 'Ș', 'ţ': 'ț', 'Ţ': 'Ț'})
REVIEWED = {'verified', 'manually_verified', 'reviewed', 'approved'}


def normalize(value):
    value = unicodedata.normalize('NFC', value).translate(DIACRITICS)
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in value.replace('\r\n', '\n').replace('\r', '\n').split('\n')]
    return '\n'.join(line for line in lines if line).strip()


def clean(raw_dir, output, approved_only=False):
    stats = {'read': 0, 'accepted': 0, 'duplicates': 0, 'invalid': 0, 'unverified': 0}
    accepted, seen = [], set()
    for path in sorted(raw_dir.glob('*.jsonl')):
        with path.open(encoding='utf-8-sig') as handle:
            for line_no, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                stats['read'] += 1
                try:
                    record = json.loads(line)
                    if not isinstance(record, dict):
                        raise ValueError('Not an object')
                    if not all(isinstance(record.get(k), str) and record[k].strip() for k in ('id', 'text', 'mode', 'source', 'license')):
                        raise ValueError('Missing required fields')
                    text = normalize(record['text'])
                    if not text:
                        raise ValueError('Empty text')
                except (ValueError, json.JSONDecodeError, TypeError) as exc:
                    stats['invalid'] += 1
                    print(f'INVALID {path.name}:{line_no}: {exc}')
                    continue
                if approved_only and not (record.get('final_approved') is True and record.get('transcription_status', '').lower() in REVIEWED):
                    stats['unverified'] += 1
                    continue
                key = (record['mode'].strip().lower(), text.casefold())
                if key in seen:
                    stats['duplicates'] += 1
                    continue
                seen.add(key)
                record['text'] = text
                record.setdefault('theme', None)
                record.setdefault('rhyme_scheme', None)
                record['dataset_status'] = 'approved' if (record.get('final_approved') is True and record.get('transcription_status', '').lower() in REVIEWED) else 'provisional_unapproved'
                accepted.append(record)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('w', encoding='utf-8') as handle:
        for record in accepted:
            handle.write(json.dumps(record, ensure_ascii=False) + '\n')
    stats['accepted'] = len(accepted)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print(f'Output: {output}')
    return stats


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw-dir', type=Path, default=Path('data/raw'))
    parser.add_argument('--output', type=Path, default=Path('data/processed/chunks.jsonl'))
    parser.add_argument('--approved-only', action='store_true', help='Exclude all unapproved records; for approved-only use')
    args = parser.parse_args()
    clean(args.raw_dir, args.output, args.approved_only)
