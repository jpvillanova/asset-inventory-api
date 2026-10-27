"""Popula o banco com ativos de exemplo (inclusive ativos web com URL).

Uso:
    python -m scripts.seed_demo
"""

from sqlmodel import Session, select

from app.database import create_db_and_tables, engine
from app.models import Asset, AssetStatus

DEMO_ASSETS = [
    {"name": "Portal Institucional", "category": "web", "status": AssetStatus.em_uso,
     "owner": "TI", "url": "https://example.com"},
    {"name": "API de Clientes", "category": "web", "status": AssetStatus.em_uso,
     "owner": "Dev", "url": "https://api.example.com"},
    {"name": "Notebook Dell Latitude", "category": "notebook",
     "status": AssetStatus.em_uso, "owner": "joao", "serial_number": "SN-001"},
    {"name": "Switch Cisco 24p", "category": "rede",
     "status": AssetStatus.em_estoque, "location": "Rack A"},
]


def main() -> None:
    create_db_and_tables()
    with Session(engine) as session:
        for data in DEMO_ASSETS:
            exists = session.exec(select(Asset).where(Asset.name == data["name"])).first()
            if not exists:
                session.add(Asset(**data))
        session.commit()
    print(f"Seed concluído: {len(DEMO_ASSETS)} ativos garantidos.")


if __name__ == "__main__":
    main()
