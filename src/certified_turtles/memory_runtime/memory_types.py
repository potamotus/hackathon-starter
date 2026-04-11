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


def memory_instructions(include_index_rules: bool = True) -> str:
    lines = [
        "# session_guidance",
        "You have a Claude-like persistent memory system and session memory system.",
        "",
        *WHEN_TO_ACCESS_SECTION,
        "",
        *TRUSTING_RECALL_SECTION,
        "",
        *TYPES_SECTION,
        *WHAT_NOT_TO_SAVE_SECTION,
    ]
    if include_index_rules:
        lines.extend(
            (
                "",
                "## How to save memories",
                "",
                "Write each memory to its own topic file using the documented frontmatter format.",
                "",
                *MEMORY_FRONTMATTER_EXAMPLE,
                "",
                "MEMORY.md is an index, not a dump. Each line should be a compact pointer to a topic file. Keep MEMORY.md concise because lines after 200 and bytes after ~25KB are not guaranteed to stay visible.",
                "- Organize memory semantically by topic, not chronologically.",
                "- Update existing files instead of creating near-duplicates.",
                "- Remove or correct memories that become wrong or outdated.",
            )
        )
    return "\n".join(lines)
