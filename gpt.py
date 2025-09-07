#!/usr/bin/env python3
import os
import sys
import json
import readline
import requests
from pathlib import Path

# Terminal colors
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

# Load API key from ~/.config/chatgpt.env if present
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    print(f"{RED}Error:{RESET} OPENAI_API_KEY not set in ~/.config/chatgpt.env")
    sys.exit(1)

print(f"{YELLOW}ChatGPT Streaming Assistant (type 'exit' to quit){RESET}\n")

history = []

def stream_chat(messages):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "stream": True,
    }
    with requests.post(url, headers=headers, json=data, stream=True) as resp:
        buffer = ""
        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            payload = line[6:]
            if payload == "[DONE]":
                break
            try:
                chunk = json.loads(payload)
                content = (
                    chunk.get("choices", [{}])[0]
                        .get("delta", {})
                        .get("content", "")
                )
                if content:
                    print(f"{content}", end="", flush=True)
                    buffer += content
            except Exception:
                continue
        return buffer

try:
    while True:
        try:
            prompt = input(f"{GREEN}> {RESET}")
        except EOFError:
            print()
            break
        if prompt.strip() == "":
            continue
        if prompt.strip().lower() == "exit":
            break

        messages = []
        for entry in history:
            messages.append(entry)
        messages.append({"role": "user", "content": prompt})

        print(f"{GREEN}ChatGPT>{CYAN} ", end="", flush=True)
        response = stream_chat(messages)
        print(f"{RESET}",end="", flush=True)

        if response.strip():
            print()
            history.append({"role": "user", "content": prompt})
            history.append({"role": "assistant", "content": response})
            print()
except KeyboardInterrupt:
    print(f"\n{RESET}")
