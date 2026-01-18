import sys
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Adiciona o diretório pai ao path para importar arquivos compartilhados
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import carregar_todos_os_dados, salvar_no_arquivo
from shared.utils import extrair_nome_e_data, validar_data

# --- CONFIGURAÇÕES ---
TOKEN = '8372581903:AAFZgxbKBjcmdeSvxGCaw5Jw8qcUUaX2Zl4'
ARQUIVO_DADOS = '../aniversarios.json'
ADMIN_ID = 6055192479  # Você vai mudar isso depois de descobrir seu ID

# --- COMANDOS DO BOT ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ESTA LINHA ABAIXO VAI MOSTRAR SEU ID NO TERMINAL DO VS CODE
    print(f"\n✅ MENSAGEM RECEBIDA! O SEU ID REAL É: {update.effective_user.id}\n")
    
    await update.message.reply_text(
        "🎂 *Assistente de Aniversários Ativado!*\n\n"
        "Comandos:\n"
        "• `/salvar Nome DD/MM` - Salva um novo aniversário\n"
        "• `/lista` - Vê seus aniversários salvos\n"
        "• `/deletar Nome` - Remove um nome da sua lista",
        parse_mode='Markdown'
    )

async def salvar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    frase_completa = " ".join(context.args)
    
    nome, data = extrair_nome_e_data(frase_completa)
    
    if not data:
        await update.message.reply_text("❌ Use o formato: /salvar Nome Sobrenome 15/05")
        return
    
    todos_os_dados = carregar_todos_os_dados(ARQUIVO_DADOS)
    if user_id not in todos_os_dados:
        todos_os_dados[user_id] = {}
    
    todos_os_dados[user_id][nome] = data
    salvar_no_arquivo(todos_os_dados, ARQUIVO_DADOS)
    
    await update.message.reply_text(f"✅ Salvei {nome} para o dia {data}!")

async def listar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_chat.id)
    todos_os_dados = carregar_todos_os_dados(ARQUIVO_DADOS)
    minha_lista = todos_os_dados.get(user_id, {})
    
    if not minha_lista:
        await update.message.reply_text("📭 Sua lista está vazia.")
        return
    
    texto = "\n".join([f"• {n}: {d}" for n, d in minha_lista.items()])
    await update.message.reply_text(f"📅 *Seus Aniversários:*\n\n{texto}", parse_mode='Markdown')

async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Acesso restrito ao administrador.")
        return
    
    dados = carregar_todos_os_dados(ARQUIVO_DADOS)
    resumo = f"📊 *Relatório Admin*\n\nUsuários: {len(dados)}\nAniversários: {sum(len(v) for v in dados.values())}"
    await update.message.reply_text(resumo, parse_mode='Markdown')

# --- EXECUÇÃO ---
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("salvar", salvar))
    app.add_handler(CommandHandler("lista", listar))
    app.add_handler(CommandHandler("admin", admin_dashboard))
    
    print("🚀 Bot iniciado! Vá ao Telegram e dê /start")
    app.run_polling()