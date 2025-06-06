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
    for materia in dados["materias"]:
        tempo_total = sum(t["tempoEstudado"] for t in materia["topicos"])
        html += f"<div><h3>{materia['nome']} - {tempo_total:.1f} horas estudadas</h3><ul>"
        html += "<h3>Tópicos:</h3>"
        for topico in materia["topicos"]:
            html += f"<li>{topico['nome']}</li>"
        html += "</ul>"
        html += f'''
        <form action="/adicionar_topico" method="POST">
            <input type="hidden" name="materia" value="{materia['nome']}">
            <input type="text" name="topico" placeholder="Novo tópico" required>
            <button type="submit">Adicionar Tópico</button>
        </form>
        </div><hr>
        '''
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

