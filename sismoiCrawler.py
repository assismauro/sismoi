import urllib
from bs4 import BeautifulSoup
import requests
import os

# url base que deve ser varrida procurando os arquivos
url = 'http://www.cprm.gov.br/publique/Gestao-Territorial/Geologia-de-Engenharia-e-Riscos-Geologicos/Setorizacao-de-Riscos-Geologicos-4138.html'

# diretório destino para salvamento dos arquivos, com a máscara onde entrará o nome do arquivo
destdirmask = r'D:\Atrium\Projects\SISMOI\DADOS\RiscosGeologicos\{0}'

# filtro dos links a serem investigados
filterstr = '=282'

# tipo de arquivo a ser buscado
extensao = '.zip'

conn = urllib.request.urlopen(url)
html = conn.read()

# obtém os links existentes na página
soup = BeautifulSoup(html, 'lxml')
links = soup.find_all('a')

# percorre os links
for tag in links:
    link = tag.get('href',None)
    if link is not None:
        if filterstr in link.lower():
            print('******************************* ',link)
            conn=urllib.request.urlopen(r'http://www.cprm.gov.br'+link)
            html=conn.read()

            # obtém os links existentes na página
            soup = BeautifulSoup(html, 'lxml')
            links = soup.find_all('a')

            # percorre os links
            for tag in links:
                link=tag.get('href',None)
                if link is not None:
                    if '.zip' in link.lower():
                        print('Baixando {0}'.format(link))
                        # tratamento de exceção porque erros estranhos podem acontecer aqui, melhor ignorar
                        # pro programa não parar
                        try:
                            fname=destdirmask.format(os.path.split(link)[1])
                            # aqui ele testa pra ver se o arquivo já foi baixado.
                            # Necessário se vc for reiniciar o programa sem querer baixar arquivos já baixados antes
                            if not os.path.isfile(fname):
                                zipF=requests.get(link, allow_redirects=True)
                                open(fname, 'wb').write(zipF.content)
                        except Exception:
                            pass