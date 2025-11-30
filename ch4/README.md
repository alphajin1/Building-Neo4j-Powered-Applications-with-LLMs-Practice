# Chapter 4: Building Your Neo4j Graph with Movies Dataset

## 빠른 시작

```bash
# 1. 환경변수 설정 (프로젝트 루트에서)
# .env 파일 생성 (NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD 설정)

# 2. 패키지 설치
pip install neo4j python-dotenv pandas

# 3. 그래프 빌드 실행
cd ch4
python3 graph_build.py
```

## 주요 사항

- **데이터 소스**: Google Cloud Storage에서 CSV 파일 직접 로드
- **APOC 필요**: `apoc.create.relationship` 사용 (Neo4j Desktop에서 APOC 플러그인 설치 필요)
- **데이터 제한**: 기본적으로 10,000개 영화만 로드 (`movie_limit = 10000`)
- **데이터베이스 정리**: 실행 시 기존 데이터 자동 삭제 (`db_cleanup()`)

## 필요한 환경변수

프로젝트 루트의 `.env` 파일:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

## 참고

- Neo4j Desktop 사용 시 APOC 플러그인 설치 필요
- 인터넷 연결 필요 (Google Cloud Storage 접근)

