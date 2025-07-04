from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
import json
import time

def flatten_metadata(md):
    flat = {}
    for k, v in md.items():
        if v is None:
            flat[k] = ""  # Chroma не принимает None, заменяем на пустую строку
        elif isinstance(v, (list, dict)):
            flat[k] = json.dumps(v, ensure_ascii=False)
        else:
            flat[k] = v
    return flat

with open("/Users/zarinamacbook/rag_system/main_copy.json", "r", encoding="utf-8") as f:
    docs_raw = json.load(f)

print(f"📚 Загружено документов: {len(docs_raw)}")

docs = []
for d in docs_raw:
    content = d.get("content", "")
    metadata = d.get("metadata", {})  # если нет, используем пустой словарь
    docs.append(
        Document(
            page_content=content,
            metadata=flatten_metadata(metadata)
        )
    )

print("📝 Преобразовано в LangChain Documents.")
print("⏳ Начинаю индексацию...")

embeddings = OllamaEmbeddings(model="llama3")

batch_size = 20
vectorstore = None
for i in range(0, len(docs), batch_size):
    batch = docs[i:i+batch_size]
    print(f"  🟦 Индексация документов {i+1} — {min(i+batch_size, len(docs))} ...")
    if vectorstore is None:
        vectorstore = Chroma.from_documents(
            batch, embedding=embeddings, persist_directory="./chroma_db"
        )
    else:
        vectorstore.add_documents(batch)
    print(f"  ✅ {min(i+batch_size, len(docs))} документов проиндексировано.")
    time.sleep(0.5)

vectorstore.persist()

print("🎉 Индексация завершена.")
