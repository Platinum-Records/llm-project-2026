"""Clean raw JSONL fragments while retaining provenance and review status.

Run from repository root:
    python src/ingestion/clean.py
    python src/ingestion/clean.py --approved-only
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


def prepare(record):
    for field in ('id', 'text', 'mode', 'source', 'license'):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError(f'Missing or invalid {field}')
    for field in ('id', 'mode', 'source', 'license'):
        record[field] = record[field].strip()
    record['mode'] = record['mode'].lower()
    if record['mode'] not in {'folk', 'rap'}:
        raise ValueError('Unknown mode')

    for field in ('authorship', 'region', 'theme', 'rhyme_scheme', 'transcription_status'):
        value = record.get(field)
        if value is not None and (not isinstance(value, str) or not normalize(value)):
            raise ValueError(f'Invalid {field}')
        record[field] = normalize(value) if value is not None else None
    record['transcription_status'] = (record['transcription_status'] or 'unreviewed').lower()
    record.setdefault('final_approved', False)
    if type(record['final_approved']) is not bool:
        raise ValueError('Invalid final_approved')

    original = record['text']
    modern = record.pop('text_modernized', original)
    if not isinstance(modern, str) or not normalize(modern):
        raise ValueError('Empty or invalid modernized text')
    record['text_original'] = original if record['mode'] == 'folk' else None
    record['text'] = normalize(modern)
    scheme = record['rhyme_scheme']
    if scheme is not None:
        if not re.fullmatch(r'[A-Z]+', scheme) or len(scheme) != len(record['text'].splitlines()):
            raise ValueError('Rhyme scheme must have one letter per verse line')

    approved = record['final_approved'] and record['transcription_status'] in REVIEWED
    record['dataset_status'] = 'approved' if approved else 'provisional_unapproved'


def clean(raw_dir, output, approved_only=False):
    stats = {'read': 0, 'accepted': 0, 'duplicates': 0, 'invalid': 0, 'unverified': 0}
    accepted, seen, seen_ids = [], set(), set()
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
                    prepare(record)
                    if record['id'] in seen_ids:
                        raise ValueError(f"Duplicate ID: {record['id']}")
                except ValueError as exc:
                    stats['invalid'] += 1
                    print(f'INVALID {path.name}:{line_no}: {exc}')
                    continue
                seen_ids.add(record['id'])
                if approved_only and record['dataset_status'] != 'approved':
                    stats['unverified'] += 1
                    continue
                key = (record['mode'], record['text'].casefold())
                if key in seen:
                    stats['duplicates'] += 1
                    continue
                seen.add(key)
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
