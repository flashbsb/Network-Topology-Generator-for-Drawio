#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SCRIPT OTIMIZADO PARA GERAÇÃO DE TOPOLOGIAS DE REDE COM CLI e GUI
"""

import sys
import csv
import os
import re
import math
import logging
import uuid
import chardet
import json
import networkx as nx
import time
import random
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from datetime import datetime
from collections import defaultdict
import platform
import glob

versionctr = "vA1.19"

# Tente importar psutil para monitoramento de memória, mas não é obrigatório
PSUTIL_AVAILABLE = False
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    pass  # psutil não está instalado, mas não é crítico



# =====================================================
# GLOBAL HELP TEXT (ADICIONAR NO INÍCIO DO SCRIPT)
# =====================================================

HELP_TEXT = """
GERADOR DE TOPOLOGIAS DE REDE {versionctr}
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
		python -m pip install networkx chardet numpy pillow psutil

	# Linux Debian:
    1. Instalar Python 3 e pip (apt)
		apt update & apt install python3 pip python3-tk
    2. Instalar dependências Python
		python3 -m pip install networkx chardet numpy pillow psutil

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
         RTIC-SPO99-99;RTOC-SPO98-99;Link Principal;2;#036897;0;1;14

    2. elementos.csv (OPCIONAL - necessário para layout geográfico ou regionalização das camadas)
       Caso arquivo não existente, elemento não encontrado ou elemento sem definições, serão utilizadas as informações do arquivo json para definir camada, nivel e cor.
       Formato:
         elemento;camada;nivel;cor;siteid;apelido
       Exemplo:
         RTIC-SPO99-99;INNER-CORE;1;#FF0000;SP01

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
        "INNER-CORE": {{
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
       • Ex: "INNER-CORE": "036897"

    2. LAYER_STYLES:
       • Configura aparência dos equipamentos
       • Principais propriedades:
         - shape: Forma do equipamento (ex: mxgraph.cisco.routers.router)
         - width/height: Tamanho do ícone
         - fillColor: Cor de preenchimento (sobrescreve LAYER_COLORS)
       • Ex: "width": 100

    3. LAYER_DEFAULT_BY_PREFIX
	• Define a camada do elemento baseado em seu nome
 	• Ex: "RTIC": "camada": "INNER-CORE", "nivel": 1

    4. CONNECTION_STYLES
	• Define as caracteristicas das cores e formato das conexões por camada
 	• Ex: "INNER-CORE": "color": "#036897", "strokeWidth": "2"

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

Atualizações em https://github.com/flashbsb/Network-Topology-Generator-for-Drawio

## MIT License
https://github.com/flashbsb/Network-Topology-Generator-for-Drawio/blob/main/LICENSE
""".format(versionctr=versionctr)

# Configuração de logging será feita no main() com timestamp
logger = logging.getLogger(__name__)

# Função para logar uso de memória
def log_memory_usage(message=""):
    """Registra uso de memória com mensagem opcional"""
    if not PSUTIL_AVAILABLE:
        return
    
    try:
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss / 1024 / 1024  # MB
        logger.debug("🧠 %sUso de memória: %.2f MB", f"{message} - " if message else "", mem)
    except Exception as e:
        logger.error("Falha ao medir memória: %s", str(e))

# Templates XML para geração do arquivo draw.io
DRAWIO_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="{timestamp}" agent="Mozilla/5.0" etag="{etag}" version="21.3.7">
"""

DRAWIO_DIAGRAM_TEMPLATE = """  <diagram name="{page_name}" id="{diagram_id}">
    <mxGraphModel dx="1422" dy="793" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="0" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="1">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
"""

DRAWIO_FOOTER = """
</mxfile>
"""

# =====================================================
# GUI IMPLEMENTATION
# =====================================================

class TopologyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Gerador de Topologias de Rede - Drawio") 
        self.root.geometry("500x800")
        self.root.resizable(True, True)
        
        # Configurações padrão
        self.config = self.load_config()
        self.connection_files = []
        self.elementos_file = "elementos.csv" if os.path.exists("elementos.csv") else ""
        self.localidades_file = "localidades.csv" if os.path.exists("localidades.csv") else ""
        
        # Variáveis de controle
        self.include_orphans = tk.BooleanVar(value=False)
        self.regionalization = tk.BooleanVar(value=False)
        self.circular_layout = tk.BooleanVar(value=True)
        self.organic_layout = tk.BooleanVar(value=False)
        self.geographic_layout = tk.BooleanVar(value=False)
        self.hierarchical_layout = tk.BooleanVar(value=False)
        self.generate_logs = tk.BooleanVar(value=False)  # Nova opção para logs
        self.ignore_optional = tk.BooleanVar(value=False)
        
        # Variáveis de controle - inicializar como False
        self.hide_connection_layers = tk.BooleanVar(value=False)  # Valor inicial desmarcado
        self.hide_node_names = tk.BooleanVar(value=False)         # Valor inicial desmarcado     
        
        # Verificar disponibilidade de recursos
        self.has_elementos = os.path.exists("elementos.csv")
        self.has_localidades = os.path.exists("localidades.csv")
        self.has_config = os.path.exists("config.json")
        
        # Criar interface
        self.create_widgets()
        
        # Atualizar estado inicial dos controles
        self.update_ui_state()
        
        # Adicionar referência ao texto de ajuda
        self.help_text = HELP_TEXT
        
    def load_config(self):
        """Tenta carregar o config.json ou retorna padrão se não existir"""
        config_file = 'config.json'
        default_config = {
            "LAYER_STYLES": {},
            "LAYER_COLORS": {"default": "#036897"},
            "PAGE_DEFINITIONS": [{"name": "VISÃO GERAL", "visible_layers": None}],
            "CIRCULAR_LAYOUT": {"center_x": 500, "center_y": 500, "base_radius": 100, "radius_increment": 50},
            "ORGANIC_LAYOUT": {"k_base": 0.25, "k_min": 0.8, "k_max": 2.5, "iterations_per_node": 10},
            "GEOGRAPHIC_LAYOUT": {"canvas_width": 1000, "canvas_height": 800, "margin": 50, "min_distance": 30},
            "NODE_STYLE": {"shape": "mxgraph.cisco.routers.router", "fillColor": "#ffffff", "strokeColor": "#000000"},
            "CONNECTION_STYLE_BASE": {"edgeStyle": "orthogonalEdgeStyle", "curved": "0", "rounded": "0"},
            "CONNECTION_STYLES": {"default": {"color": "#000000", "strokeWidth": "2"}},
            "LEGEND_CONFIG": {"position": {"x": 50, "y": 30}, "item_spacing": 40}
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Logar informações da configuração
                logger.debug("⚙️ Configurações carregadas:")
                logger.debug("  - Páginas: %s", [p['name'] for p in config["PAGE_DEFINITIONS"]])
                logger.debug("  - Cores de camada: %s", list(config["LAYER_COLORS"].keys()))
                
                # Logar parâmetros de layout
                for layout in ["CIRCULAR_LAYOUT", "ORGANIC_LAYOUT", "GEOGRAPHIC_LAYOUT", "HIERARCHICAL_LAYOUT"]:
                    if layout in config:
                        logger.debug("  - %s: %s", layout, json.dumps(config[layout], indent=2))
                
                return config
            return default_config
        except Exception as e:
            logger.exception("Erro ao carregar configuração", exc_info=True)
            return default_config

    def create_widgets(self):
        # Frame principal com scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        title = ttk.Label(scrollable_frame, text=f"Gerador de Topologias de Rede - Drawio", 
                         font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        # Frame de status
        status_frame = ttk.LabelFrame(scrollable_frame, text="Status de Recursos")
        status_frame.grid(row=1, column=0, columnspan=3, sticky="we", padx=5, pady=5)
        status_frame.columnconfigure(1, weight=1)
        
        # Status dos arquivos
        ttk.Label(status_frame, text="config.json:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        config_status = ttk.Label(status_frame, text="✔ Disponível" if self.has_config else "❌ Não encontrado", 
                                foreground="green" if self.has_config else "red")
        config_status.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(status_frame, text="elementos.csv:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        elementos_status = ttk.Label(status_frame, text="✔ Disponível" if self.has_elementos else "⚠ Opcional não encontrado", 
                                   foreground="green" if self.has_elementos else "orange")
        elementos_status.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(status_frame, text="localidades.csv:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        localidades_status = ttk.Label(status_frame, text="✔ Disponível" if self.has_localidades else "⚠ Opcional não encontrado", 
                                     foreground="green" if self.has_localidades else "orange")
        localidades_status.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # Frame de arquivos
        files_frame = ttk.LabelFrame(scrollable_frame, text="Arquivos de Entrada")
        files_frame.grid(row=2, column=0, columnspan=3, sticky="we", padx=5, pady=10)
        files_frame.columnconfigure(2, weight=1)
        
        # Conexões
        ttk.Label(files_frame, text="Arquivo(s) de Conexões:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Button(files_frame, text="Selecionar...", command=self.select_connection_files).grid(row=0, column=1, padx=5, pady=5)
        self.connections_label = ttk.Label(files_frame, text="Nenhum selecionado", foreground="gray", wraplength=400)
        self.connections_label.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        # Elementos
        ttk.Label(files_frame, text="Arquivo de Elementos:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Button(files_frame, text="Selecionar...", command=self.select_elementos_file).grid(row=1, column=1, padx=5, pady=5)
        self.elementos_label = ttk.Label(files_frame, text=self.elementos_file if self.elementos_file else "Padrão (elementos.csv)", 
                                       foreground="blue", wraplength=400)
        self.elementos_label.grid(row=1, column=2, sticky="w", padx=5, pady=5)
        
        # Localidades
        ttk.Label(files_frame, text="Arquivo de Localidades:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Button(files_frame, text="Selecionar...", command=self.select_localidades_file).grid(row=2, column=1, padx=5, pady=5)
        self.localidades_label = ttk.Label(files_frame, text=self.localidades_file if self.localidades_file else "Padrão (localidades.csv)", 
                                         foreground="blue", wraplength=400)
        self.localidades_label.grid(row=2, column=2, sticky="w", padx=5, pady=5)
        
        # Frame de opções
        options_frame = ttk.LabelFrame(scrollable_frame, text="Opções de Geração")
        options_frame.grid(row=3, column=0, columnspan=3, sticky="we", padx=5, pady=10)
        
        # Opções de processamento
        self.orphans_check = ttk.Checkbutton(options_frame, text="Incluir elementos sem conexões", 
                       variable=self.include_orphans)
        self.orphans_check.pack(anchor="w", padx=5, pady=5)
        
        self.ignore_optional_check = ttk.Checkbutton(
            options_frame, 
            text="Remover customizações opcionais dos elementos e conexões",
            variable=self.ignore_optional
        )
        self.ignore_optional_check.pack(anchor="w", padx=5, pady=5)        
        
        self.regional_check = ttk.Checkbutton(options_frame, text="Regionalização das camadas", 
                       variable=self.regionalization)
        self.regional_check.pack(anchor="w", padx=5, pady=5)
        
        # Novas opções de visualização
        self.hide_conn_check = ttk.Checkbutton(options_frame, text="Ocultar camadas de conexão", 
                       variable=self.hide_connection_layers)
        self.hide_conn_check.pack(anchor="w", padx=5, pady=5)
        
        self.hide_names_check = ttk.Checkbutton(options_frame, text="Gerar elementos sem nomes", 
                       variable=self.hide_node_names)
        self.hide_names_check.pack(anchor="w", padx=5, pady=5)
        
        # Nova opção para gerar logs
        self.logs_check = ttk.Checkbutton(options_frame, text="Gerar logs", 
                       variable=self.generate_logs)
        self.logs_check.pack(anchor="w", padx=5, pady=5)
        
        # Layouts
        layouts_frame = ttk.LabelFrame(options_frame, text="Layouts")
        layouts_frame.pack(fill="x", padx=5, pady=5)
        
        buttons_frame = ttk.Frame(layouts_frame)
        buttons_frame.pack(pady=5)

        # Botão "Marcar todos"
        self.mark_all_btn = ttk.Button(
            buttons_frame, 
            text="Marcar Todos",
            command=self.mark_all_layouts
        )
        self.mark_all_btn.pack(side="left", padx=5)

        # Botão "Desmarcar todos"
        self.unmark_all_btn = ttk.Button(
            buttons_frame, 
            text="Desmarcar Todos",
            command=self.unmark_all_layouts
        )
        self.unmark_all_btn.pack(side="left", padx=5)

        # Individual layout checkboxes
        layouts_grid = ttk.Frame(layouts_frame)
        layouts_grid.pack(fill="x", padx=20, pady=(0, 5))
        
        self.circular_check = ttk.Checkbutton(layouts_grid, text="Circular", variable=self.circular_layout)
        self.circular_check.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.organic_check = ttk.Checkbutton(layouts_grid, text="Orgânico", variable=self.organic_layout)
        self.organic_check.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        self.geographic_check = ttk.Checkbutton(layouts_grid, text="Geográfico", variable=self.geographic_layout)
        self.geographic_check.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        self.hierarchical_check = ttk.Checkbutton(layouts_grid, text="Hierárquico", variable=self.hierarchical_layout)
        self.hierarchical_check.grid(row=0, column=3, padx=10, pady=5, sticky="w")
        
        # Frame de ação
        action_frame = ttk.Frame(scrollable_frame)
        action_frame.grid(row=4, column=0, columnspan=3, sticky="we", padx=5, pady=20)
        
        # Botão de geração
        generate_btn = ttk.Button(action_frame, text="Gerar Topologias", command=self.generate_topologies,
                                 style="Accent.TButton")
        generate_btn.pack(pady=10, ipadx=20, ipady=10)

        # Botão de Ajuda (adicionar após o título)
        help_btn = ttk.Button(
            scrollable_frame, 
            text="Ajuda", 
            command=self.show_help,
            style="Help.TButton"
        )
        help_btn.grid(row=5, column=2, sticky="ne", padx=10, pady=(0, 15)) 
 
        # Barra de status
        self.status_var = tk.StringVar(value="Pronto para gerar topologias")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")
        
        # Estilo para o botão principal
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"), foreground="#00008B", background="#036897")
        
        # Estilo para botão de ajuda
        style.configure("Help.TButton", 
                        font=("Arial", 10, "bold"), 
                        foreground="#000000",
                        background="#FF8C00")

    def show_help(self):
        """Exibe janela de ajuda com conteúdo completo"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Ajuda do Gerador de Topologias")
        help_window.geometry("900x700")
        help_window.resizable(True, True)
        
        # Frame principal
        main_frame = ttk.Frame(help_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Área de texto com rolagem
        text_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#F0F0F0",
            padx=10,
            pady=10
        )
        text_area.pack(fill=tk.BOTH, expand=True)
        
        # Inserir texto de ajuda
        text_area.insert(tk.INSERT, self.help_text)
        text_area.configure(state="disabled")  # Somente leitura
        
        # Botão de fechar
        close_btn = ttk.Button(
            main_frame,
            text="Fechar",
            command=help_window.destroy
        )
        close_btn.pack(pady=10)


    def mark_all_layouts(self):
        """Marca todos os layouts disponíveis com tratamento especial para geográfico"""
        self.circular_layout.set(True)
        self.organic_layout.set(True)
        self.hierarchical_layout.set(True)
        
        # Verificar disponibilidade dos arquivos diretamente
        if self.has_elementos and self.has_localidades:
            self.geographic_layout.set(True)

    def unmark_all_layouts(self):
        """Desmarca todos os layouts disponíveis"""
        self.circular_layout.set(False)
        self.organic_layout.set(False)
        self.hierarchical_layout.set(False)
        self.geographic_layout.set(False)

    def update_ui_state(self):
        # Atualizar estado dos controles baseado na disponibilidade de arquivos
        self.has_elementos = os.path.exists(self.elementos_file) if self.elementos_file else False
        self.has_localidades = os.path.exists(self.localidades_file) if self.localidades_file else False
        
        # Habilitar/desabilitar controles
        state_orphans = "normal" if self.has_elementos else "disabled"
        self.orphans_check.configure(state=state_orphans)
        
        # Regionalização requer elementos E localidades
        state_regional = "normal" if (self.has_elementos and self.has_localidades) else "disabled"
        self.regional_check.configure(state=state_regional)
        
        # Layout geográfico requer elementos E localidades
        state_geo = "normal" if (self.has_elementos and self.has_localidades) else "disabled"
        self.geographic_check.configure(state=state_geo)
        
        # Atualizar variáveis se arquivos não existirem
        if not self.has_localidades:
            self.regionalization.set(False)
            self.geographic_layout.set(False)
        
        if not self.has_config:
            self.ignore_optional_check.configure(state="disabled")
            self.ignore_optional.set(False)
        
        # Atualizar estado dos botões
        self.update_button_states()

    def update_button_states(self):
        """Atualiza estado dos botões baseado na disponibilidade de recursos"""
        self.mark_all_btn["state"] = "normal"
        self.unmark_all_btn["state"] = "normal"
        
    def select_connection_files(self):
        files = filedialog.askopenfilenames(
            title="Selecione arquivo(s) de conexões",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
        )
        if files:
            self.connection_files = list(files)
            file_names = ", ".join([os.path.basename(f) for f in files[:3]])
            if len(files) > 3:
                file_names += f", ... (+{len(files)-3} mais)"
            self.connections_label.config(text=file_names, foreground="blue")

    def select_elementos_file(self):
        file = filedialog.askopenfilename(
            title="Selecione arquivo de elementos",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
        )
        if file:
            self.elementos_file = file
            self.elementos_label.config(text=os.path.basename(file), foreground="blue")
            self.update_ui_state()

    def select_localidades_file(self):
        file = filedialog.askopenfilename(
            title="Selecione arquivo de localidades",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
        )
        if file:
            self.localidades_file = file
            self.localidades_label.config(text=os.path.basename(file), foreground="blue")
            self.update_ui_state()

    def generate_topologies(self):
        hide_node_names = self.hide_node_names.get()
        hide_connection_layers = self.hide_connection_layers.get()
        
        if not self.connection_files:
            messagebox.showerror("Erro", "Selecione pelo menos um arquivo de conexões!")
            return
            
        if not any([self.circular_layout.get(), self.organic_layout.get(), 
                   self.geographic_layout.get(), self.hierarchical_layout.get()]):
            messagebox.showerror("Erro", "Selecione pelo menos um tipo de layout!")
            return
            
        # Configurar logging se necessário
        if self.generate_logs.get():
            log_file = f'topologia_gui_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.info("Logs habilitados, gravando em: %s", log_file)

            # Novo registro de informações
            logger.info("Execução iniciada via GUI")
            logger.info("Opções usadas (diferentes do padrão):")
            
            # Verificar diferenças em relação ao padrão
            if self.include_orphans.get():
                logger.info("  Incluir nós órfãos")
            if self.regionalization.get():
                logger.info("  Regionalização")
                
            layouts = ""
            if self.circular_layout.get(): layouts += "c"
            if self.organic_layout.get(): layouts += "o"
            if self.geographic_layout.get(): layouts += "g"
            if self.hierarchical_layout.get(): layouts += "h"
            if layouts != "c":  # Padrão é apenas circular
                logger.info("  Layouts: %s", layouts)
                
            if self.elementos_file != "elementos.csv":
                logger.info("  Elementos: %s", self.elementos_file)
            if self.localidades_file != "localidades.csv":
                logger.info("  Localidades: %s", self.localidades_file)
                
            if self.hide_node_names.get():
                logger.info("  Ocultar nomes dos nós")
            if self.hide_connection_layers.get():
                logger.info("  Ocultar camadas de conexão")
        
        # Registrar informações do sistema
        logger.debug("Sistema: %s %s", sys.platform, platform.platform())
        logger.debug("Python: %s", sys.version)
        logger.debug("Dependências: networkx=%s", nx.__version__)
        
        # Determinar layouts selecionados
        layouts = ""
        if self.circular_layout.get(): layouts += "c"
        if self.organic_layout.get(): layouts += "o"
        if self.geographic_layout.get(): layouts += "g"
        if self.hierarchical_layout.get(): layouts += "h"
        
        # Criar instância de configuração
        config = self.load_config()
        
        # Processar cada arquivo
        success = True
        total_files = len(self.connection_files)
        
        for idx, file in enumerate(self.connection_files):
            self.status_var.set(f"Processando arquivo {idx+1}/{total_files}: {os.path.basename(file)}")
            self.root.update()
            
            try:
                # CORREÇÃO: Passar os parâmetros na ordem correta
                result = self.process_single_file(
                    file, 
                    config, 
                    self.include_orphans.get(), 
                    layouts, 
                    self.regionalization.get(),
                    self.elementos_file,
                    self.localidades_file,
                    hide_node_names,          # Corrigido
                    hide_connection_layers,    # Corrigido
                    ignore_optional=self.ignore_optional.get()
                )
                if not result:
                    success = False
                    self.status_var.set(f"Erro ao processar: {os.path.basename(file)}")
            except Exception as e:
                logger.error(f"Erro ao processar {file}: {str(e)}", exc_info=True)
                success = False
                self.status_var.set(f"Erro grave em: {os.path.basename(file)}")
        
        if success:
            messagebox.showinfo("Sucesso", "Todas as topologias foram geradas com sucesso!")
            self.status_var.set("Processamento concluído com sucesso")
        else:
            messagebox.showwarning("Aviso", "Algumas topologias podem não ter sido geradas corretamente. Verifique os logs.")
            self.status_var.set("Processamento concluído com erros")
            
        # Log final de memória
        log_memory_usage("Final do processamento")

    def process_single_file(self, conexoes_file, config, include_orphans, layouts_choice, 
                            regionalization, elementos_file, localidades_file, 
                            hide_node_names, hide_connection_layers, ignore_optional):
        """Processa um arquivo de conexões completo"""
        file_start = time.perf_counter()
        logger.info("⏱️ [INICIO] Processando arquivo: %s", conexoes_file)
        logger.debug("Parâmetros: orphans=%s, layouts=%s, regional=%s, hide_names=%s, hide_cnx=%s",
                    include_orphans, layouts_choice, regionalization, 
                    hide_node_names, hide_connection_layers)
        
        try:
            # Criar instância do gerador com arquivos personalizados
            generator = TopologyGenerator(
                elementos_file=elementos_file, 
                conexoes_file=conexoes_file, 
                config=config, 
                include_orphans=include_orphans, 
                regionalization=regionalization,
                localidades_file=localidades_file,
                hide_node_names=hide_node_names,            # Nova opção
                hide_connection_layers=hide_connection_layers, # Nova opção
                ignore_optional=ignore_optional
            )
            
            if not generator.valid:
                return False
                
            if not generator.read_elementos():
                return False
                
            if not generator.read_conexoes():
                return False
                
            base_name = os.path.splitext(conexoes_file)[0]
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            success = True
            
            # Dicionário de mapeamento de layouts
            layout_map = {
                'c': ('circular', 'Circular'),
                'o': ('organico', 'Orgânico'),
                'g': ('geografico', 'Geográfico'),
                'h': ('hierarquico', 'Hierárquico')
            }
            
            generated_layouts = []
            
            # Gerar layouts selecionados
            for char in layouts_choice:
                if char in layout_map:
                    layout_key, layout_name = layout_map[char]
                    
                    # Verificar disponibilidade do geográfico
                    if char == 'g' and not generator.has_geographic_data:
                        logger.warning("Layout geográfico solicitado mas sem dados geográficos. Ignorando.")
                        continue
                    
                    layout_start = time.perf_counter()
                    output_file = f"{base_name}_{timestamp}_{layout_key}.drawio"
                    if generator.generate_drawio(output_file, layout_key):
                        gen_time = time.perf_counter() - layout_start
                        logger.info("✅ %s gerado em %.2fs (%.1fKB)", 
                                  layout_name, gen_time, os.path.getsize(output_file)/1024)
                        generated_layouts.append(layout_name)
                    else:
                        success = False
            
            # Log de performance detalhada
            file_time = time.perf_counter() - file_start
            logger.info("✅ [SUCESSO] Arquivo processado em %.2fs | Layouts: %s | Nós: %d | Conexões: %d",
                      file_time, ', '.join(generated_layouts), 
                      len(generator.nodes), len(generator.connections))
            
            # Registrar elementos sem siteid
            if generator.nodes_without_siteid:
                nodes_list = ", ".join(generator.nodes_without_siteid[:10])
                if len(generator.nodes_without_siteid) > 10:
                    nodes_list += f", ... (+{len(generator.nodes_without_siteid) - 10} mais)"
                logger.debug("%d elementos sem siteid movidos para camada especial: %s", 
                              len(generator.nodes_without_siteid), nodes_list)        
            
            return success
        except Exception as e:
            logger.exception("💥 [FALHA] Erro no processamento")
            logger.error("Contexto: layouts=%s, regional=%s, elementos=%s",
                       layouts_choice, regionalization, elementos_file)
            return False

# =====================================================
# CORE FUNCTIONALITY
# =====================================================

def load_config(config_file='config.json'):
    """Carrega configurações do arquivo JSON com tratamento robusto de erros"""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        logger.info("Configurações carregadas de %s", config_file)
        
        # Converter estrutura antiga LAYER_SHAPES para nova LAYER_STYLES
        if "LAYER_SHAPES" in config and "LAYER_STYLES" not in config:
            config["LAYER_STYLES"] = {}
            for layer, shape in config["LAYER_SHAPES"].items():
                config["LAYER_STYLES"][layer] = {"shape": shape}
            logger.info("Convertido LAYER_SHAPES para LAYER_STYLES")
            
        # Logar informações da configuração
        logger.debug("⚙️ Configurações carregadas:")
        logger.debug("  - Páginas: %s", [p['name'] for p in config["PAGE_DEFINITIONS"]])
        logger.debug("  - Cores de camada: %s", list(config["LAYER_COLORS"].keys()))
        
        # Logar parâmetros de layout
        for layout in ["CIRCULAR_LAYOUT", "ORGANIC_LAYOUT", "GEOGRAPHIC_LAYOUT", "HIERARCHICAL_LAYOUT"]:
            if layout in config:
                logger.debug("  - %s: %s", layout, json.dumps(config[layout], indent=2))
            
        return config
        
    except FileNotFoundError:
        logger.critical("Arquivo de configuração não encontrado: %s", config_file)
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.critical("Erro ao decodificar JSON em %s: %s", config_file, str(e))
        sys.exit(1)
        
def verificar_dependencias():
    """Verifica dependências críticas e informa como instalar"""
    dependencias = {
        "tkinter": "Interface gráfica (normalmente já incluída no Python)",
        "networkx": "Gerenciamento de grafos e layouts",
        "chardet": "Detecção de codificação de arquivos"
    }
    
    faltando = []
    for modulo, descricao in dependencias.items():
        try:
            __import__(modulo)
        except ImportError:
            faltando.append((modulo, descricao))
    
    if faltando:
        print("ERRO: Dependências faltando!")
        print("="*50)
        for modulo, descricao in faltando:
            print(f"• {modulo} ({descricao})")
        
        print("\nInstale os pacotes faltantes com:")
        print("pip install " + " ".join([m[0] for m in faltando]))
        print("\nBaixe o Python completo em: https://python.org/downloads")
        input("Pressione Enter para sair...")
        sys.exit(1)

class TopologyGenerator:
    def __init__(self, elementos_file, conexoes_file, config, include_orphans=False, 
                 regionalization=False, localidades_file='localidades.csv',
                 hide_node_names=False, hide_connection_layers=False,
                 ignore_optional=False):
        self.elementos_file = elementos_file
        self.conexoes_file = conexoes_file
        self.config = config
        self.include_orphans = include_orphans
        self.regionalization = regionalization
        self.localidades_file = localidades_file
        self.nodes = defaultdict(dict)
        self.connections = []
        self.layers = defaultdict(list)
        self.node_ids = {}
        self.layer_ids = {}
        self.circular_alignments = defaultdict(list)
        self.node_colors = defaultdict(list)
        self.valid = True
        self.localidades_map = self._load_localidades()
        self.has_geographic_data = False
        self.nodes_without_siteid = []  # Nova lista para nós sem siteid
        self.ignore_optional = ignore_optional 
        
        # Novas opções de visualização
        self.hide_node_names = hide_node_names
        self.hide_connection_layers = hide_connection_layers
        logger.info(f"Opções: hide_node_names={hide_node_names}, hide_connection_layers={hide_connection_layers}")
        
        self._initialize() 
        logger.info("Inicialização concluída")
    
    def _dms_to_decimal(self, dms_str, coord_type, site_id):
        """
        Converte coordenadas DMS para decimal com tratamento robusto
        
        Args:
            dms_str (str): Coordenada no formato DMS
            coord_type (str): 'lat' ou 'lon'
            site_id (str): ID do site para logs
            
        Returns:
            float: Valor decimal ou None se falhar
        """
        if not dms_str or str(dms_str).strip() == '':
            logger.error("Coordenada vazia para site %s", site_id)
            return None
        
        try:
            # Pré-processamento da string
            dms_clean = str(dms_str).strip().upper()
            direcao = None
            
            # Extrair direção (N/S/E/W)
            if dms_clean[-1] in ['N', 'S', 'E', 'W']:
                direcao = dms_clean[-1]
                dms_clean = dms_clean[:-1].strip()
            
            # Normalizar formato
            dms_clean = dms_clean.replace(',', '.').replace(' ', '')
            parts = [p for p in dms_clean.split('.') if p != '']
            
            if len(parts) < 2:
                logger.error("Formato inválido para site %s: %s", site_id, dms_str)
                return None
            
            # Combinar partes fracionadas
            if len(parts) > 3:
                seconds_str = '.'.join(parts[2:])
                parts = parts[:2] + [seconds_str]
            
            # Converter para floats
            try:
                graus = float(parts[0])
                minutos = float(parts[1])
                segundos = float(parts[2]) if len(parts) > 2 else 0.0
            except ValueError as e:
                logger.error("Valor não numérico em %s: %s", site_id, dms_str)
                return None
            
            # Calcular valor decimal
            decimal = graus + minutos/60 + segundos/3600
            
            # Determinar direção padrão se não especificada
            if not direcao:
                if coord_type == 'lat': direcao = 'S'
                elif coord_type == 'lon': direcao = 'W'
            
            # Aplicar sinal conforme direção
            if direcao in ['S', 'W']:
                decimal = -decimal
                
            return decimal
            
        except Exception as e:
            logger.error("Erro na conversão para site %s: %s - %s", site_id, dms_str, str(e))
            return None
            
    def _update_node_layer(self, node_name, old_camada, new_camada, nivel):
        """Atualiza o registro de camadas quando a camada de um nó é alterada"""
        # Remover da camada antiga
        if old_camada in self.layers and node_name in self.layers[old_camada]:
            self.layers[old_camada].remove(node_name)
        
        # Atualizar camada no nó
        self.nodes[node_name]['camada'] = new_camada
        
        # Registrar na nova camada
        self._register_node(node_name, nivel)

    def _determine_layer_by_prefix(self, node_name):
        """Determina camada/nível baseado em prefixos do config"""
        prefix_map = self.config.get("LAYER_DEFAULT_BY_PREFIX", {})
        for prefix in sorted(prefix_map.keys(), key=len, reverse=True):
            if node_name.startswith(prefix):
                layer_info = prefix_map[prefix]
                return layer_info["camada"], layer_info["nivel"]
        
        # Se não encontrado, usa default
        default_info = prefix_map.get("default", {"camada": "default", "nivel": 10})
        return default_info["camada"], default_info["nivel"]


    def _load_localidades(self):
        """
        Carrega mapeamento de localidades para dados geográficos
        
        Returns:
            dict: Mapeamento localidade -> {regiao, latitude, longitude}
        """
        if not os.path.exists(self.localidades_file):
            logger.info("Arquivo localidades.csv não encontrado")
            return {}
        
        try:
            encoding = self._detect_encoding(self.localidades_file)
            mapping = {}
            with open(self.localidades_file, 'r', encoding=encoding, errors='replace') as f:
                reader = csv.DictReader(f, delimiter=';')
                valid_count = 0
                invalid_count = 0
                
                for row in reader:
                    site_id = row.get('siteid', '').strip()
                    localidade = row.get('Localidade', '').strip()
                    regiao = row.get('RegiaoGeografica', '').strip()
                    lat_str = row.get('Latitude', '').strip()
                    lon_str = row.get('Longitude', '').strip()
                    
                    if not site_id:
                        site_id = f"Linha {reader.line_num}"
                    
                    # Validar dados obrigatórios
                    if not all([localidade, regiao, lat_str, lon_str]):
                        logger.warning("Dados incompletos para site %s", site_id)
                        continue
                    
                    # Converter coordenadas
                    lat_decimal = self._dms_to_decimal(lat_str, 'lat', site_id)
                    lon_decimal = self._dms_to_decimal(lon_str, 'lon', site_id)
                    
                    if None in [lat_decimal, lon_decimal]:
                        invalid_count += 1
                        continue
                    
                    # Armazenar dados válidos
                    mapping[site_id] = {  # Alterado para usar siteid como chave
                        'regiao': regiao,
                        'latitude': lat_decimal,
                        'longitude': lon_decimal
                    }
                    valid_count += 1
                
                logger.info("Mapeamento carregado: %d válidas, %d inválidas", valid_count, invalid_count)
            return mapping
        except Exception as e:
            logger.error("Erro ao carregar localidades: %s", str(e))
            return {}

    def _initialize(self):
        """Verifica arquivos (elementos.csv agora opcional)"""
        if not os.path.exists(self.conexoes_file):
            logger.error("Arquivo de conexões não encontrado: %s", self.conexoes_file)
            self.valid = False
            return
            
        # Sempre definir um encoding padrão
        self.encoding_elementos = 'utf-8'  # Valor padrão
        
        # Detecção de encoding condicional
        if os.path.exists(self.elementos_file):
            self.encoding_elementos = self._detect_encoding(self.elementos_file)
            
        self.encoding_conexoes = self._detect_encoding(self.conexoes_file)
        logger.info("Codificações detectadas: elementos=%s, conexoes=%s", 
                   self.encoding_elementos, self.encoding_conexoes)

    def _detect_encoding(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(4)  # Lê suficiente para detectar BOM
                
                # Verifica presença de BOM UTF-8
                if raw_data.startswith(b'\xef\xbb\xbf'):
                    return 'utf-8-sig'
                
                # Detecção padrão para outros casos
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'
                return 'utf-8-sig' if encoding.lower() == 'utf-8' else encoding
        except Exception as e:
            logger.error("Falha ao detectar encoding: %s", str(e))
            return 'utf-8-sig'  # Padrão seguro para Windows

    def _normalize_color(self, color_str):
        """
        Normaliza valores de cor para formato hexadecimal
        
        Args:
            color_str (str): Valor de cor
            
        Returns:
            str: Cor normalizada ou 'none'
        """
        if color_str is None:
            return None
        if not isinstance(color_str, str):
            return str(color_str)
        if color_str.lower() == "none":
            return "none"
        if not color_str.startswith('#') and color_str != "":
            return f'#{color_str}'
        return color_str

    def read_elementos(self):
        if not os.path.exists(self.elementos_file):
            logger.warning("Arquivo de elementos não encontrado. Continuando sem ele.")
            return True
            
        try:
            with open(self.elementos_file, 'r', encoding=self.encoding_elementos, errors='replace') as f:
                # Verificar cabeçalhos obrigatórios
                header = f.readline().strip().split(';')
                if 'elemento' not in header:
                    logger.error("Cabeçalho 'elemento' não encontrado em elementos.csv")
                    return False
                    
                f.seek(0)  # Voltar ao início
                reader = csv.DictReader(f, delimiter=';')
                row_count = 0
                for row in reader:
                    row_count += 1
                    self._process_elemento_row(row)
                
                logger.info("Processadas %d linhas de elementos", row_count)
                return True
                
        except Exception as e:
            logger.error("Falha na leitura de elementos: %s", str(e), exc_info=True)
            return False

    def _apply_regionalization(self, node_name, node_data):
        """Aplica dados regionais se a flag estiver ativa (modifica a camada)"""
        if not self.regionalization or not self.localidades_map:
            return
            
        # Verificar se a regionalização já foi aplicada
        if node_data.get('regionalized'):
            return
            
        siteid = node_data.get('siteid', '')
        if siteid and siteid in self.localidades_map:
            loc_data = self.localidades_map[siteid]
            regiao = loc_data['regiao']
            old_camada = node_data['camada']
            
            # Aplicar apenas se ainda não tiver sufixo regional
            if not old_camada.endswith(f"_{regiao}"):
                new_camada = f"{old_camada}_{regiao}"
                
                # Aplicar atualização de camada
                self._update_node_layer(node_name, old_camada, new_camada, node_data['nivel'])
                logger.debug(f"Regionalização aplicada a {node_name}: {old_camada} -> {new_camada}")
                
                # Marcar como regionalizado
                node_data['regionalized'] = True
        else:
            # Mover para camada especial SEM_SITEID
            old_camada = node_data['camada']
            new_camada = "SEM_SITEID"
            self._update_node_layer(node_name, old_camada, new_camada, 10)  # Nível 10
            logger.debug(f"Elemento sem siteid movido para camada especial: {node_name}")  # Alterado para DEBUG
            self.nodes_without_siteid.append(node_name)

    def _apply_geodata(self, node_name, node_data):
        """Aplica dados geográficos (coordenadas) se disponíveis, sem alterar a camada"""
        if not self.localidades_map:
            return
            
        siteid = node_data.get('siteid', '')
        if siteid and siteid in self.localidades_map:
            loc_data = self.localidades_map[siteid]
            # Apenas atribui as coordenadas
            node_data['coordenadas'] = (loc_data['latitude'], loc_data['longitude'])
            logger.debug(f"Dados geográficos aplicados a {node_name} via siteid: {siteid}")
        else:
            # Marcar para processamento especial no layout geográfico
            node_data['coordenadas'] = None
            logger.debug(f"Sem dados geográficos para {node_name}")

    def _process_elemento_row(self, row):
        origem = row['elemento'].strip()
        if not origem:
            return
            
        # Usar 'camada' em vez de 'tipo'
        camada_original = row.get('camada', '').strip()
        nivel_str = row.get('nivel', '').strip()
        
        siteid = row.get('siteid', '').strip()  # Novo campo
        if self.ignore_optional:
            origemcor = None  # Ignorar cor definida no CSV
        else:
            origemcor = row.get('cor', '').strip()
        
        nivel = None
        if nivel_str:
            try:
                nivel = int(nivel_str)
            except ValueError:
                logger.warning(f"Valor de nível inválido para {origem}: '{nivel_str}'")
        
        # Determinar camada/nível se necessário
        need_camada_inference = not camada_original
        need_nivel_inference = nivel is None
        
        if need_camada_inference or need_nivel_inference:
            inferred_camada, inferred_nivel = self._determine_layer_by_prefix(origem)
            if need_camada_inference:
                camada_original = inferred_camada
            if need_nivel_inference:
                nivel = inferred_nivel
                
        # VALIDAÇÃO ADICIONADA
        if not camada_original:
            logger.error(f"Camada indefinida para {origem}")
            return
            
        if nivel is None:
            logger.warning(f"Nível indefinido para {origem}, usando padrão 10")
            nivel = 10
        
        if origemcor:
            self.node_colors[origem].append(origemcor)
            
        # CORREÇÃO PRINCIPAL: NÃO aplicar regionalização aqui
        # A regionalização será aplicada posteriormente no fluxo
        camada_final = camada_original
        coordenadas = None
        
        apelido = row.get('apelido', '').strip()  # Novo campo
        
        # Atualizar dados do nó
        if origem not in self.nodes:
            self.nodes[origem] = {
                'camada': camada_final,
                'nivel': nivel,
                'cor': origemcor if origemcor else None,
                'coordenadas': coordenadas,
                'regionalized': False,
                'siteid': siteid,
                'apelido': apelido  # Novo campo
            }
        else:
            self.nodes[origem]['apelido'] = apelido  # Atualizar apelido
            self.nodes[origem]['nivel'] = nivel
            if origemcor:
                self.nodes[origem]['cor'] = origemcor
            self.nodes[origem]['siteid'] = siteid  # Novo campo

        # Aplicar dados geográficos independentemente da regionalização
        self._apply_geodata(origem, self.nodes[origem])
        
        # Aplicar regionalização APENAS se flag ativa
        if self.regionalization:
            self._apply_regionalization(origem, self.nodes[origem])
        
        self._register_node(origem, nivel)
        logger.info(f"Processado: {origem} | Camada: {camada_final} | Nível: {nivel} | Cor: {origemcor} | SiteID: {siteid}")
        if self.ignore_optional and row.get('cor'):
            logger.debug("Ignorando cor definida para %s (opção -d)", origem)
    
    def read_conexoes(self):
        try:
            logger.info(f"Abrindo arquivo: {self.conexoes_file}")
            
            # Adicionar log de debug para verificar caminho real
            if not os.path.exists(self.conexoes_file):
                logger.error(f"Arquivo não encontrado: {self.conexoes_file}")
                return False        
        
            with open(self.conexoes_file, 'r', encoding=self.encoding_conexoes, errors='replace') as f:
                reader = csv.DictReader(f, delimiter=';')
                row_count = 0
                for row in reader:
                    row_count += 1
                    origem = row['ponta-a'].strip()
                    destino = row['ponta-b'].strip()
                    
                    for node in [origem, destino]:
                        if node not in self.nodes:
                            camada, nivel = self._determine_layer_by_prefix(node)
                            node_data = {
                                'camada': camada,
                                'nivel': nivel,
                                'cor': None,
                                'coordenadas': None,
                                'regionalized': False,  # Novo campo
                                'siteid': ''            # Novo campo
                            }
                            self.nodes[node] = node_data
                            # Aplicar dados geográficos
                            self._apply_geodata(node, node_data)
                            # Registrar o nó criado
                            self._register_node(node, nivel)
                            
                        # Aplicar regionalização se ativa (apenas uma vez)
                        if self.regionalization:
                            self._apply_regionalization(node, self.nodes[node])
                                
                    self._process_conexao_row(row)
                
                logger.info("Processadas %d linhas de conexões", row_count)
                self._validate_data()
                
                # Verificação de dados geográficos
                self.has_geographic_data = any(
                    data.get('coordenadas') is not None 
                    for data in self.nodes.values()
                )
                
                logger.info("Dados geográficos disponíveis: %s", 
                           "Sim" if self.has_geographic_data else "Não")
                return True
                
            # VERIFICAR CABEÇALHOS (novo código)
            first_row = next(reader, None)
            if first_row:
                logger.debug("Cabeçalhos detectados: %s", list(first_row.keys()))
                
        except Exception as e:
            logger.error("Falha na leitura de conexões: %s", str(e), exc_info=True)
            return False

    def _validate_colors(self):
        """Verifica consistência de cores e reporta divergências"""
        for node, colors in self.node_colors.items():
            if len(set(colors)) > 1:
                logger.warning("Divergência de cores para %s: %s", node, ', '.join(set(colors)))
                if node in self.nodes:
                    self.nodes[node]['cor'] = colors[0]  # Usar primeira cor

    def _register_node(self, node_name, nivel):
        """Registra nó nas estruturas internas"""
        if node_name not in self.node_ids:
            self.node_ids[node_name] = str(uuid.uuid4())
            logger.debug(f"Registrado nó: {node_name} | ID: {self.node_ids[node_name]}")
            
        node_data = self.nodes[node_name]
        
        if node_data['camada'] not in self.layer_ids:
            self.layer_ids[node_data['camada']] = str(uuid.uuid4())
            
        if node_name not in self.layers[node_data['camada']]:
            self.layers[node_data['camada']].append(node_name)
            
        if node_name not in self.circular_alignments[nivel]:
            self.circular_alignments[nivel].append(node_name)

    def _process_conexao_row(self, row):
        """Processa uma linha de conexão com chaves normalizadas"""
        # Alteração crítica: manter hífens nos nomes das colunas
        normalized_row = {k.lower().replace(' ', ''): v for k, v in row.items()}
        
        # Usar nomes originais sem remover hífens
        origem = normalized_row.get('ponta-a', '').strip()  # Mantém o hífen!
        destino = normalized_row.get('ponta-b', '').strip()  # Mantém o hífen!
        
        if not origem or not destino:
            return
            
        # Criar camada específica para conexões
        camada_original = self.nodes[origem]['camada']
        camada_conexao = f"{camada_original}_CNX"

        # Se a opção estiver ativa, ignorar propriedades opcionais
        if self.ignore_optional:
            conn_data = {
                'origem': origem,
                'destino': destino,
                'camada': camada_conexao,
                'texto_conexao': row.get('textoconexao', '').strip(),
                'strokeWidth': None,
                'strokeColor': None,
                'dashed': '0',
                'fontStyle': '1',
                'fontSize': '14'
            }
        else:
            conn_data = {
                'origem': origem,
                'destino': destino,
                'camada': camada_conexao,
                'texto_conexao': row.get('textoconexao', '').strip(),
                'strokeWidth': row.get('strokeWidth', '').strip() if 'strokeWidth' in row and row['strokeWidth'] else None,
                'strokeColor': row.get('strokeColor', '').strip() if 'strokeColor' in row and row['strokeColor'] else None,
                'dashed': row.get('dashed', '0').strip() if 'dashed' in row else '0',
                'fontStyle': row.get('fontStyle', '1').strip() if 'fontStyle' in row else '1',
                'fontSize': row.get('fontSize', '14').strip() if 'fontSize' in row else '14'
            }
        
        self.connections.append(conn_data)
        
        # Registrar camada de conexões se nova
        if camada_conexao not in self.layer_ids:
            self.layer_ids[camada_conexao] = str(uuid.uuid4())
        
        if camada_conexao not in self.layers:
            self.layers[camada_conexao] = []
        if self.ignore_optional and any(row.get(k) for k in ['strokeWidth', 'strokeColor', 'dashed']):
            logger.debug("Ignorando propriedades de conexão para %s-%s (opção -d)", origem, destino)            

    def _validate_data(self):
        """Valida dados e trata nós sem conexões, listando os nós removidos"""
        all_nodes = set(self.nodes.keys())
        connected_nodes = set()
        for conn in self.connections:
            connected_nodes.add(conn['origem'])
            connected_nodes.add(conn['destino'])
            
        orphan_nodes = all_nodes - connected_nodes
        if orphan_nodes:
            orphan_list = sorted(orphan_nodes)
            orphan_count = len(orphan_list)
            
            # Mostrar até 10 nós para evitar logs muito longos
            display_list = orphan_list[:10]
            display_text = ', '.join(display_list)
            if orphan_count > 10:
                display_text += f', ... (+{orphan_count - 10} mais)'
            
            if self.include_orphans:
                logger.warning(  # Alterado para logger.warning
                    "%d nós sem conexões incluídos (opção -y): %s", 
                    orphan_count, 
                    display_text
                )
            else:
                logger.warning(  # Alterado para logger.warning
                    "%d nós sem conexões removidos: %s", 
                    orphan_count, 
                    display_text
                )
                # Remover nós órfãos
                for node in orphan_list:
                    if node in self.nodes:
                        node_data = self.nodes[node]
                        camada = node_data['camada']
                        nivel = node_data['nivel']
                        
                        if camada in self.layers and node in self.layers[camada]:
                            self.layers[camada].remove(node)
                        
                        if nivel in self.circular_alignments and node in self.circular_alignments[nivel]:
                            self.circular_alignments[nivel].remove(node)
                        
                        del self.nodes[node]
                    
                    # REMOVER DA LISTA DE NÓS SEM SITEID
                    if node in self.nodes_without_siteid:
                        self.nodes_without_siteid.remove(node)
                    
                    if node in self.node_ids:
                        del self.node_ids[node]
                    
                    if node in self.node_colors:
                        del self.node_colors[node]
        else:
            logger.info("Nenhum nó sem conexões encontrado")

    def calculate_circular_positions(self):
        """
        Calcula posições para layout circular baseado em níveis
        
        Returns:
            dict: Mapeamento nó -> (x, y)
        """
        start_time = time.perf_counter()
        logger.info("Calculando layout circular...")
        cfg = self.config["CIRCULAR_LAYOUT"]
        center_x, center_y = cfg["center_x"], cfg["center_y"]
        base_radius = cfg["base_radius"]
        radius_increment = cfg["radius_increment"]
        positions = {}
        
        # Agrupar nós por nível
        level_nodes = defaultdict(list)
        for node, data in self.nodes.items():
            level = data['nivel']
            level_nodes[level].append(node)
        
        levels = sorted(level_nodes.keys())
        min_level = min(levels) if levels else 1
        max_level = max(levels) if levels else 1
        
        # Posicionar nós em círculos concêntricos
        for level in levels:
            nodes = level_nodes[level]
            radius = base_radius + (level - min_level) * radius_increment
            angle_step = 2 * math.pi / len(nodes)
            offset_angle = -math.pi/2  # Iniciar no topo
            
            for idx, node in enumerate(nodes):
                angle = offset_angle + idx * angle_step
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions[node] = (x, y)
        
        # Tratar nós sem nível definido
        placed_nodes = set(positions.keys())
        all_defined_nodes = set(self.nodes.keys())
        missing_nodes = all_defined_nodes - placed_nodes
        
        if missing_nodes:
            logger.warning("%d nós sem nível, posicionando no nível %d", len(missing_nodes), max_level+1)
            level = max_level + 1
            radius = base_radius + (level - min_level) * radius_increment
            missing_list = sorted(missing_nodes)
            angle_step = 2 * math.pi / len(missing_list)
            
            for idx, node in enumerate(missing_list):
                angle = offset_angle + idx * angle_step
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions[node] = (x, y)
        
        elapsed = time.perf_counter() - start_time
        logger.debug("⚙️ Layout circular calculado em %.3fs | Níveis: %d", 
                   elapsed, len(self.circular_alignments))
        return positions

    def calculate_organico_positions(self):
        """
        Calcula posições para layout orgânico usando algoritmo de força
        
        Returns:
            dict: Mapeamento nó -> (x, y)
        """
        start_time = time.perf_counter()
        logger.info("Calculando layout orgânico...")
        G = nx.Graph()
        G.add_nodes_from(self.nodes.keys())
        G.add_edges_from([(c['origem'], c['destino']) for c in self.connections])
        
        num_nodes = len(G.nodes)
        if num_nodes == 0:
            logger.warning("Nenhum nó para layout orgânico")
            return {}
        
        cfg = self.config.get("ORGANIC_LAYOUT", {})
        k_base = cfg.get("k_base", 0.25)
        k_min = cfg.get("k_min", 0.8)
        k_max = cfg.get("k_max", 2.5)
        iterations_per_node = cfg.get("iterations_per_node", 10)
        iterations_min = cfg.get("iterations_min", 500)
        iterations_max = cfg.get("iterations_max", 2000)
        scale_per_node = cfg.get("scale_per_node", 0.5)
        scale_min = cfg.get("scale_min", 5.0)
        scale_max = cfg.get("scale_max", 30.0)
        base_width = cfg.get("base_width", 1400)
        base_height = cfg.get("base_height", 1000)
        
        # Calcular parâmetros dinâmicos baseados na rede
        k_value = max(k_min, min(k_max, k_base * math.sqrt(num_nodes)))
        iterations_value = max(iterations_min, min(iterations_max, num_nodes * iterations_per_node))
        scale_value = max(scale_min, min(scale_max, num_nodes * scale_per_node))
        
        logger.info("Parâmetros orgânicos: k=%.2f, iterações=%d, escala=%.2f", 
                   k_value, iterations_value, scale_value)
        
        # Calcular layout com networkx
        pos = nx.spring_layout(
            G,
            k=k_value,
            iterations=iterations_value,
            seed=42,  # Semente fixa para reprodutibilidade
            scale=scale_value,
            threshold=0.0001
        )
        
        # Normalizar posições
        all_x = [x for x, _ in pos.values()]
        all_y = [y for _, y in pos.values()]
        
        if not all_x or not all_y:
            return {}
        
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        
        size_factor = max(1.0, math.log(num_nodes + 1))
        target_width = base_width * size_factor
        target_height = base_height * size_factor
        
        range_x = max_x - min_x if max_x != min_x else 1
        range_y = max_y - min_y if max_y != min_y else 1
        
        scale_x = target_width / range_x
        scale_y = target_height / range_y
        
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        offset_x = target_width/2 - center_x * scale_x
        offset_y = target_height/2 - center_y * scale_y
        
        result = {
            node: (
                pos[node][0] * scale_x + offset_x,
                pos[node][1] * scale_y + offset_y
            )
            for node in G.nodes
        }
        
        elapsed = time.perf_counter() - start_time
        logger.debug("⚙️ Layout orgânico calculado em %.3fs | Nós: %d | Arestas: %d", 
                   elapsed, len(G.nodes), len(G.edges))
        return result

    def calculate_geographic_positions(self):
        """Versão corrigida com tratamento especial para SEM_SITEID"""
        start_time = time.perf_counter()
        logger.info("Calculando layout geográfico...")
        cfg = self.config.get("GEOGRAPHIC_LAYOUT", {})
        
        # FILTRAR APENAS NÓS QUE AINDA EXISTEM
        valid_nodes = {}
        for node, data in list(self.nodes.items()):
            if data.get('coordenadas') is not None:
                valid_nodes[node] = data['coordenadas']
        
        # FILTRAR NÓS SEM SITEID QUE AINDA EXISTEM
        valid_nodes_without_siteid = [n for n in self.nodes_without_siteid if n in self.nodes]
        
        # Se não houver nós com coordenadas, usar apenas os sem siteid
        if not valid_nodes and not valid_nodes_without_siteid:
            return {}
        
        # ================================================
        # TRATAMENTO ESPECIAL PARA ELEMENTOS SEM SITEID
        # ================================================
        # Calcular centro do canvas
        canvas_width = cfg.get("canvas_width", 5000)
        canvas_height = cfg.get("canvas_height", 5000)
        center_x = canvas_width / 2
        center_y = canvas_height / 2
        
        # Posicionar elementos SEM_SITEID em espiral no centro
        sem_siteid_positions = {}
        spiral_radius = 200
        angle_step = 0.5
        
        # USAR APENAS NÓS VÁLIDOS
        for idx, node in enumerate(valid_nodes_without_siteid):
            angle = idx * angle_step
            radius = spiral_radius + idx * 50  # Aumenta o raio a cada nó
            
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            sem_siteid_positions[node] = (x, y)
            logger.info(f"Posicionando elemento sem siteid no centro: {node} em ({x:.1f}, {y:.1f})")
        # ================================================
        
        # Se não houver nós com coordenadas, usar apenas os sem siteid
        if not valid_nodes:
            return sem_siteid_positions
        
        # Usar .values() para acessar as coordenadas diretamente
        coords = valid_nodes.values()
        
        # Calcular bounding box
        lats = [c[0] for c in coords]  # Corrigido!
        lons = [c[1] for c in coords]  # Corrigido!
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # Configurações
        margin = cfg["margin"]
        min_distance = cfg["min_distance"]
        
        # Mapear nós por coordenada
        nodes_by_coord = defaultdict(list)
        for node, coord in valid_nodes.items():
            nodes_by_coord[coord].append(node)
        
        positions = {}
        for coord, nodes in nodes_by_coord.items():
            lat, lon = coord
            
            # Normalizar para coordenadas do canvas
            x = margin + (lon - min_lon) * (canvas_width - 2*margin) / (max_lon - min_lon)
            y = canvas_height - margin - (lat - min_lat) * (canvas_height - 2*margin) / (max_lat - min_lat)
            
            # Evitar sobreposição de nós no mesmo local
            if len(nodes) > 1:
                angle_step = 360 / len(nodes)
                for i, node in enumerate(nodes):
                    angle_rad = math.radians(i * angle_step)
                    dx = min_distance * math.cos(angle_rad)
                    dy = min_distance * math.sin(angle_rad)
                    positions[node] = (x + dx, y + dy)
            else:
                positions[nodes[0]] = (x, y)
        
        logger.info("Posições geográficas calculadas para %d nós", len(positions))
        
        # ================================================
        # ALGORITMO DE PREVENÇÃO DE SOBREPOSIÇÃO
        # ================================================
        logger.info("Aplicando prevenção de sobreposição...")
        node_sizes = {}
        for node in positions:
            style = self._get_node_style(self.nodes[node])
            node_sizes[node] = max(style["width"], style["height"])
        
        # Converter para lista para iterar
        nodes = list(positions.keys())
        changed = True
        max_iterations = 20
        iter_count = 0
        
        while changed and iter_count < max_iterations:
            changed = False
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    node1 = nodes[i]
                    node2 = nodes[j]
                    
                    x1, y1 = positions[node1]
                    x2, y2 = positions[node2]
                    
                    # Calcular distância euclidiana
                    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    
                    # Calcular distância mínima requerida
                    min_required = node_sizes[node1]/2 + node_sizes[node2]/2 + cfg.get("min_node_distance", 150)
                    
                    if distance < min_required:
                        changed = True
                        # Calcular vetor de direção
                        dx = x2 - x1
                        dy = y2 - y1
                        if dx == 0 and dy == 0:
                            # Caso raro de mesma posição
                            angle = random.uniform(0, 2 * math.pi)
                            dx = math.cos(angle)
                            dy = math.sin(angle)
                            distance = 1
                        
                        # Fator de deslocamento (proporcional à sobreposição)
                        move_factor = (min_required - distance) / distance
                        
                        # Aplicar deslocamento mantendo o ponto médio
                        move_x = dx * move_factor * 0.5
                        move_y = dy * move_factor * 0.5
                        
                        # Atualizar posições
                        positions[node1] = (
                            positions[node1][0] - move_x,
                            positions[node1][1] - move_y
                        )
                        positions[node2] = (
                            positions[node2][0] + move_x,
                            positions[node2][1] + move_y
                        )
            iter_count += 1
        
        logger.info(f"Prevenção de sobreposição concluída em {iter_count} iterações")
        # ================================================
        
        # Combinar todas as posições
        positions.update(sem_siteid_positions)   # Adiciona posições dos elementos sem siteid
        
        elapsed = time.perf_counter() - start_time
        logger.debug("⚙️ Layout geográfico calculado em %.3fs | Nós com coord: %d | Sem coord: %d", 
                   elapsed, len(valid_nodes), len(valid_nodes_without_siteid))
        return positions


    def calculate_hierarchical_positions(self):
        """Calcula posições para layout hierárquico"""
        start_time = time.perf_counter()
        logger.info("Calculando layout hierárquico...")
        cfg = self.config.get("HIERARCHICAL_LAYOUT", {})
        vertical_spacing = cfg.get("vertical_spacing", 200)
        horizontal_spacing = cfg.get("horizontal_spacing", 100)
        top_margin = cfg.get("top_margin", 50)
        left_margin = cfg.get("left_margin", 50)
        
        # Agrupar nós por nível
        nodes_by_level = defaultdict(list)
        max_width_per_level = defaultdict(int)
        for node, data in self.nodes.items():
            level = data.get('nivel', 10)  # Default para nível 10
            nodes_by_level[level].append(node)
            
            # Pré-calcular tamanhos dos nós
            style = self._get_node_style(data)
            max_width_per_level[level] = max(max_width_per_level[level], style["width"])
        
        # Ordenar níveis do menor (topo) para maior (base)
        sorted_levels = sorted(nodes_by_level.keys())
        
        # Calcular posições
        positions = {}
        current_y = top_margin
        
        for level in sorted_levels:
            nodes = nodes_by_level[level]
            level_width = max_width_per_level[level]
            
            # Calcular largura total necessária
            total_width = len(nodes) * level_width + (len(nodes) - 1) * horizontal_spacing
            start_x = left_margin + (cfg.get("canvas_width", 2000) - total_width) / 2
            
            # Distribuir nós horizontalmente
            x = start_x
            for node in nodes:
                data = self.nodes[node]
                style = self._get_node_style(data)
                
                # Posicionar centro do nó
                pos_x = x + style["width"] / 2
                pos_y = current_y + style["height"] / 2
                
                positions[node] = (pos_x, pos_y)
                x += style["width"] + horizontal_spacing
            
            # Avançar para próximo nível
            current_y += max(style["height"] for node in nodes) + vertical_spacing
        
        elapsed = time.perf_counter() - start_time
        logger.debug("⚙️ Layout hierárquico calculado em %.3fs | Níveis: %d", 
                   elapsed, len(nodes_by_level))
        return positions


    def _get_node_style(self, node_data, scale_factor=1.0):
        """
        Gera estilo visual para um nó baseado em sua camada
        
        Args:
            node_data (dict): Dados do nó
            scale_factor (float): Fator de escala para dimensionamento
            
        Returns:
            dict: {style: string, width: int, height: int}
        """
        camada = node_data['camada']
        
        # Estilo especial para elementos sem siteid
        if camada == "SEM_SITEID":
            return {
                "style": "shape=mxgraph.basic.ellipse;fillColor=#FF0000;strokeColor=#FFFFFF;",
                "width": 60 * scale_factor,
                "height": 60 * scale_factor
            }
        
        camada_base = camada.split('_', 1)[0]  # Remover sufixo regional
        
        # Obter estilo da camada ou padrão
        layer_styles = self.config["LAYER_STYLES"].get(
            camada_base, 
            self.config["LAYER_STYLES"].get("default", {})
        )

        # Determinar cor de preenchimento
        fill_color = None
        if node_data.get('cor'):
            fill_color = self._normalize_color(node_data['cor'])
        elif layer_styles.get('fillColor'):
            fill_color = self._normalize_color(layer_styles['fillColor'])
        else:
            fill_color = self._normalize_color(
                self.config["LAYER_COLORS"].get(
                    camada_base, 
                    self.config["LAYER_COLORS"]["default"]
                )
            )
        
        # Obter outras propriedades
        stroke_color = layer_styles.get('strokeColor', 
            self.config["NODE_STYLE"].get('strokeColor', '#ffffff'))
        stroke_color = self._normalize_color(stroke_color)

        # Aplicar fator de escala
        width = layer_styles.get("width", 80) * scale_factor
        height = layer_styles.get("height", 80) * scale_factor

        # Construir string de estilo
        style_template = self.config["NODE_STYLE"].copy()
        style_template["fillColor"] = fill_color
        style_template["strokeColor"] = stroke_color

        shape_str = layer_styles.get("shape", "mxgraph.cisco.routers.router")
        
        # Adicionar propriedades extras
        if isinstance(layer_styles, dict):
            for key, value in layer_styles.items():
                if key not in ["shape", "fillColor", "strokeColor"]:
                    shape_str += f";{key}={value}"
        
        style_template["shape"] = shape_str
        
        # Obter e escalar tamanho da fonte
        base_font_size = int(self.config["NODE_STYLE"].get("fontSize", 14))
        scaled_font_size = max(1, int(base_font_size * scale_factor))  # Mínimo 1px
        
        # Adicionar ao estilo
        style_template["fontSize"] = str(scaled_font_size)
        # ========================================
        
        # Construir string de estilo final
        style_str = ";".join([f"{key}={value}" for key, value in style_template.items()])
        
        return {
            "style": style_str,
            "width": width,
            "height": height
        }

    def _get_connection_style(self, connection, scale_factor=1.0):
        """
        Gera estilo visual para uma conexão com suporte a escala
        
        Args:
            connection (dict): Dados da conexão
            scale_factor (float): Fator de escala para dimensionamento
            
        Returns:
            str: String de estilo
        """
        # Determinar camada base (removendo sufixos)
        camada_base = connection['camada'].replace("_CNX", "").split('_', 1)[0]
        
        # Obter estilo base da camada ou padrão
        base_style = self.config["CONNECTION_STYLES"].get(
            camada_base, 
            self.config["CONNECTION_STYLES"]["default"]
        )
        
        # Normalizar cor da conexão
        stroke_color = (
            self._normalize_color(connection["strokeColor"]) 
            if connection["strokeColor"] 
            else self._normalize_color(base_style["color"])
        )
        
        # Obter tamanho base da fonte (com fallback)
        try:
            base_font_size = int(connection.get('fontSize', '14'))
        except (ValueError, TypeError):
            base_font_size = 14
        
        # Aplicar fator de escala com mínimo de 1px
        scaled_font_size = max(1, int(base_font_size * scale_factor))
        
        # Obter estilo base para conexões
        style_template = self.config["CONNECTION_STYLE_BASE"].copy()
        
        # Atualizar com propriedades específicas
        style_template.update({
            "strokeWidth": connection['strokeWidth'] or base_style['strokeWidth'],
            "strokeColor": stroke_color,
            "dashed": connection['dashed'] or '0',
            "fontStyle": connection['fontStyle'] or '1',
            "fontSize": str(scaled_font_size),  # USAR VALOR ESCALADO
            "fontColor": stroke_color
        })
        
        # Construir string de estilo final
        return ";".join([f"{key}={value}" for key, value in style_template.items()])

    def generate_drawio(self, output_file, layout_type):
        """
        Gera arquivo draw.io com o layout especificado
        """
        logger.info("🖼️ Gerando diagrama: %s", output_file)
        gen_start = time.perf_counter()
        
        # Mapear nomes em português para chaves em inglês
        layout_key_map = {
            'circular': 'CIRCULAR_LAYOUT',
            'organico': 'ORGANIC_LAYOUT',
            'geografico': 'GEOGRAPHIC_LAYOUT',
            'hierarquico': 'HIERARCHICAL_LAYOUT'
        }
        
        layout_key = layout_key_map.get(layout_type)
        if not layout_key:
            logger.error("Tipo de layout inválido: %s", layout_type)
            return False
            
        try:
            # Selecionar algoritmo de layout
            if layout_type == 'circular':
                positions = self.calculate_circular_positions()
            elif layout_type == 'organico':
                positions = self.calculate_organico_positions()
            elif layout_type == 'geografico':
                positions = self.calculate_geographic_positions()
            elif layout_type == 'hierarquico':
                positions = self.calculate_hierarchical_positions()
            else:
                logger.error("Tipo de layout inválido: %s", layout_type)
                return False
                   
            if not positions:
                logger.error("Nenhuma posição calculada para %s", layout_type)
                return False
                
            # Obter fator de escala e status de bloqueio para este layout
            layout_config = self.config[layout_key]
            scale_factor = layout_config.get("node_scale_factor", 1)
            locked = layout_config.get("locked", 0)
            
            logger.info("Layout %s | Nós: %d | Conexões: %d | Fator escala: %.1f | Locked: %d", 
                       layout_type, len(positions), len(self.connections), scale_factor, locked)
            
            # Iniciar conteúdo do arquivo
            content = [
                DRAWIO_HEADER.format(
                    timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    etag=str(uuid.uuid4())
                )
            ]

            # Gerar cada página definida no config
            for page_def in self.config["PAGE_DEFINITIONS"]:
                logger.info("Gerando página: %s", page_def["name"])
                page_content = self._generate_page(page_def, positions, layout_type, scale_factor, locked)
                content.append(page_content)
                
            content.append(DRAWIO_FOOTER)
            
            # Escrever arquivo final
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            
            # Registrar tempo de geração
            gen_time = time.perf_counter() - gen_start
            file_size = os.path.getsize(output_file) / 1024
            logger.info("✅ Diagrama gerado em %.2fs (%.1fKB)", gen_time, file_size)
            return True
            
        except Exception as e:
            logger.exception("💥 ERRO CRÍTICO durante geração")
            logger.error("Contexto: layout=%s, nodes=%d, connections=%d",
                       layout_type, len(positions), len(self.connections))
            return False

    def _generate_page(self, page_def, positions, layout_type, scale_factor=1.0, locked=0):
        """
        Gera conteúdo XML para uma página específica
        
        Args:
            page_def (dict): Definição da página do config
            positions (dict): Mapeamento nó -> posição
            layout_type (str): Tipo de layout usado
            scale_factor (float): Fator de escala para dimensionamento de nós
            locked (int): Status de bloqueio das camadas (0=editável, 1=bloqueado)
            
        Returns:
            str: Conteúdo XML da página
        """
        diagram_content = DRAWIO_DIAGRAM_TEMPLATE.format(
            page_name=page_def["name"],
            diagram_id=str(uuid.uuid4())
        )
        
        page_content = [diagram_content]
        visible_layers = set(self.layers.keys()) if page_def["visible_layers"] is None else set(page_def["visible_layers"])

        
        # Expandir camadas visíveis
        expanded_visible_layers = set()
        for layer in visible_layers:
            expanded_visible_layers.add(layer)
            # Incluir camadas regionais
            for existing_layer in self.layers.keys():
                if existing_layer.startswith(layer + '_'):
                    expanded_visible_layers.add(existing_layer)
            # Incluir camadas de conexão
            cnx_layer_base = f"{layer}_CNX"
            if cnx_layer_base in self.layers:
                expanded_visible_layers.add(cnx_layer_base)
        
        # Adicionar imagem de fundo para layout geográfico
        if layout_type == 'geografico':
            bg_cfg = self.config.get("GEOGRAPHIC_LAYOUT", {}).get("background_image", {})
            if os.path.exists('brasil-map.png'):
                bg_cfg = bg_cfg.copy()
                bg_cfg["url"] = 'brasil-map.png'
                logger.info("Usando imagem local como fundo")
            elif bg_cfg.get("url", "").startswith("http"):
                logger.info("Usando imagem remota como fundo")
            else:
                logger.warning("Imagem de fundo não encontrada")
                bg_cfg = None

            if bg_cfg:
                bg_id = str(uuid.uuid4())
                page_content.extend([
                    f'        <mxCell id="{bg_id}" value="" style="shape=image;image={bg_cfg["url"]};',
                    f'          imageAspect=0;aspect=fixed;verticalLabelPosition=bottom;verticalAlign=top;',
                    f'          opacity={bg_cfg.get("opacity", 30)};" vertex="1" parent="1" visible="1">',
                    f'          <mxGeometry x="{bg_cfg["x"]}" y="{bg_cfg["y"]}" width="{bg_cfg["width"]}" height="{bg_cfg["height"]}" as="geometry"/>',
                    f'        </mxCell>'
                ])

        # Adicionar objetos de camada em ordem alfabética
        sorted_layers = sorted(self.layer_ids.items(), key=lambda x: x[0])
        for layer, lid in sorted_layers:
            # Determinar visibilidade da camada
            layer_visible = "1"
            if self.hide_connection_layers:
                layer_visible = "1"
                if layer.endswith("_CNX") and self.hide_connection_layers:
                    layer_visible = "0"
                
            if layer not in expanded_visible_layers:
                continue
                
            page_content.extend([
                f'        <object id="{lid}" label="{layer}">',
                f'          <mxCell style="locked={locked};" parent="0" visible="{layer_visible}"/>',
                f'        </object>'
            ])

        # Precomputar nós a serem gerados
        generated_nodes = set()
        for node in positions:
            if node in self.nodes and self.nodes[node]['camada'] in expanded_visible_layers:
                generated_nodes.add(node)
        
        # Adicionar conexões apenas se ambos os nós existirem
        for conn in self.connections:
            if (conn['camada'] not in expanded_visible_layers or
                conn['origem'] not in self.node_ids or
                conn['destino'] not in self.node_ids):
                continue
                
            # CORREÇÃO: Passar scale_factor como segundo argumento
            style = self._get_connection_style(conn, scale_factor)
            page_content.extend([
                f'        <mxCell id="{uuid.uuid4()}" value="{conn["texto_conexao"]}" style="{style}" edge="1"',
                f'          parent="{self.layer_ids[conn["camada"]]}" source="{self.node_ids[conn["origem"]]}"',
                f'          target="{self.node_ids[conn["destino"]]}">',
                '          <mxGeometry relative="1" as="geometry"/>',
                '        </mxCell>'
            ])

        # CORREÇÃO: Aplicar nós sem nomes
        for node in generated_nodes:
            data = self.nodes[node]
            apelido = data.get('apelido', '')  # Obter apelido se existir
            style = self._get_node_style(data, scale_factor)
            x, y = positions[node]
            
            # Usar apelido se disponível, senão usar nome original
            label = ""
            if not self.hide_node_names:
                label = apelido if apelido else node  # Priorizar apelido
            
            page_content.extend([
                f'        <object id="{self.node_ids[node]}" label="{label}">',
                f'          <mxCell style="{style["style"]}" vertex="1" parent="{self.layer_ids[data["camada"]]}">',
                f'            <mxGeometry x="{x - style["width"]/2}" y="{y - style["height"]/2}" ',
                f'width="{style["width"]}" height="{style["height"]}" as="geometry"/>',
                f'          </mxCell>',
                f'        </object>'
            ])

        # Calcular bounding box para posicionar legenda
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        for node in generated_nodes:
            x, y = positions[node]
            style = self._get_node_style(self.nodes[node], scale_factor)
            width = style["width"]
            height = style["height"]
            
            node_min_x = x - width/2
            node_min_y = y - height/2
            node_max_x = x + width/2
            node_max_y = y + height/2
            
            min_x = min(min_x, node_min_x)
            min_y = min(min_y, node_min_y)
            max_x = max(max_x, node_max_x)
            max_y = max(max_y, node_max_y)
        
        if min_x == float('inf'):
            min_x = min_y = 0
            max_x = max_y = 1000

        # Criar camada LEGENDA
        legenda_layer_id = str(uuid.uuid4())
        page_content.extend([
            f'        <object id="{legenda_layer_id}" label="LEGENDA">',
            f'          <mxCell style="locked={locked};" parent="0" visible="1"/>',
            f'        </object>'
        ])
        
        # Configuração e geração da legenda
        legend_config = self.config.get("LEGEND_CONFIG", {
            "position": {"x": 50, "y": 30},
            "item_spacing": 40,
            "text_offset": 45,
            "item_size": 30,
            "margin": 50
        })
        
        margin = legend_config.get("margin", 50)
        pos_x = max_x - 300
        pos_y = max_y + margin
        
        base_layers = set()
        for layer in expanded_visible_layers:
            base_layer = layer.split('_', 1)[0]
            base_layers.add(base_layer)

        base_layers = sorted(base_layers)
        
        if base_layers:
            # Título da legenda com o nome da página
            page_name = page_def["name"].replace('"', '&quot;')
            page_content.extend([
                f'        <mxCell id="legend-title" value="{page_name}" style="text;html=1;strokeColor=none;fillColor=none;'
                f'align=left;verticalAlign=middle;fontStyle=1;fontSize=16;" vertex="1" parent="{legenda_layer_id}">',
                f'          <mxGeometry x="{pos_x}" y="{pos_y}" width="200" height="30" as="geometry"/>',
                f'        </mxCell>'
            ])
            
            pos_y += 30
            
            # Itens da legenda (sem escala aplicada)
            for base_layer in sorted(base_layers):
                layer_style = self.config["LAYER_STYLES"].get(
                    base_layer,
                    self.config["LAYER_STYLES"]["default"]
                )
                
                # Criar nó fictício para obter estilo
                fake_node_data = {'camada': base_layer, 'cor': None, 'tipo': 'Exemplo'}
                style_dict = self._get_node_style(fake_node_data, scale_factor=1.0)
                
                # Ajustar estilo para item de legenda
                style_str = style_dict["style"]
                parts = style_str.split(';')
                new_parts = [p for p in parts if not p.startswith('width=') and not p.startswith('height=')]
                new_parts.append(f'width={legend_config["item_size"]}')
                new_parts.append(f'height={legend_config["item_size"]}')
                new_style_str = ';'.join(new_parts)
                
                # Adicionar ícone
                item_id = str(uuid.uuid4())
                page_content.extend([
                    f'        <object id="{item_id}" label="">',
                    f'          <mxCell style="{new_style_str}" vertex="1" parent="{legenda_layer_id}">',
                    f'            <mxGeometry x="{pos_x}" y="{pos_y}" width="{legend_config["item_size"]}" height="{legend_config["item_size"]}" as="geometry"/>',
                    f'          </mxCell>',
                    f'        </object>'
                ])
                
                # Adicionar texto
                text_id = str(uuid.uuid4())
                layer_name = base_layer.replace("-", " ")
                page_content.extend([
                    f'        <mxCell id="{text_id}" value="{layer_name}" style="text;html=1;strokeColor=none;fillColor=none;'
                    f'align=left;verticalAlign=middle;fontSize=14;" vertex="1" parent="{legenda_layer_id}">',
                    f'          <mxGeometry x="{pos_x + legend_config["text_offset"]}" y="{pos_y + 5}" width="200" height="30" as="geometry"/>',
                    f'        </mxCell>'
                ])
                
                pos_y += legend_config["item_spacing"]
        
        # Fechar elementos
        page_content.append("      </root>")
        page_content.append("    </mxGraphModel>")
        page_content.append("  </diagram>")
                       
        return '\n'.join(page_content)

# =====================================================
# MAIN FUNCTION WITH CLI/GUI SWITCH
# =====================================================

def run_gui():
    root = tk.Tk()
    app = TopologyGUI(root)
    root.mainloop()

def process_file(conexoes_file, config, include_orphans=False, layouts_choice="cog", 
                regionalization=False, elementos_file='elementos.csv', 
                localidades_file='localidades.csv', hide_node_names=False, 
                hide_connection_layers=False, ignore_optional=False):
    """
    Processa um arquivo de conexões completo
    
    Args:
        conexoes_file (str): Caminho do arquivo de conexões
        config (dict): Configurações carregadas
        include_orphans (bool): Incluir nós sem conexões
        layouts_choice (str): String com layouts selecionados (ex: "co")
        regionalization (bool): Ativar regionalização
        elementos_file (str): Caminho para arquivo de elementos
        localidades_file (str): Caminho para arquivo de localidades
    """
    file_start = time.perf_counter()
    logger.info("⏱️ [INICIO] Processando arquivo: %s", conexoes_file)
    logger.debug("Parâmetros: orphans=%s, layouts=%s, regional=%s, hide_names=%s, hide_cnx=%s",
                include_orphans, layouts_choice, regionalization, 
                hide_node_names, hide_connection_layers)
    
    try:
        generator = TopologyGenerator(
            elementos_file, 
            conexoes_file, 
            config, 
            include_orphans, 
            regionalization,
            localidades_file,
            hide_node_names,
            hide_connection_layers,
            ignore_optional=ignore_optional
        )
        
        if not generator.valid:
            return False
            
        if not generator.read_elementos():
            return False
            
        if not generator.read_conexoes():
            return False
            
        base_name = os.path.splitext(conexoes_file)[0]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        success = True
        
        # Dicionário de mapeamento de layouts
        layout_map = {
            'c': ('circular', 'Circular'),
            'o': ('organico', 'Orgânico'),
            'g': ('geografico', 'Geográfico'),
            'h': ('hierarquico', 'Hierárquico')
        }
        
        # Lista de layouts a processar
        layouts_to_process = []
        for char in layouts_choice:
            if char in layout_map:
                layout_key, layout_name = layout_map[char]
                # Verificar disponibilidade do geográfico
                if char == 'g':
                    if not generator.has_geographic_data:
                        logger.warning("Layout geográfico solicitado mas sem dados geográficos. Ignorando.")
                        continue
                layouts_to_process.append((layout_key, layout_name))
        
        generated_layouts = []
        # Gerar apenas os layouts selecionados
        for layout_key, layout_name in layouts_to_process:
            output_file = f"{base_name}_{timestamp}_{layout_key}.drawio"
            if generator.generate_drawio(output_file, layout_key):
                generated_layouts.append(layout_name)
            else:
                success = False
        
        # Log de performance detalhada
        file_time = time.perf_counter() - file_start
        logger.info("✅ [SUCESSO] Arquivo processado em %.2fs | Layouts: %s | Nós: %d | Conexões: %d",
                  file_time, ', '.join(generated_layouts), 
                  len(generator.nodes), len(generator.connections))
        
        # Registrar elementos sem siteid
        if generator.nodes_without_siteid:
            nodes_list = ", ".join(generator.nodes_without_siteid[:10])
            if len(generator.nodes_without_siteid) > 10:
                nodes_list += f", ... (+{len(generator.nodes_without_siteid) - 10} mais)"
            logger.debug("%d elementos sem siteid movidos para camada especial: %s", 
                          len(generator.nodes_without_siteid), nodes_list)        
        
        return success
    except Exception as e:
        logger.exception("💥 [FALHA] Erro no processamento")
        logger.error("Contexto: layouts=%s, regional=%s, elementos=%s",
                   layouts_choice, regionalization, elementos_file)
        return False

def main():
    global_start = time.perf_counter()
    verificar_dependencias() 
    
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description='Gerador de Topologias de Rede',
        add_help=False
    )
    
    # Argumentos posicionais
    parser.add_argument(
        'arquivos', 
        nargs='*', 
        help='Arquivos de conexões CSV'
    )
    
    # Argumentos opcionais
    parser.add_argument(
        '-g',
        metavar='DIRETÓRIO',
        default=None,
        help='Diretório base para arquivos de entrada (conexoes.csv, elementos.csv, localidades.csv)'
    )
    parser.add_argument(
        '-y', 
        action='store_true', 
        help='Incluir nós sem conexões'
    )
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true', 
        help='Modo verboso (mostra logs na tela)'
    )
    parser.add_argument(
        '-l', 
        action='store_true', 
        help='Gerar logs em arquivo'
    )
    parser.add_argument(
        '-t', 
        metavar='LAYOUTS', 
        default='cogh', 
        help='Layouts a gerar (c=circular, o=orgânico, g=geográfico, h=hierárquico). Padrão: cogh'
    )
    parser.add_argument(
        '-r', 
        action='store_true', 
        help='Ativar separação regional das camadas'
    )
    parser.add_argument(
        '-e', 
        metavar='ELEMENTOS', 
        default='elementos.csv', 
        help='Caminho para arquivo de elementos (opcional)'
    )
    parser.add_argument(
        '-s', 
        metavar='LOCALIDADES', 
        default='localidades.csv', 
        help='Caminho para arquivo de localidades (opcional)'
    )
    parser.add_argument(
        '-h', '--help',
        action='store_true',
        help='Mostrar ajuda rápida'
    )
    parser.add_argument(
        '-o', 
        metavar='OPÇÕES', 
        default='', 
        help='Opções: n (nós sem nomes), c (ocultar camadas de conexão)'
    )
    parser.add_argument(
        '-d', 
        action='store_true', 
        help='Desprezar definições opcionais dos elementos e conexões (usar apenas config.json)'
    )
    parser.add_argument(
     '-c',
     type=str,
     default='config.json',
     help='Caminho para o arquivo de configuração (padrão: config.json)'
    )
    
    # Tentar analisar os argumentos
    try:
        args = parser.parse_args()
    except SystemExit:
        print(HELP_TEXT)
        sys.exit(1)
    
    # Tratar pedidos de ajuda
    if args.help:
        print(HELP_TEXT)
        sys.exit(0)

    # Registrar informações iniciais
    logger.info("🚀 Iniciando GeradorTopologias %s", versionctr)
    logger.info("Hora de início: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
 
    # Configurar logging
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    
    # ================================================
    # VALIDAÇÃO DETALHADA DO DIRETÓRIO BASE
    # ================================================
    base_dir = args.g
    logger.debug(f"Argumento -g recebido: '{base_dir}'")
    
    # Função auxiliar para normalizar caminhos
    def normalize_path(path):
        return os.path.normpath(os.path.abspath(path)) if path else None
    
    def apply_base_dir(filename):
        if base_dir and filename:
            # Normalizar e validar caminho
            normalized_dir = os.path.abspath(os.path.normpath(base_dir))
            if not os.path.exists(normalized_dir):
                logger.error(f"Diretório base não existe: {normalized_dir}")
                return filename
                
            full_path = os.path.join(normalized_dir, os.path.basename(filename))
            logger.debug(f"BaseDir aplicado: {filename} -> {full_path}")
            return full_path
        return filename

    # ================================================
    # REGRAS PARA -g (sobrescreve outras opções)
    # ================================================
    if base_dir:
        # Força o uso do diretório base para elementos/localidades
        elementos_file = os.path.join(base_dir, "elementos.csv")
        localidades_file = os.path.join(base_dir, "localidades.csv")
        logger.info(f"Usando caminhos fixos no diretório base (-g ativo):")
        logger.info(f" - elementos: {elementos_file}")
        logger.info(f" - localidades: {localidades_file}")
    else:
        # Modo sem -g: respeita opções -e e -s se fornecidas
        elementos_file = apply_base_dir(args.e)
        localidades_file = apply_base_dir(args.s)
    
    # ================================================
    # BUSCA INTELIGENTE DE ARQUIVOS
    # ================================================
    conexoes_files = []
    if args.arquivos:
        # Processa arquivos explicitamente fornecidos pelo usuário
        for f in args.arquivos:
            full_path = apply_base_dir(f)
            if os.path.exists(full_path):
                conexoes_files.append(full_path)
            else:
                logger.error(f"Arquivo não encontrado: {full_path}")
    elif base_dir:
        # Modo -g: busca APENAS por "conexoes*.csv" no diretório base
        logger.info("Buscando arquivos de conexão no diretório base...")
        search_path = os.path.join(base_dir, "conexoes*.csv")
        logger.debug(f"Padrão de busca: {search_path}")
        found_files = glob.glob(search_path, recursive=False)
        
        # Remove duplicatas e valida
        seen = set()
        for f in found_files:
            if os.path.isfile(f) and f not in seen:
                seen.add(f)
                conexoes_files.append(f)
        
        if conexoes_files:
            logger.info(f"Encontrados {len(conexoes_files)} arquivo(s) de conexão:")
            for f in conexoes_files:
                logger.info(f" - {os.path.basename(f)}")
        else:
            logger.warning("Nenhum arquivo de conexão encontrado no diretório")

    # ================================================
    # VERIFICAÇÃO FINAL DOS CAMINHOS
    # ================================================
    logger.debug("="*50)
    logger.debug("RESUMO DE CAMINHOS:")
    logger.debug(f"Diretório base: {base_dir}")
    logger.debug(f"Arquivo de elementos: {elementos_file} -> Existe: {os.path.exists(elementos_file) if elementos_file else 'N/A'}")
    logger.debug(f"Arquivo de localidades: {localidades_file} -> Existe: {os.path.exists(localidades_file) if localidades_file else 'N/A'}")
    logger.debug(f"Arquivos de conexões: {conexoes_files}")
    logger.debug("="*50)
    
    # Se não houver arquivos para processar, executar GUI
    if not conexoes_files:
        logger.info("Nenhum arquivo de conexões encontrado, iniciando GUI")
        run_gui()
        return

    # Remover handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    
    # Configurar handlers baseado nas opções
    if args.verbose:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(stream_handler)
    
    if args.l:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f'topologia_log_{timestamp_str}.txt'
        error_file = f'topologia_errors_{timestamp_str}.log'
        
        # Handler para logs gerais
        file_level = logging.DEBUG if args.verbose else logging.INFO
        file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(file_level)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        
        # Handler separado para erros
        error_handler = logging.FileHandler(error_file, mode='w', encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(error_handler)

        # Novo registro de informações
        logger.info("Execução iniciada via CLI")
        logger.info("Opções usadas (diferentes do padrão):")
        if args.y:
            logger.info("  -y (incluir nós órfãos)")
        if args.r:
            logger.info("  -r (regionalização)")
        if args.t != "cogh":
            logger.info("  -t %s (layouts)", args.t)
        if args.e != "elementos.csv":
            logger.info("  -e %s (elementos)", args.e)
        if args.s != "localidades.csv":
            logger.info("  -s %s (localidades)", args.s)
        if args.o:
            logger.info("  -o %s (visualização)", args.o)
    
    # Registrar informações do sistema
    logger.debug("Sistema: %s %s", sys.platform, platform.platform())
    logger.debug("Python: %s", sys.version)
    logger.debug("Dependências: networkx=%s", nx.__version__)
    
    config = load_config(args.c) if hasattr(args, 'c') else load_config()
    
    # Validar escolha de layouts
    valid_layouts = {'c', 'o', 'g', 'h'}
    layouts_choice = args.t.lower()
    
    if not all(char in valid_layouts for char in layouts_choice):
        logger.error("Opção -t contém caracteres inválidos: '%s'. Use apenas: c, o, g, h", layouts_choice)
        print(f"Erro: opção -t contém caracteres inválidos: '{layouts_choice}'. Use apenas: c, o, g, h")
        sys.exit(1)

    # Verificar existência dos arquivos
    valid_files = []
    for f in conexoes_files:
        if os.path.exists(f):
            valid_files.append(f)
        else:
            logger.error(f"Arquivo não encontrado: {f}")
    
    if not valid_files:
        logger.error("Nenhum arquivo CSV válido especificado")
        print("Erro: Nenhum arquivo CSV válido")
        sys.exit(1)
    
    # Processar opções de visualização
    hide_node_names = 'n' in args.o
    hide_connection_layers = 'c' in args.o
    
    # Processar cada arquivo com as novas opções
    results = []
    for conexoes_file in valid_files:
        results.append(process_file(
            conexoes_file, 
            config, 
            args.y, 
            layouts_choice, 
            args.r,
            elementos_file,
            localidades_file,
            hide_node_names,
            hide_connection_layers,
            ignore_optional=args.d
        ))
    
    # Relatório final de execução
    success_count = sum(1 for r in results if r)
    total_files = len(valid_files)
    total_time = time.perf_counter() - global_start
    
    logger.info("✅ PROCESSAMENTO CONCLUÍDO")
    logger.info("   Arquivos processados: %d/%d com sucesso", success_count, total_files)
    logger.info("   Tempo total: %.2f segundos", total_time)
    log_memory_usage("Final do processamento")
    
    if success_count < total_files:
        logger.error("⛔ Um ou mais arquivos falharam no processamento")
        sys.exit(1)
        
    logger.info("✨ Todas as operações concluídas com sucesso")

# ... (o restante do código permanece igual) ...

if __name__ == "__main__":
    main()
