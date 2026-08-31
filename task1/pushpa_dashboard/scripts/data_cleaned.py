from pathlib import Path
import pandas as pd


# paths
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR /"src"/ "Data" / "raw"
PROCESSED_DIR = BASE_DIR /"src"/ "Data" / "processed"

train_info = pd.read_csv(RAW_DIR / "train_info.csv")
train_schedule = pd.read_csv(RAW_DIR / "train_schedule.csv")

# Remove leading/trailing spaces from text columns

for df in [train_info, train_schedule]:
    for column in df.select_dtypes(include="object"):
        df[column] = df[column].str.strip()



# Remove duplicate rows if they exist

train_info = train_info.drop_duplicates()
train_schedule = train_schedule.drop_duplicates()


# Keep numeric columns in the correct type

train_info["Train_No"] = pd.to_numeric(train_info["Train_No"])
train_schedule["Train_No"] = pd.to_numeric(train_schedule["Train_No"])
train_schedule["SN"] = pd.to_numeric(train_schedule["SN"])
train_schedule["Distance"] = pd.to_numeric(train_schedule["Distance"])


# Save cleaned files

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

train_info.to_csv(
    PROCESSED_DIR / "train_info_cleaned.csv",
    index=False
)

train_schedule.to_csv(
    PROCESSED_DIR / "train_schedule_cleaned.csv",
    index=False
)

print("Cleaning completed.")
print(f"Train info rows: {len(train_info)}")
print(f"Train schedule rows: {len(train_schedule)}")