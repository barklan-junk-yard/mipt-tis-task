import fastapi as fa
from fastapi.responses import HTMLResponse
import databases
from fastapi.staticfiles import StaticFiles

app = fa.FastAPI(
    title="ilyanaapp",
    debug=True,
)

db = databases.Database("sqlite:///./main.db")

async def dbdata():
    queries = [
        """--sql
        create table if not exists artist (
            id integer primary key autoincrement not null,
            name varchar(255),
            born integer,
            bornDeltaSeconds integer,
            died integer,
            diedDeltaSeconds integer
        );
    """,
        """--sql
        create table if not exists country (
            id integer primary key autoincrement not null,
            name varchar(255) NOT NULL UNIQUE
        );
    """,
        """--sql
        create table if not exists city (
            id integer primary key autoincrement not null,
            name varchar(255),
            countryId integer,
            FOREIGN KEY(countryId) REFERENCES country(id)
        );
    """,
        """--sql
        create table if not exists place (
            id integer primary key autoincrement not null,
            name varchar(255),
            foundationDate integer, -- select datetime(1092941466, 'unixepoch');
            cityId integer,
            FOREIGN KEY(cityId) REFERENCES city(id)
        );
    """,
        """--sql
        create table if not exists category (
            id integer primary key autoincrement not null,
            name varchar(255)
        );
    """,
        """--sql
        create table if not exists item (
            id integer primary key autoincrement not null,
            name varchar(255),
            creationDate integer,
            categoryId integer references category(id),
            placeId integer references place(id) not null
        );
    """,
        """--sql
        create table if not exists artistCountry (
            id integer primary key autoincrement not null,
            countryId integer references country(id) not null,
            artistId integer references artist(id) not null
        );
    """,
        """--sql
        create table if not exists artistItem (
            id integer primary key autoincrement not null,
            artistId integer references artist(id) not null,
            itemId integer references item(id) not null
        );
    """,
    ]

    for query in queries:
        await db.execute(query=query)

    inserting = [
        "INSERT INTO country(name) VALUES ('United States'), ('United Kingdom')",
        "INSERT INTO artist(name) VALUES ('Elsa'), ('Hector'), ('Laurence')",
        "INSERT INTO artistCountry(countryId, artistId) VALUES (1, 1), (2, 1), (1, 3)",
        "INSERT INTO city(name, countryId) VALUES ('Dallas', 1), ('York', 2)",
        "INSERT INTO place(name, cityId) VALUES ('Some museum in Dallas', 1), ('Some museum in York', 2)",
        "INSERT INTO item(name, placeId) VALUES ('Black square', 1),"
        + " ('Yellow square', 2), ('Green square', 1), ('Blue square', 2)",
        "INSERT INTO artistItem(artistId, itemId) VALUES (1, 1), (2, 1), (1, 3), (3, 2), (3, 1)",
    ]
    for inser in inserting:
        try:
            await db.execute(query=inser)
        except:
            pass


@app.on_event("startup")
async def startup():
    await db.connect()

    await dbdata()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()


api = fa.APIRouter()
front = fa.APIRouter()

tables = [
    "artist",
    "country",
    "city",
    "place",
    "category",
    "item",
    "artistCountry",
    "artistItem",
]


start = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Document</title>
</head>
<style>

#wrapper {
  margin: 30px auto;
  width: 70%;
}

.btn {
  padding: 16px 32px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 4px 2px;
  transition-duration: 0.4s;
  cursor: pointer;
  background-color: white;
  color: black;
  border: 2px solid #555555;
}

.btn:hover {
  background-color: #555555;
  color: white;
}

a,a:visited,a:hover,a:active{
  -webkit-backface-visibility:hidden;
          backface-visibility:hidden;
	position:relative;
  transition:0.5s color ease;
	text-decoration:none;
	color:#81b3d2;
	font-size:1.5em;
}
a:hover{
	color:#d73444;
}
a.before:before,a.after:after{
  content: "";
  transition:0.5s all ease;
  -webkit-backface-visibility:hidden;
          backface-visibility:hidden;
  position:absolute;
}
a.before:before{
  top:-0.25em;
}
a.after:after{
  bottom:-0.25em;
}
a.before:before,a.after:after{
  height:5px;
  height:0.35rem;
  width:0;
  background:#d73444;
}

#sourcecode {
    position: fixed;
    top: 10px;
    right: 15%;
    background-color: LavenderBlush;
    border: 3px solid;
    padding: 8px;
    font-size: 12px;
    border-radius: 5px;
}
</style>
<body>
<div id="wrapper">
"""

end = """
</div>
</body>
</html>
"""


def content(somehtml):
    return start + somehtml + end


@app.get("/")
async def index():
    return HTMLResponse(
        content(
            """
            <h1>Hey! You're at Ilyana's place.</h1>

    <script defer>
        function resetdb() {
            fetch('http://127.0.0.1:8000/api/reset', {
                method: 'POST',
            }).then(response => response.json())
            .then(data => {
                document.getElementById('output').innerHTML = data;
                console.log('Success:', data);
            })
            .catch((error) => {
            console.error('Error:', error);
            });
        }

    </script>
        <h2><a href="http://127.0.0.1:8000/artist">Artists</a></h2>
        <h2><a href="http://127.0.0.1:8000/place">Places</a></h2>
        <h2><a href="http://127.0.0.1:8000/item">Items</a></h2>
        <br>

        <div style="display:flex; justify-content:center; gap: 30px;">
            <button class="btn" onclick="resetdb()">Reset Database</button>

            <!--
            <form action="" id="form">
                <label for="formi">Type SQL here:</label><br>
                <input type="text" id="formi">
            </form>
            -->
        </div>


        <div style="margin: 20px;justify-content:center;display:flex;" id="output"></div>

        <h3 style="margin-top: 60px;">Conceptual diagram:</h3>
        <img style="object-fit: contain; max-width: 100%;" src="http://127.0.0.1:8000/static/conceptbw.png"></img>

        <h3 style="margin-top: 40px;">Logical/Physycal ERD:</h3>
        <img style="object-fit: contain; max-width: 100%;" src="http://127.0.0.1:8000/static/diag.gif"></img>

        <div id="sourcecode">
            <a href="http://127.0.0.1:8000/static/main.py">Download source code.</a>
        </div
    """
        )
    )


@api.post("/reset")
async def reset():
    try:
        for table in tables:
            await db.execute(f"drop table if exists {table};")
        await dbdata()
        return "Success!"
    except:
        return "Failed!"


async def one(what: str, id):
    query = f"SELECT * FROM {what} WHERE id = :id;"
    return await db.fetch_one(query=query, values={"id": id})


@front.get("/item")
async def front23422():
    r = ""
    items = await db.fetch_all("SELECT * FROM item;")
    for item in items:
        category = await one("category", item["categoryId"])
        categoryName = category["name"] if category else ""
        place = await one("place", item["placeId"])
        placeName = place["name"]

        artistsString = ""
        artists = await db.fetch_all("SELECT * FROM artistItem;")
        for row in artists:
            if row["itemId"] == item["id"]:
                artistId = row["artistId"]
                artist = await one("artist", artistId)
                artistName = artist["name"]
                artistsString += f"{artistName}, "

        r += f"<br>{item['name']}, creation date: {item['creationDate']}, \
            place: {placeName}, category: {categoryName}, artist: {artistsString}<br>"
    return HTMLResponse(content(r))


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
    items = await db.fetch_all("SELECT * FROM artistItem;")
    for row in items:
        if row["artistId"] == id:
            itemId = row["itemId"]
            item = await one("item", itemId)
            itemName = item["name"]
            r += f"{itemName}<br>"

    return HTMLResponse(content(r))


@front.get("/place/{id}")
async def frontsdf2352a(id: int):
    r = ""
    sub = await one("place", id)
    city = await one("city", sub["cityId"])
    cityName = city["name"]
    country = await one("country", city["countryId"])
    countryName = country["name"]

    r += f'{sub["name"]}, foundation date: {sub["foundationDate"]}, city: {cityName} (country: {countryName})'

    r += "<br><br>Items: <br>"
    items = await db.fetch_all("SELECT * FROM item;")
    for row in items:
        if row["placeId"] == id:
            itemName = row["name"]
            r += f"{itemName}<br>"

    return HTMLResponse(content(r))


for sub in ["artist", "place"]:
    somepython = (
        f'@front.get("/{sub}")\n'
        + f"async def frontrere3{sub}():\n"
        + f'\tresp = ""\n'
        + f'\tfor {sub} in await db.fetch_all("SELECT * FROM {sub};"):\n'
        + f'\t\tid = {sub}["id"]\n'
        + f'\t\tname = {sub}["name"]\n'
        + f'\t\tresp += "<a href=\'http://127.0.0.1:8000/{sub}/"'
        + ' + f"{id}\'>"'
        + ' + f"{name}</a><br>"\n'
        + f"\treturn HTMLResponse(content(resp))\n"
    )

    exec(somepython)


app.include_router(api, prefix="/api")
app.include_router(front)

app.mount("/static", StaticFiles(directory="./"), name="static")
