from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import sqlite3
from functools import wraps
from werkzeug.security import check_password_hash

app = Flask(__name__)

app.secret_key = "MANFRANP_CHAVE_SECRETA_2026"

ADMIN_UTILIZADOR = "admin"

ADMIN_SENHA_HASH = "scrypt:32768:8:1$tq3IoGwv5UuudFQc$8955d4be47aba11dbcf7c2612ada33e0bb8775f53872a1f60dd322892d4cede2d87a1aa96d8438e083cc1d5ffa670fc46a3335129dab6a9b5f89d75446ee0f75"


def criar_banco():

    conexao = sqlite3.connect("manfranp.db")
    cursor = conexao.cursor()

    # ==============================
    # CONTACTOS
    # ==============================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            mensagem TEXT NOT NULL,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("PRAGMA table_info(contactos)")

    colunas_contactos = cursor.fetchall()

    nomes_colunas_contactos = [
        coluna[1]
        for coluna in colunas_contactos
    ]

    if "lido" not in nomes_colunas_contactos:

        cursor.execute("""
            ALTER TABLE contactos
            ADD COLUMN lido INTEGER DEFAULT 0
        """)

    cursor.execute("""
        UPDATE contactos
        SET lido = 0
        WHERE lido IS NULL
    """)

    # ==============================
    # PEDIDOS
    # ==============================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            projeto TEXT NOT NULL,
            descricao TEXT NOT NULL,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("PRAGMA table_info(pedidos)")

    colunas_pedidos = cursor.fetchall()

    nomes_colunas_pedidos = [
        coluna[1]
        for coluna in colunas_pedidos
    ]

    if "estado" not in nomes_colunas_pedidos:

        cursor.execute("""
            ALTER TABLE pedidos
            ADD COLUMN estado TEXT DEFAULT 'Novo'
        """)

    if "lido" not in nomes_colunas_pedidos:

        cursor.execute("""
            ALTER TABLE pedidos
            ADD COLUMN lido INTEGER DEFAULT 0
        """)

    cursor.execute("""
        UPDATE pedidos
        SET estado = 'Novo'
        WHERE estado IS NULL OR estado = ''
    """)

    cursor.execute("""
        UPDATE pedidos
        SET lido = 0
        WHERE lido IS NULL
    """)

    # ==============================
    # ORÇAMENTOS
    # ==============================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            cliente TEXT NOT NULL,
            email TEXT NOT NULL,
            projeto TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            prazo TEXT NOT NULL,
            observacoes TEXT,
            estado TEXT DEFAULT 'Rascunho',
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
        )
    """)

    cursor.execute("""
        UPDATE orcamentos
        SET estado = 'Rascunho'
        WHERE estado IS NULL OR estado = ''
    """)

    conexao.commit()
    conexao.close()


def administrador_required(funcao):

    @wraps(funcao)
    def verificar_login(*args, **kwargs):

        if not session.get("administrador"):

            return redirect(url_for("login"))

        return funcao(*args, **kwargs)

    return verificar_login


# ==========================================
# SITE
# ==========================================

@app.route("/")
def inicio():

    return render_template("index.html")


# ==========================================
# CONTACTO
# ==========================================

@app.route("/contacto", methods=["POST"])
def contacto():

    dados = request.get_json()

    if not dados:

        return jsonify({
            "sucesso": False,
            "mensagem": "Não foram recebidos dados."
        })

    nome = dados.get("nome", "").strip()
    email = dados.get("email", "").strip()
    mensagem = dados.get("mensagem", "").strip()

    if not nome or not email or not mensagem:

        return jsonify({
            "sucesso": False,
            "mensagem": "Preencha todos os campos."
        })

    try:

        conexao = sqlite3.connect("manfranp.db")
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO contactos
            (nome, email, mensagem, lido)
            VALUES (?, ?, ?, ?)
        """, (
            nome,
            email,
            mensagem,
            0
        ))

        conexao.commit()
        conexao.close()

        print()
        print("==============================")
        print("NOVA MENSAGEM - MANFRANP")
        print("==============================")
        print("Nome:", nome)
        print("Email:", email)
        print("Mensagem:", mensagem)
        print("==============================")
        print()

        return jsonify({
            "sucesso": True,
            "mensagem": "Mensagem recebida e guardada com sucesso!"
        })

    except Exception as erro:

        print("ERRO AO GUARDAR CONTACTO:", erro)

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao guardar a mensagem."
        })


# ==========================================
# PEDIDO
# ==========================================

@app.route("/pedido", methods=["POST"])
def pedido():

    dados = request.get_json()

    if not dados:

        return jsonify({
            "sucesso": False,
            "mensagem": "Não foram recebidos dados."
        })

    nome = dados.get("nome", "").strip()
    email = dados.get("email", "").strip()
    projeto = dados.get("projeto", "").strip()
    descricao = dados.get("descricao", "").strip()

    if not nome or not email or not projeto or not descricao:

        return jsonify({
            "sucesso": False,
            "mensagem": "Preencha todos os campos."
        })

    try:

        conexao = sqlite3.connect("manfranp.db")
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO pedidos
            (nome, email, projeto, descricao, estado, lido)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            nome,
            email,
            projeto,
            descricao,
            "Novo",
            0
        ))

        conexao.commit()
        conexao.close()

        print()
        print("==============================")
        print("NOVO PEDIDO - MANFRANP")
        print("==============================")
        print("Cliente:", nome)
        print("Email:", email)
        print("Projeto:", projeto)
        print("Descrição:", descricao)
        print("Estado: Novo")
        print("==============================")
        print()

        return jsonify({
            "sucesso": True,
            "mensagem": "Pedido recebido e guardado com sucesso!"
        })

    except Exception as erro:

        print("ERRO AO GUARDAR PEDIDO:", erro)

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao guardar o pedido."
        })


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        utilizador = request.form.get("utilizador")
        senha = request.form.get("senha")

        if (
            utilizador == ADMIN_UTILIZADOR
            and check_password_hash(
                ADMIN_SENHA_HASH,
                senha
            )
        ):

            session["administrador"] = True

            return redirect(url_for("admin"))

        return render_template(
            "login.html",
            erro="Utilizador ou senha incorretos."
        )

    return render_template("login.html")


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ==========================================
# PAINEL ADMINISTRATIVO
# ==========================================

@app.route("/admin")
@administrador_required
def admin():

    conexao = sqlite3.connect("manfranp.db")
    cursor = conexao.cursor()

    # CONTACTOS

    cursor.execute("""
        SELECT COUNT(*)
        FROM contactos
    """)

    total_contactos = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM contactos
        WHERE lido = 0
    """)

    contactos_nao_lidos = cursor.fetchone()[0]

    cursor.execute("""
        SELECT
            id,
            nome,
            email,
            mensagem,
            data,
            lido
        FROM contactos
        ORDER BY id DESC
    """)

    contactos = cursor.fetchall()

    # PEDIDOS

    cursor.execute("""
        SELECT COUNT(*)
        FROM pedidos
    """)

    total_pedidos = cursor.fetchone()[0]

    cursor.execute("""
        SELECT
            id,
            nome,
            email,
            projeto,
            descricao,
            data,
            estado,
            lido
        FROM pedidos
        ORDER BY id DESC
    """)

    pedidos = cursor.fetchall()

    # ESTADOS

    cursor.execute("""
        SELECT
            id,
            estado
        FROM pedidos
    """)

    estados_resultado = cursor.fetchall()

    estados_pedidos = {}

    for pedido_id, estado in estados_resultado:

        if not estado:
            estado = "Novo"

        estados_pedidos[pedido_id] = estado

    # CONTADORES

    cursor.execute("""
        SELECT COUNT(*)
        FROM pedidos
        WHERE estado = 'Novo'
    """)

    total_novos = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM pedidos
        WHERE estado = 'Em análise'
    """)

    total_em_analise = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM pedidos
        WHERE estado = 'Em andamento'
    """)

    total_em_andamento = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM pedidos
        WHERE estado = 'Concluído'
    """)

    total_concluidos = cursor.fetchone()[0]

    # NOTIFICAÇÕES

    cursor.execute("""
        SELECT COUNT(*)
        FROM pedidos
        WHERE lido = 0
    """)

    pedidos_nao_lidos = cursor.fetchone()[0]

    total_notificacoes = (
        pedidos_nao_lidos +
        contactos_nao_lidos
    )

    # ORÇAMENTOS

    cursor.execute("""
        SELECT COUNT(*)
        FROM orcamentos
    """)

    total_orcamentos = cursor.fetchone()[0]

    cursor.execute("""
        SELECT
            id,
            pedido_id,
            cliente,
            email,
            projeto,
            descricao,
            valor,
            prazo,
            observacoes,
            estado,
            data
        FROM orcamentos
        ORDER BY id DESC
    """)

    orcamentos = cursor.fetchall()

    total_atividade = (
        total_contactos +
        total_pedidos +
        total_orcamentos
    )

    conexao.close()

    return render_template(
        "admin.html",

        total_contactos=total_contactos,
        total_pedidos=total_pedidos,
        total_atividade=total_atividade,

        total_notificacoes=total_notificacoes,

        total_novos=total_novos,
        total_em_analise=total_em_analise,
        total_em_andamento=total_em_andamento,
        total_concluidos=total_concluidos,

        contactos_nao_lidos=contactos_nao_lidos,
        pedidos_nao_lidos=pedidos_nao_lidos,

        contactos=contactos,
        pedidos=pedidos,
        estados_pedidos=estados_pedidos,

        total_orcamentos=total_orcamentos,
        orcamentos=orcamentos
    )


# ==========================================
# MARCAR CONTACTO COMO LIDO
# ==========================================

@app.route(
    "/admin/contacto/lido/<int:id>",
    methods=["POST"]
)
@administrador_required
def marcar_contacto_lido(id):

    conexao = sqlite3.connect("manfranp.db")
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE contactos
        SET lido = 1
        WHERE id = ?
    """, (id,))

    conexao.commit()
    conexao.close()

    return jsonify({
        "sucesso": True
    })


# ==========================================
# MARCAR PEDIDO COMO LIDO
# ==========================================

@app.route(
    "/admin/pedido/lido/<int:id>",
    methods=["POST"]
)
@administrador_required
def marcar_pedido_lido(id):

    conexao = sqlite3.connect("manfranp.db")
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE pedidos
        SET lido = 1
        WHERE id = ?
    """, (id,))

    conexao.commit()
    conexao.close()

    return jsonify({
        "sucesso": True
    })


# ==========================================
# ALTERAR ESTADO DO PEDIDO
# ==========================================

@app.route(
    "/admin/pedido/estado/<int:id>",
    methods=["POST"]
)
@administrador_required
def alterar_estado_pedido(id):

    estado = request.form.get(
        "estado",
        "Novo"
    )

    estados_permitidos = [
        "Novo",
        "Em análise",
        "Em andamento",
        "Concluído"
    ]

    if estado not in estados_permitidos:

        estado = "Novo"

    conexao = sqlite3.connect("manfranp.db")
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE pedidos
        SET estado = ?
        WHERE id = ?
    """, (
        estado,
        id
    ))

    conexao.commit()
    conexao.close()

    return redirect(url_for("admin"))


# ==========================================
# CRIAR ORÇAMENTO
# ==========================================

@app.route(
    "/admin/orcamento/criar/<int:pedido_id>",
    methods=["POST"]
)
@administrador_required
def criar_orcamento(pedido_id):

    valor = request.form.get(
        "valor",
        ""
    ).strip()

    prazo = request.form.get(
        "prazo",
        ""
    ).strip()

    observacoes = request.form.get(
        "observacoes",
        ""
    ).strip()

    if not valor or not prazo:

        return redirect(url_for("admin"))

    try:

        valor_limpo = (
            valor
            .replace("Kz", "")
            .replace("kz", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )

        valor_numerico = float(valor_limpo)

    except ValueError:

        return redirect(url_for("admin"))

    conexao = sqlite3.connect("manfranp.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            nome,
            email,
            projeto,
            descricao
        FROM pedidos
        WHERE id = ?
    """, (pedido_id,))

    pedido = cursor.fetchone()

    if not pedido:

        conexao.close()

        return redirect(url_for("admin"))

    nome = pedido[0]
    email = pedido[1]
    projeto = pedido[2]
    descricao = pedido[3]

    cursor.execute("""
        INSERT INTO orcamentos
        (
            pedido_id,
            cliente,
            email,
            projeto,
            descricao,
            valor,
            prazo,
            observacoes,
            estado
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        pedido_id,
        nome,
        email,
        projeto,
        descricao,
        valor_numerico,
        prazo,
        observacoes,
        "Rascunho"
    ))

    conexao.commit()
    conexao.close()

    return redirect(url_for("admin"))


# ==========================================
# ALTERAR ESTADO DO ORÇAMENTO
# ==========================================

@app.route(
    "/admin/orcamento/estado/<int:id>",
    methods=["POST"]
)
@administrador_required
def alterar_estado_orcamento(id):

    estado = request.form.get(
        "estado",
        "Rascunho"
    )

    estados_permitidos = [
        "Rascunho",
        "Enviado",
        "Aprovado",
        "Recusado"
    ]

    if estado not in estados_permitidos:

        estado = "Rascunho"

    conexao = sqlite3.connect("manfranp.db")
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE orcamentos
        SET estado = ?
        WHERE id = ?
    """, (
        estado,
        id
    ))

    conexao.commit()
    conexao.close()

    return redirect(url_for("admin"))


# ==========================================
# GERAR PDF DO ORÇAMENTO
# ==========================================

@app.route(
    "/admin/orcamento/pdf/<int:id>",
    methods=["GET"]
)
@administrador_required
def gerar_pdf_orcamento(id):

    try:

        from io import BytesIO

        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import (
            getSampleStyleSheet,
            ParagraphStyle
        )
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            Image
        )

        conexao = sqlite3.connect("manfranp.db")
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT
                id,
                pedido_id,
                cliente,
                email,
                projeto,
                descricao,
                valor,
                prazo,
                observacoes,
                estado,
                data
            FROM orcamentos
            WHERE id = ?
        """, (id,))

        orcamento = cursor.fetchone()

        conexao.close()

        if not orcamento:

            return "Orçamento não encontrado.", 404

        (
            orcamento_id,
            pedido_id,
            cliente,
            email,
            projeto,
            descricao,
            valor,
            prazo,
            observacoes,
            estado,
            data
        ) = orcamento

        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title=f"Orçamento MANFRANP #{orcamento_id}",
            author="MANFRANP | Projetos & Tecnologia"
        )

        estilos = getSampleStyleSheet()

        estilo_titulo = ParagraphStyle(
            "TituloMANFRANP",
            parent=estilos["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1e3a8a"),
            alignment=TA_LEFT,
            spaceAfter=5
        )

        estilo_subtitulo = ParagraphStyle(
            "SubtituloMANFRANP",
            parent=estilos["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=12
        )

        estilo_secao = ParagraphStyle(
            "SecaoMANFRANP",
            parent=estilos["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#1e3a8a"),
            spaceBefore=10,
            spaceAfter=7
        )

        estilo_texto = ParagraphStyle(
            "TextoMANFRANP",
            parent=estilos["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=colors.HexColor("#334155")
        )

        estilo_pequeno = ParagraphStyle(
            "PequenoMANFRANP",
            parent=estilos["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#64748b")
        )

        def seguro(valor):

            if valor is None:
                return ""

            return (
                str(valor)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

        def paragrafo(valor, estilo=estilo_texto):

            texto = seguro(valor).replace(
                "\n",
                "<br/>"
            )

            return Paragraph(
                texto or "-",
                estilo
            )

        elementos = []

        logo_path = (
            app.root_path +
            "/static/images/logo.png"
        )

        try:

            logo = Image(
                logo_path,
                width=38 * mm,
                height=10 * mm,
                kind="proportional"
            )

            elementos.append(logo)
            elementos.append(
                Spacer(1, 5 * mm)
            )

        except Exception:

            pass

        elementos.append(
            Paragraph(
                "ORÇAMENTO",
                estilo_titulo
            )
        )

        elementos.append(
            Paragraph(
                f"MANFRANP | Projetos & Tecnologia "
                f"&nbsp;&nbsp;|&nbsp;&nbsp; "
                f"Orçamento #{orcamento_id}",
                estilo_subtitulo
            )
        )

        cabecalho = Table(
            [
                [
                    Paragraph(
                        "CLIENTE",
                        estilo_pequeno
                    ),
                    Paragraph(
                        "ESTADO",
                        estilo_pequeno
                    ),
                    Paragraph(
                        "DATA",
                        estilo_pequeno
                    )
                ],
                [
                    paragrafo(
                        cliente,
                        estilo_texto
                    ),
                    paragrafo(
                        estado,
                        estilo_texto
                    ),
                    paragrafo(
                        data,
                        estilo_texto
                    )
                ]
            ],
            colWidths=[
                80 * mm,
                45 * mm,
                45 * mm
            ]
        )

        cabecalho.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#eaf2ff")
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.HexColor("#cbd5e1")
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e2e8f0")
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ])
        )

        elementos.append(cabecalho)

        elementos.append(
            Spacer(1, 6 * mm)
        )

        elementos.append(
            Paragraph(
                "DADOS DO PROJETO",
                estilo_secao
            )
        )

        dados_projeto = Table(
            [
                [
                    Paragraph(
                        "Projeto",
                        estilo_pequeno
                    ),
                    paragrafo(projeto)
                ],
                [
                    Paragraph(
                        "Email",
                        estilo_pequeno
                    ),
                    paragrafo(email)
                ],
                [
                    Paragraph(
                        "Descrição",
                        estilo_pequeno
                    ),
                    paragrafo(descricao)
                ]
            ],
            colWidths=[
                35 * mm,
                135 * mm
            ]
        )

        dados_projeto.setStyle(
            TableStyle([
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.HexColor("#cbd5e1")
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e2e8f0")
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#f8fafc")
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ])
        )

        elementos.append(dados_projeto)

        elementos.append(
            Spacer(1, 6 * mm)
        )

        elementos.append(
            Paragraph(
                "VALOR E PRAZO",
                estilo_secao
            )
        )

        valor_formatado = (
            f"{float(valor):,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        estilo_valor = ParagraphStyle(
            "ValorGrande",
            parent=estilo_texto,
            fontSize=17,
            leading=20,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#166534")
        )

        resumo = Table(
            [
                [
                    Paragraph(
                        "VALOR DO PROJETO",
                        estilo_pequeno
                    ),
                    Paragraph(
                        "PRAZO DE ENTREGA",
                        estilo_pequeno
                    )
                ],
                [
                    Paragraph(
                        f"{valor_formatado} Kz",
                        estilo_valor
                    ),
                    paragrafo(
                        prazo,
                        estilo_texto
                    )
                ]
            ],
            colWidths=[
                85 * mm,
                85 * mm
            ]
        )

        resumo.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#f0fdf4")
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    colors.HexColor("#bbf7d0")
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#dcfce7")
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                )
            ])
        )

        elementos.append(resumo)

        elementos.append(
            Spacer(1, 6 * mm)
        )

        elementos.append(
            Paragraph(
                "OBSERVAÇÕES",
                estilo_secao
            )
        )

        elementos.append(
            Paragraph(
                (
                    seguro(observacoes)
                    .replace("\n", "<br/>")
                    if observacoes
                    else "Sem observações adicionais."
                ),
                estilo_texto
            )
        )

        elementos.append(
            Spacer(1, 10 * mm)
        )

        aviso = Table(
            [
                [
                    Paragraph(
                        "Este orçamento foi emitido pela "
                        "MANFRANP e representa uma proposta "
                        "de prestação de serviços. Valores e "
                        "prazos podem ser ajustados mediante "
                        "acordo entre as partes.",
                        estilo_pequeno
                    )
                ]
            ],
            colWidths=[170 * mm]
        )

        aviso.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#f8fafc")
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.HexColor("#cbd5e1")
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                )
            ])
        )

        elementos.append(aviso)

        def rodape(canvas, documento):

            canvas.saveState()

            canvas.setStrokeColor(
                colors.HexColor("#cbd5e1")
            )

            canvas.line(
                18 * mm,
                13 * mm,
                192 * mm,
                13 * mm
            )

            canvas.setFont(
                "Helvetica",
                8
            )

            canvas.setFillColor(
                colors.HexColor("#64748b")
            )

            canvas.drawString(
                18 * mm,
                8 * mm,
                "MANFRANP | Projetos & Tecnologia"
            )

            canvas.drawRightString(
                192 * mm,
                8 * mm,
                f"Página {documento.page}"
            )

            canvas.restoreState()

        doc.build(
            elementos,
            onFirstPage=rodape,
            onLaterPages=rodape
        )

        buffer.seek(0)

        nome_arquivo = (
            f"MANFRANP_Orcamento_{orcamento_id}.pdf"
        )

        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=False,
            download_name=nome_arquivo
        )

    except ImportError:

        return (
            "A biblioteca ReportLab não está instalada. "
            "No terminal, execute: pip install reportlab",
            500
        )

    except Exception as erro:

        print(
            "ERRO AO GERAR PDF:",
            erro
        )

        return (
            "Não foi possível gerar o PDF deste orçamento.",
            500
        )


# ==========================================
# APAGAR ORÇAMENTO
# ==========================================

@app.route(
    "/admin/orcamento/apagar/<int:id>",
    methods=["POST"]
)
@administrador_required
def apagar_orcamento(id):

    conexao = sqlite3.connect("manfranp.db")
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM orcamentos
        WHERE id = ?
    """, (id,))

    conexao.commit()
    conexao.close()

    return redirect(url_for("admin"))


# ==========================================
# APAGAR CONTACTO
# ==========================================

@app.route(
    "/admin/contacto/apagar/<int:id>",
    methods=["POST"]
)
@administrador_required
def apagar_contacto(id):

    conexao = sqlite3.connect("manfranp.db")
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM contactos
        WHERE id = ?
    """, (id,))

    conexao.commit()
    conexao.close()

    return redirect(url_for("admin"))


# ==========================================
# APAGAR PEDIDO
# ==========================================

@app.route(
    "/admin/pedido/apagar/<int:id>",
    methods=["POST"]
)
@administrador_required
def apagar_pedido(id):

    conexao = sqlite3.connect("manfranp.db")
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM pedidos
        WHERE id = ?
    """, (id,))

    conexao.commit()
    conexao.close()

    return redirect(url_for("admin"))


# ==========================================
# INICIAR
# ==========================================

if __name__ == "__main__":

    criar_banco()

    app.run(debug=True)