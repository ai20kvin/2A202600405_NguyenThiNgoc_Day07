from src.chunking import SentenceChunker
from src.store import EmbeddingStore
from src.models import Document
from src.agent import KnowledgeBaseAgent

# Mock LLM
def mock_llm(prompt):
    return f"[Mock Answer] Based on context: {prompt[:100]}..."

# Load all docs
docs = [
    Document(id='01_quy_dinh_chung', content=open('data/01_quy_dinh_chung.md', encoding='utf-8').read(), metadata={'category': 'quy_dinh', 'source': 'local', 'language': 'vi'}),
    Document(id='02_ban_chi_dao_hoi_dong', content=open('data/02_ban_chi_dao_hoi_dong.md', encoding='utf-8').read(), metadata={'category': 'quy_dinh', 'source': 'local', 'language': 'vi'}),
    Document(id='03_diem_thi_phong_thi', content=open('data/03_diem_thi_phong_thi.md', encoding='utf-8').read(), metadata={'category': 'quy_dinh', 'source': 'local', 'language': 'vi'}),
    Document(id='04_doi_tuong_dieu_kien', content=open('data/04_doi_tuong_dieu_kien.md', encoding='utf-8').read(), metadata={'category': 'quy_dinh', 'source': 'local', 'language': 'vi'}),
    Document(id='05_trach_nhiem_thi_sinh', content=open('data/05_trach_nhiem_thi_sinh.md', encoding='utf-8').read(), metadata={'category': 'quy_dinh', 'source': 'local', 'language': 'vi'}),
    Document(id='06_cong_tac_de_thi', content=open('data/06_cong_tac_de_thi.md', encoding='utf-8').read(), metadata={'category': 'quy_dinh', 'source': 'local', 'language': 'vi'}),
    Document(id='07_in_sao_van_chuyen_de', content=open('data/07_in_sao_van_chuyen_de.md', encoding='utf-8').read(), metadata={'category': 'quy_dinh', 'source': 'local', 'language': 'vi'}),
    Document(id='08_coi_thi', content=open('data/08_coi_thi.md', encoding='utf-8').read(), metadata={'category': 'quy_dinh', 'source': 'local', 'language': 'vi'}),
    Document(id='09_cham_thi', content=open('data/09_cham_thi.md', encoding='utf-8').read(), metadata={'category': 'quy_dinh', 'source': 'local', 'language': 'vi'}),
    Document(id='10_phuc_khao_tot_nghiep', content=open('data/10_phuc_khao_tot_nghiep.md', encoding='utf-8').read(), metadata={'category': 'quy_dinh', 'source': 'local', 'language': 'vi'})
]

# Chunk docs using SentenceChunker
chunker = SentenceChunker(max_sentences_per_chunk=2)  # Custom param
chunked_docs = []
for doc in docs:
    chunks = chunker.chunk(doc.content)
    for i, chunk in enumerate(chunks):
        chunked_docs.append(Document(id=f"{doc.id}_chunk_{i}", content=chunk, metadata={**doc.metadata, 'doc_id': doc.id}))

# Setup store and agent
store = EmbeddingStore()
store.add_documents(chunked_docs)
agent = KnowledgeBaseAgent(store, mock_llm)

# Benchmark queries
queries = [
    "Quy định chung về thi cử là gì?",
    "Trách nhiệm của thí sinh trong kỳ thi?",
    "Cách chấm thi như thế nào?",
    "Điều kiện để phúc khảo bài thi?",
    "Công tác coi thi được quy định ra sao?"
]

print("=== Benchmark Results ===")
for query in queries:
    answer = agent.answer(query, top_k=3)
    print(f"Query: {query}")
    print(f"Answer: {answer[:200]}...")
    print()