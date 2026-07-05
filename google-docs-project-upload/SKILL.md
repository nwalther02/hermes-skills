---
name: google-docs-project-upload
description: Work with Google Docs in a Google Drive Projects/projectname folder convention. Use when the user says "upload to google docs", "create docs and move to drive", "create a gdoc from markdown", asks to find/read/call/open/summarize/project documents from Google Drive Projects, or references a document named projectname_doccontent such as fitness-pwa_authtest or test_testcontent.
---

# Google Docs Projects

## Core Convention

Use the document title convention `projectname_doccontent`.

- Treat the substring before the first underscore as `projectname`.
- Route project documents under `Projects/<projectname>` in Google Drive.
- Project names may contain hyphens, but not underscores.
- If a requested title has no underscore and no explicit project name, ask for the project before creating, moving, or searching.

Read [references/project-folders.md](references/project-folders.md) before resolving folders.

## Communication Budget

Default to terse output while this skill is active.

- Use short status fragments only when useful: `Creating`, `Moved to Projects/test`, `Verified`.
- Ask only blocking questions.
- For routine success, final response should include only title, path, URL, and verification.
- Expand temporarily for errors, missing folders, duplicate matches, destructive updates, permission problems, or user-requested explanation.
- Persist ultra-terse caveman mode across later project-doc turns only when the user explicitly says `caveman mode` or `/caveman`; stop when the user says `normal mode`.

## Folder Resolution

1. Use the Projects root folder from the reference.
2. Prefer a known child-folder ID from the reference when `projectname` is listed.
3. Verify known folder IDs when possible with Drive metadata:
   - expected name equals `projectname`
   - MIME type is `application/vnd.google-apps.folder`
   - parent includes the Projects root when parent metadata is exposed
4. If `projectname` is not listed, list the Projects root folder and match a child folder by exact name.
5. If no exact child folder exists:
   - For create/upload requests, ask whether to create `Projects/<projectname>` or use a different existing folder.
   - For find/read requests, say the project folder was not found and ask for the intended project or folder.

## Create Or Upload

Use this path when the user asks to upload markdown, create a Google Doc, create docs and move to Drive, or convert content into a project Google Doc.

1. Identify source content.
   - Use the file path the user provided, the selected/current artifact, or content pasted in chat.
   - If multiple plausible sources exist, ask which one to use before creating anything in Drive.

2. Determine the Google Doc title.
   - Prefer the user's explicit document name.
   - Otherwise use the source filename without extension.
   - Preserve the title exactly except for trimming surrounding whitespace.

3. Resolve `Projects/<projectname>` using Folder Resolution.

4. Check duplicates before creating.
   - List `Projects/<projectname>`.
   - If a same-named item exists, do not create another silently.
   - Ask whether to reuse/update the existing file or create a differently named document.

5. Choose the creation route.
   - Basic docs use native Google Docs creation: blank docs, headings, paragraphs, simple lists, simple links, simple tables, and default Google Docs styling.
   - Polished or complex deliverables use the Documents plugin DOCX-first route: formal reports, branded docs, layout-sensitive artifacts, complex tables, figures/images, page-level QA, Word compatibility, or explicit high-fidelity export needs.
   - If ambiguous, choose native creation for normal Google Docs and DOCX-first only when the request sounds designed, branded, polished, or layout-sensitive.

6. Create basic native docs.
   - Read the Google Docs `reference-native-create-direct.md` when available.
   - Create with Google Drive `_create_file` using MIME type `application/vnd.google-apps.document`.
   - Read the new document once with `_get_document`.
   - Write content with direct Google Docs `_batch_update_document` requests.
   - Use real Docs paragraph styles and list requests; do not fake bullets when a real list is intended.

7. Create polished DOCX-first docs.
   - Read the Documents skill and Google Docs import reference before starting.
   - Create the DOCX in scratch/staging, not as a user-facing deliverable.
   - Sanitize with Documents `google_docs_title_sanitize.py`.
   - Render and inspect page PNGs before import. If the renderer fails with missing `liblcms2.2.dylib`, read [references/rendering-troubleshooting.md](references/rendering-troubleshooting.md) and retry with `scripts/render_docx_with_runtime_libs.py`.
   - Import with Google Drive document import using `upload_mode: native_google_docs`.
   - Re-read the imported document and repair only conversion drift.

8. Move and verify.
   - Move or add the created Google Doc directly into `Projects/<projectname>` using the resolved folder ID.
   - Verify Drive metadata with fields like `id,name,mimeType,parents,webViewLink`.
   - Confirm MIME type is `application/vnd.google-apps.document`.
   - Confirm parents include the resolved project folder ID.
   - Verify content with `_get_document_text` for simple docs or `_get_document` for structure-sensitive docs.

## Find Or Read

Use this path when the user asks to get, call, open, fetch, read, summarize, inspect, update, or use an existing project document from Google Drive.

1. Determine project and document target.
   - If the user gives a full title like `projectname_doccontent`, infer `projectname` from the prefix and search for that exact title inside `Projects/<projectname>`.
   - If the user gives a project plus a partial document name, resolve `Projects/<projectname>` and search/list documents there.
   - If the user gives only a project name, list the project folder contents and choose only when there is a single obvious match; otherwise ask which document.

2. Resolve `Projects/<projectname>` using Folder Resolution.

3. Search inside that project folder first.
   - Prefer exact title matches over partial matches.
   - Do not search all of Drive unless the project-folder search fails and the user asks for a broader search.
   - If multiple plausible matches exist, show concise candidates with titles and links and ask which to use.

4. Retrieve content with the narrowest useful tool.
   - Use `_get_document_text` for text summaries or extracted notes.
   - Use `_get_document` for structure, styles, tabs, lists, tables, chips, or edits.
   - Use `_fetch` or `_export_file` only when an export/raw file is actually needed.
   - Preserve the source document; reading/summarizing must not mutate the Drive file.

5. Report source grounding.
   - State the resolved path `Projects/<projectname>`.
   - Include the document title and URL.
   - For summaries or extracted notes, make clear they came from the retrieved Google Doc.
