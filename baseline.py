from src.chunking import ChunkingStrategyComparator
from src.models import Document

# Load sample docs
docs = [
    Document(id='01_quy_dinh_chung', content=open('data/01_quy_dinh_chung.md', encoding='utf-8').read(), metadata={'category': 'quy_dinh', 'source': 'local', 'language': 'vi'}),
    Document(id='02_ban_chi_dao_hoi_dong', content=open('data/02_ban_chi_dao_hoi_dong.md', encoding='utf-8').read(), metadata={'category': 'quy_dinh', 'source': 'local', 'language': 'vi'}),
    Document(id='09_cham_thi', content=open('data/09_cham_thi.md', encoding='utf-8').read(), metadata={'category': 'quy_dinh', 'source': 'local', 'language': 'vi'})
]

comparator = ChunkingStrategyComparator()
for doc in docs:
    print(f'\n=== {doc.id} ===')
    result = comparator.compare(doc.content, chunk_size=200)
    for strategy, stats in result.items():
        print(f'{strategy}: {stats["num_chunks"]} chunks, avg length {stats["avg_chunk_length"]:.1f}')