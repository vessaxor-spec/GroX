from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from grox.llama_cpp_backend import LlamaCppCLIBackend, LlamaCppHandle


class LlamaCppCpuPolicyTests(unittest.TestCase):
    def test_cpu_only_invocation_disables_automatic_device_memory_fit(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cli = root / "llama-cli"
            cli.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import sys

                    if "--version" in sys.argv:
                        print("version: 10218 (de699957b)")
                        raise SystemExit(0)
                    print('{"status":"ok"}')
                    """
                ),
                encoding="utf-8",
            )
            cli.chmod(0o755)
            model = root / "seed.gguf"
            model.write_bytes(b"fake")
            scratch = root / "scratch"
            scratch.mkdir()

            backend = LlamaCppCLIBackend(cli, scratch_root=scratch, timeout_seconds=1)
            result = backend.invoke(
                LlamaCppHandle(model_id="seed", artifact_path=model),
                {
                    "prompt": "Return status ok.",
                    "json_schema": {
                        "type": "object",
                        "properties": {"status": {"type": "string"}},
                        "required": ["status"],
                    },
                },
            )

            self.assertEqual(result["text"], '{"status":"ok"}')
            command = list(backend.last_command or ())
            self.assertIn("--fit", command)
            self.assertEqual(command[command.index("--fit") + 1], "off")
            self.assertIn("-ngl", command)
            self.assertEqual(command[command.index("-ngl") + 1], "0")


if __name__ == "__main__":
    unittest.main()
