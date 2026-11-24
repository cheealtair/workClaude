import sys
from pathlib import Path
import win32com.client

pptx = str(Path(sys.argv[1]).resolve())
jobs = []
for arg in sys.argv[2:]:
    num, out = arg.split("=", 1)
    jobs.append((int(num), str(Path(out).resolve())))
app = win32com.client.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(pptx, True, False, False)
try:
    print("slides", pres.Slides.Count)
    for num, out in jobs:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        pres.Slides(num).Export(out, "PNG", 1920, 1080)
        print("wrote", out)
finally:
    pres.Close()
    app.Quit()
