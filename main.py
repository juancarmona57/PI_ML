from fastapi import FastAPI
import pandas as pd
from typing import Optional

app = FastAPI()

#https://pi_ml-1-m1052667.deta.app

# Primero creamos una función para cargar los archivos csv de las diferentes plataformas
def cargardf(valor):
    amazon='amazon'
    netflix ='netflix'
    disney='disney'
    hulu='hulu'
    archivos = [amazon,netflix,disney,hulu]
    df = pd.read_csv(netflix+".csv")
    if valor == "amazon":
      df = pd.read_csv(amazon+".csv")
    if valor == "hulu":
      df = pd.read_csv(hulu+".csv")
    if valor == "todos":
       lista_df = []
       for archivo in archivos:
            df1 = pd.read_csv(archivo+".csv")
            lista_df.append(df1)
       df = pd.concat(lista_df)
    return df

@app.get("/")
def read_root():
    return {"Hola": 'Bienvenido'}

@app.get("/get_longest/{plataforma}/{duration_type}/{año}")
def get_longest(plataforma: str, duration_type: str, año: int): 
    df = cargardf(plataforma) 
    df = df[(df['duration_type'] == duration_type) & (df['release_year'] == año) & (df['type'] == "movie")]
    df = df.sort_values('duration_int', ascending=False)
    title = df.iloc[0, 2]
    duration_int = df.iloc[0, 12]
    duration_type = df.iloc[0, 13]
    result = {"title": str(title), "duration_int": str(duration_int), "duration_type": str(duration_type)}
    return result

# Consigna 2: Cantidad de películas por plataforma con un puntaje mayor a XX en determinado año.
@app.get("/get_score_count/{platform}/{year}/{scored}")
def get_score_count(platform: str, scored: float, year: int):
    # Controlamos que la plataforma ingresada sea correcta
    platform = platform.lower()

    platforms = ["amazon", "disney", "hulu", "netflix"]
    if platform not in platforms:
        return ("Plataforma incorrecta! Debe ingresar una de las siguientes: amazon, disney, hulu, netflix")
    
    # Verificar que el rango de scored sea valido. No deberia ser menor que 0 ni mayor que 5
    if scored is not None and (scored < 0 or scored > 5):
        return("El score promedio no puede ser menor que 0 o mayor que 5.")
    
    # Filtrar las películas para la plataforma, año y puntaje especificados
    df_filtered_movies = df[(df.platform == platform) & (df.score > scored) & (df.date_added.str.contains(str(year)))] 
    # & (df.type == 'movie')] Segun sli.do no hay que filtrar por movies

    # Verificar que hay al menos una película que cumpla con los filtros
    if not df_filtered_movies.empty:
        count = df_filtered_movies.groupby('platform').size()
        return count.to_dict()
    else:
        return("No se encontró ninguna pelicula con los parametros dados.")
    


# Consigna 3: Cantidad de películas por plataforma con filtro de PLATAFORMA.
@app.get("/get_count_platform/{platform}")
def get_count_platform(platform):
    # Controlamos que la plataforma ingresada sea correcta
    platform = platform.lower()

    platforms = ["amazon", "disney", "hulu", "netflix"]
    if platform not in platforms:
        return ("Plataforma incorrecta! Debe ingresar una de las siguientes: amazon, disney, hulu, netflix")
    
    # Filtrar las películas para la plataforma especificada
    df_filtered_movies = df[(df.platform == platform)] # & (df.type == 'movie')] Segun sli.do no hay que filtrar por movies

    # Agrupar por plataforma y contar el número de filas resultantes
    count = df_filtered_movies.groupby('platform').size()
    
    # Verificar que hay al menos una película que cumpla con los filtros
    if df_filtered_movies.empty:
        return("No hay peliculas para esa plataforma")
    return count.to_dict()


# Consigna 4: Actor que más se repite según plataforma y año.
@app.get("/get_actor/{platform}/{year}")
def get_actor(platform: str, year: int):
    # Controlamos que la plataforma ingresada sea correcta
    platform = platform.lower()

    platforms = ["amazon", "disney", "hulu", "netflix"]
    if platform not in platforms:
        return ("Plataforma incorrecta! Debe ingresar una de las siguientes: amazon, disney, hulu, netflix")
    

    # Verificar que el año esté dentro del rango válido
    if year is not None and year < 1920:
        raise ValueError("El año debe de ser mayor a 1920")
    
    # Filtrar las películas para la plataforma y año especificado
    df_filtered = df[(df.platform == platform) & (df.release_year == year)]
         
    # Poner el cast en un array para poder hacer el recorrido
    df_cast_filtered= df_filtered.assign(actor=df_filtered.cast.str.split(',')).explode('cast')
    
    # Contar la cantidad de apariciones de cada actor
    actor_count = df_cast_filtered.cast.value_counts()
    
    # Obtener el actor que más se repite y su cantidad de apariciones
    max_actor = actor_count.index[0]
    max_count = int(actor_count.iloc[0])
    actor = dict({'actor': max_actor, 'count': max_count})

    return actor