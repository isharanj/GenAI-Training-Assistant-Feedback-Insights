"""Thin LLM wrapper so the provider can be swapped to whatever your company approves."""
from . import config


def complete(prompt: str, system: str | None = None, max_tokens: int | None = None) -> str:
    """Send a prompt to the configured provider and return the text reply."""
    max_tokens = max_tokens or config.MAX_TOKENS
    provider = config.LLM_PROVIDER

    if provider == "anthropic":
        import anthropic

        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
        model = config.LLM_MODEL or "claude-haiku-5-5"
        kwargs = {"system": system} if system else {}
        msg = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return "".join(b.text for b in msg.content if b.type == "text").strip()

    if provider in ("openai", "azure_openai"):
        from openai import AzureOpenAI, OpenAI

        client = AzureOpenAI() if provider == "azure_openai" else OpenAI()
        model = config.LLM_MODEL or "gpt-4o-mini"  # for Azure this is the deployment name
        messages = ([{"role": "system", "content": system}] if system else []) + [
            {"role": "user", "content": prompt}
        ]
        resp = client.chat.completions.create(
            model=model, messages=messages, max_tokens=max_tokens, temperature=0
        )
        return resp.choices[0].message.content.strip()

    raise ValueError(f"Unknown LLM_PROVIDER: {provider}")
