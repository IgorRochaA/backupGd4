from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException ,StaleElementReferenceException
from datetime import datetime
import random
import csv
import time
import os

erros_encontrados = [] # lista para armazenar os erros encontrados

def arquivo_salvo(diretorios_de_backup, driver): # função para salvar os arquivos nas pastas correspondentes
    print("\n \n \n \n -------------------------------------\nIniciando o processo de salvamento dos arquivos...") # informa que o processo de salvamento começou
    todos_os_arquivos_salvos = diretorios_de_backup # lista com todos os caminhos das pastas
    
    if not todos_os_arquivos_salvos: # verifica se a lista está vazia
        print("Nenhuma pasta encontrada para processar.")
        return
    
    time.sleep(3) # espera 3 segundos para garantir que a página carregou

    for diretorio_destino in todos_os_arquivos_salvos: # percorre a lista de caminhos das pastas

        try:

            nome_da_pasta_inicial = os.path.basename(diretorio_destino) # pega o nome da pasta

            nome_da_pasta = nome_da_pasta_inicial.replace('_', ' ') # substitui os underscores por espaços

            time.sleep(3) # espera 3 segundos para garantir que a página carregou

            barra_de_busca = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"#topSearchInput"))
            ) # localiza a barra de busca
            
            barra_de_busca.send_keys(Keys.CONTROL + "a") # seleciona todo o texto na barra de busca
            barra_de_busca.send_keys(Keys.BACKSPACE) # apaga o texto na barra de busca
            
            barra_de_busca.send_keys(nome_da_pasta) # digita o nome da pasta na barra de busca
            barra_de_busca.send_keys(Keys.RETURN) # aperta enter para buscar
            print(f"Buscando pelo arquivo: {nome_da_pasta} ...") # mostra o nome do arquivo que está sendo procurado
            
            email_encontrado = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='option']"))
            )
            print("Email encontrado na busca.")
            download_realizado = False # flag para indicar se o download foi realizado
            for email_na_lista in email_encontrado:
                try: 
                    email_na_lista.click() # clica no email encontrado
                    time.sleep(1) # espera 1 segundo para garantir que o email carregou

                    seletor_conferencia_de_nome = "div[id^='UniqueMessageBody_'] > div > div > div > div > table > tbody > tr:nth-child(2) > td:nth-child(1)" # seletor para conferir o nome do arquivo no email

                    nome_do_arquivo = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, seletor_conferencia_de_nome))
                    ).text.strip() # pega o nome do arquivo no email

                    if nome_do_arquivo == nome_da_pasta: # compara o nome do arquivo com o nome da pasta

                        print(f"Arquivo '{nome_do_arquivo}' encontrado no email. Iniciando download...\n") # informa que o arquivo foi encontrado

                        seletor_botao_de_download = "div[id^='UniqueMessageBody_'] > div > div > div > div > table > tbody > tr:nth-child(2) > td:nth-child(2) > ul > li > a" # seletor para o botão de download
                        botao_de_download = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, seletor_botao_de_download))
                        ) # localiza o botão de download
                        url_extraida = botao_de_download.get_attribute("href") # extrai a URL do botão de download
                        print(f"Download do arquivo {nome_do_arquivo} iniciado.")
                        tempo_espera = 0 # variavel para contar o tempo de espera do download

                        prefs = {
                            "download.default_directory": os.path.abspath(diretorio_destino), # Diretório de download padrão
                            "download.prompt_for_download": False, # Desativar prompt para download
                            "directory_upgrade": True, # Permitir que o diretório de download seja atualizado
                            "safebrowsing.enabled": True, # Ativar proteção contra downloads perigosos
                            "plugins.always_open_pdf_externally": True, # Baixar PDFs diretamente
                            "download.directory_upgrade": True  # Atualizar o diretório de download, se necessário
                        }  # Configurações de preferências do Chrome
                        new_chrome_options = Options()  # Configurações do Chrome
                        new_chrome_options.add_argument("--headless")  # Executa o navegador em modo headless (sem interface gráfica)
                        new_chrome_options.add_argument("--start-maximized") # Inicia o navegador maximizado
                        new_chrome_options.add_experimental_option("prefs", prefs) # Adiciona as preferências ao Chrome
                        #new_chrome_options.add_argument("--incognito")  # Navegação anônima

                        new_driver = webdriver.Chrome(options=new_chrome_options)  # Inicializa um novo navegador
                        new_driver.get(url_extraida) # Acessa a URL de download

                        while tempo_espera < 30: # espera até 30 segundos para o download ser concluído
                            if os.path.exists(nome_do_arquivo): # verifica se o arquivo foi baixado
                                print(f"SUCESSO: O arquivo '{nome_do_arquivo}' foi salvo na pasta correta!") # informa que o arquivo foi salvo
                                break # sai do loop
                            else: # se o arquivo não foi baixado, espera 1 segundo e verifica novamente
                                print(f"Aguardando o download do arquivo '{nome_do_arquivo}'... ({tempo_espera + 1}/30 segundos)") # informa que o download está em andamento
                                time.sleep(1) # espera 1 segundo
                            tempo_espera += 1 # incrementa o tempo de espera
                        new_driver.quit() # fecha o navegador de download
                        download_realizado = True # marca que o download foi realizado
                        break # sai do loop de emails, pois o arquivo foi encontrado e o download iniciado
                    else:
                        print(f"ERRO: O arquivo '{nome_da_pasta}' não foi encontrado no email.")
                except Exception as e:
                    print(f"ERRO ao tentar clicar no email ou processar o download: {e}")
                    continue # tenta o próximo email na lista
            if not download_realizado: # se o download não foi realizado, informa que o arquivo não foi encontrado
                print(f"ERRO: O arquivo '{nome_da_pasta}' não foi encontrado no email.")

        except TimeoutException:
            print(f"ERRO: O arquivo '{nome_da_pasta}' não foi encontrado no email.")
            continue # pula para o próximo diretório
        except Exception as e:
            print(f"ERRO ao processar o arquivo '{nome_da_pasta}': {e}")
            continue # pula para o próximo diretório

    print("processo finalizado \n \n \n \n -------------------------------------") # informa que o processo de salvamento foi finalizado
    driver.quit() # fecha o navegador principal

def salvar_relatorio_de_erros(lista_de_erros): # função para salvar o relatório de erros em um arquivo CSV
    """
    Salva uma lista de dicionários de erro em um arquivo CSV.
    O arquivo é nomeado com a data e hora atuais para não ser sobrescrito.
    """

    nome_arquivo = f"relatorio_de_erros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv" # nome do arquivo com data e hora
    
    cabecalhos = ["timestamp", "obra", "status", "colaborador", "erro"] # cabeçalhos das colunas

    try:
        with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv: # abre o arquivo em modo de escrita
            
            writer = csv.DictWriter(arquivo_csv, fieldnames=cabecalhos) # cria o escritor de dicionários

            writer.writeheader()# escreve os cabeçalhos no arquivo
            
            writer.writerows(lista_de_erros) # escreve as linhas de erro no arquivo
            
        print(f"Relatório de erros salvo com sucesso em: '{nome_arquivo}'")

    except Exception as e:
        print(f"Ocorreu um erro ao tentar salvar o relatório de erros: {e}")

def lista_emp_status_colaborador(obra , status , nome): # função para criar a estrutura de pastas

    print(f"Obra: {obra} \nStatus: {status} \nNome: {nome} \n")  # mostra os dados que estão sendo processados
    obra_limpa = obra.replace(" ", "_").replace("/", "_") # limpa o caminho obra
    status_limpo = status.replace(" ", "_").replace("/", "_") # limpa o caminho status
    nome_limpo = nome.replace(" ", "_").replace("/", "_") # limpa o caminho nome

    caminho_pasta_texto = os.path.join(r"caminho_para_salvar_backup") # caminho da pasta de backup <-- alterar aqui

    caminho_pasta = os.path.join(caminho_pasta_texto, obra_limpa, status_limpo, nome_limpo) # caminhos a serem criados

    try:    
        os.makedirs(caminho_pasta, exist_ok=True) # cria a pasta se elas não existirem
        print(f"Pasta criada com sucesso: {caminho_pasta}")

    except Exception as e:
        print(f"Erro ao criar pasta: {e}") # retorna em caso de erro

        return

def percorrer_pastas(lista_de_pastas):
    lista_de_pastas = os.path.abspath(lista_de_pastas) # converte o caminho relativo em absoluto
    if not os.path.isdir(lista_de_pastas): # verifica se o caminho é uma pasta
        print(f"A pasta {lista_de_pastas} não existe.")
        return [] # retorna uma lista vazia se a pasta não existir
    
    pastas_folhas = [] # lista para armazenar os caminhos das pastas sem subpastas

    for dirpath, dirnames, filenames in os.walk(lista_de_pastas): # percorre a pasta e suas subpastas
        if not dirnames:  # Verifica se é uma pasta sem subpastas
            pastas_folhas.append(dirpath) # adiciona o caminho da pasta à lista

    return pastas_folhas # retorna a lista de pastas

def solicitar_backup(email, senha , status , obra): # função para solicitar o backup no gd4
    usuario = email # email do usuario
    senha = senha # senha do usuario

    obras_para_selecionar = obra # obra a ser selecionada
    status_colaboradores = status # status a serem selecionados
    #status_colaboradores = ["Todos"]

    chrome_options = Options()  # Configurações do Chrome
    chrome_options.add_argument("--start-maximized")  # Inicia o navegador maximizado
    chrome_options.add_argument("--incognito")  # Navegação anônima
    driver = webdriver.Chrome(options=chrome_options)  # Inicializa o navegador
    driver.get("https://plataforma.autodoc.com.br/login") # Acessa a página de login do gd4

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='email_input']"))
        ).send_keys(usuario) # Preenche o campo de email

        driver.find_element(By.XPATH, "//*[@id='single-spa-application:mf-login']/div[2]/div[1]/div/form/button").click() # clica no botão de login

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div[1]/div/form/div[1]/span[2]/input"))
        ).send_keys(senha) #preenche o campo de senha

        driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div[1]/div/form/button").click() #clica no botão de login

        # Navegar para "Meus Produtos"
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/main/section[1]/div[2]/a/div/div/div[3]/span"))
        ).click() # clica na opção " Colaboradores "

        seletor_status = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#filtros-historico > div:nth-child(6) > div:nth-child(1) > div > select"))
        ) # Seleciona o campo para selecionar o status
            
        selecionar = Select(seletor_status) # Cria o seletor para o status
        selecionar.select_by_value(status) # Seleciona o status
        print(f"Opção '{status}' selecionada.") # mostra em que status esta no loop

        selecao_empresa = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"#lista-obras-0 > div:nth-child({obra}) > div > label"))
        ) # Seleciona o campo para selecionar a obra
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selecao_empresa) # rola a página até o elemento

        selecao_empresa.click() # se não estiver selecionada, clica para selecionar

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#content-wrapper > div:nth-child(1) > div.row.margen-top-filtro > div > input.btn.btn-primary.btn-block"))
        ).click() # clica no botão "Exibir Colaboradores"

        # Loop principal para processar todas as páginas
        pagina_atual = 1 # contador de páginas
        while True: # loop infinito, será interrompido quando não houver mais páginas
            print(f"\nProcessando a página {pagina_atual} de colaboradores.") # informa em que página esta no loop
            
            try:
                
                WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#historico-lista > tbody > tr"))
                ) # espera até que todos os colaboradores estejam carregados

                num_colaboradores = len(driver.find_elements(By.CSS_SELECTOR, "#historico-lista > tbody > tr")) # conta o número de colaboradores na página
                
            except TimeoutException: # em caso de timeout, informa que não foi possível carregar a tabela
                print("A tabela de colaboradores demorou muito para carregar ou não há colaboradores nesta página.")
                break # sai do loop principal

            # Itera sobre cada colaborador na lista
            for colaborador_element in range(1, num_colaboradores + 1): # iterar de baixo para cima para evitar problemas de carregamento

                try:
                    # Clique no colaborador
                    time.sleep(random.uniform(0.5, 1.5)) # Pausa aleatória para simular comportamento humano
                    
                    colaborador_link = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f"#historico-lista > tbody > tr:nth-child({colaborador_element}) > td:nth-child(1)"))
                    ) # localiza o link do colaborador

                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", colaborador_link) # rola a página até o elemento

                    nome_do_colaborador = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f"#historico-lista > tbody > tr:nth-child({colaborador_element}) > td:nth-child(2)"))
                    ) # localiza o nome do colaborador
                    nome_do_colaborador_element = nome_do_colaborador.text.strip() # extrai o texto do nome do colaborador

                    lista_emp_status_colaborador(obra, status, nome_do_colaborador_element) # cria a pasta do colaborador

                    time.sleep(0.5) # Pequena pausa para a rolagem estabilizar
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", colaborador_link) # rola a página até o elemento novamente
                    colaborador_link.click() # clica no link do colaborador
                    print(f"Clicou no colaborador: {nome_do_colaborador_element}") 

                    # Aguarde a página de detalhes carregar
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Gerar Backup"))
                    ) 
                    
                    # Clique no botão "Gerar Backup"

                    print("Tentando clicar em 'Gerar Backup'...")
                    botao_backup = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Gerar Backup"))
                    ) # localiza o botão de gerar backup
                    
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_backup) # rola a página até o elemento
                    time.sleep(0.5) # Pequena pausa para a rolagem estabilizar 

                    driver.execute_script("arguments[0].click();", botao_backup) # clica no botão de gerar backup através do JavaScript

                    print(f"Gerando backup... numero {nome_do_colaborador_element}. Aguarde...") 

                    # Volte para a lista de colaboradores.
                    # A primeira chamada a driver.back() volta para a página anterior, onde o backup é solicitado
                    driver.back()# A segunda chamada a driver.back() volta para a lista principal de colaboradores
                    driver.back()

                    # Aguarde o carregamento da lista de colaboradores
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#historico-lista"))
                    ) # espera até que a tabela de colaboradores esteja carregada

                except (TimeoutException, StaleElementReferenceException) as e: # captura exceções específicas
                    print(f"!!!!! ERRO ao processar colaborador na posição {num_colaboradores}. Pulando para o próximo. !!!!!")
                    info_erro = {
                        "colaborador_element": nome_do_colaborador_element,
                        "obra": selecao_empresa.text,
                        "status": status
                    } # cria um dicionário com as informações do erro
                    erros_encontrados.append(info_erro) # adiciona o erro à lista de erros
                    print(f"      Detalhe do erro: {type(e).__name__}")
                    # Em caso de erro, tenta recarregar a página da lista para se recuperar
                    driver.back() # volta para a lista de colaboradores
                    continue # pula para o próximo colaborador

            # Lógica para navegar para a próxima página
            try:
                # O seletor do botão de próxima página geralmente contém 'next' ou uma seta.
                botao_proxima_pagina = driver.find_element(By.CSS_SELECTOR, "#content-wrapper > div:nth-child(2) > div > div > div > div.text-center > ul > li:nth-child(4) > a") # localiza o botão de próxima página

                if "disabled" in botao_proxima_pagina.find_element(By.XPATH, "./parent::li").get_attribute("class"): # verifica se o botão está desabilitado
                    print("Botão de próxima página desabilitado. Fim da lista.")
                    break
                else: # se o botão não estiver desabilitado, clica para ir para a próxima página
                    botao_proxima_pagina.click() # clica no botão de próxima página
                    print(f"Navegando para a página {pagina_atual + 1}...")
                    pagina_atual += 1 # incrementa o contador de páginas
            
            except NoSuchElementException: # se o botão de próxima página não for encontrado, sai do loop
                print("Nenhum botão de próxima página encontrado. Fim da automação.")
                break # sai do loop principal

    except Exception as e:# captura qualquer outra exceção
        print(f"Ocorreu um erro: {e}")
        driver.get(driver.current_url)#     recarrega a página atual em caso de erro
    finally:
        if erros_encontrados:# se houver erros, salva o relatório
            print(f"\nForam encontrados {len(erros_encontrados)} erros. Salvando relatório...") 
            salvar_relatorio_de_erros(erros_encontrados)# chama a função para salvar o relatório de erros
        else:
            print("\nExecução finalizada sem erros registrados.")
            
        print("Fechando o navegador.")
        driver.quit() # fecha o navegador

def clicar_email_nao_lido_outlook(email, senha): # função para clicar no email não lido do outlook
    # Defina suas credenciais
    email_usuario = email # recebe o email do usuario
    senha_email = senha # recebe a senha do email

    chrome_options = Options() # cria opções de configuração do Chrome
    chrome_options.add_argument("--start-maximized")  # Inicia o navegador maximizado
    chrome_options.add_argument("--incognito")  # Navegação anônima
    driver = webdriver.Chrome(options=chrome_options) # Inicializa o driver do Chrome
    driver.get(f"https://outlook.live.com/") # Acessa o Outlook
    print("navegador aberto")

    try:

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Entrar"))
        ).click() # clica no link 'Entrar'

        campo_email = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        webdriver.ActionChains(driver).move_to_element(campo_email).send_keys(email_usuario).perform() # clica no campo de email e coloca o email

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#idSIButton9"))
        ).click() # clica no botão 'Avançar'

        time.sleep(2)  # Espera para garantir que a transição de página ocorreu
        campo_senha = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#i0118"))
        )
        webdriver.ActionChains(driver).move_to_element(campo_senha).send_keys(senha_email).perform() # clica no campo de senha e coloca a senha

        botao_avancar = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#idSIButton9"))
        )
        webdriver.ActionChains(driver).move_to_element(botao_avancar).click().perform() # clica no botão 'Avançar'

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#KmsiCheckboxField"))
        ).click() # clica na checkbox 'Manter-me conectado'
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#idSIButton9"))
        ).click() # clica no botão 'Entrar'
        time.sleep(3) # espera 3 segundos para carregar a página

        lista_de_pastas = (r"caminho\para\as\pastas") # caminho da pasta onde estão as pastas de backup <-- alterar aqui

        time.sleep(3) # espera 3 segundos para garantir que a página carregou

        pastas = percorrer_pastas(lista_de_pastas) # chama a função para percorrer as pastas e retorna uma lista com os caminhos

        arquivo_salvo(pastas, driver) # chama a função para salvar os arquivos

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

def main (): # função principal
    # Defina suas credenciais
    email = "seu_email_aqui" # <-- alterar aqui
    senha = "sua_senha_aqui" # <-- alterar aqui

    # Chamar as funções
    solicitar_backup(email, senha, "ativo" , "2") # chama a função para solicitar o backup, parametros status e obra
    solicitar_backup(email, senha, "inativo" , "2") # chama a função para solicitar o backup, parametros status e obra
    
    clicar_email_nao_lido_outlook(email, senha) # chama a função para clicar no email não lido do outlook

if __name__ == "__main__":
    main() # chama a função main
