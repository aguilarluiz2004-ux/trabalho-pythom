import customtkinter
from CTkMessagebox import CTkMessagebox
import sqlite3  # Usando SQLite em vez de pandas e os
import tkinter as tk
from tkinter import ttk

# --- Funções do Banco de Dados ---

# Nome do arquivo do banco de dados
DATABASE = "alunos.db"

def conectar_e_criar_tabela():
    """Conecta ao banco de dados e garante que a tabela 'alunos' exista."""
    # O sqlite3.connect cria o arquivo de banco de dados se ele não existir
    conexao = sqlite3.connect(DATABASE)
    cursor = conexao.cursor()
    # Usamos "IF NOT EXISTS" para não dar erro se a tabela já foi criada
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            Matricula INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome TEXT NOT NULL,
            Idade INTEGER,
            Curso TEXT
        )
    """)
    conexao.commit()
    conexao.close()

def cadastrar():
    nome = entry_nome.get()
    idade = entry_idade.get()
    curso = entry_curso.get()

    if nome == "" or idade == "" or curso == "":
        CTkMessagebox(title="Atenção", message="Preencha todos os campos!", icon="warning")
        return

    try:
        conexao = sqlite3.connect(DATABASE)
        cursor = conexao.cursor()
        # Inserimos os dados, a Matrícula será gerada automaticamente pelo AUTOINCREMENT
        cursor.execute("INSERT INTO alunos (Nome, Idade, Curso) VALUES (?, ?, ?)", (nome, idade, curso))
        # Pegamos o ID (Matricula) do último item inserido para mostrar na mensagem
        matricula_gerada = cursor.lastrowid
        conexao.commit()
        conexao.close()

        CTkMessagebox(title="Sucesso", message=f"Aluno {nome} cadastrado com matrícula {matricula_gerada}!", icon="check")

        entry_nome.delete(0, tk.END)
        entry_idade.delete(0, tk.END)
        entry_curso.delete(0, tk.END)
    except Exception as e:
        CTkMessagebox(title="Erro de Cadastro", message=f"Ocorreu um erro: {e}", icon="cancel")
        
    if not idade.isdigit():
            CTkMessagebox(title="Erro", message="A idade deve ser um número inteiro!", icon="warning")
    



def pesquisar():
    matricula = entry_pesquisa.get()

    if matricula == "":
        CTkMessagebox(title="Atenção", message="Digite a matrícula do aluno!", icon="warning")
        return

    try:
        conexao = sqlite3.connect(DATABASE)
        cursor = conexao.cursor()
        # Seleciona o aluno com a matrícula informada
        cursor.execute("SELECT * FROM alunos WHERE Matricula = ?", (matricula,))
        aluno = cursor.fetchone() # Pega o primeiro (e único) resultado
        conexao.close()

        if aluno: # Se 'aluno' não for None, ele foi encontrado
            # aluno[0] = Matricula, aluno[1] = Nome, etc.
                CTkMessagebox(title="Resultado", message=f"Matrícula: {aluno[0]}\nNome: {aluno[1]}\nIdade: {aluno[2]}\nCurso: {aluno[3]}", icon="info")
        else:
            CTkMessagebox(title="Não encontrado", message="Aluno não encontrado.", icon="warning")

    except Exception as e:
        CTkMessagebox(title="Erro de Pesquisa", message=f"Ocorreu um erro: {e}", icon="cancel")


def excluir():
    matricula = entry_pesquisa.get()

    if matricula == "":
        CTkMessagebox(title="Atenção", message="Digite a matrícula do aluno!", icon="warning")
        return

    try:
        conexao = sqlite3.connect(DATABASE)
        cursor = conexao.cursor()
        # Primeiro, verificamos se o aluno existe
        cursor.execute("SELECT * FROM alunos WHERE Matricula = ?", (matricula,))
        aluno = cursor.fetchone()

        if aluno:
            msg = CTkMessagebox(title="Confirmar Exclusão",
                                message=f"Tem certeza que deseja excluir o aluno com matrícula {matricula}?",
                                icon="question",
                                option_1="Não",
                                option_2="Sim")
            
            if msg.get() == "Sim":
                cursor.execute("DELETE FROM alunos WHERE Matricula = ?", (matricula,))
                conexao.commit()
                CTkMessagebox(title="Sucesso", message=f"Aluno com matrícula {matricula} foi excluído!", icon="check")
            else:
                CTkMessagebox(title="Cancelado", message="A exclusão foi cancelada.", icon="info")
        else:
            CTkMessagebox(title="Erro", message="Matrícula não encontrada.", icon="warning")
        
        conexao.close()
    except Exception as e:
        CTkMessagebox(title="Erro ao Excluir", message=f"Ocorreu um erro: {e}", icon="cancel")

def listar():
    try:
        conexao = sqlite3.connect(DATABASE)
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM alunos")
        alunos = cursor.fetchall() # Pega todos os resultados
        conexao.close()

        if not alunos:
            CTkMessagebox(title="Aviso", message="Nenhum aluno cadastrado.", icon="info")
        else:
            lista_janela = customtkinter.CTkToplevel(janela)
            lista_janela.title("Lista de Alunos")
            lista_janela.geometry("600x400")

            style = ttk.Style()
            style.theme_use("default")
            
            # Solução: Usar cores fixas para o tema escuro
            bg_color = "#2b2b2b"      # Cor de fundo escura
            text_color = "#dce4ee"    # Cor do texto clara
            selected_color = "#36719f"  # Um tom de azul para o item selecionado
            
            style.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0, rowheight=25)
            style.map("Treeview", background=[("selected", selected_color)], foreground=[("selected", text_color)])
            
            tree = ttk.Treeview(lista_janela, columns=("Matricula", "Nome", "Idade", "Curso"), show="headings", style="Treeview")

            tree.heading("Matricula", text="Matrícula")
            tree.heading("Nome", text="Nome")
            tree.heading("Idade", text="Idade")
            tree.heading("Curso", text="Curso")

            for aluno in alunos:
                tree.insert("", tk.END, values=aluno)

            tree.pack(expand=True, fill="both", padx=10, pady=10)
    except Exception as e:
        CTkMessagebox(title="Erro ao Listar", message=f"Ocorreu um erro: {e}", icon="cancel")

# --- Interface Gráfica ---

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

janela = customtkinter.CTk()
janela.title("Sistema de Cadastro de Alunos")
janela.geometry("500x550")

# Executa a função para criar o banco e a tabela assim que o programa inicia
conectar_e_criar_tabela()

customtkinter.CTkLabel(janela, text="Cadastro de Aluno", font=customtkinter.CTkFont(size=18, weight="bold")).pack(pady=10)

customtkinter.CTkLabel(janela, text="Nome:").pack(pady=(10, 0))
entry_nome = customtkinter.CTkEntry(janela, width=250)
entry_nome.pack()

customtkinter.CTkLabel(janela, text="Idade:").pack(pady=(10, 0))
entry_idade = customtkinter.CTkEntry(janela, width=250)
entry_idade.pack()

customtkinter.CTkLabel(janela, text="Curso:").pack(pady=(10, 0))
entry_curso = customtkinter.CTkEntry(janela, width=250)
entry_curso.pack()

btn_cadastrar = customtkinter.CTkButton(janela, text="Cadastrar", command=cadastrar)
btn_cadastrar.pack(pady=10)

customtkinter.CTkLabel(janela, text="Pesquisar / Excluir aluno pela Matrícula:", font=customtkinter.CTkFont(size=14)).pack(pady=10)
entry_pesquisa = customtkinter.CTkEntry(janela, width=150)
entry_pesquisa.pack()

btn_pesquisar = customtkinter.CTkButton(janela, text="Pesquisar", command=pesquisar)
btn_pesquisar.pack(pady=5)

btn_excluir = customtkinter.CTkButton(janela, text="Excluir", command=excluir, fg_color="red", hover_color="darkred")
btn_excluir.pack(pady=5)

btn_listar = customtkinter.CTkButton(janela, text="Listar todos os alunos", command=listar, fg_color="orange", hover_color="darkorange", text_color="black")
btn_listar.pack(pady=20)

janela.mainloop()