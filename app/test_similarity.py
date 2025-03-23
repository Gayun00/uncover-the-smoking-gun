import numpy as np
from sklearn.metrics.pairwise import (
    cosine_similarity,
    euclidean_distances,
    manhattan_distances
)
from sklearn.feature_extraction.text import TfidfVectorizer

def compare_similarities():
    # 테스트용 문장들
    sentences = [
        "낚시터에서 물고기를 많이 잡았다",        # 기준 문장
        "낚시터에서 고기를 잔뜩 잡았다",          # 매우 유사
        "낚시터에 갔다",                         # 관련 있음
        "물고기를 좋아한다",                     # 약간 관련
        "오늘 날씨가 좋다"                       # 무관
    ]
    
    # TF-IDF 벡터화
    tfidf = TfidfVectorizer()
    vectors = tfidf.fit_transform(sentences).toarray()
    
    # 기준 문장(첫 번째)과 나머지 문장들 비교
    base = vectors[0].reshape(1, -1)
    others = vectors[1:]
    
    # 각 방식으로 유사도 계산
    cosine = cosine_similarity(base, others)[0]
    euclidean = 1 / (1 + euclidean_distances(base, others)[0])  # 거리를 유사도로 변환
    manhattan = 1 / (1 + manhattan_distances(base, others)[0])
    
    print("=== 유사도 비교 ===")
    print("기준 문장:", sentences[0])
    print("\n각 문장별 유사도:")
    
    for i, sentence in enumerate(sentences[1:], 1):
        print(f"\n문장: {sentence}")
        print(f"코사인 유사도: {cosine[i-1]:.3f}")
        print(f"유클리드 유사도: {euclidean[i-1]:.3f}")
        print(f"맨해튼 유사도: {manhattan[i-1]:.3f}")

if __name__ == "__main__":
    compare_similarities() 