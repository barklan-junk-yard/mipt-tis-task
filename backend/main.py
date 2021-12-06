"""
WARNING: extremely bad code - do not try this at home
"""

import fastapi as fa
from fastapi.responses import HTMLResponse
from starlette.middleware import cors
import databases

LOCAL_SETUP = True
DOMAIN = "localhost"
PROJECT_NAME = "ilyanaapp"
# BACKEND_CORS_ORIGINS = [
#     "*",
# ]
DATABASE_URI = "sqlite:///./main.db"


app = fa.FastAPI(
    title=PROJECT_NAME,
    debug=LOCAL_SETUP,
)

# if BACKEND_CORS_ORIGINS:
#     app.add_middleware(
#         cors.CORSMiddleware,
#         allow_origins=[str(origin) for origin in BACKEND_CORS_ORIGINS],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

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
            categoryId integer references category(id),
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

    inserting = [
        "INSERT INTO country(name) VALUES ('United States'), ('United Kingdom')",
        "insert into artist(name) VALUES ('Elsa'), ('Hector'), ('Laurence')",
        "insert into artistCountry(countryId, artistId) VALUES (1, 1), (2, 1), (1, 3)",
        "insert into city(name, countryId) VALUES ('Dallas', 1), ('York', 2)",
        "insert into place(name, cityId) VALUES ('Some museum in Dallas', 1), ('Some museum in York', 2)",
        "insert into item(name, placeId, artistId) VALUES ('Black square', 1, 1), ('Yellow square', 2, 1), ('Green square', 1, 2), ('Blue square', 2, 3)",
    ]
    for inser in inserting:
        try:
            await db.execute(query=inser)
        except:
            pass


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()


api = fa.APIRouter()
front = fa.APIRouter()

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
        + f"async def post_{table}():\n"
        + f'\tquery = "INSERT INTO {table}(text, completed) VALUES (:text, :completed);"\n'
        + '\treturn await db.fetch_one(query=query, values={"id": id})'
    )

    delete_handler = (
        f'@api.delete("/{table}")\n'
        + f"async def delete_{table}(id: int):\n"
        + f'\tquery = "delete from {table} where id = :id;"\n'
        + '\tawait db.execute(query=query, values={"id": id})\n'
        + '\treturn "All good"'
    )

start = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
"""

end = """
</body>
</html>
"""

def content(somehtml):
    return start + somehtml + end


@app.get("/")
async def index():
    return HTMLResponse(content("""
        <h2><a href="http://127.0.0.1:8000/api/artist">Artists</a></h2><br>
        <h2><a href="http://127.0.0.1:8000/api/place">Places</a></h2><br>
        <h2><a href="http://127.0.0.1:8000/api/item">Items</a></h2>
    """))


@front.get("/artist")
async def front324():
    resp = ""
    for artist in await db.fetch_all("SELECT * FROM artist;"):
        id = artist["id"]
        name = artist["name"]
        resp += f"<a href='http://127.0.0.1:8000/artist/{id}'>{name}</a><br>"
    return HTMLResponse(content(resp))

async def one(what: str, id):
    query = f"SELECT * FROM {what} WHERE id = :id;"
    return await db.fetch_one(query=query, values={"id": id})

@front.get("/artist/{id}")
async def fronts2352a(id: int):
    r = ""
    artist = await one("artist", id)
    r += f'{artist["name"]}, born: {artist["born"]}, died: {artist["died"]}'
    r += "<br>Countries: <br>"
    for row in await db.fetch_all("SELECT * FROM artistCountry"):
        if row["artistId"] == id:
            country = await one("country", row["countryId"])
            r += "<br>"
            r += country["name"]

    r += "<br><br>Items: <br>"
    items = await db.fetch_all("SELECT * FROM item;")
    for row in items:
        print(row["artistId"])
        if row["artistId"] == id:
            itemName = row['name']
            r += "   "
            r += f"<a href='http://127.0.0.1:8000/item/{id}'>{itemName}</a><br>"


    return HTMLResponse(content(r))




app.include_router(api, prefix="/api")
app.include_router(front)
