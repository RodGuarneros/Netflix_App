
import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import firebase_admin
from firebase_admin import credentials, firestore
import json

# conexión local

# if not firebase_admin._apps:
#     path = "/content/"
#     cred = credentials.Certificate(path + "netflix-firebase.json")
#     firebase_admin.initialize_app(cred)
# db = firestore.client()
# dbFilmes = db.collection("pelis")
# sidebar = st.sidebar

# conexión despliegue en producción

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="netflix-app-rodrigo-guarneros")

st.header("Netflix app")
st.subheader(f"Elaborado por Rodrigo Guarneros")

# para reducir sintexis
sidebar = st.sidebar

# para las select box de abajo, necesito el dataframe de manera global

pelis_ref = db.collection(u"pelis").stream()
pelis_dict = [peli.to_dict() for peli in pelis_ref]
pelis_dataframe = pd.DataFrame(pelis_dict)


# Mostrar el dataframe
@st.cache_data
def display_data():
    pelis_ref = db.collection(u"pelis").stream()
    pelis_dict = [peli.to_dict() for peli in pelis_ref]
    pelis_dataframe = pd.DataFrame(pelis_dict)
    st.caption(f"El total de películas disponibles es de: {len(pelis_dataframe)-1}")
    st.dataframe(pelis_dataframe)
    
checkbox_mostrar = st.sidebar.checkbox("Mostrar todos los filmes")

if checkbox_mostrar:
  st.markdown("""---""")
  st.text("Hecho! (usando st.cache)")
# correr la app streamlit
  if  __name__ == '__main__':
    display_data()
else:
  st.sidebar.write("Da click para mostrar el conjunto de datos")

#función que obtiene la información según la búsqueda
@st.cache_data
def loadByFilme(filme):
    filmes_ref = dbFilmes.where(u"filme", u"==", filme)
    currentFilme = None
    for myfilme in filmes_ref.stream():
        currentFilme = myfilme
    return currentFilme

#función de filtrado por título
@st.cache_data
# def load_data_bytitle(title):
#     title_lower = title.lower()  # Convierte la palabra clave en lowercase
#     pelis_ref = db.collection(u"pelis").stream()
#     pelis_dict = [peli.to_dict() for peli in pelis_ref]
#     pelis_dataframe = pd.DataFrame(pelis_dict)
#     filtered_data_bytitle = pelis_dataframe[
#         pelis_dataframe["name"].str.lower().str.contains(title_lower)  # Convierte los datos de la base de datos en minúsculas para comparar con el titulo o palabra clave que se busca
#     ]
#     return filtered_data_bytitle
def load_data_bytitle(title):
    title_lower = title.lower()
    filtered_data_bytitle = pelis_dataframe[pelis_dataframe["name"].str.lower().str.contains(title_lower)]
    return filtered_data_bytitle

#función filtrado por director
@st.cache_data
# def load_data_bydirector(director):
#     director_lower = director.lower()  # Convierte el nombre del director en lowercase
#     pelis_ref = db.collection(u"pelis").stream()
#     pelis_dict = [peli.to_dict() for peli in pelis_ref]
#     pelis_dataframe = pd.DataFrame(pelis_dict)
#     filtered_data_bydirector = pelis_dataframe[
#         pelis_dataframe["director"].str.lower().str.contains(director_lower)  # Convierte los datos de la base de datos en minúsculas para comparar con el nombre del director o palabra clave que se busca
#     ]
#     return filtered_data_bydirector
def load_data_bydirector(director):
    director_lower = director.lower()
    filtered_data_bydirector = pelis_dataframe[pelis_dataframe["director"].str.lower().str.contains(director_lower)]
    return filtered_data_bydirector


# Implementación del filtrado por filme
sidebar.markdown("""---""")

sidebar.subheader("Título del filme:")
filmeSearch = sidebar.text_input("Palabra clave")
btnFiltrar = sidebar.button("Buscar filmes")

if btnFiltrar:
    doc = load_data_bytitle(filmeSearch)
    if doc is None:
        st.markdown('<span style="color:red; font-size:10px;">Este filme no existe</span>', unsafe_allow_html=True)
    else:
        st.write(f"EL total de filmes con el término '{filmeSearch}' es de: {len(doc)}")
        st.write(doc)

# Implementación de caja de selección de director y filtrado
sidebar.markdown("""---""")

# caja de selección de director
sidebar.subheader("Seleccione el director de su interés: ")
director_opciones = pd.unique(pelis_dataframe["director"])
director_seleccionado = sidebar.selectbox("Lista desplegable:", director_opciones)
btnFiltrarDirector = sidebar.button("Filtra por director")

if btnFiltrarDirector:
    doc = load_data_bydirector(director_seleccionado)
    if doc.empty:
      sidebar.write(f"La base de datos no tiene películas del director '{director_seleccionado}'.")
    else:
      st.caption(f"El total de películas del director '{director_seleccionado}' es de: {len(doc)}")
      st.write(doc)

# implementación de sección de carga de nuevos registros con la estructura de datos pre-establecida

sidebar.markdown("""---""")
dbPelis = db.collection(u"pelis")
sidebar.header("Nuevo filme")

name = sidebar.text_input("Título: ")
company = sidebar.selectbox("Compañía: ", pd.unique(pelis_dataframe["company"]))
director = sidebar.selectbox("Director: ", pd.unique(pelis_dataframe["director"]))
genre = sidebar.selectbox("Genre: ", pd.unique(pelis_dataframe["genre"]))

submit = sidebar.button('Crear nuevo registro')

# Una vez que cada elmentos sea enviado, se actualizará la base en firebase

if name and company and director and genre and submit:
  doc_ref = db.collection("pelis").document(name)
  doc_ref.set({
    "name": name,
    "company": company,
    "director": director,
    "genre": genre
  })
  sidebar.markdown('<span style="color:red; font-size:10px;">Registro insertado correctamente</span>', unsafe_allow_html=True)
