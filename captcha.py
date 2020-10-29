import pytesseract

from collections import Counter
from string import ascii_letters, digits

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def obter_caracteres(imagem):
    caracteres = [list() for _ in range(5)]
    resultados = tentar_layouts(imagem)
    for posicao in range(5):
        for resultado in resultados:
            for indice, caractere in enumerate(caracteres):
                try:
                    caractere.append(resultado[indice])
                except IndexError:
                    pass
    return caracteres


def tentar_layouts(imagem):
    resultados = []
    layouts = [5, 6, 7, 10]
    for layout in layouts:
        resultados.append(reconhecer_caracteres(imagem, layout))
    return resultados


def reconhecer_caracteres(captcha, layout):

    caracteres_permitidos = digits + ascii_letters

    return pytesseract.image_to_string(
        captcha,
        config=
        f"""--psm {layout}
        -c tessedit_char_whitelist={caracteres_permitidos}""")


def remover_ruidos(imagem):
    limite = 1
    largura, altura = imagem.size
    pixels = imagem.load()

    # for linha in range(altura):
    #     for coluna in range(largura):
    #         if pixels[coluna, linha] > 128:
    #             continue
    #         escuros = 0
    #         for pixel in range(coluna, largura):
    #             if pixels[pixel, linha] < 128:
    #                 escuros += 1
    #             else:
    #                 break
    #         if escuros <= limite:
    #             for pixel in range(escuros):
    #                 pixels[coluna + pixel, linha] = 255
    #         coluna += escuros

    for coluna in range(largura):
        for linha in range(altura):
            if pixels[coluna, linha] > 128:
                continue
            escuros = 0
            for pixel in range(linha, altura):
                if pixels[coluna, pixel] < 128:
                    escuros += 1
                else:
                    break
            if escuros <= limite:
                for pixel in range(escuros):
                    pixels[coluna, linha + pixel] = 255
            linha += escuros

    return imagem

def reforcar_tracos(imagem):
    limite = 1
    largura, altura = imagem.size
    pixels = imagem.load()
    # for linha in range(altura):
    #     for coluna in range(largura):
    #         if pixels[coluna, linha] < 128:
    #             continue
    #         escuros = 0
    #         for pixel in range(coluna, largura):
    #             if pixels[pixel, linha] > 128:
    #                 escuros += 1
    #             else:
    #                 break
    #         if escuros <= limite + 1:  # Reforço maior.
    #             for pixel in range(escuros):
    #                 pixels[coluna + pixel, linha] = 0
    #         coluna += escuros

    for coluna in range(largura):
        for linha in range(altura):
            if pixels[coluna, linha] < 128:
                continue
            escuros = 0
            for pixel in range(linha, altura):
                if pixels[coluna, pixel] > 128:
                    escuros += 1
                else:
                    break
            if escuros <= limite + 1:
                for pixel in range(escuros):
                    pixels[coluna, linha + pixel] = 0
            linha += escuros

    return imagem


def contar_caracteres(listas):
    for lista in listas:
        mais_comuns = [list() for _ in range(len(listas))]
        for indice, _ in enumerate(mais_comuns):
            try:
                mais_comuns[indice] = Counter(listas[indice]).most_common()[0][0]
            except IndexError:
                pass
    return mais_comuns


def resultado(listas):
    result = ''
    c = [list() for _ in range(5)]
    for i, _ in enumerate(c):
        for lista in listas:
            c[i].append(lista[i])
    for i, _ in enumerate(c):
        for lista in listas:
            c[i] = Counter(c[i]).most_common()[0][0]
    for x in c:
        result += x
    return result
