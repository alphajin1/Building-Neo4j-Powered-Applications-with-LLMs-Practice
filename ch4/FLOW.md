# Chapter 4: Knowledge Graph Building Flow

## 전체 프로세스 흐름

```mermaid
flowchart TD
    Start([시작]) --> Cleanup[데이터베이스 정리<br/>MATCH n DETACH DELETE n]
    Cleanup --> Index[인덱스 및 제약조건 생성<br/>UNIQUE constraints, Indexes]
    
    Index --> LoadMovies[영화 노드 로드<br/>Movie nodes 생성<br/>10,000개 제한]
    
    LoadMovies --> LoadGenres[장르 노드 및 관계<br/>Genre nodes<br/>HAS_GENRE 관계]
    LoadGenres --> LoadCompanies[제작사 노드 및 관계<br/>ProductionCompany nodes<br/>PRODUCED_BY 관계]
    LoadCompanies --> LoadCountries[제작 국가 노드 및 관계<br/>Country nodes<br/>PRODUCED_IN 관계]
    LoadCountries --> LoadLanguages[언어 노드 및 관계<br/>SpokenLanguage nodes<br/>HAS_LANGUAGE 관계]
    LoadLanguages --> LoadKeywords[키워드 속성 설정<br/>Movie.keywords]
    
    LoadKeywords --> LoadActors[배우 노드 및 관계<br/>Person:Actor nodes<br/>ACTED_IN 관계]
    LoadActors --> LoadCrew[감독/제작자 노드 및 관계<br/>Person:Director/Producer<br/>DIRECTED/PRODUCED 관계]
    
    LoadCrew --> LoadLinks[링크 정보 설정<br/>movieId, imdbId]
    LoadLinks --> LoadRatings[평점 노드 및 관계<br/>Person:User nodes<br/>RATED 관계]
    
    LoadRatings --> GraphReady[지식 그래프 완성<br/>Neo4j Knowledge Graph]
    
    GraphReady --> NextChapter[다음 단계: ch5<br/>벡터 임베딩 생성<br/>벡터 검색 준비]
    
    style Start fill:#e1f5ff
    style GraphReady fill:#c8e6c9
    style NextChapter fill:#fff9c4
```

## 데이터 소스 및 로드 순서

```mermaid
graph LR
    subgraph "데이터 소스 (Google Cloud Storage)"
        CSV1[normalized_movies.csv]
        CSV2[normalized_genres.csv]
        CSV3[normalized_production_companies.csv]
        CSV4[normalized_production_countries.csv]
        CSV5[normalized_spoken_languages.csv]
        CSV6[normalized_keywords.csv]
        CSV7[normalized_cast.csv]
        CSV8[normalized_crew.csv]
        CSV9[normalized_links.csv]
        CSV10[normalized_ratings_small.csv]
    end
    
    subgraph "Neo4j 지식 그래프"
        N1[(Movie)]
        N2[(Genre)]
        N3[(ProductionCompany)]
        N4[(Country)]
        N5[(SpokenLanguage)]
        N6[(Person:Actor)]
        N7[(Person:Director)]
        N8[(Person:Producer)]
        N9[(Person:User)]
    end
    
    CSV1 --> N1
    CSV2 --> N2
    CSV3 --> N3
    CSV4 --> N4
    CSV5 --> N5
    CSV6 --> N1
    CSV7 --> N6
    CSV8 --> N7
    CSV8 --> N8
    CSV9 --> N1
    CSV10 --> N9
    
    N2 -.HAS_GENRE.-> N1
    N3 -.PRODUCED_BY.-> N1
    N4 -.PRODUCED_IN.-> N1
    N5 -.HAS_LANGUAGE.-> N1
    N6 -.ACTED_IN.-> N1
    N7 -.DIRECTED.-> N1
    N8 -.PRODUCED.-> N1
    N9 -.RATED.-> N1
```

## 인덱스 및 제약조건 구조

```mermaid
graph TB
    subgraph "제약조건 (UNIQUE)"
        C1[Movie.tmdbId UNIQUE]
        C2[Movie.movieId UNIQUE]
        C3[ProductionCompany.company_id UNIQUE]
        C4[Genre.genre_id UNIQUE]
        C5[SpokenLanguage.language_code UNIQUE]
        C6[Country.country_code UNIQUE]
    end
    
    subgraph "인덱스"
        I1[Person.actor_id INDEX]
        I2[Person.crew_id INDEX]
        I3[Movie.movieId INDEX]
        I4[Person.user_id INDEX]
    end
    
    C1 --> Movie[(Movie)]
    C2 --> Movie
    C3 --> PC[(ProductionCompany)]
    C4 --> Genre[(Genre)]
    C5 --> Lang[(SpokenLanguage)]
    C6 --> Country[(Country)]
    
    I1 --> Person1[(Person:Actor)]
    I2 --> Person2[(Person:Director/Producer)]
    I3 --> Movie
    I4 --> Person3[(Person:User)]
```

## RAG 및 검색 준비 관점

```mermaid
flowchart LR
    subgraph "ch4: 지식 그래프 구축"
        A1[CSV 데이터] --> A2[Neo4j 노드 생성]
        A2 --> A3[관계 생성]
        A3 --> A4[인덱스 생성]
    end
    
    subgraph "ch5: 벡터 검색 준비"
        B1[임베딩 생성] --> B2[벡터 인덱스]
        B2 --> B3[벡터 검색]
    end
    
    subgraph "검색 및 RAG"
        C1[사용자 쿼리] --> C2[벡터 검색]
        C2 --> C3[관련 영화 검색]
        C3 --> C4[그래프 관계 탐색]
        C4 --> C5[RAG 응답 생성]
    end
    
    A4 --> B1
    B3 --> C2
    A3 --> C4
    
    style A4 fill:#c8e6c9
    style B2 fill:#fff9c4
    style C5 fill:#ffccbc
```

## 주요 노드 및 관계 타입

```mermaid
erDiagram
    Movie ||--o{ HAS_GENRE : has
    Movie ||--o{ PRODUCED_BY : produced_by
    Movie ||--o{ PRODUCED_IN : produced_in
    Movie ||--o{ HAS_LANGUAGE : has
    Movie ||--o{ ACTED_IN : "acted in"
    Movie ||--o{ DIRECTED : directed
    Movie ||--o{ PRODUCED : produced
    Movie ||--o{ RATED : rated
    
    Movie {
        int tmdbId PK
        int movieId
        string title
        string overview
        string keywords
    }
    
    Genre {
        int genre_id PK
        string genre_name
    }
    
    ProductionCompany {
        int company_id PK
        string company_name
    }
    
    Country {
        string country_code PK
        string country_name
    }
    
    SpokenLanguage {
        string language_code PK
        string language_name
    }
    
    Person {
        int actor_id
        int crew_id
        int user_id
        string name
        string role
    }
```

## 실행 순서 요약

1. **초기화**: 데이터베이스 정리 및 인덱스 생성
2. **핵심 노드**: Movie 노드 생성 (10,000개)
3. **속성 노드**: Genre, ProductionCompany, Country, SpokenLanguage
4. **키워드**: Movie 노드에 keywords 속성 추가
5. **인물 노드**: Actor, Director, Producer, User
6. **링크 정보**: movieId, imdbId 설정
7. **평점 데이터**: User와 Movie 간 RATED 관계

## ch5 연결점

- Movie 노드의 `overview` 속성 → ch5에서 벡터 임베딩 생성
- 생성된 벡터 인덱스 → 벡터 유사도 검색
- 그래프 관계 → RAG에서 컨텍스트 확장

