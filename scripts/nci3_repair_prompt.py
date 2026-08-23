from pathlib import Path

path = Path('src/grox/reasoning/local_llama_cpp.py')
text = path.read_text(encoding='utf-8')
old = '''        prompt = (\n            _ASSISTANT_SYSTEM\n            + "\nCommander input follows verbatim between markers.\n"\n            + "<commander-input>\n"\n            + message\n            + "\n</commander-input>\n\n"\n            + "Produce the direct Commander-facing response now."\n        )\n'''
# The bootstrap renderer converted the escaped newlines above into physical
# newlines inside string literals. Match that exact broken source separately.
broken = '''        prompt = (\n            _ASSISTANT_SYSTEM\n            + "
Commander input follows verbatim between markers.
"\n            + "<commander-input>
"\n            + message\n            + "
</commander-input>

"\n            + "Produce the direct Commander-facing response now."\n        )\n'''
replacement = '''        prompt = (\n            _ASSISTANT_SYSTEM\n            + "\\nCommander input follows verbatim between markers.\\n"\n            + "<commander-input>\\n"\n            + message\n            + "\\n</commander-input>\\n\\n"\n            + "Produce the direct Commander-facing response now."\n        )\n'''
if text.count(broken) != 1:
    raise RuntimeError(f'expected one broken assistant prompt, found {text.count(broken)}')
path.write_text(text.replace(broken, replacement), encoding='utf-8')

for temp in (
    Path('.nci3-bootstrap-trigger'),
    Path('.nci3-repair-trigger'),
    Path('scripts/nci3_repair_prompt.py'),
    Path('.github/workflows/nci3-repair-prompt.yml'),
):
    temp.unlink(missing_ok=True)
