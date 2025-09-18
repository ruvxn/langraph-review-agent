import pandas as pd
from typing import List
from src.utils import RawReview

#check schema for required columns
REQUIRED = {"review_id","review","username","email","date","reviewer_name","rating"}


def load_reviews(path: str) -> List[RawReview]:
    df = pd.read_csv(path)
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

# convert row from csv to model
    records: List[RawReview] = []
    for _, row in df.iterrows():
        records.append(
            RawReview(
                review_id=str(row["review_id"]),
                review=str(row["review"]),
                username=str(row["username"]),
                email=str(row["email"]),
                date=str(row["date"]),
                reviewer_name=str(row["reviewer_name"]),
                rating=int(row["rating"]),
            )
        )
    return records
