import base64
import captcha as cap

from selenium import webdriver
from selenium.webdriver.common.by import By
from pprint import pprint
from PIL import Image


browser = webdriver.Chrome()
browser.get('https://srv01.tjpe.jus.br/consultaprocessualunificada/')

browser.find_element(By.LINK_TEXT, 'Parte').click()

cpf_cnpf_element = browser.find_element(By.ID, 'cpfCnpj',)
button_element = browser.find_element(By.CLASS_NAME, 'button-consultar')


resolve_captch = 1
cont = 0
while resolve_captch == 1:

    captcha_text_element = browser.find_element(By.ID, 'captcha')
    captcha_image_element = browser.find_element(By.CSS_SELECTOR, 'body > div > div.content-wrapper > ui-view > section.content.ng-scope > ng-include > div > div > div > div > form > div.form-group.ng-scope > div.top-alignment.captcha-wrapper > img.ng-isolate-scope')

    encoded = captcha_image_element.screenshot_as_base64
    data = base64.b64decode(encoded)

    captcha_name = 'captcha_' + str(cont) + '.png'

    with open(captcha_name, 'wb') as ImageFile:
        ImageFile.write(data)
        ImageFile.close()


    original = Image.open(captcha_name)
    original.save("final.tif")  # reading the image from the request
    captcha = Image.open("final.tif").convert("1")
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

    pprint(mais_frequentes)
    result = cap.resultado(mais_frequentes)
    print(result)

    cpf_cnpf_element.send_keys('sua_consulta')
    captcha_text_element.send_keys(result)
    button_element.click()

    text_result_element = browser.find_element(By.CSS_SELECTOR,
                                                 'body > div > div.content-wrapper > ui-view > section.content.ng-scope > ng-include > div > div.ng-scope.ng-isolate-scope.alert.alert-dismissible.alert-info > div > span > li')

    print(text_result_element.text)

    if cont == 10:
        resolve_captch = 0
    else:
        cont += 1









