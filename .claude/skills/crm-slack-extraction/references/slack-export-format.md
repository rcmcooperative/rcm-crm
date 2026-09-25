# Slack Standard Export — file structure

Reference for `crm-slack-extraction`. Covers only what a Slack Standard
Export (public channels only — the current RCM Cooperative Free-tier
export type) actually contains. This is a self-contained copy for this
skill; if a private-channel export type is added later, this file will
need a second section for that format.

## Top-level contents of the export ZIP

- `users.json` — full workspace member directory (see below). This is
  NOT scoped to public-channel activity — it lists every workspace
  member regardless of which channels they've posted in.
- `channels.json` — public channel directory (see below).
- One folder per public channel, named after the channel, each
  containing one JSON file per day messages were sent
  (`YYYY-MM-DD.json`). No folder exists for a date with no activity.

## `users.json`

An array of one object per workspace member. Fields this skill uses:

- `id` — the stable identifier referenced by every message's `user`
  field. Never match on name — always match on this ID first, falling
  back to name/email only when resolving a candidate People match.
- `name` — the Slack username/handle.
- `real_name` — the person's stated real name.
- `deleted` — `true` for deactivated accounts. `parse_slack_export.py`
  filters these out entirely; a deleted user is never a candidate
  participant.
- `is_bot` — flags bot/app accounts. Also filtered out entirely.
- `profile.email` — the matching key for resolving to an existing
  People row.
- `profile.display_name` — UI display name, may differ from
  `real_name`. Prefer `real_name` when both are present.

## `channels.json`

An array of one object per public channel:

- `id`, `name`
- `created` — Unix timestamp of channel creation.
- `creator` — user ID of whoever created it.
- `is_archived`
- `topic.value` / `purpose.value` — free text, useful context for
  Step 2's channel-to-entity mapping decision.
- `members` — array of user IDs currently in the channel. This is
  what "membership = participant" reads from (see SKILL.md Step 1) —
  note it's current membership at export time, not membership at any
  particular point during the messages being read.

## Per-day message files

Each day's file is a JSON array of message objects. Fields this skill
uses:

- `type` — almost always `"message"`. Anything else is not a
  contribution and is skipped.
- `subtype` — flags non-standard messages (`channel_join`,
  `channel_leave`, `bot_message`, topic/purpose changes, pin/unpin
  events, etc.). `parse_slack_export.py` excludes all of these from
  activity counts — a join/leave notice is not a contribution. See
  `NON_CONTRIBUTION_SUBTYPES` in the script for the exact list.
- `user` — the author's user ID (matches `users.json`). A message with
  no `user` field (some subtypes/system messages) can't be attributed
  to anyone and is skipped for per-user counting, though its
  timestamp still counts toward the channel's date range.
- `text` — message content, in Slack's own markup (e.g. `<@U12345>`
  for mentions, not resolved to names). Used only for the Step 4
  summarisation step, never for counting.
- `ts` — a timestamp string that also serves as the message's unique
  ID. Used for `date-started`/`date-last-activity` and to identify
  thread parents (see below).
- `thread_ts` — present only on messages that are part of a thread;
  equals the parent message's own `ts`. A thread's PARENT message has
  `thread_ts == ts`; a reply has `thread_ts` pointing at a different,
  earlier `ts`.
- `reply_count` — present on thread-parent messages only. Gives the
  total number of replies that thread received — this is the
  "replies received" signal attributed to the thread's starter.
- `reactions` — array of `{name, users, count}` objects, present only
  if the message got at least one reaction. Sum `count` across a
  user's messages for the "reactions received" signal.
- `files` — array of file metadata and links only. Standard Export
  never includes file contents, only links back to the workspace.

## What's structurally absent, not filtered

- No edit history or deletion logs. An edited message appears only in
  its final edited form; a deleted message doesn't appear at all.
  There's no way to detect either from this export.
- No private channel or DM content, and no canvases outside public
  channels — this is the defining limit of a Standard Export, not
  something this skill works around.

## Known limitations this skill inherits from the format

- `reply_count` reflects the state of the thread at whatever moment
  the day-file containing the parent message was generated — later
  replies (on later dates) update the count on re-export, but this
  skill only ever reads one export snapshot, so a "replies received"
  count reflects that snapshot, not necessarily the thread's eventual
  total if activity continues after the export date range.
- A user who left the channel before export time won't appear in
  `channels.json`'s `members`, even if they posted messages during
  the export window — their messages are still counted in
  `lead-signals-<name>.csv`, but they won't be added to
  `people-participants` under the membership-based rule. Worth
  knowing this can happen; not something the script currently flags
  separately.
