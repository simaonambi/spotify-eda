# 🎵 Spotify EDA - Exploratory Data Analysis Pipeline

**Exploratory Data Analysis** de dados musicais do Spotify, integrando múltiplas fontes de dados públicas.

## 📋 Visão Geral

Este projeto implementa um **pipeline ETL completo** (Extract, Transform, Load, Visualize) para análise de dados musicais:

- **Semana 1 (EXTRACTION)** ✅ COMPLETA
- **Semana 2 (TRANSFORMATION)** 🔄 EM PROGRESSO
- **Semana 3 (LOAD)** 📝 PLANEJADA
- **Semana 4 (VISUALIZATION)** 📝 PLANEJADA

---

##  Status Atual - Semana 1 (EXTRACTION)

###  Concluído

- ✓ Integração de 3 fontes de dados
- ✓ Extração de 750 registos
- ✓ Geração de 8 ficheiros Parquet (94.1 KB)
- ✓ Validação básica de dados
- ✓ Documentação técnica completa

###  Estatísticas

| Métrica | Valor |
|---------|-------|
| **Tempo de Extração** | 87.8 segundos |
| **Taxa de Extração** | 8.5 registos/segundo |
| **Total de Registos** | 750 |
| **Ficheiros Gerados** | 8 (Parquet) |
| **Tamanho Total** | 94.1 KB |

###  Dados Extraídos

#### Spotify Web Crawler (13.3 KB)
- `spotify_tracks.parquet`: 8 tracks populares
- `spotify_artists.parquet`: 8 artists
- `spotify_playlists.parquet`: 5 playlists públicas

#### Spotify Charts (18.0 KB)
- `spotify_charts_playlists.parquet`: 30 playlists por género
- `spotify_charts_tracks.parquet`: 100 tracks em tendência
- `spotify_charts_artists.parquet`: 49 artists em destaque

#### Last.fm API (62.8 KB)
- `lastfm_top_tracks.parquet`: 500 tracks globais
- `lastfm_artists.parquet`: 50 artists com metadados

---

## 🏗️ Arquitetura

### Estrutura de Pastas

```
spotify-eda/
│
├── src/
│   ├── extract/              # Week 1 ✓ COMPLETA
│   │   ├── __init__.py
│   │   ├── main_extract.py               (280 lines, 9.8 KB)
│   │   ├── spotify_crawler.py            (250 lines, 9.6 KB)
│   │   ├── spotify_charts.py             (320 lines, 11 KB)
│   │   └── lastfm_api.py                 (340 lines, 11 KB)
│   │
│   ├── transform/            # Week 2 
│   │   └── [módulos em desenvolvimento]
│   │
│   ├── validate/             # Week 2 
│   │   └── [módulos em desenvolvimento]
│   │
│   ├── config/               # Configuração
│   │   ├── config.py
│   │   └── logging_config.py
│   │
│   └── orchestration/        # Week 2 
│       └── [orquestrador em desenvolvimento]
│
├── data/
│   ├── raw/                  # Week 1 OUTPUT (8 Parquet files)
│   ├── staging/              # Week 2 OUTPUT (em desenvolvimento)
│   └── curated/              # Week 3 OUTPUT (planejado)
│
├── tests/                    # Testes unitários
├── reports/                  # Relatórios e logs
├── logs/                     # Ficheiros de log
├── requirements.txt          # Dependências Python
├── README.md                 # Este ficheiro
└── .gitignore
```

### Módulos Implementados (Week 1)

#### 1️⃣ **main_extract.py** (Orquestrador Principal)

```python
ExtractionOrchestrator
├── run_extraction()          # Executa pipeline completa
├── _extract_spotify()        # Step 1: Web Crawler
├── _extract_spotify_charts() # Step 2: Charts extractor
├── _extract_lastfm()         # Step 3: Last.fm API
└── _print_summary()          # Relatório final
```

**Uso:**
```bash
python src/extract/main_extract.py
```

####  **spotify_crawler.py** (Web Scraper Spotify)

```python
SpotifyCrawler
├── get_popular_tracks(limit=50)      # Extrai tracks populares
├── get_artists_info(artist_names)    # Informação de artistas
├── get_playlists(limit=10)           # Playlists públicas
└── crawl_all(output_dir)             # Executa tudo
```

**Dados extraídos:**
- Tracks com: `track_id`, `track_name`, `artist_name`, `popularity`, `duration_ms`
- Artists com: `artist_id`, `artist_name`, `followers`, `popularity`, `genres`

####  **spotify_charts.py** (Charts Extractor)

```python
SpotifyChartsExtractor
├── extract_genre_playlists(genres, playlists_per_genre)
├── extract_popular_tracks(limit)
├── extract_featured_artists(limit)
└── extract_all()                     # Executa tudo
```

**Alternativa ao MPD Dataset (Million Playlist Dataset):**
- Motivo: MPD é 6GB, demora 30-60 min download
- Solução: Spotify Charts é instantâneo, 100 tracks, 49 artists, 30 playlists

####  **lastfm_api.py** (Cliente REST Last.fm)

```python
LastfmAPI
├── get_top_tracks(limit=500, period='overall')      # Tracks globais
├── get_artist_info(artist_names)                    # Info detalhada
├── get_similar_artists(artist_name, limit=10)       # Artistas similares
└── extract_lastfm(api_key, api_secret, output_dir)  # Executa tudo
```

**Dados extraídos:**
- Tracks com: `track_name`, `artist_name`, `playcount`, `listeners`
- Artists com: `artist_name`, `mbid`, `listeners`, `playcount`, `tags`, `bio`

---

##  Como Executar

### Pré-requisitos

- Python 3.9+
- pip ou conda

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
pandas==2.0.3
numpy==1.24.3
pyarrow==12.0.1
requests==2.31.0
beautifulsoup4==4.12.2
urllib3==2.0.4
python-dotenv==1.0.0
spotipy==2.23.0
python-json-logger==2.0.7
```

### 2. Configurar Variáveis de Ambiente

Criar ficheiro `.env`:

```env
# Last.fm API
LASTFM_API_KEY=your_api_key_here
LASTFM_API_SECRET=your_api_secret_here

# Spotify (opcional, para futuro)
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

**Como obter API Keys:**
- Last.fm: https://www.last.fm/api/account/create
- Spotify: https://developer.spotify.com/dashboard

### 3. Executar Extração (Week 1)

```bash
python src/extract/main_extract.py
```

**Output esperado:**
```
======================================================================
 SPOTIFY EDA - WEEK 1 EXTRACTION (LIGHTWEIGHT)
======================================================================
Sources:
  1. Spotify Web Crawler
  2. Spotify Charts (lightweight alternative)
  3. Last.fm API
======================================================================

======================================================================
 SPOTIFY EDA - WEEK 1 (LIGHTWEIGHT VERSION) 🎵
======================================================================
Started at: 2026-05-16 22:00:00
Sources: Spotify Crawler + Spotify Charts + Last.fm API
======================================================================

█████████████████████████████████████████████████████████████████████
STEP 1/3: SPOTIFY WEB CRAWLER
█████████████████████████████████████████████████████████████████████
...

✓ EXTRACTION COMPLETE!
======================================================================
 Duration: 87.8 seconds (1.5 minutes)
 Output: data/raw/
======================================================================
```

---

##  Output Gerado

Todos os ficheiros são salvos em **`data/raw/`** em formato **Parquet** (coluna comprimido):

```
data/raw/
├── spotify_tracks.parquet              (5.0 KB)
├── spotify_artists.parquet             (4.1 KB)
├── spotify_playlists.parquet           (4.2 KB)
├── spotify_charts_playlists.parquet    (5.7 KB)
├── spotify_charts_tracks.parquet       (7.1 KB)
├── spotify_charts_artists.parquet      (5.2 KB)
├── lastfm_top_tracks.parquet           (32.7 KB)
└── lastfm_artists.parquet              (30.1 KB)

TOTAL: 94.1 KB, 750 records
```

### Ler os Dados

```python
import pandas as pd

# Ler um ficheiro Parquet
df = pd.read_parquet('data/raw/spotify_tracks.parquet')

# Ver primeiras linhas
print(df.head())

# Informações
print(df.info())
print(df.describe())
```

---

##  Esquema de Dados

### Tracks

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `track_id` | str | Identificador único |
| `track_name` | str | Nome da música |
| `artist_name` | str | Nome do artista |
| `album_name` | str | Nome do álbum |
| `release_year` | int | Ano de lançamento |
| `popularity` | int | 0-100 score |
| `duration_ms` | int | Duração em millisegundos |
| `playcount` | int | Número de reproduções (Last.fm) |
| `listeners` | int | Número de listeners (Last.fm) |

### Artists

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `artist_id` | str | Identificador único |
| `artist_name` | str | Nome do artista |
| `followers` | int | Número de seguidores |
| `popularity` | int | 0-100 score |
| `genres` | str | Géneros separados por comma |
| `mbid` | str | MusicBrainz ID (Last.fm) |
| `tags` | str | Tags/labels (Last.fm) |

### Playlists

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `playlist_id` | str | Identificador único |
| `playlist_name` | str | Nome da playlist |
| `description` | str | Descrição |
| `num_tracks` | int | Número de músicas |
| `followers` | int | Número de seguidores |
| `genre` | str | Género principal |

---

##  Documentação Técnica

### Decisões de Design

**1. Por que Parquet?**
- Formato coluna comprimido (3-5x menor que CSV)
- Rápido para leitura/escrita
- Mantém tipos de dados
- Ideal para data pipelines

**2. Por que 3 Fontes?**
- **Spotify Crawler**: Dados públicos sem autenticação
- **Spotify Charts**: Dados em tendência, leve e rápido
- **Last.fm API**: Dados reais de scrobbles, global

**3. Por que não MPD?**
- MPD é 6GB (heavy download)
- Spotify Charts é instantâneo
- Ambas servem o propósito de análise

### Rate Limiting

Implementado para evitar banimentos:

```python
# Last.fm
time.sleep(0.05)  # 50ms entre requests

# Spotify Crawler
random.uniform(1, 3)  # 1-3 segundos entre passos

# Spotify Charts
time.sleep(0.1)  # 100ms entre requests
```

### Error Handling

Todos os módulos implementam tratamento de exceções:

```python
try:
    data = api.get_tracks()
except requests.exceptions.RequestException as e:
    logger.error(f"API error: {e}")
    # Continua com dados parciais
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

---

##  Semana 2 (TRANSFORMATION) - Próximos Passos

### O que Falta Implementar

**Módulos a Criar:**

1. **src/transform/cleaning.py** (340 linhas)
   - Remove nulos, duplicados, standardiza tipos
   - `DataCleaner` class com métodos reutilizáveis

2. **src/transform/normalization.py** (350 linhas)
   - Lowercase, trim, remove acentos
   - Normaliza datas em ISO 8601
   - `DataNormalizer` class

3. **src/transform/integration.py** (300 linhas)
   - Join de 3 fontes por artist/track
   - Resolução de conflitos
   - Rastreamento de provenance

4. **src/validate/quality_rules.py** (450 linhas)
   - Validação de qualidade customizada
   - `QualityValidator` com múltiplas regras
   - Relatórios em Markdown/JSON

5. **src/orchestration/transform_orchestrator.py** (250 linhas)
   - Orquestra: clean → normalize → validate → integrate
   - Output: data/staging/ (5 Parquet files)

### Output Esperado (Week 2)

```
data/staging/
├── clean_tracks.parquet
├── clean_artists.parquet
├── clean_playlists.parquet
├── integrated_tracks.parquet
└── integrated_artists.parquet

reports/
└── data_quality_report.md (validation results)
```

---

##  Testes

Não há testes automatizados ainda. Planeado para Week 2:

```bash
pytest tests/
```

---

##  Logging

Todos os módulos usam logging estruturado:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Extraction started")
logger.warning("Partial data received")
logger.error("API connection failed")
```

Logs salvos em: `logs/spotify_eda.log`

---

##  Configuração

Ficheiro: `src/config/config.py`

```python
# Paths
RAW_DATA_PATH = 'data/raw'
STAGING_DATA_PATH = 'data/staging'
CURATED_DATA_PATH = 'data/curated'

# Batch sizes
BATCH_SIZE = 100
MAX_RETRIES = 3

# API limits
RATE_LIMIT_DELAY = 0.05  # segundos
```

---

##  Contribuindo

### Git Workflow

1. Criar branch para cada feature/semana
2. Commits pequenos com mensagens claras
3. Conventional Commits:

```bash
git commit -m "feat: add week 2 cleaning module"
git commit -m "fix: handle missing values in tracks"
git commit -m "docs: update README with week 1 results"
```

### Checklist para Commits

- [ ] Código testado localmente
- [ ] Docstrings atualizadas
- [ ] README atualizado se necessário
- [ ] Logs implementados
- [ ] Error handling incluído

---

##  Support & Issues

### Problemas Comuns

**Problema 1: ModuleNotFoundError**
```
ModuleNotFoundError: No module named 'pandas'
```
**Solução:** `pip install -r requirements.txt`

**Problema 2: Missing .env file**
```
ValueError: LASTFM_API_KEY not set in .env file
```
**Solução:** Criar `.env` com credenciais (ver secção Configurar)

**Problema 3: Slow execution**
- Aumentar rate limit delays se necessário
- Verificar conexão internet
- Considerar usar amostra menor para testes

---

##  Recursos Externos

### APIs Utilizadas

- **Spotify Web**: https://open.spotify.com (sem autenticação)
- **Last.fm API**: https://www.last.fm/api
- **Documentação Parquet**: https://parquet.apache.org/

### Bibliotecas

- **Pandas**: Data manipulation & analysis
- **NumPy**: Numerical computing
- **PyArrow**: Parquet I/O
- **Requests**: HTTP client
- **BeautifulSoup4**: Web scraping

---

##  Métricas de Performance

| Métrica | Valor |
|---------|-------|
| Tempo Extração | 87.8s |
| Taxa Extração | 8.5 registos/s |
| Tamanho Médio Ficheiro | 11.8 KB |
| Compressão Parquet | ~60% vs CSV |
| Memória Usada | ~250 MB |

---

##  Timeline

| Semana | Fase | Status | Deliverables |
|--------|------|--------|--------------|
| **1** | Extract |  DONE | 8 Parquet files, 750 records |
| **2** | Transform |  IN PROGRESS | 5 Parquet + quality report |
| **3** | Load |  PLANNED | Database warehouse |
| **4** | Visualize |  PLANNED | Dashboard, BI, reports |

---

## 👥 Equipa

- **Simão Nambi** (ID: 53558) - Desenvolvimento principal
- **Tiago Neto** (ID: a54172) - Validação e testes
- **Instituição**: Universidade da Beira Interior (UBI), Covilhã

---

##  Licença

Projeto educacional desenvolvido para disciplina de **Engenharia de Dados e Transformação** (ETD).

---

##  Resumo Executivo

Este projeto demonstra um **pipeline ETL profissional** de dados musicais, com:

 **Semana 1:** Extração de 3 fontes (750 registos em 87.8s)
 **Semana 2:** Transformação e validação de qualidade
 **Semana 3:** Load para data warehouse
 **Semana 4:** Visualização e análise

**Status Atual:** Week 1 completa, pronta para Week 2

---

**Última Atualização:** 16 de Maio de 2026  
**Versão:** 1.0.0 - Week 1 Complete
