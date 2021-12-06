"""
WARNING: extremely bad code - do not try this at home
"""

import fastapi as fa
from starlette.middleware import cors
import databases

LOCAL_SETUP = True
DOMAIN = "localhost"
PROJECT_NAME = "ilyanaapp"
BACKEND_CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8000",
]
DATABASE_URI = "sqlite:///./main.db"


app = fa.FastAPI(
    title=PROJECT_NAME,
    debug=LOCAL_SETUP,
)

if BACKEND_CORS_ORIGINS:
    app.add_middleware(
        cors.CORSMiddleware,
        allow_origins=[str(origin) for origin in BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

db = databases.Database(DATABASE_URI)


@app.on_event("startup")
async def startup():
    await db.connect()

    queries = []

    queries.append(
        """--sql
        create table if not exists artist (
            id integer primary key autoincrement not null,
            name varchar(255),
            born integer,
            died integer
        );
    """
    )

    queries.append(
        """--sql
        create table if not exists country (
            id integer primary key autoincrement not null,
            name varchar(255) NOT NULL UNIQUE
        );
    """
    )

    queries.append(
        """--sql
        create table if not exists city (
            id integer primary key autoincrement not null,
            name varchar(255),
            countryId integer,
            FOREIGN KEY(countryId) REFERENCES country(id)
        );
    """
    )

    queries.append(
        """--sql
        create table if not exists place (
            id integer primary key autoincrement not null,
            name varchar(255),
            foundationDate integer, -- select datetime(1092941466, 'unixepoch');
            cityId integer,
            FOREIGN KEY(cityId) REFERENCES city(id)
        );
    """
    )

    queries.append(
        """--sql
        create table if not exists category (
            id integer primary key autoincrement not null,
            name varchar(255)
        );
    """
    )

    queries.append(
        """--sql
        create table if not exists item (
            id integer primary key autoincrement not null,
            name varchar(255),
            creationDate integer,
            categoryId integer references category(id) not null,
            placeId integer references place(id) not null,
            artistId integer references artist(id) not null
        );
    """
    )

    queries.append(
        """--sql
        create table if not exists artistCountry (
            id integer primary key autoincrement not null,
            countryId integer references country(id) not null,
            artistId integer references artist(id) not null
        );
    """
    )

    for query in queries:
        print(query)
        await db.execute(query=query)

    # Insert some data.
    query = "INSERT INTO country(name) VALUES (:name)"
    values = [
        {"name": "United States"},
        {"name": "United Kingdom"},
    ]
    try:
        await db.execute_many(query=query, values=values)
    except:
        pass


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()


api = fa.APIRouter()

tables = ["artist", "country", "city", "place", "category", "item"]

for table in tables:
    multi_handler = (
        f'@api.get("/{table}")\n'
        + f"async def read_{table}s():\n"
        + f'\treturn await db.fetch_all("SELECT * FROM {table}")'
    )
    exec(multi_handler)

    id_handler = (
        f'@api.get("/{table}'
        + '/{id}")\n'
        + f"async def read_single_{table}(id: int):\n"
        + f'\tquery = "SELECT * FROM {table} WHERE id = :id;"\n'
        + '\treturn await db.fetch_one(query=query, values={"id": id})'
    )
    exec(id_handler)

    post_handler = (
        f'@api.post("/{table}")\n'
        + f'async def post_{table}():\n'
        + f'\tquery = "INSERT INTO {table}(text, completed) VALUES (:text, :completed);"\n'
        + '\treturn await db.fetch_one(query=query, values={"id": id})'
    )

    put_handler = (
        f''
    )

    delete_handler = (
        f'@api.delete("/{table}")\n'
        + f'async def delete_{table}(id: int):\n'
        + f'\tquery = "delete from {table} where id = :id;"\n'
        + '\tawait db.execute(query=query, values={"id": id})\n'
        + '\treturn "All good"'
    )

# @api.get("/country")
# async def read_countries():
#     return await db.fetch_all("SELECT * FROM country")

# @api.post("/item")
# async def create_item():
#     return None

app.include_router(api, prefix="/api")
