import sys
import os
import re
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- DEBUG ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Adiciona o diretório raiz ao path para as importações funcionarem
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import carregar_todos_os_dados, salvar_no_arquivo

# --- CONFIGURAÇÕES ---
TOKEN = '8372581903:AAFZgxbKBjcmdeSvxGCaw5Jw8qcUUaX2Zl4'
ADMIN_ID = 6055192479

logger.info(f"🔧 Bot iniciando com TOKEN: {TOKEN[:20]}...") 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"✅ /start recebido de {update.effective_user.id} - {update.effective_user.first_name}")
    print(f"\n✅ MENSAGEM RECEBIDA! O SEU ID REAL É: {update.effective_user.id}\n")
    
    mensagem = (
        "🎂 Assistente de Aniversarios Ativado!\n\n"
        "COMANDOS:\n"
        "/salvar Nome DD/MM - Salva um novo aniversario\n"
        "/lista - Mostra todos os aniversarios salvos\n"
        "/deletar Nome - Deleta um aniversario\n"
        "/salvar_lista - Salva multiplos aniversarios (separados por |)\n\n"
        "No dia do aniversario, te mandarei uma mensagem lembrando!"
    )
    
    await update.message.reply_text(mensagem)

async def salvar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_chat.id)
        frase = " ".join(context.args)
        logger.info(f"Tentando salvar: {frase} para user {user_id}")
        
        # Lógica inteligente de data que você aprovou
        padrao_data = r"(\d{1,2}/\d{1,2})"
        resultado = re.search(padrao_data, frase)
        
        if not resultado:
            logger.warning(f"Formato inválido de data: {frase}")
            await update.message.reply_text("❌ Use: /salvar Nome 15/05")
            return
        
        data = resultado.group(1)
        nome = frase.replace(data, "").strip()
        logger.info(f"Nome: {nome}, Data: {data}")
        
        todos_os_dados = carregar_todos_os_dados()
        if user_id not in todos_os_dados:
            todos_os_dados[user_id] = {}
        
        minha_lista = todos_os_dados[user_id]
        
        # Verifica se já existe um nome case-insensitive igual
        nome_existente = None
        for n in minha_lista.keys():
            if n.lower() == nome.lower():
                nome_existente = n
                break
        
        # Se existe, atualiza; se não, cria novo
        if nome_existente:
            minha_lista[nome_existente] = data
            logger.info(f"✅ Atualizado: {nome_existente} - {data}")
            await update.message.reply_text(f"✅ Atualizei {nome_existente} para {data}!")
        else:
            minha_lista[nome] = data
            logger.info(f"✅ Salvo: {nome} - {data}")
            await update.message.reply_text(f"✅ Salvei {nome} para {data}!")
        
        salvar_no_arquivo(todos_os_dados)
    except Exception as e:
        logger.error(f"❌ Erro em salvar: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Erro: {e}")

async def salvar_lista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Salva múltiplos aniversários de uma vez. Cada linha = um aniversário"""
    try:
        user_id = str(update.effective_chat.id)
        
        texto = None
        
        # Tenta pegar texto da mensagem que foi respondida
        if update.message.reply_to_message:
            texto = update.message.reply_to_message.text
            logger.info(f"Processando lista de reply_to_message")
        
        # Se não achou, tenta pelos args
        if not texto and context.args:
            texto = " ".join(context.args)
            logger.info(f"Processando lista de args")
        
        if not texto:
            await update.message.reply_text(
                "❌ Use assim:\n\n"
                "*Opção 1:* Responda a uma mensagem com a lista (uma por linha), depois envie `/salvar_lista`\n\n"
                "*Opção 2:* Envie `/salvar_lista` seguido da lista separada por `|`:\n"
                "`/salvar_lista 10/6 Isabelle | 12/7 Roseane | 21/7 Carol`",
                parse_mode='Markdown'
            )
            return
        
        # Divide por quebra de linha ou |
        linhas = texto.replace("|", "\n").split("\n")
        linhas = [l.strip() for l in linhas if l.strip()]
        
        if not linhas:
            await update.message.reply_text("❌ Nenhuma linha encontrada.")
            return
        
        todos_os_dados = carregar_todos_os_dados()
        if user_id not in todos_os_dados:
            todos_os_dados[user_id] = {}
        
        minha_lista = todos_os_dados[user_id]
        salvos = []
        erros = []
        
        for linha in linhas:
            padrao_data = r"(\d{1,2}/\d{1,2})"
            resultado = re.search(padrao_data, linha)
            
            if not resultado:
                erros.append(f"❌ {linha} - formato inválido")
                logger.warning(f"Formato inválido: {linha}")
                continue
            
            data = resultado.group(1)
            nome = linha.replace(data, "").strip()
            
            if not nome:
                erros.append(f"❌ {data} - sem nome")
                logger.warning(f"Sem nome para data {data}")
                continue
            
            # Verifica se já existe case-insensitive
            nome_existente = None
            for n in minha_lista.keys():
                if n.lower() == nome.lower():
                    nome_existente = n
                    break
            
            if nome_existente:
                minha_lista[nome_existente] = data
                salvos.append(f"✅ Atualizei '{nome_existente}' para {data}")
                logger.info(f"Atualizado: {nome_existente} - {data}")
            else:
                minha_lista[nome] = data
                salvos.append(f"✅ Salvei '{nome}' para {data}")
                logger.info(f"Salvo: {nome} - {data}")
        
        salvar_no_arquivo(todos_os_dados)
        
        mensagem = "".join([s + "\n" for s in salvos])
        if erros:
            mensagem += "\n" + "".join([e + "\n" for e in erros])
        
        await update.message.reply_text(mensagem if mensagem else "✅ Tudo pronto!")
        logger.info(f"Processadas {len(salvos)} linhas com sucesso, {len(erros)} erros")
        
    except Exception as e:
        logger.error(f"❌ Erro em salvar_lista: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Erro: {e}")

async def listar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_chat.id) # Garantia de ser string
        logger.info(f"Listando aniversários para user {user_id}")
        todos_os_dados = carregar_todos_os_dados()
        
        minha_lista = todos_os_dados.get(user_id, {})
        
        if not minha_lista:
            logger.info(f"Lista vazia para user {user_id}")
            await update.message.reply_text("📭 Sua lista está vazia.")
            return
        
        texto = "\n".join([f"• {n}: {d}" for n, d in minha_lista.items()])
        logger.info(f"Lista enviada: {len(minha_lista)} itens")
        await update.message.reply_text(f"📅 *Seus Aniversários:*\n\n{texto}", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"❌ Erro em listar: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Erro: {e}")

async def deletar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_chat.id)
        nome_busca = " ".join(context.args)
        logger.info(f"Tentando deletar: {nome_busca} para user {user_id}")
        
        if not nome_busca:
            await update.message.reply_text("❌ Use: /deletar Nome (ou parte dele)")
            return
        
        todos_os_dados = carregar_todos_os_dados()
        minha_lista = todos_os_dados.get(user_id, {})
        
        # Busca todas as correspondências
        nomes_encontrados = []
        for nome in minha_lista.keys():
            if nome_busca.lower() in nome.lower():
                nomes_encontrados.append(nome)
        
        if not nomes_encontrados:
            logger.warning(f"Nome contendo '{nome_busca}' não encontrado para user {user_id}")
            await update.message.reply_text(f"❌ Não encontrei nenhum nome contendo '{nome_busca}'.")
            return
        
        # Se encontrou exatamente 1, deleta direto
        if len(nomes_encontrados) == 1:
            nome_deletar = nomes_encontrados[0]
            data = minha_lista[nome_deletar]
            del minha_lista[nome_deletar]
            todos_os_dados[user_id] = minha_lista
            salvar_no_arquivo(todos_os_dados)
            logger.info(f"✅ Deletado: {nome_deletar}")
            await update.message.reply_text(f"🗑️ Deletei '{nome_deletar}' ({data}) da sua lista!")
            return
        
        # Se encontrou múltiplas, mostra opções
        opcoes = "\n".join([f"{i+1}. {nome} - {minha_lista[nome]}" for i, nome in enumerate(nomes_encontrados)])
        mensagem = f"❓ Encontrei {len(nomes_encontrados)} correspondências:\n\n{opcoes}\n\nSeja mais específico! Digite o nome completo com /deletar"
        logger.info(f"Múltiplas correspondências encontradas: {nomes_encontrados}")
        await update.message.reply_text(mensagem)
        
    except Exception as e:
        logger.error(f"❌ Erro em deletar: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Erro: {e}")

if __name__ == '__main__':
    try:
        logger.info("=" * 50)
        logger.info("🚀 Bot iniciando...")
        logger.info("=" * 50)
        
        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("salvar", salvar))
        app.add_handler(CommandHandler("salvar_lista", salvar_lista))
        app.add_handler(CommandHandler("lista", listar))
        app.add_handler(CommandHandler("deletar", deletar))
        
        logger.info("✅ Handlers adicionados")
        logger.info("=" * 50)
        print("🚀 Bot rodando na nova estrutura!")
        print("Esperando mensagens do Telegram...\n")
        
        app.run_polling()
    except Exception as e:
        logger.error(f"❌ ERRO FATAL: {e}", exc_info=True)
        print(f"\n❌ ERRO AO INICIAR BOT:\n{e}\n")