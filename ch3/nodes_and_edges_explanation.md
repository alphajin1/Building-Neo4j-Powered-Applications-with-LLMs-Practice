# imdb_kg.py의 노드(Node)와 엣지(Edge) 설명

## 📊 그래프 데이터베이스 기본 개념

그래프 데이터베이스는 **노드(Node)**와 **엣지(Edge/Relationship)**로 구성됩니다.

```
노드(Node) ──[엣지/관계]──> 노드(Node)
```

## 🎯 이 코드에서의 구조

### 시각적 표현

```
┌─────────────────┐         ┌─────────────────────────────────────────────┐
│  Movie 노드      │         │  Plot 노드                                   │
│  - title         │         │  - description                               │
│  - year          │         │                                             │
└─────────────────┘         └─────────────────────────────────────────────┘
         │                              │
         │    HAS_PLOT (엣지)          │
         └─────────────────────────────┘
```

## 1️⃣ 노드 (Node) - 엔티티

### 정의
**노드**는 그래프에서 **실제 객체나 엔티티**를 나타냅니다. 관계형 DB의 "행(row)"과 비슷하지만, 관계를 직접 표현할 수 있습니다.

### 이 코드의 노드들

#### 🎬 Movie 노드 (5개)
```cypher
CREATE (m:Movie {title: 'The Matrix', year: 1999})
CREATE (m:Movie {title: 'Inception', year: 2010})
CREATE (m:Movie {title: 'Interstellar', year: 2014})
CREATE (m:Movie {title: 'The Dark Knight', year: 2008})
CREATE (m:Movie {title: 'Pulp Fiction', year: 1994})
```

**구조:**
- **라벨(Label)**: `Movie` (노드의 타입/카테고리)
- **속성(Properties)**:
  - `title`: 영화 제목
  - `year`: 개봉 연도

**예시:**
```
노드 1: Movie {title: 'The Matrix', year: 1999}
노드 2: Movie {title: 'Inception', year: 2010}
...
```

#### 📝 Plot 노드 (5개)
```cypher
CREATE (p:Plot {description: 'A computer hacker learns from mysterious rebels...'})
CREATE (p:Plot {description: 'A thief who steals corporate secrets...'})
...
```

**구조:**
- **라벨(Label)**: `Plot` (노드의 타입/카테고리)
- **속성(Properties)**:
  - `description`: 영화 줄거리 설명

**예시:**
```
노드 1: Plot {description: 'A computer hacker learns...'}
노드 2: Plot {description: 'A thief who steals...'}
...
```

### 노드의 특징

1. **라벨(Label)**: 노드의 타입을 나타냄 (`Movie`, `Plot`)
2. **속성(Properties)**: 노드에 저장된 데이터 (`title`, `year`, `description`)
3. **고유성**: 각 노드는 독립적인 엔티티

## 2️⃣ 엣지 (Edge/Relationship) - 관계

### 정의
**엣지**는 두 노드 사이의 **관계(Relationship)**를 나타냅니다. 방향이 있는 화살표로 표현됩니다.

### 이 코드의 엣지

#### 🔗 HAS_PLOT 관계 (5개)
```cypher
MATCH (m:Movie {title: 'The Matrix'}), 
      (p:Plot {description: 'A computer hacker learns...'})
CREATE (m)-[:HAS_PLOT]->(p)
```

**구조:**
- **시작 노드**: `Movie` 노드
- **관계 타입**: `HAS_PLOT` (관계의 이름)
- **종료 노드**: `Plot` 노드
- **방향**: `Movie` → `Plot` (단방향)

**시각적 표현:**
```
[The Matrix] ──[HAS_PLOT]──> [Plot description...]
[Inception] ──[HAS_PLOT]──> [Plot description...]
[Interstellar] ──[HAS_PLOT]──> [Plot description...]
...
```

### 엣지의 특징

1. **방향성**: `(m)-[:HAS_PLOT]->(p)` 
   - `Movie`에서 `Plot`로 향하는 단방향 관계
   - `<-[:HAS_PLOT]-`로 반대 방향도 가능하지만, 이 코드는 단방향만 사용

2. **관계 타입**: `HAS_PLOT` (관계의 의미를 나타냄)

3. **속성**: 이 코드의 엣지는 속성이 없지만, 속성을 추가할 수 있음
   ```cypher
   CREATE (m)-[:HAS_PLOT {created_at: '2024-01-01'}]->(p)
   ```

## 📋 전체 그래프 구조

### 노드 목록

| 노드 ID | 라벨 | 속성 |
|---------|------|------|
| 1 | Movie | title: 'The Matrix', year: 1999 |
| 2 | Movie | title: 'Inception', year: 2010 |
| 3 | Movie | title: 'Interstellar', year: 2014 |
| 4 | Movie | title: 'The Dark Knight', year: 2008 |
| 5 | Movie | title: 'Pulp Fiction', year: 1994 |
| 6 | Plot | description: 'A computer hacker learns...' |
| 7 | Plot | description: 'A thief who steals...' |
| 8 | Plot | description: 'A team of explorers...' |
| 9 | Plot | description: 'When the menace known as...' |
| 10 | Plot | description: 'The lives of two mob hitmen...' |

### 엣지 목록

| 시작 노드 | 관계 타입 | 종료 노드 |
|----------|----------|----------|
| Movie (The Matrix) | HAS_PLOT | Plot (hacker learns...) |
| Movie (Inception) | HAS_PLOT | Plot (thief who steals...) |
| Movie (Interstellar) | HAS_PLOT | Plot (team of explorers...) |
| Movie (The Dark Knight) | HAS_PLOT | Plot (Joker emerges...) |
| Movie (Pulp Fiction) | HAS_PLOT | Plot (two mob hitmen...) |

## 🔍 코드 분석

### 노드 생성 부분 (13-25줄)

```python
# Movie 노드 생성
tx.run("CREATE (m:Movie {title: 'The Matrix', year: 1999})")
#      └─ 노드 변수 └─ 라벨 └─ 속성 딕셔너리

# Plot 노드 생성
tx.run("CREATE (p:Plot {description: '...'})")
#      └─ 노드 변수 └─ 라벨 └─ 속성
```

**Cypher 문법 설명:**
- `CREATE`: 노드/관계 생성
- `(m:Movie)`: `m`은 변수, `Movie`는 라벨
- `{title: '...', year: 1999}`: 속성 딕셔너리

### 엣지 생성 부분 (28-52줄)

```python
tx.run("""
    MATCH (m:Movie {title: 'The Matrix'}),  # 시작 노드 찾기
          (p:Plot {description: '...'})      # 종료 노드 찾기
    CREATE (m)-[:HAS_PLOT]->(p)              # 관계 생성
    """)
```

**Cypher 문법 설명:**
- `MATCH`: 기존 노드를 찾음
- `(m)-[:HAS_PLOT]->(p)`: 
  - `(m)`: 시작 노드
  - `-[:HAS_PLOT]->`: 관계 타입과 방향
  - `(p)`: 종료 노드

### 쿼리 부분 (57-60줄)

```python
result = tx.run("""
    MATCH (m:Movie)-[:HAS_PLOT]->(p:Plot)
    #     └─ Movie 노드 └─ 관계 └─ Plot 노드
    RETURN m.title AS movie, m.year AS year, p.description AS plot
    """)
```

**의미:**
- `Movie` 노드에서 `HAS_PLOT` 관계를 따라 `Plot` 노드를 찾음
- 두 노드의 속성을 반환

## 💡 노드 vs 엣지 비교

| 구분 | 노드 (Node) | 엣지 (Edge/Relationship) |
|------|------------|-------------------------|
| **역할** | 엔티티 (실제 객체) | 관계 (연결) |
| **예시** | 영화, 줄거리 | "영화가 줄거리를 가짐" |
| **라벨** | `Movie`, `Plot` | `HAS_PLOT` |
| **속성** | `title`, `year`, `description` | (이 코드에서는 없음) |
| **방향** | 없음 | 있음 (단방향 또는 양방향) |
| **개수** | 10개 (Movie 5 + Plot 5) | 5개 |

## 🎯 실제 그래프 시각화

```
                    ┌─────────────────────────────────────┐
                    │  Movie: The Matrix (1999)           │
                    └─────────────────────────────────────┘
                              │
                              │ HAS_PLOT
                              ▼
                    ┌─────────────────────────────────────┐
                    │  Plot: A computer hacker learns...   │
                    └─────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │  Movie: Inception (2010)            │
                    └─────────────────────────────────────┘
                              │
                              │ HAS_PLOT
                              ▼
                    ┌─────────────────────────────────────┐
                    │  Plot: A thief who steals...        │
                    └─────────────────────────────────────┘

                    ... (나머지 3개도 동일한 구조)
```

## 🔑 핵심 정리

1. **노드 = 엔티티**: 실제 존재하는 객체 (영화, 줄거리)
2. **엣지 = 관계**: 노드들 사이의 연결 (영화가 줄거리를 가짐)
3. **방향성**: 관계는 방향이 있음 (`Movie` → `Plot`)
4. **라벨**: 노드와 관계의 타입을 구분
5. **속성**: 노드와 관계에 데이터 저장

## 🚀 확장 가능성

이 구조를 확장하면:
- `Actor` 노드 추가
- `DIRECTED_BY` 관계 추가 (영화 → 감독)
- `ACTED_IN` 관계 추가 (배우 → 영화)
- `GENRE` 노드 추가
- 등등...

이렇게 하면 더 풍부한 지식 그래프가 됩니다!

