# after appending the tool result, if it's a big read_file result,
# replace older large tool results with a short placeholder before the next call
def trim_history(messages, max_keep_full=1):
    tool_indices = [i for i, m in enumerate(messages) if m.get("role") == "tool"]
    for i in tool_indices[:-max_keep_full]:  # keep only the most recent few full
        if len(messages[i]["content"]) > 300:
            messages[i]["content"] = f"[trimmed, was {len(messages[i]['content'])} chars]"
    return messages
