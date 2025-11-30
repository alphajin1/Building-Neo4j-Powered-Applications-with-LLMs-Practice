# Chapter 5: Vector Search and RAG Implementation Flow

## 전체 프로세스 흐름

```mermaid
flowchart TD
    Start([시작]) --> Prereq{ch4 지식 그래프<br/>준비 완료?}
    Prereq -->|아니오| Error1[ch4 먼저 실행 필요]
    Prereq -->|예| CheckEmbeddings{임베딩<br/>생성됨?}
    
    CheckEmbeddings -->|아니오| GenerateEmbed[임베딩 생성<br/>generate_embeddings.py]
    GenerateEmbed --> StoreEmbed[Neo4j에 저장<br/>Movie.embedding]
    
    StoreEmbed --> CreateIndex[벡터 인덱스 생성<br/>overview_embeddings]
    CheckEmbeddings -->|예| CreateIndex
    
    CreateIndex --> SearchReady[벡터 검색 준비 완료]
    
    SearchReady --> VectorSearch[벡터 검색 테스트<br/>vector_search.py]
    VectorSearch --> HaystackMethod[Haystack 방식<br/>Neo4jDocumentStore]
    VectorSearch --> CypherMethod[Cypher 방식<br/>db.index.vector.queryNodes]
    
    HaystackMethod --> ChatbotReady[챗봇 준비]
    CypherMethod --> ChatbotReady
    
    ChatbotReady --> LaunchChatbot[챗봇 실행<br/>search_chatbot.py]
    LaunchChatbot --> GradioUI[Gradio 웹 인터페이스]
    GradioUI --> UserQuery[사용자 쿼리 입력]
    UserQuery --> QueryEmbedding[쿼리 임베딩 생성]
    QueryEmbedding --> VectorSearch2[벡터 유사도 검색]
    VectorSearch2 --> Results[영화 추천 결과]
    Results --> Display[사용자에게 표시]
    
    style Start fill:#e1f5ff
    style SearchReady fill:#c8e6c9
    style ChatbotReady fill:#c8e6c9
    style Display fill:#ffccbc
    style Error1 fill:#ffcdd2
```

## ch4에서 ch5로의 연결

```mermaid
flowchart LR
    subgraph "ch4: 지식 그래프 구축"
        A1[Movie 노드 생성] --> A2[overview 속성<br/>영화 줄거리 텍스트]
    end
    
    subgraph "ch5: 벡터 검색 준비"
        B1[overview 추출] --> B2[OpenAI 임베딩 생성<br/>text-embedding-ada-002<br/>1536차원]
        B2 --> B3[embedding 속성 저장]
        B3 --> B4[벡터 인덱스 생성<br/>overview_embeddings]
    end
    
    subgraph "검색 및 RAG"
        C1[사용자 쿼리] --> C2[쿼리 임베딩]
        C2 --> C3[벡터 유사도 검색]
        C3 --> C4[관련 영화 검색]
        C4 --> C5[추천 결과 반환]
    end
    
    A2 --> B1
    B4 --> C3
    
    style A2 fill:#c8e6c9
    style B4 fill:#fff9c4
    style C5 fill:#ffccbc
```

## 임베딩 생성 프로세스

```mermaid
flowchart TD
    Start([generate_embeddings.py<br/>실행]) --> Retrieve[영화 데이터 조회<br/>WHERE embedding IS NULL<br/>AND overview IS NOT NULL]
    
    Retrieve --> Filter[필터링<br/>'None' 문자열 제외<br/>빈 문자열 제외]
    
    Filter --> Parallel[병렬 처리 시작<br/>ThreadPoolExecutor<br/>max_workers=20]
    
    Parallel --> Process1[영화 1 처리]
    Parallel --> Process2[영화 2 처리]
    Parallel --> ProcessN[영화 N 처리]
    
    Process1 --> Embed1[OpenAI API 호출<br/>text-embedding-ada-002]
    Process2 --> Embed2[OpenAI API 호출<br/>text-embedding-ada-002]
    ProcessN --> EmbedN[OpenAI API 호출<br/>text-embedding-ada-002]
    
    Embed1 --> Store1[Neo4j 저장<br/>SET m.embedding]
    Embed2 --> Store2[Neo4j 저장<br/>SET m.embedding]
    EmbedN --> StoreN[Neo4j 저장<br/>SET m.embedding]
    
    Store1 --> Verify[검증<br/>임베딩 확인]
    Store2 --> Verify
    StoreN --> Verify
    
    Verify --> Complete([완료])
    
    style Start fill:#e1f5ff
    style Parallel fill:#fff9c4
    style Complete fill:#c8e6c9
```

## 벡터 인덱스 구조

```mermaid
graph TB
    subgraph "Neo4j 벡터 인덱스"
        Index[overview_embeddings<br/>VECTOR INDEX]
        Config[인덱스 설정<br/>dimensions: 1536<br/>similarity: cosine]
    end
    
    subgraph "Movie 노드"
        Movie[(Movie)]
        Prop1[tmdbId]
        Prop2[title]
        Prop3[overview<br/>텍스트]
        Prop4[embedding<br/>1536차원 벡터]
    end
    
    Index --> Config
    Index --> Prop4
    Prop4 --> Movie
    Movie --> Prop1
    Movie --> Prop2
    Movie --> Prop3
    
    style Index fill:#fff9c4
    style Prop4 fill:#c8e6c9
```

## 벡터 검색 방식 비교

```mermaid
flowchart TD
    Query([사용자 쿼리<br/>예: 'organized crime movie']) --> Embedding[쿼리 임베딩 생성<br/>OpenAI text-embedding-ada-002]
    
    Embedding --> Method{검색 방식 선택}
    
    Method -->|방식 1| Haystack[Haystack 방식<br/>Neo4jDocumentStore]
    Method -->|방식 2| Cypher[Cypher 방식<br/>db.index.vector.queryNodes]
    
    Haystack --> HaystackStep1[Neo4jDocumentStore 초기화<br/>index: overview_embeddings<br/>node_label: Movie]
    HaystackStep1 --> HaystackStep2[query_by_embedding 호출<br/>top_k=3]
    HaystackStep2 --> HaystackResult[결과 반환<br/>Document 객체]
    
    Cypher --> CypherStep1[Neo4jDynamicDocumentRetriever 초기화<br/>runtime_parameters: query_embedding]
    CypherStep1 --> CypherStep2[Pipeline 구성<br/>query_embedder + retriever]
    CypherStep2 --> CypherStep3[Cypher 쿼리 실행<br/>CALL db.index.vector.queryNodes]
    CypherStep3 --> CypherResult[결과 반환<br/>Document 객체]
    
    HaystackResult --> Display[영화 추천 결과<br/>title, overview, score]
    CypherResult --> Display
    
    style Query fill:#e1f5ff
    style Haystack fill:#fff9c4
    style Cypher fill:#fff9c4
    style Display fill:#ffccbc
```

## 챗봇 인터페이스 Flow

```mermaid
sequenceDiagram
    participant User as 사용자
    participant Gradio as Gradio UI
    participant Chatbot as search_chatbot.py
    participant Embedder as OpenAI Embedder
    participant Neo4j as Neo4j Database
    participant VectorIndex as Vector Index
    
    User->>Gradio: 영화 선호도 입력<br/>예: "organized crime"
    Gradio->>Chatbot: perform_vector_search_cypher()
    
    Chatbot->>Embedder: 쿼리 텍스트 전달
    Embedder->>Embedder: text-embedding-ada-002<br/>임베딩 생성
    Embedder->>Chatbot: query_embedding 반환
    
    Chatbot->>Neo4j: Cypher 쿼리 실행<br/>db.index.vector.queryNodes
    Neo4j->>VectorIndex: 벡터 유사도 검색<br/>cosine similarity
    VectorIndex->>Neo4j: top_k=3 영화 반환
    Neo4j->>Chatbot: 영화 결과 + score
    
    Chatbot->>Chatbot: 결과 포맷팅<br/>title, overview, score
    Chatbot->>Gradio: 추천 결과 반환
    Gradio->>User: 영화 추천 표시
```

## RAG 파이프라인 준비 상태

```mermaid
flowchart LR
    subgraph "데이터 준비"
        D1[ch4: 지식 그래프<br/>Movie 노드 + 관계]
        D2[ch5: 벡터 임베딩<br/>Movie.embedding]
        D3[ch5: 벡터 인덱스<br/>overview_embeddings]
    end
    
    subgraph "검색 기능"
        S1[벡터 검색<br/>유사도 기반]
        S2[그래프 탐색<br/>관계 기반]
    end
    
    subgraph "RAG 구성요소"
        R1[Retrieval<br/>벡터 검색]
        R2[Augmentation<br/>그래프 컨텍스트]
        R3[Generation<br/>LLM 응답]
    end
    
    D1 --> S2
    D2 --> S1
    D3 --> S1
    
    S1 --> R1
    S2 --> R2
    R1 --> R3
    R2 --> R3
    
    style D3 fill:#c8e6c9
    style S1 fill:#fff9c4
    style R3 fill:#ffccbc
```

## 주요 컴포넌트 및 파일

```mermaid
graph TB
    subgraph "파일 구조"
        F1[generate_embeddings.py<br/>임베딩 생성]
        F2[vector_search.py<br/>검색 테스트]
        F3[search_chatbot.py<br/>챗봇 인터페이스]
    end
    
    subgraph "기능"
        Func1[임베딩 생성<br/>OpenAI API]
        Func2[벡터 인덱스 생성<br/>CREATE VECTOR INDEX]
        Func3[Haystack 검색<br/>Neo4jDocumentStore]
        Func4[Cypher 검색<br/>db.index.vector.queryNodes]
        Func5[Gradio UI<br/>웹 인터페이스]
    end
    
    F1 --> Func1
    F2 --> Func2
    F2 --> Func3
    F2 --> Func4
    F3 --> Func4
    F3 --> Func5
    
    style F1 fill:#e1f5ff
    style F2 fill:#e1f5ff
    style F3 fill:#e1f5ff
```

## 실행 순서 요약

1. **전제 조건 확인**: ch4에서 Movie 노드와 overview 속성이 준비되어 있어야 함
2. **임베딩 생성**: `generate_embeddings.py` 실행
   - Movie.overview에서 텍스트 추출
   - OpenAI API로 임베딩 생성 (1536차원)
   - Movie.embedding 속성에 저장
   - 병렬 처리로 효율성 향상
3. **벡터 인덱스 생성**: `vector_search.py` 실행 시 자동 생성
   - 인덱스명: `overview_embeddings`
   - 차원: 1536
   - 유사도 함수: cosine
4. **검색 테스트**: `vector_search.py`로 두 가지 방식 테스트
   - Haystack 방식: Neo4jDocumentStore 사용
   - Cypher 방식: db.index.vector.queryNodes 사용
5. **챗봇 실행**: `search_chatbot.py` 실행
   - Gradio 웹 인터페이스 시작
   - 사용자 쿼리 입력 받기
   - 벡터 검색 수행
   - 영화 추천 결과 반환

## 기술 스택

- **임베딩 모델**: OpenAI text-embedding-ada-002 (1536차원)
- **벡터 인덱스**: Neo4j Vector Index (cosine similarity)
- **검색 프레임워크**: Haystack (neo4j-haystack)
- **UI 프레임워크**: Gradio
- **데이터베이스**: Neo4j

## ch6 연결점 (예상)

- 벡터 검색 결과 → LLM 프롬프트에 통합
- 그래프 관계 탐색과 벡터 검색 결합
- RAG 파이프라인 완성

