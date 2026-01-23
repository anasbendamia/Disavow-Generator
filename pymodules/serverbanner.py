# pymodules/serverbanner.py
# Copyright (c) 2026 Banshee (https://www.banshee.pro)
# License: AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

VERSION = "1.0.0"

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_BLUE = "\033[44m"


def print_banner(port: int, mode: str, workers: int = None, using_default_credentials: bool = False):
    c = Colors

    banner = f"""
{c.CYAN}{c.BOLD}
    ____  _
   / __ \\(_)_______   __  ______  _      __
  / / / / / ___/ __ `/ | / / __ \\| | /| / /
 / /_/ / (__  ) /_/ /| |/ / /_/ /| |/ |/ /
/_____/_/____/\\__,_/ |___/\\____/ |__/|__/
{c.RESET}{c.DIM}         Generator v{VERSION}{c.RESET}
"""

    print(banner)
    print(f"  {c.DIM}{'─' * 44}{c.RESET}")
    print()
    print(f"  {c.CYAN}●{c.RESET} Mode      {c.BOLD}{mode}{c.RESET}")
    print(f"  {c.CYAN}●{c.RESET} Port      {c.BOLD}{port}{c.RESET}")
    if workers and mode == "Production":
        print(f"  {c.CYAN}●{c.RESET} Workers   {c.BOLD}{workers}{c.RESET}")
    print()
    print(f"  {c.DIM}{'─' * 44}{c.RESET}")
    print()

    if using_default_credentials:
        print(f"  {c.YELLOW}{c.BOLD}⚠  Default credentials:{c.RESET}")
        print()
        print(f"     Username: {c.BOLD}user{c.RESET}")
        print(f"     Password: {c.BOLD}passwd{c.RESET}")
        print()
        print(f"  {c.DIM}   Change them in Settings after login!{c.RESET}")
        print()
        print(f"  {c.DIM}{'─' * 44}{c.RESET}")
        print()

    print(f"  {c.GREEN}▶{c.RESET} Server running at {c.BOLD}{c.CYAN}http://localhost:{port}{c.RESET}")
    print()
    print(f"  {c.DIM}Press Ctrl+C to stop{c.RESET}")
    print()
