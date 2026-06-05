#!/usr/bin/env python3
"""Docker entrypoint for TelemetryFlow Hermes.

Sets up ~/.hermes/ from /app/ templates using environment variables.
All configuration is driven by env vars — the user only edits .env
next to docker-compose.yaml and runs `docker compose up -d`.

Usage (called by Docker ENTRYPOINT):
  docker-entrypoint.py          # configure + exec hermes
  docker-entrypoint.py --check  # validate env vars and exit
"""

import os
import shutil
import sys
from pathlib import Path

APP_DIR = Path("/app")
HERMES_HOME = Path.home() / ".hermes"

PROVIDER_MAP = {
    "anthropic": "anthropic",
    "openai": "openai",
    "google": "google",
    "gemini": "google",
    "deepseek": "deepseek",
    "qwen": "qwen",
    "ollama": "ollama",
    "mistral": "mistral",
    "groq": "groq",
    "grok": "grok",
    "kimi": "kimi",
    "zhipu": "opencode-go",
    "mimo": "mimo",
    "openrouter": "openrouter",
    "opencode-go": "opencode-go",
}

ENV_FORWARD_PREFIXES = (
    "TELEMETRYFLOW_",
    "ANTHROPIC_",
    "OPENAI_",
    "GOOGLE_",
    "GEMINI_",
    "DEEPSEEK_",
    "QWEN_",
    "ZHIPU_",
    "MISTRAL_",
    "GROQ_",
    "GROK_",
    "KIMI_",
    "MIMO_",
    "OPENROUTER_",
    "JIRA_",
    "TRELLO_",
    "TELEGRAM_",
    "CLICKHOUSE_",
    "LLM_",
    "KUBECONFIG",
)

PROFILES = ("triage", "investigator", "reviewer", "remediator")


def parse_model_env(raw):
    """Parse 'provider/model-name' from env var. Returns (model, provider)."""
    if "/" in raw:
        key, model = raw.split("/", 1)
    else:
        key, model = "zhipu", raw
    return model, PROVIDER_MAP.get(key, key)


def write_hermes_env():
    """Write ~/.hermes/.env from container environment variables."""
    lines = []
    for key, value in sorted(os.environ.items()):
        for prefix in ENV_FORWARD_PREFIXES:
            if key.startswith(prefix) or key == prefix:
                lines.append(f"{key}={value}")
                break
    env_file = HERMES_HOME / ".env"
    env_file.write_text("\n".join(lines) + "\n")
    return len(lines)


def copy_tree(src, dst):
    """Copy directory tree, overwriting existing files."""
    if dst.is_dir():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def write_profile_config(profile, model, provider):
    """Write profile config.yaml with model/provider substituted."""
    template = APP_DIR / "profiles" / profile / "config.yaml"
    if not template.exists():
        return False
    content = template.read_text()
    lines = content.split("\n")
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("default:"):
            out.append(f'  default: "{model}"')
        elif stripped.startswith("provider:"):
            out.append(f'  provider: "{provider}"')
        else:
            out.append(line)
    target = HERMES_HOME / "profiles" / profile / "config.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(out))
    return True


def write_default_config(model, provider):
    """Write ~/.hermes/config.yaml with model/provider substituted."""
    template = APP_DIR / "config.yaml"
    content = template.read_text()
    lines = content.split("\n")
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("default:"):
            out.append(f'  default: "{model}"')
        elif stripped.startswith("provider:"):
            out.append(f'  provider: "{provider}"')
        else:
            out.append(line)
    target = HERMES_HOME / "config.yaml"
    target.write_text("\n".join(out))


def configure():
    """Full configuration pass — sets up ~/.hermes/ from /app/ templates."""
    HERMES_HOME.mkdir(parents=True, exist_ok=True)

    default_model_raw = os.environ.get("HERMES_MODEL", "zhipu/glm-5.1")
    investigator_model_raw = os.environ.get("HERMES_INVESTIGATOR_MODEL", "anthropic/claude-sonnet-4-5")

    default_model, default_provider = parse_model_env(default_model_raw)
    inv_model, inv_provider = parse_model_env(investigator_model_raw)

    print(f"[hermes] Default model:    {default_model} via {default_provider}")
    print(f"[hermes] Investigator:     {inv_model} via {inv_provider}")

    write_default_config(default_model, default_provider)

    shutil.copy2(APP_DIR / "SOUL.md", HERMES_HOME / "SOUL.md")

    env_count = write_hermes_env()
    print(f"[hermes] .env:             {env_count} variables")

    copy_tree(APP_DIR / "skills", HERMES_HOME / "skills")
    copy_tree(APP_DIR / "plugins", HERMES_HOME / "plugins")
    copy_tree(APP_DIR / "cron", HERMES_HOME / "cron")

    hooks_dst = HERMES_HOME / "hooks"
    hooks_dst.mkdir(parents=True, exist_ok=True)
    for f in (APP_DIR / "hooks").glob("*.sh"):
        shutil.copy2(f, hooks_dst / f.name)
        (hooks_dst / f.name).chmod(0o755)

    for profile in PROFILES:
        profile_dir = HERMES_HOME / "profiles" / profile
        profile_dir.mkdir(parents=True, exist_ok=True)

        src_soul = APP_DIR / "profiles" / profile / "SOUL.md"
        if src_soul.exists():
            shutil.copy2(src_soul, profile_dir / "SOUL.md")

        mem_dir = profile_dir / "memories"
        mem_dir.mkdir(parents=True, exist_ok=True)
        src_mem = APP_DIR / "profiles" / profile / "memories"
        if src_mem.exists():
            for f in src_mem.glob("*.md"):
                shutil.copy2(f, mem_dir / f.name)

        if profile == "investigator":
            write_profile_config(profile, inv_model, inv_provider)
        else:
            write_profile_config(profile, default_model, default_provider)

    tool_count = len(list((HERMES_HOME / "plugins" / "telemetryflow" / "tools").glob("*.py")))
    skill_count = len(list((HERMES_HOME / "skills").rglob("SKILL.md")))
    print(f"[hermes] Profiles:         {len(PROFILES)} agents")
    print(f"[hermes] Skills:           {skill_count}")
    print(f"[hermes] Tools:            {tool_count}")
    print(f"[hermes] Hooks:            {len(list((HERMES_HOME / 'hooks').glob('*.sh')))}")
    print(f"[hermes] Cron jobs:        {'jobs.json' if (HERMES_HOME / 'cron' / 'jobs.json').exists() else 'none'}")


def check():
    """Validate required env vars and print diagnostics."""
    errors = []

    api_key = os.environ.get("TELEMETRYFLOW_API_KEY", "")
    auth_email = os.environ.get("TELEMETRYFLOW_AUTH_EMAIL", "")
    key_id = os.environ.get("TELEMETRYFLOW_KEY_ID", "")

    if not api_key and not auth_email and not key_id:
        errors.append("No auth method configured. Set TELEMETRYFLOW_API_KEY (Method A)")
        errors.append("  or TELEMETRYFLOW_AUTH_EMAIL + TELEMETRYFLOW_AUTH_PASSWORD (Method B)")
        errors.append("  or TELEMETRYFLOW_KEY_ID + TELEMETRYFLOW_KEY_SECRET (Method C)")

    api_url = os.environ.get("TELEMETRYFLOW_API_URL", "")
    if not api_url:
        errors.append("TELEMETRYFLOW_API_URL is not set")

    print(f"[hermes] API URL:          {api_url or '(not set)'}")
    print(
        f"[hermes] Auth method:      {'API Key' if api_key else 'JWT' if auth_email else 'Ingestion' if key_id else 'NONE'}"
    )
    print(f"[hermes] Environment:      {os.environ.get('TELEMETRYFLOW_ENVIRONMENT', '(not set)')}")

    if errors:
        print()
        for e in errors:
            print(f"[hermes] ERROR: {e}")
        return False

    print("[hermes] Configuration valid")
    return True


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        ok = check()
        sys.exit(0 if ok else 1)

    configure()

    cmd = os.environ.get("HERMES_CMD", "")
    if cmd:
        print(f"[hermes] Executing: {cmd}")
        os.execvp("/bin/sh", ["/bin/sh", "-c", cmd])
    else:
        print("[hermes] Ready. Set HERMES_CMD to run a command, or use interactively.")
        sys.exit(0)


if __name__ == "__main__":
    main()
