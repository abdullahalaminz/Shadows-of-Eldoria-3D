"""
utils.py - Terminal formatting, ANSI colors, ASCII banners, and UI helpers.
"""

import os
import sys
import time

# Reconfigure stdout/stderr to UTF-8 on Windows to prevent cp1252 encoding crashes
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Enable ANSI colors on Windows consoles
if os.name == "nt":
    os.system("")


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright foreground colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Backgrounds
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def clear_screen():
    """Clear terminal console safely."""
    os.system("cls" if os.name == "nt" else "clear")


def slow_print(text: str, delay: float = 0.012, newline: bool = True):
    """Print text with a typewriter effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    if newline:
        sys.stdout.write("\n")
        sys.stdout.flush()


def pause(prompt: str = "\nPress [ENTER] to continue..."):
    """Pause execution until user presses Enter."""
    input(f"{Colors.DIM}{prompt}{Colors.RESET}")


def colorize(text: str, color: str) -> str:
    """Wrap text in an ANSI color."""
    return f"{color}{text}{Colors.RESET}"


def render_bar(current: int, maximum: int, length: int = 20, fill_color: str = Colors.GREEN, empty_color: str = Colors.BRIGHT_BLACK) -> str:
    """Render a visual health or mana progress bar."""
    current = max(0, min(current, maximum))
    if maximum <= 0:
        fill_count = 0
    else:
        fill_count = int((current / maximum) * length)
    empty_count = length - fill_count
    bar = f"{fill_color}{'█' * fill_count}{empty_color}{'░' * empty_count}{Colors.RESET}"
    return f"[{bar}] {current}/{maximum}"


def print_box(lines: list[str], title: str = "", border_color: str = Colors.CYAN, width: int = 65):
    """Draw a decorative UI box around text lines."""
    top_border = f"╭{'─' * 2} {title} {'─' * max(0, width - len(title) - 6)}╮" if title else f"╭{'─' * (width - 2)}╮"
    bot_border = f"╰{'─' * (width - 2)}╯"

    print(f"{border_color}{top_border}{Colors.RESET}")
    for line in lines:
        stripped = ""
        in_esc = False
        for c in line:
            if c == "\033":
                in_esc = True
            elif in_esc and c == "m":
                in_esc = False
            elif not in_esc:
                stripped += c
        
        pad_size = max(0, width - 4 - len(stripped))
        print(f"{border_color}│{Colors.RESET} {line}{' ' * pad_size} {border_color}│{Colors.RESET}")
    print(f"{border_color}{bot_border}{Colors.RESET}")


def get_menu_choice(prompt: str, valid_choices: list[str]) -> str:
    """Prompt user until a valid choice is entered."""
    valid_lower = [c.lower() for c in valid_choices]
    while True:
        choice = input(f"{Colors.BRIGHT_YELLOW}{prompt}{Colors.RESET} ").strip().lower()
        if choice in valid_lower:
            return choice
        print(f"{Colors.RED}Invalid selection! Please choose one of: {', '.join(valid_choices)}{Colors.RESET}")


TITLE_BANNER = (
    Colors.BRIGHT_MAGENTA
    + """
  ╔═══════════════════════════════════════════════════════════════════════════╗
  ║    _____ _   _   ___  ______ _____  _    _ _____   ___________ _____    ║
  ║   /  ___| | | | / _ \\ |  _  \\  _  || |  | /  ___| |  _  |  ___|  ___|   ║
  ║   \\ `--.| |_| |/ /_\\ \\| | | | | | || |  | \\ `--.  | | | | |_  | |__     ║
  ║    `--. \\  _  ||  _  || | | | | | || |/\\| |`--. \\ | | | |  _| |  __|    ║
  ║   /\\__/ / | | || | | || |/ /\\ \\_/ /\\  /\\  /\\__/ / \\ \\_/ / |   | |___    ║
  ║   \\____/\\_| |_/\\_| |_/|___/  \\___/  \\/  \\/\\____/   \\___/\\_|   \\____/    ║
  ║                                                                           ║
  ║                     E L D O R I A ' S   C R Y P T                         ║
  ╚═══════════════════════════════════════════════════════════════════════════╝"""
    + Colors.RESET
)

SKULL_ART = (
    Colors.BRIGHT_RED
    + """
                   .---.
                  /     \\
                 | () () |
                  \\  ^  /
                   |||||
                   '---'"""
    + Colors.RESET
)

SWORD_ART = (
    Colors.BRIGHT_CYAN
    + """
                 /| ________________
  O|===|* >_____/ |                /
                 \\| ________________/"""
    + Colors.RESET
)

TREASURE_ART = (
    Colors.BRIGHT_YELLOW
    + """
             .----------------.
            /  _   _   _   _   \\
           |  (o) (o) (o) (o)   |
           |    [=== GOLD ===]  |
           '--------------------'"""
    + Colors.RESET
)
