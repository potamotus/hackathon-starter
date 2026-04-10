# AGENTS.md — Instructions for AI Coding Agents

You are an AI agent working on this hackathon project. Follow these rules.

## Stack
- Next.js 15 (App Router) + TypeScript + Tailwind CSS 4
- Deploy: Vercel (auto-deploy from `main`)

## How to Work

### 1. Before coding
- Read relevant files first — never assume
- Check existing code for patterns, follow them
- If task is ambiguous, ask clarifying questions before proceeding

### 2. Branching
- Always create a feature branch: `feature/<short-description>`
- Never push to `main` directly
- Small, frequent commits — prefer many small commits over one big one

### 3. Code quality
- Run `npm run build` before claiming work is done
- No `.env` files in commits — use `.env.example` as template
- Follow existing naming conventions and code style
- Delete unused code, don't leave commented-out blocks

### 4. Pull Requests
- Create PR with clear description of what changed and why
- Use conventional commits: `feat:`, `fix:`, `chore:`, `docs:`
- Request review from at least 1 teammate

### 5. Task tracking
- Use GitHub Issues for tasks — create issue, branch from it, close on merge
- One issue = one branch = one PR
- Keep issues updated with progress

### 6. What NOT to do
- Don't add dependencies without checking they're needed
- Don't refactor unrelated code
- Don't create documentation files unless asked
- Don't over-engineer — hackathon means ship fast, not perfect

## Quick Commands
```bash
npm install          # Install dependencies
npm run dev          # Start dev server (localhost:3000)
npm run build        # Production build (run before PR)
npm run lint         # Run linter
```

## Project Structure
```
src/app/          # Pages and layouts (Next.js App Router)
src/components/   # Reusable UI components
src/lib/          # Utilities, helpers, API clients
public/           # Static assets
```
