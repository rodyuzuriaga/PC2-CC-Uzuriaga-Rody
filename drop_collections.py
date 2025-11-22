import pymongo

MONGODB_URI = "mongodb+srv://rodyuzuriaga_db_user:Tph5nFFZTRepGQy9@cluster-rodyua.ne4exx7.mongodb.net/"

client = pymongo.MongoClient(MONGODB_URI)
db = client.pdf_embeddings_db

try:
    db.drop_collection("pdf_vectors")
    print("Colección 'pdf_vectors' eliminada.")
except Exception as e:
    print(f"No se pudo eliminar la colección: {e}")

print("Listado de colecciones restantes:")
for col in db.list_collection_names():
    print(f"- {col}")