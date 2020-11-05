import base64
import json
import time
from scripts import captcha as cap, classes as c

from datetime import datetime
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

browser = webdriver.Chrome(chrome_options=chrome_options)
browser.get('https://srv01.tjpe.jus.br/consultaprocessualunificada/')

wait = WebDriverWait(browser, 10)

browser.find_element(By.LINK_TEXT, 'Parte').click()

cpf_cnpf_element = browser.find_element(By.ID, 'cpfCnpj', )
button_element = browser.find_element(By.CLASS_NAME, 'button-consultar')

resolve_captch = 1
cont = 0
while resolve_captch == 1:
    try:
        global button_refresh_element
        try:
            button_refresh_element = browser.find_element(By.CSS_SELECTOR,
                                                          'body > div > div.content-wrapper > ui-view > section.content.ng-scope > ng-include > div > div > div > div > form > div.form-group.ng-scope > div.top-alignment.captcha-wrapper > span.glyphicon.glyphicon-refresh.captcha')
        except:
            resolve_captch = 0
        button_refresh_element.click()
        time.sleep(3)

        captcha_text_element = browser.find_element(By.ID, 'captcha')
        captcha_image_element = browser.find_element(By.CSS_SELECTOR,
                                                     'body > div > div.content-wrapper > ui-view > section.content.ng-scope > ng-include > div > div > div > div > form > div.form-group.ng-scope > div.top-alignment.captcha-wrapper > img.ng-isolate-scope')

        encoded = captcha_image_element.screenshot_as_base64
        data = base64.b64decode(encoded)

        captcha_name = 'captcha_' + str(cont) + '.png'

        with open('./img/'+captcha_name, 'wb') as ImageFile:
            ImageFile.write(data)
            ImageFile.close()

        original = Image.open('./img/'+captcha_name)
        original.save('./img/final.tif')  # reading the image from the request
        captcha = Image.open('img/final.tif').convert("1")
        captcha.resize((1000, 500), Image.NEAREST)

        parciais = []
        mais_frequentes = []

        parciais.append(cap.obter_caracteres(captcha))
        parciais.append(cap.obter_caracteres(captcha))
        parciais.append(cap.obter_caracteres(captcha))

        for _ in range(3):
            parciais.append(cap.obter_caracteres(cap.remover_ruidos(captcha)))

        for _ in range(3):
            parciais.append(cap.obter_caracteres(cap.reforcar_tracos(captcha)))

        for i in parciais:
            mais_frequentes.append(cap.contar_caracteres(i))

        # pprint(mais_frequentes)
        result = cap.resultado(mais_frequentes)
        # print(result)

        cpf_cnpf_element.clear()
        entrada = '19391373062'
        cpf_cnpf_element.send_keys(entrada)
        captcha_text_element.send_keys(result)
        button_element.click()

        text_result_element = browser.find_element(By.CSS_SELECTOR,
                                                   'body > div > div.content-wrapper > ui-view > section.content.ng-scope > ng-include > div > div.ng-scope.ng-isolate-scope.alert.alert-dismissible.alert-info > div > span > li')

        if 'Valor indicado para a imagem de confirmação inválido ou expirado. Tente novamente.' == text_result_element.text:
            cont += 1
        else:
            resolve_captch = 0

    except:
        print("An exception occurred")

cpf_cnpf_element.clear()
entrada = '18384102449'
cpf_cnpf_element.send_keys(entrada)
button_element.click()

time.sleep(3)

grupos = []

temElementos = True

try:
    while temElementos:
        # Get element with tag class 'list-resultados'
        grupos_list_element = browser.find_element_by_class_name('list-group')
        # Get all the elements available with tag name 'p=div'
        grupos_element = grupos_list_element.find_elements(By.CLASS_NAME, 'list-resultados-item-link')

        original_window = browser.current_window_handle

        for grup in grupos_element:
            grup.click()

            processos = []

            wait.until(EC.number_of_windows_to_be(2))

            # Loop through until we find a new window handle
            for window_handle in browser.window_handles:
                if window_handle != original_window:
                    browser.switch_to.window(window_handle)
                    break

            processos_list_element = browser.find_element(By.CSS_SELECTOR, 'body > div.wrapper > div.content-wrapper > ui-view > section.content.ng-scope > ui-view > div')
            processos_element = processos_list_element.find_elements(By.TAG_NAME, 'ul')

            for proce in processos_element:
                h4_processo_element = proce.find_element(By.TAG_NAME, 'h4')
                h4_numero_processo_element = proce.find_element(By.CLASS_NAME, 'panel-body').find_element(By.TAG_NAME, 'h4')
                div_movimentacoes_element = proce.find_elements(By.CLASS_NAME, 'result-movimentacoes')

                list_movimentacoes = []

                for e in div_movimentacoes_element:
                    data_movimetacao_element = e.find_element(By.TAG_NAME, 'label')
                    complemento_movimentacao_element = e.find_element(By.CSS_SELECTOR, 'div > div')

                    movimento = c.Movimentacoes(data_movimetacao_element.text, complemento_movimentacao_element.text)
                    list_movimentacoes.append(movimento)

                processo = c.Processo(h4_processo_element.text, h4_numero_processo_element.text, list_movimentacoes)
                processos.append(processo)

            grupo = c.Grupo(processos)
            grupos.append(grupo)

            browser.close()
            browser.switch_to.window(original_window)

        # Returns true if element is enabled else returns false
        next = browser.find_element(By.CSS_SELECTOR,
                                    'body > div > div.content-wrapper > ui-view > section.content.ng-scope > ui-view > div > div > div > div.row.pagination-resultado > div.col-sm-7.pagination-resultado > ul > li.pagination-next.ng-scope.disabled')

        if next.is_enabled():
            next.click()
        else:
            temElementos = False
except:
    print("An exception occurred")

result = c.Result(grupos)
data_e_hora_atuais = datetime.now()
data_e_hora_em_texto = data_e_hora_atuais.strftime('%d_%m_%Y %H:%M')
data_e_hora_em_texto = data_e_hora_em_texto.replace(' ', '_').replace(':', '_')
file = entrada + '_' + data_e_hora_em_texto + '.json'

with open(file, 'w', encoding='utf8') as file:
    file.write(json.dumps(result, indent=4, ensure_ascii=False, cls=c.EmployeeEncoder))
    file.close()

browser.quit()
print("Fim script")
