from core.database import db
from core.models import ProductTask, Review
import sqlalchemy as sa

# Проверим структуру таблиц
engine = db.engine
inspector = sa.inspect(engine)

print('=== ProductTask columns ===')
for column in inspector.get_columns('product_tasks'):
    print(f'{column["name"]}: {column["type"]}')

print()
print('=== Review columns ===')
for column in inspector.get_columns('reviews'):
    print(f'{column["name"]}: {column["type"]}')
