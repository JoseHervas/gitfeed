## Overview

🚀 **GitFeed** is a tool that transforms any GitHub repository into a txt file you can feed to any LLM like ChatGPT, DeepSeek, Gemini, Claude Sonnet, etc... 

## Usage

```bash
# Basic
python gitfeed.py https://github.com/user/repo.git

# Excluding some files by extension
python gitfeed.py https://github.com/user/repo.git --exclude-ext .log .tmp

# Excluding some files by size (in MB)
python gitfeed.py https://github.com/user/repo.git --max-file-size 5
```

## Common Questions

_Q: What's the difference between this and [gitingest](https://github.com/cyclotruc/gitingest)?_

Up to today (07/02/2025) Gitingest doesn't support private repos. This tool is local so as long as you have access to the repo, this tool does so too.

