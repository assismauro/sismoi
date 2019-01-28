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

totais_dados =\
'''    "id": {0},
    "municipio": "{1}",
	"impacto": {2}'''

colorMap = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']

indicadores_impacto_agua_otimista_evolucao_num_municipios = ['A','B','C','D','E']
indicadores_impacto_agua_pessimista_evolucao_num_municipios = ['A','F','G','H','I']

indicadores = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','1.1','1.2','1.3','1.4','2.1','2.2','2.3','3.1','3.2',
               '1.1.1','1.1.2','1.1.3','1.2.1','1.2.2','1.3.1','1.3.2','1.3.3','1.3.4','1.3.5','1.4.1','1.4.2','1.4.3','2.1.1','2.1.2','2.1.3','2.2.1','2.2.2',
               '2.2.3','2.3.1','2.3.2','3.1.1','3.1.2','3.1.3','3.1.4','3.2.1','3.2.2']

indicadoresRange = np.arange(0, 1 + 0.2, 0.2)

nomeFaixas = ['muito_baixo','baixo','medio','alto','muito_alto']

inputdir = r'E:\mauro.assis\sismoi\files''\\'

indicadoresFname = inputdir + 'indicadores.csv'
valoresFname = inputdir + r'valores.xlsx'
geojasontemplatefname = inputdir + 'vw_indicadores_ceara_simplified100.geojson'

outputdir = r'G:\SISMOI\sismoi_files'

evolucaodir = 'Evolucao'
municipiosdir = 'Municipios'
tendenciasdir = 'Tendencia'
mapadir = 'Mapa'
totaisdir = 'Totais'

def fixnomeindicador(indicador):
    return unidecode(indicador).replace(' ','_').replace('(','').replace(')','').replace('/','_')

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
    sourcedir=r'{0}\{1}'.format(outputdir, psourcedir)
    destdir=r'{0}\{1}'.format(outputdir, pdestdir)
    make_dir(r'{0}\{1}'.format(outputdir, pdestdir))
    for filename in glob.glob(os.path.join(sourcedir, '*.*')):
        shutil.copy(filename, destdir)

def saveJson(dirname,fname,content):
    make_dir(r'{0}\{1}'.format(outputdir, dirname))
    fname='{0}\{1}\{2}'.format(outputdir, dirname, fname)
    if fname.find('.') < 0: # não tem extensão...
        fname=fname+'.json'
    fname=unidecode(fname)
    print('Saving... {0}'.format(fname))
    with open(fname, 'w') as x_file:
        x_file.write(content)

def featureColor(value):
    '''
    >= 0   <= 0.2 => muito baixo
    >  0.2 <= 0.4 => baixo
    >  0.4 <= 0.6 => médio
    >  0.6 <= 0.8 => alto
    >  0.8        => muito alto
    '''
    return colorMap[0] if (value >= 0.0 and value <= 0.2) else  \
           colorMap[1] if (value > 0.2 and value <= 0.4) else   \
           colorMap[2] if (value > 0.4 and value <= 0.6) else   \
           colorMap[3] if (value > 0.6 and value <= 0.8) else   \
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
            s=''
            i=1
            for codigo in indicadores:
                nomeindicador = fixnomeindicador(definicoes.loc[definicoes['codigo'] == codigo]['nome fantasia'].values[0])
                saveJson(destdir, 'impacto_agua__seca__detalhe_por_municipio__contribuicao_colunas' + (
                    '_Seca' if tipo == 'S' else '_Chuva'),
                         impacto_agua__seca__detalhe_por_municipio__contribuicao_colunas)
                s = '{' + template_indice_de_seca_por_municipio_composicao.format(index + 1, row['J'], row['K'],
                                                                                  row['L'], 2005) + '}'
                #            saveJson(destdir,'indice_de_seca_por_municipio_composicao'+('_Seca' if tipo == 'S' else '_Chuva'),'[{0}]'.format(s))
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

def genTotais(definicoes,valores):
    print('Gerando Totais...')
    for tipo in ['S','C']:
        valfiltered = valores.loc[valores['Tipo'] == tipo]
        for codigo in indicadores:
            indicador = definicoes.loc[definicoes['codigo'] == codigo]
            nomeindicador = fixnomeindicador(indicador['nome fantasia'].values[0])
            for f in np.arange(0, 1, 0.2):
                rangefiltered = valfiltered[
                    (valfiltered[codigo] > (f if f > 0 else -1.0)) & (valfiltered[codigo] <= (f + 0.2))]
                if rangefiltered[codigo].count() == 0:
                    continue
                s='[\n'
                for index, row in rangefiltered.iterrows():
                    s+='  {\n'+totais_dados.format(index,row['Municipios'],row[codigo])+'\n  },\n'
                saveJson(totaisdir,'{0}_{1}_totais_{2}_colunas.json'.format(nomeindicador,'_Seca' if tipo == 'S' else '_Chuva',
                         nomeFaixas[int(f*10/2)]),
                         template_impacto_agua_evolucao_tabela_colunas)
                saveJson(totaisdir,'{0}_{1}_totais_{2}_dados.json'.format(nomeindicador,'_Seca' if tipo == 'S' else '_Chuva',
                         nomeFaixas[int(f*10/2)]),s[:-2]+'\n]')

def genMaps(definicoes,valores):
    print('Gerando mapas municipio...')
    with open(inputdir +'ceara.geojson') as f:
        map = json.load(f)
    for tipo in ['S','C']:
        valfiltered = valores.loc[valores['Tipo'] == tipo]
        for indicador in indicadores:
            for i in range(0,len(map['features'])):
                row = valfiltered.loc[valfiltered['geocod'] == map['features'][i]['properties']['geocod']]
                map['features'][i]['properties']['valor'] = float(row[indicador])
                map['features'][i]['properties']['style']['fillColor']=featureColor(float(row[indicador]))
            fname=fixnomeindicador(definicoes.loc[definicoes['codigo'] == indicador]['nome fantasia'].values[0]+('_Seca' if tipo == 'S' else '_Chuva')+'.geojson')
            saveJson(mapadir,fname,json.dumps(map))

    print("Gerando mapas mesorregiao...")
    with open(inputdir + 'ceara_mesorregiao.geojson') as f:
        map = json.load(f)
    for tipo in ['S','C']:
        valfiltered = (valores.loc[valores['Tipo'] == tipo]).groupby(['cd_geocme'], as_index=False).mean()
        for indicador in indicadores:
            for i in range(0,len(map['features'])):
                row = valfiltered.loc[valfiltered['cd_geocme'] == float(map['features'][i]['properties']['cd_geocme'])]
                map['features'][i]['properties']['valor'] = float(row[indicador])
                map['features'][i]['properties']['style']['fillColor']=featureColor(map['features'][i]['properties']['valor'])
            fname=fixnomeindicador(definicoes.loc[definicoes['codigo'] == indicador]['nome fantasia'].values[0]+('_Seca' if tipo == 'S' else '_Chuva')+'_mesoregiao.geojson')
            saveJson(mapadir,fname,json.dumps(map))

if __name__ == '__main__':
    definicoes = pd.read_csv(indicadoresFname,sep=';',encoding = "latin1", engine='python',header=0)
    valores = pd.read_excel(valoresFname,sep=',',encoding = "utf-8")
    genEvolucao(valores)
    genTendencia()
    genMaps(definicoes,valores)
    genMunicipios(definicoes,valores)
    genTotais(definicoes,valores)
    print('Done')