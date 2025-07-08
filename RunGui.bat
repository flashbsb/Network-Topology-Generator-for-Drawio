@echo off
REM Este script executa a interface gráfica do Gerador de Topologias.
REM Certifique-se de que o Python está instalado e adicionado ao PATH.

echo Iniciando o Gerador de Topologias...

REM O comando 'start "Gerador de Topologias"' abre uma nova janela com o título correto.
REM O '&' permite executar o comando pause na janela original.
start "Gerador de Topologias" python GeradorTopologias.py

echo.
echo A interface do programa foi iniciada em uma nova janela.
echo Esta janela do terminal pode ser fechada.