# Google Docs Projects — Reference

## Folder Resolution

1. Use the Projects root folder ID from SKILL.md.
2. Prefer a known child-folder ID from the table when `projectname` is listed.
3. Verify known folder IDs when possible:
   - expected name equals `projectname`
   - MIME type is `application/vnd.google-apps.folder`
   - parent includes the Projects root when parent metadata is exposed
4. If `projectname` is not listed, list the Projects root folder and match a child folder by exact name.
5. If no exact child folder exists:
   - Create/upload: ask whether to create `Projects/<projectname>` or use an existing folder.
   - Find/read: say the project folder was not found and ask for the intended project or folder.

## Create Or Upload

Use when the user asks to upload markdown, create a Google Doc, create docs and move to Drive, or convert content into a project Google Doc.

1. Identify source content — file path the user provided, selected artifact, or pasted content. If multiple plausible sources exist, ask which one before creating anything in Drive.

2. Determine title — prefer the user's explicit name; otherwise use the source filename without extension. Trim surrounding whitespace only.

3. Resolve `Projects/<projectname>` using Folder Resolution above.

4. Check duplicates — list `Projects/<projectname>`. If a same-named item exists, do not silently create another. Ask whether to reuse/update the existing file or create a differently named document.

5. Choose creation route:
   - **Native Docs** — blank docs, headings, paragraphs, simple lists, simple links, simple tables, default Google Docs styling.
   - **DOCX-first** — formal reports, branded docs, layout-sensitive artifacts, complex tables, figures/images, page-level QA, Word compatibility, or explicit high-fidelity export needs.
   - If ambiguous, default to native Docs unless the request sounds designed, branded, polished, or layout-sensitive.

6. Create native docs:
   - MIME type `application/vnd.google-apps.document`.
   - Read the new document once before writing content when the tool supports it.
   - Use real Docs paragraph styles and list requests; do not fake bullets when a real list is intended.

7. Create DOCX-first docs:
   - Create the DOCX in scratch/staging, not as a user-facing deliverable.
   - Use native-Google-Docs style: Arial, black title/headings/body, simple layout.
   - Sanitize any local DOCX before import if the Documents/Codex sanitizer is available.
   - Render and inspect page PNGs before import when render tooling is available.
   - If the renderer fails with missing `liblcms2.2.dylib`, retry with the Codex-side helper:
     ```bash
     python /Users/nicksmac/.codex/skills/google-docs-project-upload/scripts/render_docx_with_runtime_libs.py input.docx --output-dir out --emit-pdf
     ```
   - Inspect every generated `page-*.png` before importing or reporting visual QA.
   - If render cannot run, disclose that visual QA was skipped.
   - Import with native Google Docs conversion (not as raw `.docx`) unless the user asks to preserve the Word file.
   - Re-read the imported document and repair only conversion drift.

8. Move and verify:
   - Move the Google Doc into `Projects/<projectname>` using the resolved folder ID.
   - Verify Drive metadata: `id,name,mimeType,parents,webViewLink`.
   - Confirm MIME type is `application/vnd.google-apps.document`.
   - Confirm parents include the resolved project folder ID.
   - Verify content with document text readback (simple docs) or full document readback (structure-sensitive docs).

## Find Or Read

Use when the user asks to get, call, open, fetch, read, summarize, inspect, update, or use an existing project document from Google Drive.

1. Determine target:
   - Full title like `projectname_doccontent` — infer `projectname` from prefix, search for exact title inside `Projects/<projectname>`.
   - Project plus partial name — resolve `Projects/<projectname>` and search/list documents there.
   - Project name only — list project folder contents, pick only when there is a single obvious match; otherwise ask.

2. Resolve `Projects/<projectname>` using Folder Resolution above.

3. Search inside that project folder first:
   - Prefer exact title matches over partial matches.
   - Do not search all of Drive unless the project-folder search fails and the user asks for a broader search.
   - If multiple plausible matches exist, show concise candidates with titles and links and ask which to use.

4. Retrieve content with the narrowest useful tool:
   - Text readback for text summaries or extracted notes.
   - Full document readback for structure, styles, tabs, lists, tables, chips, or edits.
   - File fetch/export only when an export or raw file is actually needed.
   - Reading/summarizing must not mutate the Drive file.

5. Report source grounding:
   - State the resolved path `Projects/<projectname>`.
   - Include the document title and URL.
   - For summaries or extracted notes, make clear they came from the retrieved Google Doc.
