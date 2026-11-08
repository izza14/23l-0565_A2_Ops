import hashlib, os
import pandas as pd
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", None)
from PIL import Image

ROOT = "data/raw"
rows = []
for cls in sorted(os.listdir(ROOT)):
    for dirpath, _, files in os.walk(os.path.join(ROOT, cls)):
        for f in files:
            path = os.path.join(dirpath, f)
            data = open(path, "rb").read()
            row = {"path": path.replace("\\", "/"), "class": cls,
                   "size_kb": len(data) / 1024,
                   "sha256": hashlib.sha256(data).hexdigest(),
                   "width": None, "height": None, "mode": None, "format": None,
                   "corrupt": False}
            try:
                with Image.open(path) as im:
                    im.verify()                      # checks file integrity
                with Image.open(path) as im:         # reopen: verify() invalidates it
                    im.load()
                    row.update(width=im.width, height=im.height, mode=im.mode, format=im.format)
            except Exception:
                row["corrupt"] = True
            rows.append(row)

df = pd.DataFrame(rows)
df["duplicate"] = df.duplicated("sha256", keep="first")
df.to_csv("data/audit.csv", index=False)

print("Counts per class:\n", df["class"].value_counts())
ok = df[~df.corrupt]
print(ok.groupby("class")[["width", "height", "size_kb"]].agg(["min", "median", "max"]))
print("Colour modes:\n", ok.groupby(["class", "mode"]).size())
print("Formats:\n", ok.groupby(["class", "format"]).size())
print("Corrupt files:", df.corrupt.sum())
print("Exact duplicates:", df.duplicate.sum())
print("Duplicates across classes:", df[df.sha256.duplicated(keep=False)].groupby("sha256")["class"].nunique().gt(1).sum())