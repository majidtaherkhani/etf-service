import sys
import csv
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from configs.db.postgresql import SessionLocal
from src.modules.market_data.repository import MarketDataRepository
from src.modules.market_data.models import SecurityPrice


def read_csv_and_transform(csv_path: str) -> list[SecurityPrice]:
    prices = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        tickers = [col for col in reader.fieldnames if col != 'DATE']
        for row in reader:
            try:
                date = datetime.strptime(row['DATE'], '%Y-%m-%d')
                for ticker in tickers:
                    price_str = row.get(ticker, '').strip()
                    if price_str:
                        prices.append(SecurityPrice(
                            date=date,
                            ticker=ticker,
                            price=float(price_str)
                        ))
            except (ValueError, KeyError):
                continue
    return prices


if __name__ == "__main__":
    csv_file = Path(__file__).parent.parent / "sample-data" / "bankofmontreal-prices.csv"
    if not csv_file.exists():
        print(f"Error: CSV file not found at {csv_file}")
        sys.exit(1)
    
    prices = read_csv_and_transform(str(csv_file))
    print(f"Loaded {len(prices)} records")
    
    db = SessionLocal()
    try:
        repo = MarketDataRepository(db)
        repo.bulk_save_prices(prices)
        print(f"Inserted {len(prices)} records")
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        db.close()
