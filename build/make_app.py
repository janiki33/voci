# Baut Voci.pyw aus template + vokabeln.json (bettet die Vokabeln als JSON ein).
import json, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
vocab = json.loads((root / "vokabeln.json").read_text(encoding="utf-8"))
template = (root / "build" / "voci_template.py").read_text(encoding="utf-8")
out = template.replace("__VOCAB_JSON__", json.dumps(vocab, ensure_ascii=False))
(root / "Voci.pyw").write_text(out, encoding="utf-8")
print(f"Voci.pyw geschrieben ({len(vocab)} Vokabeln)")
