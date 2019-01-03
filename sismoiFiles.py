import os
import psycopg2 as pg
import json
import pandas as pd
import numpy as np
import errno
from unidecode import unidecode
import glob
import shutil

template_impacto_agua_evolucao_num_municipios_impacto =\
'''
{
    labels: ["Muito Baixo", "baixo", "medio", "alto", "Muito Alto"],
    datasets: [
      }
        label: "2015",
        fillColor: "rgba(220,220,220,0.2)",
        strokeColor: "rgba(220,220,220,1)",
        pointColor: "rgba(220,220,220,1)",
        pointStrokeColor: "#fff",
        pointHighlightFill: "#fff",
        pointHighlightStroke: "rgba(220,220,220,1)",
        data: %s
      },
      }
        label: "2020",
        fillColor: "rgba(151,187,205,0.2)",
        strokeColor: "rgba(151,187,205,1)",
        pointColor: "rgba(151,187,205,1)",
        pointStrokeColor: "#fff",
        pointHighlightFill: "#fff",
        pointHighlightStroke: "rgba(151,187,205,1)",
        data: %s
      },
      }
        label: "2030",
        fillColor: "rgba(151,187,205,0.2)",
        strokeColor: "rgba(151,187,205,1)",
        pointColor: "rgba(151,187,205,1)",
        pointStrokeColor: "#fff",
        pointHighlightFill: "#fff",
        pointHighlightStroke: "rgba(151,187,205,1)",
        data: %s
      },
      }
        label: "2040",
        fillColor: "rgba(151,187,205,0.2)",
        strokeColor: "rgba(151,187,205,1)",
        pointColor: "rgba(151,187,205,1)",
        pointStrokeColor: "#fff",
        pointHighlightFill: "#fff",
        pointHighlightStroke: "rgba(151,187,205,1)",
        data: %s
      },
      }
        label: "2050",
        fillColor: "rgba(151,187,205,0.2)",
        strokeColor: "rgba(151,187,205,1)",
        pointColor: "rgba(151,187,205,1)",
        pointStrokeColor: "#fff",
        pointHighlightFill: "#fff",
        pointHighlightStroke: "rgba(151,187,205,1)",
        data: %s
      }
    ]
}
'''

template_impacto_agua_evolucao_tabela_colunas=\
'''
{
  columns:[
    {title:"municipio", field:"name", sortable:true, width:200},
    {title:"2015", field:"2015", sortable:true, sorter:"number"},
	{title:"2020", field:"2020", sortable:true, sorter:"number"},
	{title:"2030", field:"2030", sortable:true, sorter:"number"},
	{title:"2040", field:"2040", sortable:true, sorter:"number"},
	{title:"2050", field:"2050", sortable:true, sorter:"number"}
  ]
}
'''

template_impacto_agua_evolucao_tabela_dados=\
'''
    {{
        "id": {0},
        "municipio": "{1}",
        "2015": "{2}",
	    "2020": "{3}",
	    "2030": "{4}",
	    "2040": "{5}",
	    "2050": "{6}"    }},
'''

template_indice_de_seca_por_municipio_composicao =\
'''
    "id": {0},
    "vulnerabilidade": "{1}",
	"exposicao": "{2}",
	"indice_seca": "{3}",
	"ano": {4}
'''

impacto_agua__seca__detalhe_por_municipio__contribuicao_colunas =\
'''
{
  columns:[
    {title:"contribuicao", field:"name", sortable:true, width:200},
    {title:"Progresso", field:"percentagem", sorter:"number", formatter:"progress"}
  ]
}
'''

impacto_agua__seca__detalhe_por_municipio__contribuicao_dados =\
'''"id": {0},
    "contribuicao": "{1}",
	"percentagem": {2}'''

totais_colunas =\
'''
{
  columns:[
    {title:"municipio", field:"name", sortable:true, width:200},
    {title:"Progresso", field:"impacto", sorter:"number", formatter:"progress"},
	{title:"Impacto", field:"impacto", sortable:true, sorter:"number"}
  ]
}
'''

colorMap = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']

indicadores_impacto_agua_otimista_evolucao_num_municipios = ['A','B','C','D','E']
indicadores_impacto_agua_pessimista_evolucao_num_municipios = ['A','F','G','H','I']

indicadores = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V']

indicadoresRange = np.arange(0, 1 + 0.2, 0.2)

nomeFaixas = ['muito_baixo','baixo','medio','alto','muito_alto']

indicadoresFname = r'D:\Atrium\Projects\SISMOI\DADOS\indicadores.csv'
valoresFname = r'D:\Atrium\Projects\SISMOI\DADOS\valores.xlsx'
geojasontemplatefname = 'vw_indicadores_ceara_simplified100.geojson'

rootdir = r'D:\Atrium\Projects\SISMOI\sismoi_files'

evolucaodir = 'Evolucao'
municipiosdir = 'Municipios'
tendenciasdir = 'Tendencia'
mapadir = 'Mapa'
totaisdir = 'Mapa'

def make_dir(path):
    if os.path.isdir(path):
        return
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

def copyFiles(psourcedir,pdestdir):
    sourcedir=r'{0}\{1}'.format(rootdir,psourcedir)
    destdir=r'{0}\{1}'.format(rootdir,pdestdir)
    make_dir(r'{0}\{1}'.format(rootdir,pdestdir))
    for filename in glob.glob(os.path.join(sourcedir, '*.*')):
        shutil.copy(filename, destdir)

def saveJson(dirname,fname,content):
    make_dir(r'{0}\{1}'.format(rootdir,dirname))
    fname='{0}\{1}\{2}'.format(rootdir,dirname,fname)
    if fname.find('.') < 0: # não tem extensão...
        fname=fname+'.json'
    fname=unidecode(fname)
    print('Saving... {0}'.format(fname))
    with open(fname, 'w') as x_file:
        x_file.write(content)

def featureColor(value):
    return colorMap[0] if (value >= 0.0 and value <= 0.2) else\
           colorMap[1] if (value > 0.2 and value <= 0.4) else\
           colorMap[2] if (value > 0.4 and value <= 0.6) else\
           colorMap[3] if (value > 0.6 and value <= 0.8) else\
           colorMap[4]

def genEvolucao(valores):
    print("Gerando Evolucao...")
    for tipo in ['S','C']:
        valfiltered = valores.loc[valores['Tipo'] == tipo]

        # água otimista
        replaces = []
        for indicador in indicadores_impacto_agua_otimista_evolucao_num_municipios:
            print('processando: {0} {1}'.format('indicadores_impacto_agua_otimista_evolucao_num_municipios',indicador))
            hist = valfiltered[indicador].groupby(pd.cut(valfiltered[indicador], indicadoresRange)).count()
            replaces.append(str(hist.values.tolist()))
        s = template_impacto_agua_evolucao_num_municipios_impacto % tuple(replaces)
        saveJson(evolucaodir,'impacto_agua_otimista_evolucao_num_municipios_impacto'+('_Seca' if tipo == 'S' else '_Chuva'),s)
        saveJson(evolucaodir,'impacto_agua_otimista_evolucao_tabela_colunas'+('_Seca' if tipo == 'S' else '_Chuva'),template_impacto_agua_evolucao_tabela_colunas)
        s=''
        for index, row in valfiltered.iterrows():
            s+=template_impacto_agua_evolucao_tabela_dados.format(index+1,row['Municipios'],row['A'],row['B'],row['C'],row['D'],row['E'])
        saveJson(evolucaodir,'impacto_agua_otimista_evolucao_tabela_dados'+('_Seca' if tipo == 'S' else '_Chuva'),'[{0}]'.format(s))

        # água pessimista
        replaces=[]
        for indicador in indicadores_impacto_agua_pessimista_evolucao_num_municipios:
            print('processando: {0} {1}'.format('indicadores_impacto_agua_pessimista_evolucao_num_municipios',indicador))
            hist = valfiltered[indicador].groupby(pd.cut(valfiltered[indicador], indicadoresRange)).count()
            replaces.append(str(hist.values.tolist()))
        s = template_impacto_agua_evolucao_num_municipios_impacto % tuple(replaces)
        saveJson(evolucaodir,'impacto_agua_pessimista_evolucao_num_municipios_impacto'+('_Seca' if tipo == 'S' else '_Chuva'),s)
        saveJson(evolucaodir,'impacto_agua_pessimista_evolucao_tabela_colunas'+('_Seca' if tipo == 'S' else '_Chuva'),template_impacto_agua_evolucao_tabela_colunas)
        s=''
        for index, row in valfiltered.iterrows():
            s+=template_impacto_agua_evolucao_tabela_dados.format(index+1,row['Municipios'],row['A'],row['F'],row['G'],row['H'],row['I'])
        saveJson(evolucaodir,'impacto_agua_pessimista_evolucao_tabela_dados'+('_Seca' if tipo == 'S' else '_Chuva'),'[{0}]'.format(s))

def genMunicipios(definicoes,valores):
    print("Gerando Municipios...")
    for tipo in ['S','C']:
        valfiltered = valores.loc[valores['Tipo'] == tipo]
        for index, row in valfiltered.iterrows():
            destdir=unidecode(r'{0}\{1}'.format(municipiosdir,row['Municipios'])).replace(' ','_')
            s = '{'+template_indice_de_seca_por_municipio_composicao.format(index + 1, row['J'], row['K'],row['L'], 2005)+'}'
            saveJson(destdir,'indice_de_seca_por_municipio_composicao'+('_Seca' if tipo == 'S' else '_Chuva'),'[{0}]'.format(s))
            saveJson(destdir,'impacto_agua__seca__detalhe_por_municipio__contribuicao_colunas'+(
                '_Seca' if tipo == 'S' else '_Chuva'),impacto_agua__seca__detalhe_por_municipio__contribuicao_colunas)
            s=''
            i=1
            for codigo in ['A','B','C','D','E','F','G','H','I']:
                nomeindicador = unidecode(definicoes.loc[definicoes['codigo'] == codigo]['nome fantasia'].values[0]).replace(' ','_').replace('(','').replace(')','')
                for column in valfiltered.columns:
                    if column.startswith('Cont'+codigo+'_'):
                        try:
                            nomecomponente = definicoes.loc[definicoes['codigo'] == column[6:]]['nome fantasia'].values[0].strip('_')
                            s += '{\r\n'+impacto_agua__seca__detalhe_por_municipio__contribuicao_dados.format(i,nomecomponente,row[column])+'\r\n},\r\n'
                            i+=1
                        except:
                            print("Erro em genMunicipio processando {0}, coluna {1}".format(nomeindicador,column))
                            raise
                s='['+s[:-3]+']'
                fname='{0}_{1}_detalhe_por_municipio__contribuicao_dados.json'.format(nomeindicador,('_Seca' if tipo == 'S' else '_Chuva'))
                saveJson(destdir,fname,s)

def genTendencia():
    print('Gerando Tendencia...')
    copyFiles(evolucaodir,tendenciasdir)

def getTotais(valores):
    print('Gerando Totais...')
    for tipo in ['S','C']:
        valfiltered = valores.loc[valores['Tipo'] == tipo]
        for faixa in nomeFaixas:
            saveJson(evolucaodir,'impacto_agua_otimista_evolucao_tabela_colunas'+('_Seca' if tipo == 'S' else '_Chuva'),template_impacto_agua_evolucao_tabela_colunas)
            for codigo in ['A','B','C','D','E','F','G','H','I']:
                indicador = definicoes.loc[definicoes['codigo'] == codigo]
                nomeindicador = unidecode(indicador['nome fantasia'].values[0]).replace(' ','_').replace('(','').replace(')','')
                for faixa in nomeFaixas:
                    saveJson(totaisdir,'{0}_{1}_totais_baixo_colunas.json'.format(nomeindicador,'_Seca' if tipo == 'S' else '_Chuva'))


def genMaps(definicoes,valores):
    print('Gerando mapas municipio...')
    with open('ceara3.geojson') as f:
        map = json.load(f)
    for tipo in ['S','C']:
        valfiltered = valores.loc[valores['Tipo'] == tipo]
        for indicador in indicadores:
            for i in range(0,len(map['features'])):
                row = valfiltered.loc[valfiltered['geocod'] == map['features'][i]['properties']['geocod']]
                map['features'][i]['properties']['valor'] = float(row[indicador])
                map['features'][i]['properties']['style']['fillColor']=featureColor(float(row[indicador]))
            fname=definicoes.loc[definicoes['codigo'] == indicador]['nome fantasia'].values[0].\
                      replace(' ','_').replace('(','').replace(')','')+('_Seca' if tipo == 'S' else '_Chuva')+'.geojson'
            saveJson(mapadir,fname,json.dumps(map))

    print("Gerando mapas mesorregiao...")
    with open('ceara_mesorregiao2.geojson') as f:
        map = json.load(f)
    for tipo in ['S','C']:
        valfiltered = (valores.loc[valores['Tipo'] == tipo]).groupby(['cd_geocme'], as_index=False).mean()
        for indicador in indicadores:
            for i in range(0,len(map['features'])):
                row = valfiltered.loc[valfiltered['cd_geocme'] == float(map['features'][i]['properties']['cd_geocme'])]
                map['features'][i]['properties']['valor'] = float(row[indicador])
                map['features'][i]['properties']['style']['fillColor']=featureColor(map['features'][i]['properties']['valor'])
            fname=definicoes.loc[definicoes['codigo'] == indicador]['nome fantasia'].values[0].\
                      replace(' ','_').replace('(','').replace(')','')+('_Seca' if tipo == 'S' else '_Chuva')+'_mesoregiao.geojson'
            saveJson(mapadir,fname,json.dumps(map))
    print()

if __name__ == '__main__':
    definicoes = pd.read_csv(indicadoresFname,sep=';',encoding = "latin1", engine='python',header=0)
    valores = pd.read_excel(valoresFname,sep=',',encoding = "utf-8")
    genEvolucao(valores)
    genTendencia()
    genMaps(definicoes,valores)
    genMunicipios(definicoes,valores)
    getTotais()
    print('Done')