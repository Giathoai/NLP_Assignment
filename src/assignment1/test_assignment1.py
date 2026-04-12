import sys
import os
import json
import re

if hasattr(sys.stdout, 'buffer'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

SAMPLE_CONTRACTS = """Bên A là Công ty TNHH Thương mại Toàn Cầu, có trụ sở tại 45 Phố Huế, Hà Nội.
Bên B là Công ty Cổ phần Dịch vụ Kỹ thuật số Đông Nam Á, địa chỉ tại 12 Nguyễn Huệ, TP.HCM.
Hai bên đồng ý ký kết hợp đồng này với các điều khoản sau.
Bên A có nghĩa vụ cung cấp dịch vụ tư vấn phần mềm, và Bên B có trách nhiệm thanh toán đúng hạn.
Nếu Bên B chậm thanh toán quá 15 ngày, Bên A có quyền tạm dừng dịch vụ.
Hợp đồng này có hiệu lực từ ngày 01/04/2025 và kết thúc vào ngày 31/03/2026.
Mọi tranh chấp phát sinh sẽ được giải quyết tại Tòa án nhân dân TP.HCM.
"""

SAMPLE_CLAUSES = [
    "Bên A là Công ty TNHH Thương mại Toàn Cầu, có trụ sở tại 45 Phố Huế, Hà Nội.",
    "Bên B có trách nhiệm thanh toán đúng hạn.",
    "Nếu Bên B chậm thanh toán quá 15 ngày, Bên A có quyền tạm dừng dịch vụ.",
    "Hợp đồng này có hiệu lực từ ngày 01/04/2025.",
]

passed = 0
failed = 0
skipped = 0

def assert_true(condition: bool, msg: str):
    global passed, failed
    mark = "[PASS]" if condition else "[FAIL]"
    print(f"  {mark} {msg}")
    if condition:
        passed += 1
    else:
        failed += 1

def skip(msg: str):
    global skipped
    print(f"  [SKIP] {msg}")
    skipped += 1

def section(title: str):
    print(f"\n{'=' * 55}")
    print(f"  {title}")
    print(f"{'=' * 55}")


section("Task 1.1 – Clause Segmenter (segmenter.py)")

try:
    from src.assignment1.segmenter import segment_clauses

    clauses = segment_clauses(SAMPLE_CONTRACTS)
    assert_true(len(clauses) > 0,
                f"segment_clauses() tra ve {len(clauses)} menh de (> 0)")

    all_strings = all(isinstance(c, str) and len(c.strip()) > 0 for c in clauses)
    assert_true(all_strings, "Tat ca menh de la chuoi khong rong")

    simple = segment_clauses("Hop dong nay co hieu luc tu ngay 01/04/2025.")
    assert_true(len(simple) == 1,
                f"Cau don khong bi tach sai (ket qua: {len(simple)} menh de)")

    ends_ok = all(c.endswith(('.', ';')) for c in clauses)
    assert_true(ends_ok, "Moi menh de ket thuc bang '.' hoac ';'")

    capitalized = all(c[0].isupper() for c in clauses if c)
    assert_true(capitalized, "Chu cai dau moi menh de duoc viet hoa")

    print(f"\n  [INFO] 3 menh de dau tien:")
    for i, c in enumerate(clauses[:3], 1):
        print(f"    {i}. {c}")

except ImportError as e:
    skip(f"Khong the import segmenter: {e}")
    clauses = []
except Exception as e:
    print(f"  [FAIL] Loi segmenter: {e}")
    failed += 1
    clauses = []


section("Task 1.2 – Noun-Phrase Chunker (chunker.py) – IOB Tagging")

try:
    import underthesea  # noqa: F401
    _has_underthesea = True
except ImportError:
    _has_underthesea = False
    skip("underthesea chua duoc cai dat  ->  pip install underthesea")
    skip("Bo qua cac test chunker (3 test)")

if _has_underthesea:
    try:
        from src.assignment1.chunker import chunk_clauses

        clauses_text = "\n".join(SAMPLE_CLAUSES)
        result = chunk_clauses(clauses_text)

        assert_true(len(result.strip()) > 0,
                    "chunk_clauses() tra ve noi dung khong rong")

        lines = [l for l in result.split('\n') if l.strip()]
        valid_fmt = all('\t' in line for line in lines)
        assert_true(valid_fmt, "Moi dong co dang 'tu \\t nhan_IOB'")

        valid_labels = True
        bad = []
        for line in lines:
            parts = line.split('\t')
            if len(parts) >= 2:
                label = parts[-1].strip()
                if label not in ("B-NP", "I-NP", "O"):
                    valid_labels = False
                    bad.append(label)
        assert_true(valid_labels,
                    f"Tat ca nhan thuoc {{B-NP, I-NP, O}}" +
                    (f" -- nhan la: {bad[:3]}" if bad else ""))

        total_words = sum(len(c.split()) for c in SAMPLE_CLAUSES)
        assert_true(len(lines) >= total_words * 0.5,
                    f"So dong output ({len(lines)}) >= 50% tong tu ({total_words})")

        print(f"\n  [INFO] 6 dong IOB dau tien:")
        for line in result.split('\n')[:6]:
            print(f"    {line}")

    except Exception as e:
        print(f"  [FAIL] Loi chunker: {e}")
        failed += 1

section("Task 1.3 – Dependency Parser (parser.py)")

_has_parser = _has_underthesea

if not _has_parser:
    skip("underthesea chua duoc cai dat  ->  pip install underthesea")
    skip("Bo qua cac test parser (5 test)")

if _has_parser:
    try:
        from src.assignment1.parser import parse_dependencies

        clauses_text = "\n".join(SAMPLE_CLAUSES)
        dep_data = parse_dependencies(clauses_text)

        assert_true(isinstance(dep_data, list),
                    "parse_dependencies() tra ve list")

        assert_true(len(dep_data) == len(SAMPLE_CLAUSES),
                    f"So phan tu ({len(dep_data)}) = so menh de ({len(SAMPLE_CLAUSES)})")

        keys_ok = all("clause" in item and "dependencies" in item
                      for item in dep_data)
        assert_true(keys_ok, "Moi phan tu co key 'clause' va 'dependencies'")

        if dep_data and dep_data[0]["dependencies"]:
            first_tok = dep_data[0]["dependencies"][0]
            required = {"Token", "Head", "Dependency"}
            has_keys = required.issubset(first_tok.keys())
            assert_true(has_keys, f"Token dict co du key: {required}")
        else:
            skip("dependencies rong, bo qua kiem tra cau truc token")

        try:
            json_str = json.dumps(dep_data, ensure_ascii=False)
            assert_true(len(json_str) > 0, "Ket qua co the serialize thanh JSON")
        except Exception as je:
            assert_true(False, f"Khong the serialize JSON: {je}")

        print(f"\n  [INFO] 5 token dau tien cua menh de 1:")
        for tok in dep_data[0]["dependencies"][:5]:
            print(f"    {str(tok['Token']):15s} -> {str(tok['Head']):15s} [{tok['Dependency']}]")

    except Exception as e:
        print(f"  [FAIL] Loi parser: {e}")
        failed += 1


# ──────────────────────────────────────────────────────────────
# Integration test: segmenter -> chunker -> parser
# ──────────────────────────────────────────────────────────────
section("Integration Test – segmenter -> chunker -> parser")

if not _has_underthesea or not _has_parser:
    missing = []
    if not _has_underthesea:
        missing.append("underthesea")
    if not _has_parser:
        missing.append("spacy/xx_sent_ud_sm")
    skip(f"Bo qua integration (thieu: {', '.join(missing)})")
else:
    try:
        from src.assignment1.segmenter import segment_clauses
        from src.assignment1.chunker import chunk_clauses
        from src.assignment1.parser import parse_dependencies

        all_clauses = segment_clauses(SAMPLE_CONTRACTS)
        clauses_text = "\n".join(all_clauses)

        chunks_out = chunk_clauses(clauses_text)
        dep_out = parse_dependencies(clauses_text)

        assert_true(len(all_clauses) > 0,
                    f"Stage 1 (segmenter): {len(all_clauses)} menh de")
        assert_true(len(chunks_out.strip()) > 0,
                    "Stage 2 (chunker): output khong rong")
        assert_true(len(dep_out) == len(all_clauses),
                    f"Stage 3 (parser): {len(dep_out)} ket qua = {len(all_clauses)} menh de")

        print(f"\n  [INFO] Pipeline hoan thanh: "
              f"{len(all_clauses)} menh de -> chunked -> parsed")

    except Exception as e:
        print(f"  [FAIL] Loi integration: {e}")
        failed += 1


# ──────────────────────────────────────────────────────────────
# Tong ket
# ──────────────────────────────────────────────────────────────
total = passed + failed
print(f"\n{'=' * 55}")
print(f"  KET QUA: {passed}/{total} test PASS, {skipped} SKIP")
if failed == 0:
    print("  >> Tat ca test PASS (hoac SKIP do thieu thu vien)")
else:
    print(f"  >> {failed} test FAIL -- xem chi tiet phia tren")
print(f"{'=' * 55}\n")

if not _has_underthesea:
    print("  [HINT] Cai underthesea:     pip install underthesea")
print()

sys.exit(0 if failed == 0 else 1)
