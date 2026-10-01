import pygetwindow as gw

windows = gw.getAllWindows()
print("SEARCHING FOR GOOGLE FLOW WINDOW:")
for w in windows:
    t = w.title.strip()
    if t:
        if any(k in t.lower() for k in ["flow", "chrome", "google"]):
            print(f"FOUND: '{t}' at ({w.left}, {w.top}, {w.width}, {w.height})")
