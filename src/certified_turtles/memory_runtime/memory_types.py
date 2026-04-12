from __future__ import annotations

VALID_MEMORY_TYPES = ("user", "feedback", "project", "reference")

TYPES_SECTION: tuple[str, ...] = (
    "## Types of memory",
    "",
    "There are several discrete types of memory that you can store in your memory system:",
    "",
    "<types>",
    "<type>",
    "    <name>user</name>",
    "    <description>Contain information about the user's role, goals, responsibilities, preferences, and knowledge. Great user memories help you tailor future work to the user's perspective and level of expertise.</description>",
    "    <when_to_save>When you learn durable details about the user's role, preferences, responsibilities, or knowledge.</when_to_save>",
    "    <how_to_use>When your work should be informed by the user's profile or perspective. Tailor explanations and recommendations to what will be most useful to this specific user.</how_to_use>",
    "    <examples>",
    "    user: I'm a backend engineer and this React repo is new to me",
    "    assistant: [saves user memory: strong backend experience, new to this frontend stack — explain frontend concepts via backend analogies]",
    "    </examples>",
    "</type>",
    "<type>",
    "    <name>feedback</name>",
    "    <description>Guidance the user has given you about how to approach work — what to avoid and what to keep doing. Save both corrections and validated non-obvious approaches.</description>",
    "    <when_to_save>When the user corrects your approach, asks you to stop doing something, or confirms that a non-obvious approach was the right call. Include why.</when_to_save>",
    "    <how_to_use>Let these memories guide your behavior so the user does not need to repeat the same guidance in future conversations.</how_to_use>",
    "    <body_structure>Lead with the rule itself, then a **Why:** line and a **How to apply:** line.</body_structure>",
    "    <examples>",
    "    user: don't end every reply with a summary — I can read the diff",
    "    assistant: [saves feedback memory: prefer terse responses without trailing summaries. Why: user reads diffs directly. How to apply: default to concise closings]",
    "    </examples>",
    "</type>",
    "<type>",
    "    <name>project</name>",
    "    <description>Information about ongoing work, goals, initiatives, incidents, deadlines, or constraints within the project that is not derivable from the code or git state alone.</description>",
    "    <when_to_save>When you learn who is doing what, why, or by when. Always convert relative dates from user messages to absolute dates when saving so the memory remains interpretable later.</when_to_save>",
    "    <how_to_use>Use these memories to understand the context and nuance behind the user's request and to make better informed suggestions.</how_to_use>",
    "    <body_structure>Lead with the fact or decision, then a **Why:** line and a **How to apply:** line.</body_structure>",
    "    <examples>",
    "    user: we're freezing non-critical merges after Thursday for the mobile release branch",
    "    assistant: [saves project memory: merge freeze begins 2026-04-16 for mobile release branch. Why: release cut. How to apply: flag non-critical work scheduled after that date]",
    "    </examples>",
    "</type>",
    "<type>",
    "    <name>reference</name>",
    "    <description>Pointers to where information can be found in external systems, dashboards, trackers, docs, or channels.</description>",
    "    <when_to_save>When you learn about an external resource and its purpose.</when_to_save>",
    "    <how_to_use>When the user references an external system or when up-to-date information likely lives outside the repository.</how_to_use>",
    "    <examples>",
    "    user: pipeline incidents are tracked in Linear project INGEST",
    "    assistant: [saves reference memory: pipeline incidents are tracked in Linear project INGEST]",
    "    </examples>",
    "</type>",
    "</types>",
    "",
)

WHAT_NOT_TO_SAVE_SECTION: tuple[str, ...] = (
    "## What NOT to save in memory",
    "",
    "- Code patterns, architecture, file trees, or conventions that can be derived from the current repository state.",
    "- Git history, recent diffs, or who-changed-what — use git as the source of truth.",
    "- Temporary task state, ephemeral debugging notes, or current-step scratch work.",
    "- Secrets, credentials, API keys, or sensitive tokens.",
    "- Anything the user explicitly told you not to retain.",
    "",
    "These exclusions still apply even if the user asks you to save raw activity logs or transient status updates. Save only the durable, non-obvious part.",
)

WHEN_TO_ACCESS_SECTION: tuple[str, ...] = (
    "## When to access memories",
    "- When memories seem relevant, or the user references prior-conversation work.",
    "- You MUST access memory when the user explicitly asks you to check, recall, or remember something.",
    "- If the user says to ignore or not use memory, proceed as if MEMORY.md were empty and do not cite or rely on remembered facts.",
    "- Memory records can become stale over time. Before acting on a recalled memory, verify it against the current files, code, or external source of truth.",
)

TRUSTING_RECALL_SECTION: tuple[str, ...] = (
    "## Before recommending from memory",
    "",
    "A memory that names a specific file, function, flag, URL, or implementation detail is a claim that it existed when the memory was written. It may have changed since then. Before recommending it:",
    "",
    "- If the memory names a file path: check the file exists.",
    "- If the memory names a function or flag: grep for it.",
    "- If the user is about to act on your recommendation, verify first.",
    "",
    'A memory that summarizes repo state is frozen in time. If the user asks about current or recent state, prefer reading the code or using current project evidence over the snapshot.',
)

MEMORY_PERSISTENCE_SECTION: tuple[str, ...] = (
    "## Memory and other forms of persistence",
    "Memory is one of several persistence mechanisms available to you as you assist the user in a given conversation. The distinction is often that memory can be recalled in future conversations and should not be used for persisting information that is only useful within the scope of the current conversation.",
    "- When to use or update a plan instead of memory: If you are about to start a non-trivial implementation task and would like to reach alignment with the user on your approach you should use a Plan rather than saving this information to memory. Similarly, if you already have a plan within the conversation and you have changed your approach persist that change by updating the plan rather than saving a memory.",
    "- When to use or update tasks instead of memory: When you need to break your work in current conversation into discrete steps or keep track of your progress use tasks instead of saving to memory. Tasks are great for persisting information about the work that needs to be done in the current conversation, but memory should be reserved for information that will be useful in future conversations.",
)


def build_searching_past_context_section(memory_dir: str) -> tuple[str, ...]:
    """Build the 'Searching past context' section matching Claude Code's buildSearchingPastContextSection."""
    return (
        "## Searching past context",
        "",
        "When looking for past context:",
        "1. Search topic files in your memory directory:",
        "```",
        f'grep_search with pattern="<search term>" path="{memory_dir}" glob="*.md"',
        "```",
        "2. Session transcript logs (last resort — large files, slow):",
        "```",
        f'grep_search with pattern="<search term>" path="{memory_dir}/../" glob="*.jsonl"',
        "```",
        "Use narrow search terms (error messages, file paths, function names) rather than broad keywords.",
        "",
    )


MEMORY_FRONTMATTER_EXAMPLE: tuple[str, ...] = (
    "```markdown",
    "---",
    "name: {{memory name}}",
    "description: {{one-line description used to decide relevance in future conversations}}",
    "type: {{user|feedback|project|reference}}",
    "---",
    "",
    "{{memory body}}",
    "```",
)


def memory_instructions(
    memory_dir: str = "",
    *,
    include_index_rules: bool = True,
    skip_index: bool = False,
) -> str:
    """Build the typed-memory behavioral instructions matching Claude Code's buildMemoryLines()."""
    dir_exists_guidance = (
        "This directory already exists — write to it directly with the file_write tool "
        "(do not run mkdir or check for its existence)."
    )
    lines = [
        "# auto memory",
        "",
        f"You have a persistent, file-based memory system at `{memory_dir}`. {dir_exists_guidance}"
        if memory_dir
        else "You have a persistent, file-based memory system.",
        "",
        "If the user explicitly asks you to remember something, save it immediately as whichever type fits best. If they ask you to forget something, find and remove the relevant entry.",
        "",
        "When responding to the user, never expose internal file paths, file names, or directory structures of the memory system. Describe actions in user-friendly terms instead.",
        "",
        *TYPES_SECTION,
        *WHAT_NOT_TO_SAVE_SECTION,
    ]
    if include_index_rules:
        if skip_index:
            lines.extend(
                (
                    "",
                    "## How to save memories",
                    "",
                    "Write each memory to its own file (e.g., `user_role.md`, `feedback_testing.md`) using this frontmatter format:",
                    "",
                    *MEMORY_FRONTMATTER_EXAMPLE,
                    "",
                    "- Organize memory semantically by topic, not chronologically",
                    "- Update or remove memories that turn out to be wrong or outdated",
                    "- Do not write duplicate memories. First check if there is an existing memory you can update before writing a new one.",
                )
            )
        else:
            lines.extend(
                (
                    "",
                    "## How to save memories",
                    "",
                    "Saving a memory is a two-step process:",
                    "",
                    "**Step 1** — write the memory to its own file (e.g., `user_role.md`, `feedback_testing.md`) using this frontmatter format:",
                    "",
                    *MEMORY_FRONTMATTER_EXAMPLE,
                    "",
                    "**Step 2** — add a pointer to that file in `MEMORY.md`. `MEMORY.md` is an index, not a memory — each entry should be one line, under ~150 characters: `- [Title](file.md) — one-line hook`. It has no frontmatter. Never write memory content directly into `MEMORY.md`.",
                    "",
                    "- `MEMORY.md` is always loaded into your conversation context — lines after 200 will be truncated, so keep the index concise",
                    "- Organize memory semantically by topic, not chronologically",
                    "- Update or remove memories that turn out to be wrong or outdated",
                    "- Do not write duplicate memories. First check if there is an existing memory you can update before writing a new one.",
                )
            )
    lines.extend(
        (
            "",
            *WHEN_TO_ACCESS_SECTION,
            "",
            *TRUSTING_RECALL_SECTION,
            "",
            *MEMORY_PERSISTENCE_SECTION,
            "",
        )
    )
    if memory_dir:
        lines.extend(build_searching_past_context_section(memory_dir))
    return "\n".join(lines)
