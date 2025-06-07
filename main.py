import http.server
import socketserver
import json
import os
from urllib.parse import parse_qs
from utils import (carregar_dados, salvar_dados,
                   html_materias, opcoes_materias, opcoes_topicos)
from utils import grafico_materias, graficos_topicos

PORTA = 8080
DIRETORIO = "templates"

# ------------------------------------------------------------ Servidor ------------------------------------------------------------


class ServidorHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    # ---------------------------------------- do_GET ( faz requisições do tipo GET ) ---------------------------------
    # Essa função responde a requisições do tipo GET quando o navegador pede uma para exibir uma página ---------
    def do_GET(self):
        if self.path == "/":
            with open(f"{DIRETORIO}/index.html", "r", encoding="utf-8") as f:
                html_base = f.read()

            info = carregar_dados()
            meta = info.get("metaSemanal", 0)

            # --------  Calcula o total de horas estudadas
            progresso = 0.0
            for materia in info.get("materias", []):
                for topico in materia.get("topicos", []):
                    progresso += topico.get("tempoEstudado", 0)

            porcentagem = min(100, (progresso / meta * 100) if meta > 0 else 0)

        # --------  Prepara os dados dos gráficos 
            grafico_materias_json = json.dumps(grafico_materias(info)).replace("</", "<\\/")
            graficos_topicos_json = json.dumps(graficos_topicos(info)).replace("</", "<\\/")

            html_final = (html_base
                        .replace("{{META}}", f"{meta:.1f}")
                        .replace("{{PROGRESSO}}", f"{progresso:.1f}")
                        .replace("{{PORCENTAGEM}}", f"{porcentagem:.1f}")
                        .replace("{{MATERIAS_DINAMICAS}}", html_materias())
                        .replace("{{GRAFICO_MATERIAS_JSON}}", grafico_materias_json)
                        .replace("{{GRAFICOS_TOPICOS_JSON}}", graficos_topicos_json))

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_final.encode("utf-8"))
            return

        elif self.path == "/materias":
            with open(f"{DIRETORIO}/materias.html", "r", encoding="utf-8") as f:
                html_base = f.read()
            html_final = html_base.replace(
                "{{MATERIAS_DINAMICAS}}", html_materias())
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_final.encode("utf-8"))
            return
        elif self.path == "/registro":
            with open(f"{DIRETORIO}/registro.html", "r", encoding="utf-8") as f:
                html = f.read()
            html = html.replace("{{OPCOES_MATERIAS}}", opcoes_materias())
            html = html.replace("{{OPCOES_TOPICOS}}", opcoes_topicos())
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        elif self.path.startswith("/static/"):
            self.path = self.path
        else:
            self.path = f"/{DIRETORIO}/404.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


# ------------------------------------------ do_POST ( Método POST ) --------------------------------------------
# Essa função responde a requisições POST, ou seja quando um formulário é enviado para o servidor


    def do_POST(self):
        comprimento = int(self.headers['Content-Length'])
        dados_brutos = self.rfile.read(comprimento).decode('utf-8')
        dados = parse_qs(dados_brutos)

        if self.path == "/adicionar_materia":
            nome = dados.get("nome", [""])[0]
            topicos_texto = dados.get("topicos", [""])[0]
            topicos_lista = []

            if topicos_texto.strip():
                nomes_topicos = [t.strip() for t in topicos_texto.split(",")]
                for nome_topico in nomes_topicos:
                    topicos_lista.append({
                        "nome": nome_topico,
                        "tempoEstudado": 0
                    })

            nova = {"nome": nome, "topicos": topicos_lista}
            info = carregar_dados()
            info["materias"].append(nova)
            salvar_dados(info)

            self.send_response(303)
            self.send_header('Location', '/materias')
            self.end_headers()
            return

        elif self.path == "/adicionar_topico":
            nome_materia = dados.get("materia", [""])[0]
            nome_topico = dados.get("topico", [""])[0]
            info = carregar_dados()
            for materia in info["materias"]:
                if materia["nome"] == nome_materia:
                    materia["topicos"].append({
                        "nome": nome_topico,
                        "tempoEstudado": 0
                    })
                    break
            salvar_dados(info)

            self.send_response(303)
            self.send_header('Location', '/materias')
            self.end_headers()
            return

        elif self.path == "/registrar_estudo":
            materia_nome = dados.get("materia", [""])[0]
            topico_selecionado = dados.get("topico", [""])[0]
            tempo = float(dados.get("tempo", [0])[0])
            anotacoes = dados.get("anotacoes", [""])[0]

            materia, topico = topico_selecionado.split("|")

            info = carregar_dados()
            for m in info["materias"]:
                if m["nome"] == materia:
                    for t in m["topicos"]:
                        if t["nome"] == topico:
                            t["tempoEstudado"] += tempo
                            break

            salvar_dados(info)

            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
            return

        elif self.path == "/definir_meta":
            nova_meta = float(dados.get("meta", [""])[0])
            info = carregar_dados()
            info["metaSemanal"] = nova_meta
            salvar_dados(info)

            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
            return


os.chdir(".")

with socketserver.TCPServer(("", PORTA), ServidorHTTPRequestHandler) as httpd:
    print(f"Servidor rodando em http://localhost:{PORTA}")
    httpd.serve_forever()
