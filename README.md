![alt text](<logo.webp>)
# GitHub Shortname Wordlist Generator

This script automates the process of fetching potential file and directory names based on partial names output by a shortscanning tool for Microsoft IIS Tilde vulnerability. It uses a Selenium-driven Chrome browser to perform searches on GitHub.

## Features

- Works on Linux, macOS and Windows.
- Uses a dedicated Chrome profile for authenticated GitHub searches (no need to close Chrome).
- Supports MFA-based GitHub login.
- Filter results by file extension.
- Supports silent mode to suppress banner output.

## Requirements

- [Python 3.x](https://www.python.org/downloads/)
- [Google Chrome](https://www.google.com/chrome/)
- [selenium](https://pypi.org/project/selenium/) (4.6+)

## Installation

1. Clone the repository:
```sh
git clone https://github.com/chrismeistre/gsnw.git
cd gsnw
```

2. Create a virtual environment:
```sh
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\Activate
```

3. Install dependencies:
```sh
pip install -r requirements.txt
```

## Setup

Before your first search, log into GitHub:

```sh
python gsnw.py --login
```

This opens a Chrome window where you can sign in (including MFA). The session is saved to a dedicated profile and persists between runs — you only need to do this once.

## Usage

```sh
python gsnw.py <search_query> [output_file] [-silent] [-e EXT]
```

| Argument | Description |
|---|---|
| `search_query` | The partial name to search for on GitHub |
| `output_file` | (Optional) File to save results to, one per line |
| `-silent` | (Optional) Suppress the banner |
| `-e`, `--ext` | (Optional) Filter results by file extension |
| `--login` | Open a browser to log into GitHub |

## Examples

Basic search:
```sh
python gsnw.py admin
```

Search with file extension filter:
```sh
python gsnw.py admin -e aspx
```

Save results to a file in silent mode:
```sh
python gsnw.py sapmai output.txt -silent
```

Combine extension filter with file output:
```sh
python gsnw.py admin -e config output.txt -silent
```

## Important Notes

- Run `--login` once before your first search. If your session expires, the script will tell you to log in again.
- The script runs in headless mode by default.
- A dedicated Chrome profile is stored at `~/.config/gsnw/chrome-profile`, separate from your main browser profile.

## Disclaimer

This script is provided "as is" without any warranties. Use it at your own risk.

## Socials
Find me on X (Twitter) [@retkoussa](https://x.com/retkoussa)
