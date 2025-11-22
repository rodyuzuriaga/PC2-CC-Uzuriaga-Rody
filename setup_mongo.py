GOOGLE_API_KEY = "AIzaSyD7zaJOTxxYyDZkLEap71UIBn5vzLUs2bI"
MONGODB_URI = "mongodb+srv://rodyuzuriaga_db_user:Tph5nFFZTRepGQy9@cluster-rodyua.ne4exx7.mongodb.net/"
COHERE_API_KEY = "Q2E7OCmr3VY40dC57y86wfCjRYuip1F1vkIX6tO2"

import cohere
co = cohere.Client(COHERE_API_KEY)

import pymongo
from PyPDF2 import PdfReader

if not MONGODB_URI:
    raise ValueError("Faltan MONGODB_URI")

# Conexión a MongoDB Atlas
client = pymongo.MongoClient(MONGODB_URI)
db = client.pdf_embeddings_db
collection = db.pdf_vectors

def crear_indice_vectorial():
  from pymongo.operations import SearchIndexModel
  existing_indexes = [index['name'] for index in collection.list_search_indexes()]
  if "vector_index" in existing_indexes:
    print("El índice 'vector_index' ya existe. No se crea nuevamente.")
    return

  search_index_model = SearchIndexModel(
    definition = {
      "fields": [
        {
          "type": "vector",
          "path": "embedding",
          "similarity": "cosine",
          "numDimensions": 768
        }
      ]
    },
    name="vector_index",
    type="vectorSearch"
  )

  collection.create_search_index(model=search_index_model)
  print("Índice vectorial creado.")

def leer_pdf(path_pdf):
    reader = PdfReader(path_pdf)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() + "\n"
    return texto.strip()

def crear_embedding(texto):
    resp = co.embed(
        model="multilingual-22-12",
        texts=[texto]
    )
    return resp.embeddings[0]

def procesar_pdf(ruta_pdf, id_base=0, chunk_size=1000, overlap=200):
    texto = leer_pdf(ruta_pdf)
    if not texto:
        print(f"El PDF {ruta_pdf} no contiene texto.")
        return 0

    trozos = []
    for i in range(0, len(texto), chunk_size - overlap):
        chunk = texto[i:i+chunk_size]
        if len(chunk) > 50:
            trozos.append(chunk)

    documentos = []
    for i, chunk in enumerate(trozos):
        embedding = crear_embedding(chunk)
        documentos.append({
            "id": id_base + i,
            "texto": chunk,
            "embedding": embedding,
            "fuente": ruta_pdf
        })

    collection.insert_many(documentos)
    print(f"Se insertaron {len(documentos)} fragmentos con embeddings para {ruta_pdf}.")
    return len(documentos)

if __name__ == "__main__":
    try:
        db.drop_collection("pdf_vectors")
        print("Colección anterior eliminada.")
    except:
        print("No había colección anterior.")
    
    try:
        db.create_collection("pdf_vectors")
        print("Colección 'pdf_vectors' creada.")
    except:
        print("Colección ya existe.")
    
    crear_indice_vectorial()
    total = 0
    total += procesar_pdf("aws-cloud-adoption-framework_XL-12-18.pdf", total)
    print(f"Total: {total} embeddings generados y almacenados en MongoDB Atlas.")