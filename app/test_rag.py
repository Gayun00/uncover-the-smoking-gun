from core.rag import EvidenceRAG

def test_document_splitting():
    # RAG 시스템 초기화
    rag = EvidenceRAG()
    
    # 문서 분할 테스트
    chunks = rag._split_documents()
    print(f"\n총 {len(chunks)}개의 청크로 분할됨\n")
    
    # 첫 번째 청크 확인
    print("=== 첫 번째 청크 ===")
    print("내용:", chunks[0].page_content)
    print("메타데이터:", chunks[0].metadata)
    
    # 청크 크기 통계
    lengths = [len(chunk.page_content) for chunk in chunks]
    avg_length = sum(lengths) / len(lengths)
    print(f"\n평균 청크 길이: {avg_length:.0f}자")
    print(f"최대 청크 길이: {max(lengths)}자")
    print(f"최소 청크 길이: {min(lengths)}자")
    
    # 각 문서별 청크 수
    doc_counts = {}
    for chunk in chunks:
        source = chunk.metadata["source"]
        doc_counts[source] = doc_counts.get(source, 0) + 1
    
    print("\n=== 문서별 청크 수 ===")
    for doc_id, count in doc_counts.items():
        print(f"{doc_id}: {count}개")

def test_search():
    rag = EvidenceRAG()
    
    # 1. 먼저 일부 증거를 발견된 상태로 설정
    rag.discover_evidence("에코_정체성")
    rag.discover_evidence("에코_기억")
    
    print("\n=== 검색 테스트 ===")
    
    # 2. 다양한 쿼리로 검색 테스트
    test_queries = [
        "낚시터에서 무슨 일이 있었나요?",
        "스탠리는 에코에게 어떤 말을 했나요?",
        "케빈은 누구인가요?"
    ]
    
    for query in test_queries:
        print(f"\n질문: {query}")
        results = rag.search_evidence(query, k=2)  # 상위 2개 결과만
        
        for i, result in enumerate(results, 1):
            print(f"\n결과 {i} (관련도: {result['relevance']:.2f})")
            print(f"출처: {result['source']}")
            print(f"내용: {result['content']}")

def test_search_scenarios():
    rag = EvidenceRAG()
    
    # 시나리오 1: 초기 상태 (아무것도 발견되지 않음)
    print("\n=== 시나리오 1: 초기 상태 ===")
    results = rag.search_evidence("낚시터에 대해 알려주세요")
    print("결과 수:", len(results))  # 아무것도 나오지 않아야 함

    # 시나리오 2: 에코의 기억만 발견
    print("\n=== 시나리오 2: 에코의 기억 발견 ===")
    rag.discover_evidence("에코_기억")
    test_queries = [
        "낚시터에서 무슨 일이 있었나요?",
        "스탠리는 에코에게 뭐라고 했나요?",
        "물고기는 몇 마리나 잡았나요?"
    ]
    
    for query in test_queries:
        print(f"\n질문: {query}")
        results = rag.search_evidence(query)
        for r in results:
            print(f"관련도: {r['relevance']:.2f}")
            print(f"내용: {r['content']}\n")

    # 시나리오 3: 복잡한 질문
    print("\n=== 시나리오 3: 복잡한 질문 ===")
    rag.discover_evidence("살인_동기")  # 추가 증거 발견
    complex_queries = [
        "에코가 스탠리를 죽인 이유는 무엇인가요?",
        "스탠리와 에코의 관계는 어땠나요?",
        "케빈은 이 사건과 어떤 관련이 있나요?"
    ]
    
    for query in complex_queries:
        print(f"\n질문: {query}")
        results = rag.search_evidence(query, k=2)
        for r in results:
            print(f"출처: {r['source']}")
            print(f"관련도: {r['relevance']:.2f}")
            print(f"내용: {r['content']}\n")

if __name__ == "__main__":
    # test_document_splitting()  # 주석 처리
    test_search() 
    test_search_scenarios() 