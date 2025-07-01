GERADOR DE TOPOLOGIAS DE REDE
====================================

VISÃO GERAL:
-----------
Ferramenta para geração automática de diagramas de rede (.drawio) a partir de dados de equipamentos e conexões. Oferece 4 algoritmos de layout, suporte a coordenadas geográficas e personalização completa via arquivo de configuração.

⭐ RECURSOS:
    - 4 layouts: Circular, Orgânico, Geográfico, Hierárquico
    - Múltiplas páginas/visões no mesmo diagrama
    - Legendas automáticas e cores por camada
    - Regionalização de camadas (ex: CORE -> CORE_SUDESTE)
    - Suporte a mapas reais (background images)
    - Interface gráfica (GUI) e linha de comando (CLI)

📦 INSTALAÇÃO DE DEPENDÊNCIAS:
----------------------------

    # Windows
    1. Instalar Python 3 (Microsof Store):
        a. abra Microsoft Store no menu iniciar.
        b. pesquise "Python 3", escolher versão superior
        c. selecionar instalar.
    2. Instalar dependências Python (CMD/PowerShell):
		python -m pip install networkx chardet numpy

	# Linux Debian:
    1. Instalar Python 3 e pip (apt)
		apt update & apt install python3 pip python3-tk
    2. Instalar dependências Python
		python3 -m pip install networkx chardet numpy

🚀 COMO USAR:
------------
    1. MODO GRÁFICO (GUI):
       Execute o script sem argumentos:
         python GeradorTopologias.py        # Linux/Windows (python ou python3, de acordo com a instalação)

    2. MODO TERMINAL (CLI):
       python GeradorTopologias.py [OPÇÕES] ARQUIVO_CONEXÕES_1.csv ARQUIVO_CONEXÕES_2.csv ...

🛠️ ARGUMENTOS DA CLI:
--------------------
    -y          Inclui nós sem conexões (órfãos)
    -v          Modo detalhado (mostra logs na tela)
    -l          Gera logs em arquivo
    -t LAYOUTS  Layouts a gerar (c=circular, o=orgânico, g=geográfico, h=hierárquico)
                Layout geográfico requer localidades.csv e elementos.csv
                Ex: -t cog → gera circular, orgânico e geográfico
    -r          Ativa regionalização das camadas (requer localidades.csv e elementos.csv)
    -g CAMINHO  Caminho customizado do diretório para leitura dos arquivos conexoes*.csv, elementos.csv e localidades.csv (caso especificado, prioriza a definição destas informações)
    -s CAMINHO  Caminho customizado para localidades.csv
    -e CAMINHO  Caminho customizado para elementos.csv
    -c CAMINHO  Caminho customizado para config.json
    -o OPÇÕES   Opções de visualização:
                n = nós sem nomes
                c = ocultar camadas de conexão
                Ex: -o nc → ativa ambas opções
    -d          Desprezar customizações opcionais dos elementos e conexões (usar apenas config.json)
    -h          Mostra esta ajuda

📂 ARQUIVOS DE ENTRADA:
----------------------

    1. conexoes.csv (OBRIGATÓRIO)
       Formato:
         ponta-a;ponta-b;textoconexao;strokeWidth;strokeColor;dashed;fontStyle;fontSize
       Exemplo:
         RTCO-SPO99-99;RTOC-SPO98-99;Link Principal;2;#036897;0;1;14

    2. elementos.csv (OPCIONAL - necessário para layout geográfico ou regionalização das camadas)
       Caso arquivo não existente, elemento não encontrado ou elemento sem definições, serão utilizadas as informações do arquivo json para definir camada, nivel e cor.
       Formato:
         elemento;camada;nivel;cor;siteid;apelido
       Exemplo:
         RTCO-SPO99-99;CORE;1;#FF0000;SP01

    3. localidades.csv (OPCIONAL - necessário para layout geográfico ou regionalização das camadas)
       Formato:
         siteid;Localidade;RegiaoGeografica;Latitude;Longitude
       Exemplo:
         SP01;SAOPAULO;Sudeste;23.32.33.S;46.38.44.W

⚙️ CONFIG.JSON (PERSONALIZAÇÃO AVANÇADA):
----------------------------------------
    Arquivo essencial que controla toda aparência e comportamento das topologias.

    🔧 ESTRUTURA BÁSICA:
    {{
      "LAYER_COLORS": {{"INNER-CORE": "#036897", "default": "#036897"}},
      "LAYER_STYLES": {{
        "CORE": {{
          "shape": "mxgraph.cisco.routers.router",
          "width": 80,
          "height": 80
        }}
      }},
      "PAGE_DEFINITIONS": [{{"name": "VISÃO GERAL", "visible_layers": null}}]
    }}

📌 SEÇÕES PRINCIPAIS:

    1. LAYER_COLORS:
       • Define cores para cada camada da rede
       • Formato HEX (com ou sem #)
       • Ex: "CORE": "036897"

    2. LAYER_STYLES:
       • Configura aparência dos equipamentos
       • Principais propriedades:
         - shape: Forma do equipamento (ex: mxgraph.cisco.routers.router)
         - width/height: Tamanho do ícone
         - fillColor: Cor de preenchimento (sobrescreve LAYER_COLORS)
       • Ex: "width": 100

    3. LAYER_DEFAULT_BY_PREFIX
	• Define a camada do elemento baseado em seu nome
 	• Ex: "RTCO": "camada": "CORE", "nivel": 1

    4. CONNECTION_STYLES
	• Define as caracteristicas das cores e formato das conexões por camada
 	• Ex: "CORE": "color": "#036897", "strokeWidth": "2"

    5. CONNECTION_STYLE_BASE
	• Define as caracteristicas de estilo das conexões
  
    6. PAGE_DEFINITIONS:
       • Cria múltiplas páginas/visões no diagrama
       • "visible_layers": null → mostra todas as camadas
       • Ex: {{"name": "VISÃO NORTE", "visible_layers": ["CORE_NORTE"]}}

    7. NODE_STYLE
	• Define as caraacteristicas de formato dos nós (roteadores, switchs, etc)

    8. LEGEND_CONFIG
	• Define as caracteristicas da legenda de todas as camadas

9. CONFIGURAÇÕES DE LAYOUT (Personalize cada algoritmo):
   • locked: 0=editável, 1=bloqueado (diagramas finais)
   • node_scale_factor: Escala global dos nós (ex: 0.5 = metade)

    a) CIRCULAR_LAYOUT:
       • center_x/y: Coordenadas do centro
       • base_radius: Raio do círculo interno
       • radius_increment: Aumento de raio por nível
       • Ex: "base_radius": 150

    b) ORGANIC_LAYOUT:
       • k_base: Distância base entre nós
       • iterations_per_node: Controla qualidade/performance
       • Ex: "k_base": 0.3

    c) GEOGRAPHIC_LAYOUT:
       • background_image: Imagem de fundo (mapa)
         - url: Caminho local/URL (ex: "brasil-map.png"), atentar que o algoritimo de repulsão vai terntar evitar sobreposição.
         - opacity: Transparência (0-100)
       • min_distance: Espaçamento entre nós
       • Ex: "opacity": 40

    d) HIERARCHICAL_LAYOUT:
       • vertical_spacing: Espaço entre níveis
       • horizontal_spacing: Espaço entre nós
       • Ex: "vertical_spacing": 200

🔍 EXEMPLOS PRÁTICOS:
--------------------

    1. GERAÇÃO SIMPLES (Linux):
       python GeradorTopologias.py -t cog -r redes.csv

    2. WINDOWS COM OPÇÕES AVANÇADAS:
       python GeradorTopologias.py -y -t gh -e "C:\\\\dados\\\\equipamentos.csv" rede_principal.csv

    3. ATIVANDO LOGS E REGIONALIZAÇÃO:
       python GeradorTopologias.py -l -r -t co campus_sp.csv

🛠️ DICAS TÉCNICAS:
------------------
    1. Formas disponíveis (mxgraph):
       • Equipamentos: mxgraph.cisco.routers.router
       • Servidores: mxgraph.office.machines.server
       • Firewalls: mxgraph.cisco.security.firewall

    2. Para nós sobrepostos no layout geográfico:
       • Aumente min_distance no config.json
       • Adicione min_node_distance

    3. Nós sem coordenadas:
       • São automaticamente posicionados em espiral no centro do mapa

    4. Problemas com acentos:
       • Salve arquivos CSV como UTF-8

⚠️ SOLUÇÃO DE PROBLEMAS COMUNS:
-------------------------------
    Problema: "Erro ao decodificar JSON"
    Solução:  Valide seu config.json em https://jsonlint.com/

    Problema: Layout geográfico não gerado
    Solução:  Verifique:
              • Formato das coordenadas em localidades.csv
              • Correspondência entre siteid e equipamentos

    Problema: Diagrama desorganizado
    Solução:  Ajuste parâmetros no config.json:
              • Circular: aumente radius_increment
              • Orgânico: aumente k_base

📤 SAÍDA GERADA:
---------------
    Padrão de nomes: NomeArquivo_TIMESTAMP_layout.drawio
    Exemplo: rede_sp_20250615143045_geografico.drawio

    ⏱️ DICA FINAL: Visualize os arquivos em https://app.diagrams.net/

## Atualizações em https://github.com/flashbsb/Network-Topology-Generator-for-Drawio

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
### Passo a Passo Explicado:

1. **Início**  
   - Script é iniciado via linha de comando ou execução direta

2. **Modo de Execução**  
   - **CLI**: Ativado com argumentos na linha de comando
   - **GUI**: Ativado sem argumentos

3. **Processamento CLI**  
   - Valida argumentos (`-t`, `-r`, `-y`, etc.)
   - Configura sistema de logs (arquivo/tela)
   - Carrega `config.json`
   - Busca arquivos CSV no diretório especificado

4. **Interface Gráfica (GUI)**  
   - Carrega configuração padrão
   - Exibe janela interativa
   - Permite seleção de arquivos e opções visuais

5. **Busca de Arquivos**  
   - Verifica existência de:
     - `conexoes*.csv` (obrigatório)
     - `elementos.csv` (opcional)
     - `localidades.csv` (opcional)
   - Se não encontrar arquivos, volta para GUI

6. **Processamento Principal (por arquivo)**  
   a. **Instanciar Gerador**  
      - Inicializa estruturas de dados
      - Carrega mapeamento de localidades  
   
   b. **Ler Elementos**  
      - Processa `elementos.csv`
      - Determina camadas/níveis
      - Aplica cores personalizadas
   
   c. **Ler Conexões**  
      - Processa `conexoes.csv`
      - Cria relações entre equipamentos
      - Gera camadas de conexão
   
   d. **Aplicar Regionalização**  
      - Adiciona sufixos regionais às camadas (ex: `CORE_SUDESTE`)
      - Usa dados de `localidades.csv`
   
   e. **Validar Dados**  
      - Remove nós sem conexões (opcional)
      - Verifica consistência de cores
      - Identifica elementos sem coordenadas

7. **Geração de Layouts**  
   - Calcula posições conforme algoritmo selecionado:
     - **Circular**: Círculos concêntricos por nível
     - **Orgânico**: Algoritmo de força (networkx)
     - **Geográfico**: Posições por coordenadas geográficas
     - **Hierárquico**: Disposição em níveis verticais

8. **Geração do Diagrama**  
   - Cria arquivo `.drawio` com:
     - Múltiplas páginas/visões
     - Elementos posicionados
     - Conexões estilizadas
     - Legenda automática
     - Imagem de fundo (layout geográfico)

9. **Saída**  
   - Gera relatório final
   - Salva arquivos com timestamp
   - Exibe métricas de desempenho

## Interface Gráfica (GUI)

![Screenshot da Interface Gráfica](docs/images/gui-screenshot.png)
> *Captura da interface Gráfica principal mostrando layout*

## MIT License
https://github.com/flashbsb/Network-Topology-Generator-for-Drawio/blob/main/LICENSE
