import psutil
import os

my_pid = os.getpid()
killed = []
for p in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmdline = p.info.get('cmdline') or []
        cmd_str = " ".join(cmdline)
        if 'bot.py' in cmd_str and p.info['pid'] != my_pid:
            p.kill()
            killed.append(p.info['pid'])
    except Exception:
        pass

print(f"Killed PIDs: {killed}")
