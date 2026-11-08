import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("data/audit.csv")
n0 = len(df)
df = df[~df.corrupt]
conflict = df.groupby("sha256")["class"].transform("nunique") > 1   # same image in both classes
df = df[~conflict]
df = df.drop_duplicates("sha256")
df = df[df.format.isin(["JPEG", "PNG", "BMP", "GIF", "MPO"])]          # formats TensorFlow can decode
print(f"Kept {len(df)} of {n0} files")

df["label"] = (df["class"] == "ai").astype(int)   # 1 = AI-generated, 0 = real
train, temp = train_test_split(df, test_size=0.30, stratify=df.label, random_state=42)
val, test = train_test_split(temp, test_size=0.50, stratify=temp.label, random_state=42)
for name, d in [("train", train), ("val", val), ("test", test)]:
    d[["path", "label"]].to_csv(f"splits/{name}.csv", index=False)
    print(name, len(d), d.label.value_counts().to_dict())