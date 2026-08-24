# Baut Voci.pyw aus template + vokabeln.json (bettet die Vokabeln als JSON ein).
import base64, json, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
vocab = json.loads((root / "vokabeln.json").read_text(encoding="utf-8"))
template = (root / "build" / "voci_template.py").read_text(encoding="utf-8")
icon = base64.b64encode((root / "assets" / "voci64.png").read_bytes()).decode()
out = (template
       .replace("__VOCAB_JSON__", json.dumps(vocab, ensure_ascii=False))
       .replace("__ICON_B64__", icon))
(root / "Voci.pyw").write_text(out, encoding="utf-8")
print(f"Voci.pyw geschrieben ({len(vocab)} Vokabeln)")
