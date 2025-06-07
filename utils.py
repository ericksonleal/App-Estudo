import json
PORTA = 8080
DIRETORIO = "templates"
CAMINHO_DADOS = "data/dados.json"

# --------------------------------------------------- Funções ----------------------------------------------------


def carregar_dados():
    try:
        with open(CAMINHO_DADOS, "r", encoding="utf-8") as file:
            dados = json.load(file)

            if "metaSemanal" not in dados:
                dados["metaSemanal"] = 0
            if "materias" not in dados:
                dados["materias"] = []

            return dados

    except (FileNotFoundError, json.JSONDecodeError):
        return {"metaSemanal": 0, "materias": []}


def salvar_dados(dados):
    with open(CAMINHO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

# --------------------------------- Funções dinâmicas para HTML ---------------------------------------------


def html_materias():
    dados = carregar_dados()
    html = ""

    for materia in dados.get("materias", []):
        nome = materia.get("nome", "")
        html += f'<section class="materia" data-materia="{nome}">'
        html += f"<h3>{nome}</h3><ul>"
        for topico in materia.get("topicos", []):
            nome_topico = topico.get("nome", "")
            tempo = topico.get("tempoEstudado", 0)
            html += f"<li>{nome_topico} — {tempo:.1f}h</li>"
        html += "</ul></section>"

    return html

# ----------------------------- Servem para seleções de matérias como dropdowns no front-end ----------------------


def opcoes_materias():
    dados = carregar_dados()
    return "".join([f'<option value="{m["nome"]}">{m["nome"]}</option>' for m in dados["materias"]])


# ----------------------------- Seleções de tópicos como dropdowns no front-end ----------------------

def opcoes_topicos():
    dados = carregar_dados()
    opcoes = ""
    for m in dados["materias"]:
        for t in m["topicos"]:
            opcoes += f'<option value="{m["nome"]}|{t["nome"]}">{m["nome"]} - {t["nome"]}</option>'
    return opcoes

# ----------------------------- Criação das funções dos gráficos ----------------------


def grafico_materias(dados):
    materias = dados.get("materias", [])
    labels = []
    valores = []

    for materia in materias:
        nome = materia.get("nome", "Sem nome")
        total = sum(t.get("tempoEstudado", 0)
                    for t in materia.get("topicos", []))
        if total > 0:
            labels.append(nome)
            valores.append(total)

    return {"labels": labels, "valores": valores}


def graficos_topicos(dados):
    resultado = {}
    for materia in dados.get("materias", []):
        nome = materia.get("nome", "Sem nome")
        topicos = materia.get("topicos", [])

        labels = []
        valores = []

        for topico in topicos:
            horas = topico.get("tempoEstudado", 0)
            if horas > 0:
                labels.append(topico.get("nome", "Tópico"))
                valores.append(horas)

        if valores:
            resultado[nome] = {"labels": labels, "valores": valores}

    return resultado
