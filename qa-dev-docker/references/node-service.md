# Node Service Pattern

Use this when the app runs a Node server at runtime: Express, Fastify, Hono on Node, Next.js standalone server, Remix server, or a custom API process.

## Runtime Shape

- Use a dependency stage for reproducible install.
- Use a QA/build stage that runs lint, tests, typecheck, and build commands that already exist in the repo.
- Use a final runtime stage with production dependencies only.
- Run as a non-root user.
- Expose the app's internal container port, commonly `3000` or `8080`.
- Add a healthcheck against the app's actual health endpoint when one exists; otherwise use `/`.

## Package Manager

Respect the lockfile:

- `package-lock.json`: `npm ci`
- `pnpm-lock.yaml`: `corepack enable` then `pnpm install --frozen-lockfile`
- `yarn.lock`: `corepack enable` then `yarn install --immutable` when Yarn Berry is used

Do not switch package managers while adding Docker.

## Dependency Handling

- Install dev dependencies only in build/QA stages.
- Install or copy production dependencies into the runtime stage.
- Do not copy local `node_modules`.
- Do not run the final container as root.
- Set `NODE_ENV=production` in runtime unless the app documents a different production setting.

## Compose Notes

- Use `env_file` only when the repo already has a safe local convention. Never bake secrets into the image.
- Prefer explicit environment variable examples in docs over committing real `.env` values.
- Mount source code only for a deliberate dev-hot-reload service. Keep the production-shaped service immutable.

## Next.js Standalone Note

If the repo uses Next.js and has `output: "standalone"`, copy `.next/standalone`, `.next/static`, and `public` according to the framework's documented deployment pattern. Keep this separate from generic static export behavior.
