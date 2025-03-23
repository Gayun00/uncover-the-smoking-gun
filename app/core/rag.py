from typing import List, Dict
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from data.story_data import STORY_DOCUMENTS

class EvidenceRAG:
    def __init__(self):
        # 텍스트 분할기 초기화
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,        # 각 청크의 최대 길이
            chunk_overlap=50,      # 청크 간 중복되는 문자 수
            length_function=len,   # 길이 측정 함수
            separators=["\n\n", "\n", ".", "!", "?", ",", " "]  # 분할 기준
        )
        
        # 임베딩 모델 초기화
        self.embeddings = OpenAIEmbeddings()
        
        # 문서 처리 및 벡터 DB 초기화
        self.vectorstore = self._initialize_vectorstore()
        
    def _split_documents(self) -> List[Document]:
        """문서를 청크로 분할"""
        all_chunks = []
        
        for doc_id, content in STORY_DOCUMENTS.items():
            # 텍스트 분할
            chunks = self.text_splitter.split_text(content)
            
            # Document 객체로 변환
            doc_chunks = [
                Document(
                    page_content=chunk,
                    metadata={
                        "source": doc_id,
                        "discovered": False  # 초기에는 발견되지 않은 상태
                    }
                )
                for chunk in chunks
            ]
            
            all_chunks.extend(doc_chunks)
        
        return all_chunks

    def _initialize_vectorstore(self) -> Chroma:
        """벡터 DB 초기화"""
        documents = self._split_documents()
        
        return Chroma.from_documents(
            documents,
            self.embeddings,
            collection_name="echo_memory"
        )
    
    def search_evidence(self, query: str, k: int = 3) -> List[Dict]:
        """관련 증거 검색"""
        results = self.vectorstore.similarity_search_with_score(
            query,
            k=k,
            filter={"discovered": True}
        )
        
        return [{
            "content": doc.page_content,
            "source": doc.metadata["source"],
            "relevance": score
        } for doc, score in results]
    
    def discover_evidence(self, evidence_id: str) -> None:
        """새로운 증거 발견 처리"""
        # 해당 문서의 모든 청크를 찾아서 discovered를 True로 설정
        results = self.vectorstore.get(
            where={"source": evidence_id}
        )
        
        if results:
            for doc_id in results['ids']:
                self.vectorstore._collection.update(
                    ids=[doc_id],
                    metadatas=[{"discovered": True}]
                ) 