from fastapi import FastAPI, Body

app = FastAPI()


"""Dejar declarado la siguiente ruta para poder encontrar algo apenas se inicie el serividor"""

@app.get("/")
async def root():
    return {"message": "Hello World"}

"""La siguiente ruta es para tomar una variable desde ella URL y usarla dentro de la funcion como un argumneto o variable y para fijar que tipo de variable requiere la función"""

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


"""Al crear nuevas rutas de acceso en una API, hay que tener en cuenta las rutas fijas y las rutas variables, porque si estas dos rutas se pusieran al revés, en vez de escribir "the current user" cuando coloque users/me se colocara "me" por eso el orden importa."""
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}

""" Tampoco se puede redifinar rutas de acceso de la siguiente forma, ya que solo funcionara la primera que se definió."""

@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]


@app.get("/users")
async def read_users2():
    return ["Bean", "Elfo"]


"""Para restringir los valores posibiles se usa Enum una clase heredadora, si no se usan los que están en la clase y en el if stament se lanzara error"""
from enum import Enum

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}

"""La función sirve para que puedan haber otras URL dentro de la ruta que ya tenemos, es decir dejar que hayan mas slashes o / dentro de la ruta inicial, si no se hace así no se podrán usar slashes"""

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}

"""La función que viene es una forma de pedir por así decirlo, es decir que me muestren algo como el usuario lo pide"""

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
"""La lista de arriba es una lista de ejemplo, hay que tener en cuenta los indices de los elementos de la lista"""

@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]
"""Para el ejemplo vamos a usar el siguiente URL: http://127.0.0.1:8000/items/?skip=0&limit=10, esto hará un slicing en la primera lista desde skip = 0 hasta skip + limit = 10, los parametros de consulta son dados despues del signo de pregunta"""

"""Tambien pueden haber parametros opcionales es decir que si coloca una ruta que no tiene no pasa nada, | ese operador es como tener dos opciones, aunque no se puede llamar como un if pero si se puede decir como una Y de caminos esta opcion o la otra"""

@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}

"""Tambien se pueden declarar boleanos"""
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

"""Se pueden tener varios parametros de ruta y varios parametros de consulta, FastAPI los separa cada uno, no es necesario especificar uno por uno o en un orden especifico"""
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

"""Tenemos varios parametros de ruta y de consulta, es importante diferenciarlos, los de ruta estarán en la función principal y la ruta que definimos en el decorador, los parametros de consulta opcionales o tienen el pipe o tienen un valor por defecto, los parametros obligatorios no tendrán ninguno de los dos"""
@app.get("/items/{item_id}")
async def read_user_item(
    item_id: str, needy: str, skip: int = 0, limit: int | None = None
):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}

"""Lo que hacemos acá es definir una estructura y tipos de datos que esperamos, colocar campos obligatorios y opcionales, para devolvernos un objeto en python tipado, es decir los datos que espera el cliente o que nosotros le vamos a dar"""
from pydantic import BaseModel, Field, HttpUrl

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

"""Adentro de la función podemos acceder a todos los atributos del objeto directamente, tanto como si fuera un diccionario o como si no lo fuera. """
@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item_dict is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

"""Tambien se puede declarar parametros de ruta y request bodys(son los que están dentro del diccionario) al mismo tiempo, solo recordar los metodos HTTP, toca entender en profundidad que hace cada funcion y como sería con un proyecto real"""
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.model_dump()}

"""Tambien se pueden declarar request body, parametros de ruta y de consulta, siempre toca estar pendiente de lop que se quiere hacer, para definir correctamente el metodo HTTP"""
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q})
    return result

"""Tambien se pueden declarar validaciones y metadatos dentro de los modelos de pydantic de la siguiente manera, metadatos no son datos de meta, la empresa, se tienen que importar Body de la libreria FastAPI y Field de pydantic"""

from typing import Annotated, Any

class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None 

@app.put("/items/{items_id}")
async def update_item(item_id: int, item:Annotated[Item, Body(embed= True)]):
    results = {"item_id": item_id, "item": item}
    return results

"""En BaseMNodel tambien se pueden agregar listas en los tipos de datos que se esperan gracias a pydantic, de dos formas, especificando los tipos internos de la lista o sin especificar, si queremos que sean unicos los valores en vez de colocar [] colocamos set()"""

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list = []
    tags_2 = list[str] = []


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results

"""Yo puedo poner un modelo Pydantic dentro de otro modelo de la siguiente forma, es decir definir un modelo pydantic y luego usar ese mismo modelo para ponerlo dentro de un dato como tipo que tiene que ser ese dato"""

class Image(BaseModel):
    url: str
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None #Se utilizó un modelo Pydantic dentro de otro modelo pydantic, es decir esta variable será un diccionario dentro de otro diccionario


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results

"""Tambien se pueden utilizar tipos de datos más complejos para los modelos Pydantic, pero esto se tienen que revisar para verificar su uso, como en el siguiente ejemplo, en vez de utilizar, str como en el ejemplo pasado usamos HttpUrl de Pydantic(Se tienen que importar)"""

class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results

"""Tambien se pueden usar los modelos pydantic como subtippos de listas y sets, como el siguiente ejemplo"""

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results

"Se pueden definir arbitrariamente profundos modelos anidados"

class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]


@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer

"Se permiten recibir directamente una lista en el body del request, es decir una lista de dicccionarios, o un array, siempre se va a tener soporte de VsCode, algo que es increible, debido a que ni siquiera trabajando con diccionarios de python directamente se obtiene este soporte"

@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images

"Tambien se pueden recibir bodys, sin que estos sean necesariamente modelos de pydantic si no diccionarios clasicos de python, tener en cuenta que pydantic solo recibe str como llaves de diccionario, esto significa que por más que el usuario mande interos como llaves pydantic los convertería en str, en el siguiente ejemplo no se están pidiendo modelos pydantic dentro de la función"

@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]): #En este caso se recibirán diccionarios con llaves enteras y valores tipo float
    return weights

"Tambien podemos fijar que es lo que queremos devolver en le función con '->' en la función de la siguiente forma, vamos a seguir teniendo en cuenta los modelos de Pydantic definidos anteriormente"

@app.post("/items/")
async def create_item(item: Item) -> Item: #Acá cuando utilicemos el post nos devolvera un modelo Pydantic "Item"
    return item


@app.get("/items/")
async def read_items() -> list[Item]: #Acá nos devolvera una lista de modelos Pydantic "ITem"
    return [
        Item(name="Portal Gun", price=42.0),
        Item(name="Plumbus", price=32.0),
    ]

"En algunos casos vas a querer regresar algunos datos que no son exactamente el tipo de datos que declaramos en la función, por ejemplo voy a querer devolver un diccionario en vez de un modelo pydantic, en esos casos podemos usar 'the path operation decorator parameter response_model' en vez de tipo de retorno o '->' de la siguiente forma, Any es importado de la libreria typing"

@app.post("/items/", response_model=Item)
async def create_item(item: Item) -> Any:
    return item


@app.get("/items/", response_model=list[Item])
async def read_items() -> Any:
    return [
        {"name": "Portal Gun", "price": 42.0},
        {"name": "Plumbus", "price": 32.0},
    ]
#Esto siempre va a devolverle un modelo pydantic o lo que se declare en el decorador si soy cliente, lo que esto permite es ser más flexible como función para el desarrollador, en este caso -> Any no es necesarío pero quiere decir que se la función puede devolve cualquier tipo de datos 

