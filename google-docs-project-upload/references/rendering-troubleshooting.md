# Rendering Troubleshooting

Use this only for the DOCX-first route, after creating and sanitizing a local `.docx` for native Google Docs import.

## LibreOffice `liblcms2.2.dylib` Failure

Observed failure:

```text
dyld: Library not loaded: /opt/homebrew/opt/little-cms2/lib/liblcms2.2.dylib
```

If the Documents renderer fails this way, retry through:

```bash
python scripts/render_docx_with_runtime_libs.py input.docx --output-dir out --emit-pdf
```

The helper locates the bundled Documents `render_docx.py`, locates the bundled Poppler `liblcms2.2.dylib`, prepends that directory to `DYLD_LIBRARY_PATH`, and delegates rendering.

## Verification Rule

- If render succeeds, inspect every generated `page-*.png` before importing or reporting visual QA.
- If render fails because `soffice` is missing, follow the Documents fallback and disclose skipped render QA.
- If render fails for another reason, do not claim visual QA passed.
