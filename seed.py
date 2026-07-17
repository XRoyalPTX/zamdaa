import csv
import asyncio
from sqlalchemy import insert

from app.database import async_session_local 
from app.models import Location

async def seed_buryatia_locations():
    buryatia_locations = []
    file_path = "data/settlements.csv"
    
    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=';')
            
            for row in reader:
                if row["region"] == "Республика Бурятия":
                    settlement_type = row["type"]
                    settlement_name = row["settlement"]
                    
                    full_name = f"{settlement_type}. {settlement_name}" if settlement_type else settlement_name
                    
                    buryatia_locations.append({
                        "country": "Россия",
                        "region": "Республика Бурятия",
                        "district": row["municipality"],  
                        "name": full_name
                    })
                    
    except FileNotFoundError:
        print(f"Ошибка: Не удалось найти файл по пути {file_path}")
        return

    if buryatia_locations:
        print(f"Найдено {len(buryatia_locations)} населенных пунктов Бурятии. Заливаем в базу...")
        
        async with async_session_local() as db:
            await db.execute(insert(Location), buryatia_locations)
            await db.commit()
            
        print("База данных Joloo успешно наполнена локациями!")
    else:
        print("В файле не найдено локаций с регионом 'Республика Бурятия'.")

if __name__ == "__main__":
    asyncio.run(seed_buryatia_locations())