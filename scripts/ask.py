#!/bin/env python

from openai import OpenAI
import os, sys

maximum_tokens = 65536
source_code = ""
user_prompt = ""
system_prompt = ""
llm_access = ""
llm_baseurl = "https://api.deepseek.com"

def usage():
    bin = os.path.basename(sys.argv[0])
    print(f"{bin}: <content_prompt> <system_prompt>")
    print(f"")
    exit(1)

# Args
user_prompt_path = ""
system_prompt_path = ""

# sanitize inputs
if len(sys.argv) < 3:
    print(f"ERROR: insufficient arguments {len(sys.argv)}")
    usage()

# extract args
user_prompt_path  = os.path.realpath(sys.argv[1])
system_prompt_path   = os.path.realpath(sys.argv[2])
logpath = "../test-logs.md"

print(f"Using paths:")
print(f"System prompt path: {system_prompt_path}")
print(f"User prompt path: {user_prompt_path}")

with open(system_prompt_path, "r+") as file:
    system_prompt = file.read()
with open(user_prompt_path, "r+") as file:
    user_prompt = file.read();

if ('LLM_KEY' in os.environ):
    llm_access = os.environ['LLM_KEY']
if ("LLM_BASEURL" in os.environ):
    llm_baseurl = os.environ['LLM_BASEURL']

client = OpenAI(api_key=llm_access, base_url=llm_baseurl)

res = client.chat.completions.create(
        model = "deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            ],
        temperature=0,
        stream=False,
        );
# Finetuning: temperature 0 for best code analysis performance

# print(f"{len(res.choices)}::{res.choices}")
response = res.choices[0].message.content

print("-------------------------")
print(response)

with open(logpath, "a+") as file:
    file.write("\n\n----------\n\n");
    file.write(response)
