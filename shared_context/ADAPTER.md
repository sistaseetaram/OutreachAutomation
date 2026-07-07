# OutreachAutomation — Shared Context Adapter

## What this is

A pointer to the cross-project shared context store in SharedInfra. OutreachAutomation is the **write authority for leads** and a **reader of published content and brand voice**.

## Store location

```
/Users/sistaseetaram/Desktop/Claude/SharedInfra/shared_context/
  shared_context.py   ← accessor module (pure stdlib)
  store.json          ← live data (JSON, human-readable)
  schema.json         ← documented schema with field descriptions
```

## How to use from this project

```python
import sys
sys.path.insert(0, "/Users/sistaseetaram/Desktop/Claude/SharedInfra/shared_context")
from shared_context import (
    read_brand_voice,          # read: brand voice (replaces the embedded copy in setu_voice.py)
    read_icp,                  # read: ICP definition (pains, products, outreach rule)
    write_lead,                # WRITE: sync a lead record from lead_tracker.py
    read_published_posts,      # read: see what ContentGenerator has publicly stated
    link_lead_to_content,      # write: record that a post was sent as social proof to a lead
)
```

## Authority table

| Data type        | OutreachAutomation | ContentGenerator |
|------------------|-------------------|------------------|
| brand_voice      | read              | read             |
| icp              | read              | read             |
| leads            | **WRITE**         | read only        |
| published_content| **READ ONLY**     | write            |
| cross_references | write             | write            |

## When to call write_lead

After adding or updating a lead in `lead_tracker.py` (`.tmp/leads.json`), sync it to the store:

```python
from shared_context import write_lead

lead = {
    "studio": "Nine Bricks Studio",
    "founder": "Manjusha",
    "segment": "architecture",
    "track": "warm",
    "city": "Bengaluru",
    "status": "Follow-up 1",
    "source": "referral",
    "last_touch": "2026-06-02",
}
write_lead(lead, written_by="OutreachAutomation")
```

## Replacing the embedded voice copy in setu_voice.py

`tools/setu_voice.py` currently embeds brand voice inline. The comment in that file already says "If the wiki changes, update this file" — meaning it is a known manual-sync risk. The preferred path:

```python
# In setu_voice.py (or any tool that needs voice rules):
import sys
sys.path.insert(0, "/Users/sistaseetaram/Desktop/Claude/SharedInfra/shared_context")
from shared_context import read_brand_voice

bv = read_brand_voice()
FORBIDDEN_WORDS = bv.get("forbidden_words", [])
VALUES = bv.get("values", [])
POSITIONING = bv.get("positioning", "")
```

Do this migration gradually — do not break existing tools. Keep `setu_voice.py` working as a fallback until the migration is tested.

## Using published content in outreach

Before drafting an outreach message, check what proof has been publicly stated:

```python
from shared_context import read_published_posts

posts = read_published_posts(platform_filter="linkedin")
# Use post hooks + proof points as social proof references in outreach
```

This prevents claiming things in a private message that contradict what has been said publicly, and lets you reference a live post URL.

## CLI quick-check

```bash
cd /Users/sistaseetaram/Desktop/Claude/SharedInfra/shared_context
python shared_context.py status        # counts + last-write metadata
python shared_context.py brand-voice   # print voice snapshot
python shared_context.py leads         # print all leads
python shared_context.py posts         # print all published posts
```
