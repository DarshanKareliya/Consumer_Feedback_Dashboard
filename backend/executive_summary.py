"""
Expects input in the shape your pipeline already produces after
category.categorize_negative_feedback(): a list of dicts each with at least
"text" and "issue_categories" (a list of issue label strings).
"""

import logging
from collections import defaultdict

from mlx_lm import generate

from review_filter_mlx import _get_model

log = logging.getLogger(__name__)

# caps prompt size for issues with many comments
MAX_COMMENTS_PER_ISSUE_IN_PROMPT = 20

SUMMARY_PROMPT_TEMPLATE = """You are writing an executive summary section of a customer feedback report for a product team. Below is negative customer feedback, grouped by issue category, with the number of comments in each category.

Write a professional executive summary with these requirements:
- One short paragraph per issue category, in order from most to least comments
- State the comment count for each category
- Summarize the recurring complaint in your own words, do not quote comments directly
- End each category's paragraph with one concrete recommended action
- Close with a 2-3 sentence overall summary across all categories
- Professional, concise tone suitable for a stakeholder report, no bullet points, no markdown headers

Feedback by category:

{issue_blocks}

Write the executive summary now."""


def build_issue_groups(negative_items):
    """
    Groups negative items by issue category. An item can appear under more
    than one category if issue_categories has multiple entries (multi-label).
    """
    groups = defaultdict(list)
    for item in negative_items:
        categories = item.get("issue_categories") or ["uncategorized"]
        for issue in categories:
            groups[issue].append(item["text"])
    return groups


def _format_issue_blocks(groups):
    blocks = []

    for issue, comments in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        sample = comments[:MAX_COMMENTS_PER_ISSUE_IN_PROMPT]
        comment_lines = "\n".join(f"- {c}" for c in sample)
        note = ""
        if len(comments) > MAX_COMMENTS_PER_ISSUE_IN_PROMPT:
            note = f"\n(showing {MAX_COMMENTS_PER_ISSUE_IN_PROMPT} of {len(comments)} total comments in this category)"
        blocks.append(
            f"## {issue} ({len(comments)} comments){note}\n{comment_lines}")
    return "\n\n".join(blocks)


def generate_executive_summary(negative_items, max_tokens=900):
    """
    negative_items: list of dicts with "text" and "issue_categories", as
    produced by category.categorize_negative_feedback().

    Returns the summary as a plain text string.
    """
    if not negative_items:
        return "No negative feedback in this batch."
    log.info("Getting quwen model for summery")

    model, tokenizer = _get_model()

    log.info("BUILDING ISSUE GROUPS")
    groups = build_issue_groups(negative_items)
    log.info("FORMATTING ISSUE BLOCKS")
    issue_blocks = _format_issue_blocks(groups)
    prompt_text = SUMMARY_PROMPT_TEMPLATE.format(issue_blocks=issue_blocks)

    messages = [{"role": "user", "content": prompt_text}]
    prompt = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True)

    log.info("Generating executive summary across %d issue categories, %d total negative comments.",
             len(groups), len(negative_items))

    summary = generate(model, tokenizer, prompt=prompt,
                       verbose=False, max_tokens=max_tokens)
    return summary.strip()


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     sample_negative_items = [
#         {"text": "Battery drains way too fast, barely lasts half a day.", "issue_categories": ["battery"]},
#         {"text": "Battery life is disappointing compared to what was advertised.", "issue_categories": ["battery"]},
#         {"text": "Screen has noticeable ghosting during fast motion.", "issue_categories": ["display"]},
#         {"text": "Customer support took three weeks to respond to my ticket.", "issue_categories": ["support"]},
#         {"text": "Fan noise is very loud even under light load.", "issue_categories": ["thermals"]},
#     ]
#     print(generate_executive_summary(sample_negative_items))
