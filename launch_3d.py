"""
launch_3d.py - Local launcher for Shadows of Eldoria 3D.
Starts a local web server and automatically opens the game in your default browser.
"""

import http.server
import os
import socketserver
import sys
import webbrowser

PORT = 8000

# Reconfigure stdout/stderr for Windows UTF-8
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def launch():
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)

    # Find open port
    port = PORT
    handler = http.server.SimpleHTTPRequestHandler

    # Try binding to port
    for p in range(PORT, PORT + 20):
        try:
            httpd = socketserver.TCPServer(("", p), handler)
            port = p
            break
        except OSError:
            continue
    else:
        print("[!] Could not bind to ports 8000-8020. Opening index.html directly...")
        webbrowser.open(os.path.join(web_dir, "index.html"))
        return

    url = f"http://localhost:{port}/index.html"
    print("\n" + "=" * 60)
    print("  ⚔️  SHADOWS OF ELDORIA 3D - LOCAL SERVER RUNNING  ⚔️")
    print("=" * 60)
    print(f"\n  Game URL:    {url}")
    print("  Controls:    WASD (Move), Mouse (Look), Left Click (Sword)")
    print("               Right Click / E (Fireball), Space (Jump), Q (Potion)")
    print("\n  Opening in your default browser now...")
    print("  (Press Ctrl+C in this terminal when finished to stop)\n")

    webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[+] 3D Server stopped. Farewell, adventurer!\n")


if __name__ == "__main__":
    launch()
