import hashlib
import tempfile
from pathlib import Path

from services.db_handler import calculate_file_sha256


def test_calculate_file_sha256_matches_expected():
    payload = b"streaming upload test payload"
    with tempfile.NamedTemporaryFile(delete=False) as handle:
        handle.write(payload)
        temp_path = handle.name

    try:
        expected = hashlib.sha256(payload).hexdigest()
        assert calculate_file_sha256(temp_path) == expected
    finally:
        Path(temp_path).unlink(missing_ok=True)
