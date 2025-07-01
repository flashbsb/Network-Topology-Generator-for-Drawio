# 🌐 GERADOR DE TOPOLOGIAS DE REDE - DRAWIO

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)

## 🔍 Visão Geral
Ferramenta para geração automatizada de topologias hierárquicas de redes backbone nacionais, produzindo datasets prontos para visualização em ferramentas como Draw.io.

![Screenshot da Interface](docs/images/gui-screenshot.png)

Ferramenta para geração automática de diagramas de rede (.drawio) a partir de dados de equipamentos e conexões.

## 🔥 Recursos Principais
- **4 layouts**: Circular, Orgânico, Geográfico, Hierárquico
- **Visualizações múltiplas**: Diversas páginas no mesmo diagrama
- **Personalização completa**: Via arquivo `config.json`
- **Regionalização automática**: Ex: `CORE` → `CORE_SUDESTE`
- **Duas interfaces**: CLI (linha de comando) e GUI (gráfica)

## ⚙️ Instalação das dependências para execução do script

```bash
# Windows (via Microsoft Store)
1. Abra Microsoft Store
2. Busque "Python 3.12+"
3. Clique em Instalar
4. Instalar dependências Python (CMD/PowerShell):
python -m pip install networkx chardet numpy pillow psutil

# Linux (Debian/Ubuntu)
1. Instalar Python 3 e pip (apt):
sudo apt update && sudo apt install python3 pip python3-tk -y
2. Instalar dependências Python
python3 -m pip install networkx chardet numpy pillow psutil
```

## 🚀 Como Usar

### Modo Gráfico (GUI)
```bash
python GeradorTopologias.py
```

### Modo Terminal (CLI)
```bash
python GeradorTopologias.py [OPÇÕES] conexoes1.csv conexoes2.csv ...
```

### ⚡ Opções da CLI
| Opção | Descrição |
|-------|-----------|
| `-y`  | Incluir nós sem conexões |
| `-t cog` | Layouts (c=circular, o=orgânico, g=geográfico, h=hierárquico) |
| `-r`  | Ativar regionalização das camadas |
| `-g pasta/` | Diretório com arquivos CSV |
| `-o nc` | Opções: n (sem nomes), c (ocultar conexões) |
| `-d`  | Ignorar customizações nos CSV |

## 📂 Arquivos de Entrada

### 1. conexoes.csv (Obrigatório)
```csv
ponta-a;ponta-b;textoconexao;strokeWidth;strokeColor;dashed;fontStyle;fontSize
RTIC-SPO99-99;RTOC-SPO98-99;Link Principal;2;#036897;0;1;14
```

### 2. elementos.csv (Opcional)
```csv
elemento;camada;nivel;cor;siteid;apelido
RTIC-SPO99-99;INNER-CORE;1;#FF0000;SP01;Core-SP
```

### 3. localidades.csv (Opcional)
```csv
siteid;Localidade;RegiaoGeografica;Latitude;Longitude
SP01;SAOPAULO;Sudeste;23.32.33.S;46.38.44.W
```

> **Nota**: Coordenadas no formato **DMS** (Graus.Minutos.Segundos.Direção)

## ⚙️ Configuração Avançada (config.json)

### Estrutura Principal
```json
{
  "LAYER_COLORS": {
    "INNER-CORE": "#036897",
    "OUTER-CORE": "#0385BE"
  },
  "LAYER_STYLES": {
    "INNER-CORE": {
      "shape": "mxgraph.cisco19.rect",
      "width": 50,
      "height": 50
    }
  },
  "LAYER_DEFAULT_BY_PREFIX": {
    "RTIC": {"camada": "INNER-CORE", "nivel": 1},
    "RTOC": {"camada": "OUTER-CORE", "nivel": 2}
  }
}
```

### Principais Seções
1. **LAYER_COLORS**: Cores padrão por camada
2. **LAYER_STYLES**: Aparência dos equipamentos
3. **LAYER_DEFAULT_BY_PREFIX**: Mapeamento nome→camada
4. **PAGE_DEFINITIONS**: Visões/páginas do diagrama
5. **GEOGRAPHIC_LAYOUT**: Configuração de mapa

## 🛠️ Exemplos Práticos

### 1. Geração completa
```bash
python GeradorTopologias.py -t cogh -r redes.csv
```

### 2. Com diretório customizado
```bash
python GeradorTopologias.py -g meus_dados/ -t o
```

### 3. Opções avançadas
```bash
python GeradorTopologias.py -y -d -o nc -t gh rede_principal.csv
```

## ⚠️ Solução de Problemas

| Problema | Solução |
|----------|---------|
| JSON inválido | Valide em [jsonlint.com](https://jsonlint.com) |
| Nós sobrepostos | Aumente `radius_increment` (circular) ou `min_distance` (geográfico) |
| Sem coordenadas | Nós são posicionados em espiral no centro |
| Regionalização falha | Verifique correspondência de siteid entre arquivos |
| Acentos incorretos | Salve CSVs como UTF-8 |

## 📌 Dicas Importantes
1. Use prefixos do config.json (RTIC, RTOC, RTPR) nos nomes dos equipamentos
2. Para layout geográfico:
   - Arquivos `elementos.csv` e `localidades.csv` são obrigatórios
   - Nós sem siteid vão para camada `SEM_SITEID`
3. Priorize `-g` para organizar seus arquivos:
   ```
   projeto/
   ├── conexoes.csv
   ├── elementos.csv
   ├── localidades.csv
   └── config.json
   ```

## 📤 Saída
Arquivos no formato:  
`NomeArquivo_TIMESTAMP_layout.drawio`  
Ex: `rede_sp_20250615143045_geografico.drawio`

> **Dica final**: Visualize os arquivos em [app.diagrams.net](https://app.diagrams.net/)

## Como gerar os arquivos de testes para carga do script
Use o Gerador de Topologias para Backbone Nacional [https://github.com/flashbsb/Backbone-Network-Topology-Generator] para criar os arquivos conexoes.csv, elementos.csv e localidades.csv (aplicativo irá gerar a massa de dados de teste).

## Fluxo do Programa

```mermaid
graph TD
    A[Início] --> B{Modo de Execução}
    B -->|CLI| C[Processar Argumentos]
    B -->|GUI| D[Iniciar Interface Gráfica]
    
    C --> E[Validar Argumentos]
    E --> F[Configurar Logging]
    F --> G[Carregar Configuração]
    G --> H[Buscar Arquivos de Entrada]
    
    D --> I[Carregar Configuração]
    I --> J[Exibir Interface]
    J --> K[Selecionar Arquivos e Opções]
    K --> L[Gerar Topologias]
    
    H --> M{Arquivos Encontrados?}
    M -->|Sim| N[Processar Arquivos]
    M -->|Não| O[Iniciar GUI]
    
    N --> P[Loop por Arquivo de Conexões]
    P --> Q[Instanciar Gerador]
    Q --> R[Ler Elementos]
    R --> S[Ler Conexões]
    S --> T[Aplicar Regionalização]
    T --> U[Validar Dados]
    U --> V[Calcular Layouts]
    V --> W[Gerar Diagrama Draw.io]
    W --> X[Salvar Arquivo]
    
    L --> Y[Loop por Arquivo de Conexões]
    Y --> Z[Processar Arquivo]
    Z --> W
    
    X --> AA[Relatório Final]
    AA --> AB[Fim]
```
```mermaid
graph LR
    A[config.json] --> B[Definições de Estilo]
    C[elementos.csv] --> D[Camadas/Níveis]
    E[localidades.csv] --> F[Regionalização]
    G[conexoes.csv] --> H[Relações]
    B & D & F & H --> I[Gerador]
    I --> J[Diagrama Draw.io]
```

### Análise do Script

O script é uma ferramenta avançada para geração automática de diagramas de rede no formato do Draw.io.

### 1. **Objetivo Principal**
Transformar dados estruturados de equipamentos e conexões de rede em diagramas visuais profissionais com múltiplos layouts e camadas.

### 2. **Arquivos de Entrada**
- **`conexoes.csv` (Obrigatório)**: 
  - Formato: `ponta-a;ponta-b;textoconexao;strokeWidth;strokeColor;dashed;fontStyle;fontSize`
  - Define as ligações entre dispositivos
- **`elementos.csv` (Opcional)**:
  - Formato: `elemento;camada;nivel;cor;siteid;apelido`
  - Atribui propriedades aos equipamentos
- **`localidades.csv` (Opcional)**:
  - Formato: `siteid;Localidade;RegiaoGeografica;Latitude;Longitude`
  - Fornece dados geográficos para posicionamento

### 3. **Arquivo de Configuração (`config.json`)**
Define todo o comportamento visual:
- **`LAYER_COLORS`**: Cores por tipo de equipamento
- **`LAYER_STYLES`**: Formas e propriedades visuais
- **`LAYER_DEFAULT_BY_PREFIX`**: Mapeamento automático de equipamentos para camadas
- **`PAGE_DEFINITIONS`**: Visões pré-definidas (ex: "CORE", "EDGE")
- **Parâmetros de Layout**: Configurações específicas para cada algoritmo

### 4. **Algoritmos de Layout Implementados**
1. **Circular**:
   - Disposição em anéis concêntricos por nível
   - Configuração: raio base e incremento

2. **Orgânico**:
   - Algoritmo de força (`spring_layout` do NetworkX)
   - Parâmetros ajustáveis: distância entre nós, iterações

3. **Geográfico**:
   - Posicionamento por coordenadas geográficas
   - Tratamento especial para nós sem localização
   - Suporte a imagens de fundo (mapas)

4. **Hierárquico**:
   - Organização vertical por níveis
   - Espaçamento configurável entre camadas

### 5. **Funcionalidades Avançadas**
- **Regionalização Automática**:
  - Adiciona sufixos regionais às camadas (ex: `CORE_SUDESTE`)
  - Requer dados geográficos completos

- **Tratamento de Erros**:
  - Nós sem coordenadas são posicionados em espiral
  - Validação de arquivos e codificação automática

- **Otimizações**:
  - Escalonamento dinâmico de elementos
  - Prevenção de sobreposição (layout geográfico)
  - Controle de memória e performance

### 6. **Sistema de Camadas**
- **Estrutura Multi-nível**:
  ```plaintext
  INNER-CORE (Nível 1)
  │
  ├── OUTER-CORE (Nível 2)
  │
  ├── EDGE (Nível 5)
  │   │
  │   └── ACCESS-EDGE (Nível 6)
  │
  └── SEM_SITEID (Nós sem localização)
  ```
- **Visões Filtradas**:
  - Exibição seletiva por tipo de equipamento
  - Legendas automáticas

### 7. **Geração de Saída**
- Formato `.drawio` (XML estruturado)
- Recursos visuais:
  - Ícones específicos por tipo de equipamento
  - Estilos de conexão personalizáveis
  - Elementos bloqueáveis para diagramas finais

### 8. **Mecanismos Especiais**
- **Detecção de Codificação**: Identifica automaticamente charset dos CSVs
- **Tratamento de Órfãos**: Opção para incluir/excluir nós isolados
- **Escalonamento Dinâmico**: Ajusta tamanhos conforme densidade da rede
- **Controle de Versões**: Sistema de versionamento integrado

### 9. **Modos de Operação**
1. **Interface Gráfica (GUI)**:
   - Seleção visual de arquivos
   - Pré-visualização de recursos disponíveis
   - Controle interativo de parâmetros

2. **Linha de Comando (CLI)**:
   - Opções avançadas via argumentos
   - Processamento em lote de múltiplos arquivos
   - Geração de logs detalhados

### Fluxo de Processamento Detalhado
```python
def process_file():
  1. Carregar dados dos CSVs
  2. Construir grafo de rede
  3. Aplicar regionalização (se ativado)
  4. Calcular posições conforme layout
  5. Gerar XML com:
     - Páginas múltiplas
     - Camadas hierárquicas
     - Estilos visuais
  6. Validar e salvar arquivo
```

### Casos de Uso Típicos
1. **Documentação de Infraestrutura**:
   ```bash
   python GeradorTopologias.py -t co -r infra.csv
   ```
2. **Planejamento de Expansão**:
   ```bash
   python GeradorTopologias.py -t gh -e novos_equipamentos.csv
   ```
3. **Análise Geográfica**:
   ```bash
   python GeradorTopologias.py -t g -s localidades_custom.csv
   ```

O script combina técnicas de processamento de dados, algoritmos de grafos e geração de visualizações para criar uma solução completa de documentação de redes, com ênfase em flexibilidade e qualidade visual.

🔗 **Repositório Oficial**:  
https://github.com/flashbsb/Backbone-Network-Topology-Generator

📜 **Licença**:  
[MIT License](https://github.com/flashbsb/Network-Topology-Generator-for-Drawio/blob/main/LICENSE)
