# Webservices do SISMOI - Documentação

## 1) Parâmetros da linha de comando

**-d** Ativa modo debug: nesse caso a URL acessada será replicada na tela quando houver requisição de um webservice.

**-host** Host do servidor web. Default: 127.0.0.1

**-p** Porta do serviço. Default: 5000

**-c** Tipo de cache: 0 - sem cache, 1 - cache descompactado, 2 - cache compactado, Default: 1

## 2) Ordenação dos valores:

Existem indicadores no SISMOI em que o valor mais alto é **bom** e outros em que o valor mais alto é **ruim**. Exemplo:

O indicador **Monitoramento e Prioridade Federal** pertence ao primeiro grupo. Isso significa que um valor como 0,87 para esse indicador é **bom** ou seja, quando for ser exibido na forma de uma cor, esta será verde.

Já o indicador **Exposição Biofísica** tem um comportamento oposto, ou seja, quanto maior o valor, pior o indicador. Nesse caso o mesmo valor deve ser exibido na cor vermelha.

Os serviços providos pelo **sismoyWS.py** levam isso em consideração, ou seja: quando é indicada uma cor pra um determinado valor, as cores sindicadas pela propriedade **valuecolor** respeitam essa regra.

Da mesma forma, quando necessário, caso do **getTotal**, os valores são ordenados em ordem decrescente de acordo com esse parâmetro, ou seja: os **melhores valores** estarão sempre em primeiro lugar. 

## 3) Descrição dos webservices implementados

### a) getHierarchy

Retorna a lista de todos os indicadores do SISMOI, juntamente com as suas descrições, bem como a hierarquia existente entre eles.

#### Parâmetros:
Nenhum

#### Exemplo de chamada:

```
curl -i http://127.0.0.1:5000/sismoi/getHierarchy
```
#### Retorno: 

json contendo um registro para cada indicador. Os indicadores estão ordenados por nível (level) 
e por código (id) dentro do nível. Os níveis de valores menores são os mais acima na hierarquia.

#### Descição dos campos do json:

 - **complete_description:** descrição completa do indicador.
 - **equation:** equação de ponderação do valor do indicador (null, por enquanto).
 - **id:** id do indicador.
 - **indicator_id_master:** id do indicador pai (indicador do qual este estará pendente na hierarquia).
 - **level:** nível do indicador.
 - **name:** nome do indicador.
 - **shorname:** sigla do indicador, a ser usado na equação de ponderação (null por enquanto).
 - **simple_description:** descrição simples do indicador.
 - **title:** título do indicador.
 - **years:** lista de anos em que o indicador ocorre, separados por vírgula.
 - **pessimist:** se igual a 0, o indicador é "bom" quando o valor é alto, se igual a 1, quanto maior o valor do indicador pior é.

#### Exemplo de retorno (três registros):

```json
[
  {
    "id": 1,
    "name": "Água",
    "title": "Impactos em Água",
    "shortname": null,
    "simple_description": "Consequências esperadas e resultantes das mudanças climáticas em sistemas naturais e humanos relacionados à segurança hídrica",
    "complete_description": "Este índice diz respeito aos efeitos sobre vidas, meios de subsistência, saúde, ecossistemas, economias, sociedades, culturas, serviços e infraestrutura devido a alterações climáticas ou eventos climáticos que se dão dentro de períodos específicos de tempo, vulnerabilidade e de exposição da sociedade ou sistema (IPCC, 2015), relacionados à segurança hídrica.<br><br>Referência:<br> INTERGOVERNMENTAL PANEL ON CLIMATE CHANGE - IPCC. Climate Change 2014: Synthesis Report. Working Groups I, II and III to the Fifth Assessment Report of the Intergovernmental Panel on Climate Change [Core Writing Team, R.K. Pachauri and L.A. Meyer (eds.)]. IPCC, Geneva, Switzerland, 151 pp.",
    "equation": null,
    "years": "2015",
    "level": 1,
    "pessimist": null,
    "indicator_id_master": null
  },
  {
    "id": 2,
    "name": "Seca",
    "title": "Índice de Impacto para a Seca",
    "shortname": null,
    "simple_description": "Impacto das mudanças climáticas em sistemas naturais e humanos, considerando a perturbação climática de seca",
    "complete_description": "Impacto das mudanças climáticas em sistemas naturais e humanos, resultante da interação entre os eventos climáticos relacionados à seca, vulnerabilidade e de exposição da sociedade ou sistema.<br><br>Fonte:<br> Sistema Brasileiro de Monitoramento e Observação de Impactos da Mudança Climática - SISMOI",
    "equation": null,
    "years": "2015, 2030, 2050",
    "level": 2,
    "pessimist": 1,
    "indicator_id_master": 1
  },
  {
    "id": 3,
    "name": "Chuva",
    "title": "Índice de Impacto para a Chuva",
    "shortname": null,
    "simple_description": "Impacto das mudanças climáticas em sistemas naturais e humanos, considerando a perturbação climática de excesso de chuva",
    "complete_description": "Impacto das mudanças climáticas em sistemas naturais e humanos, resultante da interação entre os eventos climáticos relacionados ao excesso de chuva, vulnerabilidade e de exposição da sociedade ou sistema.<br><br>Fonte:<br> Sistema Brasileiro de Monitoramento e Observação de Impactos da Mudança Climática - SISMOI",
    "equation": null,
    "years": "2015, 2030, 2050",
    "level": 2,
    "pessimist": 1,
    "indicator_id_master": 1
  }
]
```

### b) getGeometry

Retorna a geometria de um determinado mapa.

#### Parâmetros:

 - **clipping:** recorte do mapa. Alternativas: "semiarido", "SE", "PE", "MG", "CE", "BA", "PI", "AL", "PB", "RN", "MA"
 - **resolution:** resolução do mapa. Alternativas: "microrregiao", "mesorregiao", "municipio", "estado"

#### Exemplo de chamada:

```
curl -i http://127.0.0.1:5000/sismoi/getGeometry/clipping=SE,resolution=microrregiao
```

#### Retorno: 

json contendo os dados. Há informações de projeção e uma propriedade chamada **features**, que contém propriedades para cada registro do mapa. 

#### Descição dos campos do json:

 - **id:** da feature.
 - **name:** nome da feature.

#### Exemplo de retorno (2 registros, resolucao "municipio". Foram retiradas coordenadas geográficas por razões de espaço):

```json
{
  "type": "FeatureCollection",
  "crs": {
    "type": "name",
    "properties": {
      "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
    }
  },
  "features": [
    {
      "type": "Feature",
      "properties": {
        "id": 21,
        "uf": "CE",
        "name": "Acaraú"
      },
      "geometry": {
        "type": "MultiPolygon",
        "coordinates": [
          [
            [
			[-40.331121,-2.805455],
           		[-40.216206,-2.8167],
              		[-40.188748,-2.812914],
              		[-40.147872,-2.839507],
              		[-40.124927,-2.823793],
              		[-40.086645,-2.831316],
              		[-40.076759,-2.840906],
              		[-40.331121,-2.805455]
            ]
          ]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "id": 3991,
        "uf": "CE",
        "name": "Potiretama"
      },
      "geometry": {
        "type": "MultiPolygon",
        "coordinates": [
          [
            [
		[
			[-40.331121, -2.805455],  
			[-40.233762, -2.871358], 
			[-40.273223, -2.869949], 
			[-40.273521, -2.879356], 
			[-40.282177, -2.878471], 
			[-40.324513, -2.860845], 
			[-40.36254, -2.865738], 
			[-40.372259, -2.810277], 
			[-40.331121, -2.805455]
		]
            ]
          ]
        ]
      }
    }
  ]
}

```

### c) getMapData

Retorna os dados associados aos polígonos.

#### Parâmetros:

 - **clipping:** recorte do mapa. Alternativas: "semiárido", "SE", "PE", "MG", "CE", "BA", "PI", "AL", "PB", "RN", "MA"
 - **resolution:** resolução do mapa. Alternativas: "microrregiao", "mesorregiao", "municipio", "estado"
 - **indicator_id:** id do indicador a ser exibido
 - **scenario_id:** cenário a ser selecionado, 1 (Otimista), 2 (Pessimista) ou null quando o indicador não tiver.
 - **year:** ano a ser filtrado

#### Exemplo de chamada:

```
curl -i http://127.0.0.1:5000/sismoi/getMapData/clipping=PE,resolution=municipio,indicator_id=2,scenario_id=null,year=2015
```

#### Retorno: 

json contendo registros pesquisados. 

#### Descição dos campos do json:

 - **id:** do valor.
 - **indicator_id:** id do indicador.
 - **scenario_id:** id do cenário ou null.
 - **year:** ano a ser filtrado.
 - **value:** valor do indicador.
 - **valuecolor:** cor a ser usada quando o indicador tiver que ser exibido como cor.

#### Exemplo de retorno (alguns registros de uma consulta):

```json
[   
  {
		"id": 265041,
		"indicator_id": 2,
		"scenario_id": null,
		"year": 2015,
		"value": 0.367,
		"valuecolor": "#fdae61"
	}, {
		"id": 265155,
		"indicator_id": 2,
		"scenario_id": null,
		"year": 2015,
		"value": 0.532,
		"valuecolor": "#ffffbf"
	}, {
		"id": 265269,
		"indicator_id": 2,
		"scenario_id": null,
		"year": 2015,
		"value": 0.372,
		"valuecolor": "#fdae61"
	 }
]
```

### d) getGeometryAndData

Retorna a geometria e os dados correspondentes num json cujo formato pode ser passado direto para o renderizador (OpenStreeMap).

#### Parâmetros:

 - **clipping:** recorte do mapa. Alternativas: "semiárido", "SE", "PE", "MG", "CE", "BA", "PI", "AL", "PB", "RN", "MA"
 - **resolution:** resolução do mapa. Alternativas: "microrregiao", "mesorregiao", "municipio", "estado"
 - **indicator_id:** id do indicador a ser exibido
 - **scenario_id:** cenário a ser selecionado, 1 (Otimista), 2 (Pessimista) ou null quando o indicador não tiver.
 - **year:** ano a ser filtrado
 
#### Exemplo de chamada:

```
curl -i http://127.0.0.1:5000/sismoi/getGeometryAndData/clipping=PE,resolution=municipio,indicator_id=2,scenario_id=null,year=2015
```

#### Retorno: 

json contendo registros pesquisados. 

#### Descição dos campos do json:

 - **id:** do valor.
 - **name:** nome do registro na resolução indicadas.
 - **value:** valor do indicador associado ao registro.
 - **style:** contém o "estilo" de renderização a ser entendido pelo OpenStreetMap, onde **color** é a cor da borda, **fillcolor** é a cor do interior do polígono (e varia de acordo com o valor de value) e **weight** é a espessura da linha (ver exemplo abaixo).
 
 #### Exemplo de retorno (Registro de uma consulta, com as coordenadas reduzidas):

```json
	"features": [{
			"type": "Feature",
			"properties": {
				"id": 21,
				"name": "Acara\u00fa",
				"value": 0.468,
				"style": {
					"color": "#d7d7d7",
					"fillcolor": "#ffffbf",
					"weight": 1
				}
			},
			"geometry": {
				"type": "MultiPolygon",
				"coordinates": [[
				[
					[-40.331121, -2.805455],  
					[-40.233762, -2.871358], 
					[-40.273223, -2.869949], 
					[-40.273521, -2.879356], 
					[-40.282177, -2.878471], 
					[-40.324513, -2.860845], 
					[-40.36254, -2.865738], 
					[-40.372259, -2.810277], 
					[-40.331121, -2.805455]]]
				]
			}
		},
```

### e) getTotal

Retorna informações hierárquicas sobre os indicadores que podem ser usadas em diferentes locais do SISMOI.

#### Parâmetros:

 - **clipping:** recorte do mapa. Alternativas: "semiárido", "SE", "PE", "MG", "CE", "BA", "PI", "AL", "PB", "RN", "MA"
 - **resolution:** resolução do mapa. Alternativas: "microrregiao", "mesorregiao", "municipio", "estado"
 - **indicator_id:** id do indicador a ser exibido
 - **scenario_id:** 1 (Otimista), 2 (Pessimista) ou null quando o indicador não tiver essa cenários.
 - **year:** ano a ser filtrado (***opcional:*** se não for fornecido serão retornados todos os dados de todos os anos).
 
#### Exemplo de chamada:

```
curl -i http://127.0.0.1:5000/sismoi/getTotal/clipping=RN,indicator_id=19,resolution=municipio,scenario_id=1
```

#### Retorno: 

json contendo registros pesquisados. 

#### Descição dos campos do json:

O json é hierárquico, ou seja, existe uma estrutura de árvore entre os registros:

 - **<ano>** o primeiro nível é o ano (ex: 2015, 2030, 2050).
   - **<classe de valor>** nome da classe de valor (verylow,low,mid,high,veryhigh).
     - **count:** número de registros nessa classe.
     - **valuecolor:** cor da classe de valor.
     - **data:** conjunto de dados daquele ano e naquela classe de valor: **id** resolução (município, microrregião, mesorregião ou estado), **name** (nome do objeto na resolução), **value** (valor do indicador na resolução).
 
 Sobre a ordenação dos dados, ver tópico **Sobre a ordenação dos valores** acima.
 
 #### Exemplo de retorno (Parte da hierarquia):

```json
{
	"2010": {
		"verylow": {
			"data": [],
			"count": 0,
			"valuecolor": "#1a9641"
		},
		"count": 0,
		"low": {
			"data": [],
			"count": 0,
			"valuecolor": "#a6d96a"
		},
		"mid": {
			"data": [],
			"count": 0,
			"valuecolor": "#ffffbf"
		},
		"high": {
			"data": [{
					"id:": 60,
					"name": "\u00c3\u0081Gua Nova",
					"value:": 0.751
				}, {
					"id:": 109,
					"name": "Alexandria",
					"value:": 0.751
				}, {
					"id:": 124,
					"name": "Almino Afonso",
					"value:": 0.751
				}, ...
```

### f) getInfo (funcionando com dados aleatórios, ainda não são dados reais!!!)

Os valores dos indicadores com nível menor que 6 são compostos por indicadores de níveis abaixo.
Esse serviço retorna a composição dos valores dos indicadores com base nos níveis seguintes

#### Parâmetros:

 - **clipping:** recorte do mapa. Alternativas: "semiárido", "SE", "PE", "MG", "CE", "BA", "PI", "AL", "PB", "RN", "MA"
 - **resolution:** resolução do mapa. Alternativas: "microrregiao", "mesorregiao", "municipio", "estado"
 - **indicator_id:** id do indicador a ser exibido
 - **resolution_id:** id do objeto a ser exibido, conforme a resolução (**county_id** para a resolução **município**, **microregion_id** para a resolução **microrregiao**, **macroregion_id** para a resolução **macrorregiao**  e **state** para a resolução **estado**).  
 
#### Exemplo de chamada:

```
curl -i http://127.0.0.1:5000/sismoi/getInfo/clipping=CE,resolution=mesorregiao,indicator_id=1,resolution_id=10
```

#### Retorno: 

json contendo registros pesquisados. 

#### Descição dos campos do json:

O json é hierárquico, ou seja, existe uma estrutura de árvore entre os registros:

 - **nextlevel** ou **lastlevel** indica se a estrutura contém somente o próximo nível de indicador ou se contém todos eles.
   - **id** é o id do indicador.
   - **title** título do indicador.
   - **value** fração do indicador que compõe o indicador pesquisado. A soma em cada nível é igual a 1.
   
 Sobre a ordenação dos dados, ver tópico **Sobre a ordenação dos valores** acima.
 
 #### Exemplo de retorno para o indicador 26, nível 5:
 
 ```{
	"nextlevel": [{
		"id": 31,
		"title": "Planos ou A\u00e7\u00f5es Emergenciais e/ou Estruturais para a Chuva",
		"complete_description": "Conjunto de planos, a\u00e7\u00f5es e prioridades governamentais emerg\u00eancias existentes que podem diminuir o n\u00edvel de impacto presente e futuro de mudan\u00e7as clim\u00e1ticas considerando uma situa\u00e7\u00e3o de excesso de chuva. Informa\u00e7\u00e3o resultante da composi\u00e7\u00e3o de indicadores de alternativas ao abastecimento de \u00e1gua, planos de conting\u00eancia para desastres ambientais, ades\u00e3o ao programa cidades resilientes e monitoramento e prioridade federal contra desastres naturais.<br><br>Fonte:<br>Sistema Brasileiro de Monitoramento e Observa\u00e7\u00e3o de Impactos da Mudan\u00e7a Clim\u00e1tica - SISMOI",
		"value": 0.45
	}, {
		"id": 32,
		"title": "Gest\u00e3o dos Recursos H\u00eddricos para a Chuva",
		"complete_description": "Capacidade de resposta (positiva) da popula\u00e7\u00e3o a uma situa\u00e7\u00e3o de excesso de chuva considerando o n\u00edvel de gest\u00e3o e de pol\u00edticas p\u00fablicas relacionadas \u00e0 manuten\u00e7\u00e3o dos recursos h\u00eddricos e qualidade de saneamento b\u00e1sico. Informa\u00e7\u00e3o composta por indicadores de gerenciamento de comit\u00eas de bacias hidrogr\u00e1ficas, planejamento municipal e articula\u00e7\u00e3o interinstitucional para gerir o saneamento b\u00e1sico e o n\u00edvel de implanta\u00e7\u00e3o da Agenda 21 local.<br><br>Fonte:<br>Sistema Brasileiro de Monitoramento e Observa\u00e7\u00e3o de Impactos da Mudan\u00e7a Clim\u00e1tica - SISMOI",
		"value": 0.34
	}, {
		"id": 33,
		"title": "Capacidade Socioecon\u00f4mica Familiar para a Chuva",
		"complete_description": "Capacidade da estrutura familiar de responder positivamente a eventuais situa\u00e7\u00f5es de excesso de chuva. Informa\u00e7\u00e3o resultante da composi\u00e7\u00e3o do \u00edndice de Theil e da renda per capita.<br><br>Fonte:<br>Sistema Brasileiro de Monitoramento e Observa\u00e7\u00e3o de Impactos da Mudan\u00e7a Clim\u00e1tica - SISMOI",
		"value": 0.21
	}],
	"lastlevel": [{
		"id": 54,
		"title": "Planejamento sobre Saneamento B\u00e1sico",
		"complete_description": "N\u00edvel de implenta\u00e7\u00e3o e articula\u00e7\u00e3o de planos levou em considera\u00e7\u00e3o os munic\u00edpios que possuem um plano municipal de saneamento b\u00e1sico nas suas diferentes a\u00e7\u00f5es e/ou aqueles possu\u00edam algum tipo de articula\u00e7\u00e3o de cons\u00f3rcio p\u00fablico. As informa\u00e7\u00f5es-base foram obtidas em Pesquisa de Informa\u00e7\u00f5es B\u00e1sicas Municipais (MUNIC), do Instituto Brasileiro de Geografia e Estat\u00edstica (IBGE) para os anos de 2015 e 2017, conforme disponibilidade de dados.<br><br>Fonte:<br>Sistema Brasileiro de Monitoramento e Observa\u00e7\u00e3o de Impactos da Mudan\u00e7a Clim\u00e1tica - SISMOI",
		"value": 0.19
	}, {
		"id": 53,
		"title": "Planos de Gerenciamento dos Recursos H\u00eddricos",
		"complete_description": "Indicador composto pela pondera\u00e7\u00e3o adotada para cada vari\u00e1vel componente: Legisla\u00e7\u00e3o, gest\u00e3o de bacias hidrogr\u00e1ficas, exist\u00eancia (0,52); Plano Municipal de Saneamento B\u00e1sico, elabora\u00e7\u00e3o, comit\u00ea da bacia hidrogr\u00e1fica (0,16); Estrutura, Comit\u00ea de Bacia Hidrogr\u00e1fica (0,16); Articula\u00e7\u00e3o Intermunicipal, forma, comit\u00ea de bacia hidrogr\u00e1fica (0,16). As informa\u00e7\u00f5es-base foram obtidas em Pesquisa de Informa\u00e7\u00f5es B\u00e1sicas Municipais (MUNIC), do Instituto Brasileiro de Geografia e Estat\u00edstica (IBGE) para o per\u00edodo entre 2008 e 2017, conforme disponibilidade de dados.<br><br>Fonte:<br>Sistema Brasileiro de Monitoramento e Observa\u00e7\u00e3o de Impactos da Mudan\u00e7a Clim\u00e1tica - SISMOI",
		"value": 0.14
	}, {
		"id": 56,
		"title": "\u00cdndice de Theil",
		"complete_description": "Reflete as desigualdades de renda encontradas dentro e entre os domic\u00edlios. O \u00cdndice de Theil foi obtido no Atlas do Desenvolvimento Humano no Brasil, disponibilizado pelo Programa das Na\u00e7\u00f5es Unidas para o Desenvolvimento (PNUD) para o ano de 2010.<br><br>Fonte:<br>Sistema Brasileiro de Monitoramento e Observa\u00e7\u00e3o de Impactos da Mudan\u00e7a Clim\u00e1tica - SISMOI",
		"value": 0.14
	}, {
		"id": 49,
		"title": "Alternativa ao Abastecimento de \u00c1gua",
		"complete_description": "Articula\u00e7\u00e3o p\u00fablica e seguran\u00e7a h\u00eddrica m\u00ednima da popula\u00e7\u00e3o. A composi\u00e7\u00e3o do indicador levou em considera\u00e7\u00e3o a pondera\u00e7\u00e3o atribu\u00edda a dois aspectos: articula\u00e7\u00e3o p\u00fablica e principal solu\u00e7\u00e3o alternativa de abastecimento de \u00e1gua. Aos munic\u00edpios que  tiveram algum apoio p\u00fablico para implementa\u00e7\u00e3o de alguma solu\u00e7\u00e3o alternativa, atribuiu-se valor 1,0 (um), caso contr\u00e1rio, 0,0 (zero). Quanto ao tipo de solu\u00e7\u00e3o alternativa ao abastecimento de \u00e1gua: Outra: 0,0, Corpos d\u0092\u00e1gua: 0,2, Chafariz, bica ou mina: 0,4, Caminh\u00e3o Pipa: 0,6, Po\u00e7o particular: 0,8. A informa\u00e7\u00e3o foi obtida em Distribui\u00e7\u00e3o de \u00c1gua, Principal Solu\u00e7\u00e3o Alternativa, disponibilizada em Pol\u00edtica Nacional de Saneamento B\u00e1sico (PNSB) pelo Instituto Brasileiro de Geografia e Estat\u00edstica (IBGE) para o ano de 2008.<br><br>Fonte:<br>Sistema Brasileiro de Monitoramento e Observa\u00e7\u00e3o de Impactos da Mudan\u00e7a Clim\u00e1tica - SISMOI",
		"value": 0.13
	}, {
		"id": 52,
		"title": "Monitoramento e Prioridade Federal",
		"complete_description": "Munic\u00edpios monitorados pelo Centro Nacional de Monitoramento e Alertas de Desastres Naturais (CEMADEN) e/ou CASA CIVIL com intuito de acompanhar as amea\u00e7as naturais em \u00e1reas de riscos em munic\u00edpios brasileiros suscet\u00edveis \u00e0 ocorr\u00eancia de desastres naturais objetivando reduzir o n\u00famero de v\u00edtimas fatais. O indicador foi composto pela lista de munic\u00edpios monitorados no ano de 2018, informa\u00e7\u00e3o disponibilizada pelo Centro Nacional de Monitoramento e Alertas de Desastres Naturais (CEMADEN).<br><br>Fonte:<br>Sistema Brasileiro de Monitoramento e Observa\u00e7\u00e3o de Impactos da Mudan\u00e7a Clim\u00e1tica - SISMOI",
		"value": 0.12
	}, {
		"id": 57,
		"title": "Pessoas Pobres",
		"complete_description": "Propor\u00e7\u00e3o dos indiv\u00edduos com renda domiciliar per capita igual ou inferior a R$ 140,00 mensais, em reais de agosto de 2010. A propor\u00e7\u00e3o foi obtida em Propor\u00e7\u00e3o de Pobres, no Atlas do Desenvolvimento Humano no Brasil, disponibilizado pelo Programa das Na\u00e7\u00f5es Unidas para o Desenvolvimento (PNUD) para o ano de 2010.",
		"value": 0.1
	}, {
		"id": 51,
		"title": "Cidades Resilientes",
		"complete_description": "Cidades ou \u00e1reas urbanas que seguem par\u00e2metros internacionalmente estabelecidos, relacionados principalmente \u00e0s mudan\u00e7as clim\u00e1ticas e ao risco; governos e popula\u00e7\u00e3o integrados aos problemas da cidade, etc. A pondera\u00e7\u00e3o foi atribu\u00edda segundo a ades\u00e3o (0,8) ou n\u00e3o (0,2) ao programa. A informa\u00e7\u00e3o foi obtida atrav\u00e9s da Secretaria Nacional de Prote\u00e7\u00e3o e Defesa Civil (SEDEC) para o per\u00edodo entre 2014 e 2016.<br><br>Fonte:<br>Sistema Brasileiro de Monitoramento e Observa\u00e7\u00e3o de Impactos da Mudan\u00e7a Clim\u00e1tica - SISMOI",
		"value": 0.08
	}, {
		"id": 55,
		"title": "Agenda 21 Local",
		"complete_description": "N\u00edvel de implenta\u00e7\u00e3o e articula\u00e7\u00e3o da Agenda 21 Local foi obtido atrav\u00e9s de informa\u00e7\u00f5es sobre: Agenda 21 Local - elabora\u00e7\u00e3o, Agenda 21 Local - est\u00e1gio atual, Agenda 21 Local - f\u00f3rum, reuni\u00e3o \u00faltimos 12 meses. As informa\u00e7\u00f5es foram obtidas em Pesquisa de Informa\u00e7\u00f5es B\u00e1sicas Municipais (MUNIC), do Instituto Brasileiro de Geografia e Estat\u00edstica (IBGE) para o ano de 2008.<br><br>Fonte:<br>Sistema Brasileiro de Monitoramento e Observa\u00e7\u00e3o de Impactos da Mudan\u00e7a Clim\u00e1tica - SISMOI",
		"value": 0.05
	}, {
		"id": 50,
		"title": "Planos de Conting\u00eancia para Desastres ambientais",
		"complete_description": "Pondera\u00e7\u00e3o atribu\u00edda para a exist\u00eancia (0,8) ou n\u00e3o (0,2) de planos de conting\u00eancia para desastres ambientais. A informa\u00e7\u00e3o foi obtida em Pesquisa de Informa\u00e7\u00f5es B\u00e1sicas Municipais (MUNIC), disponibilizada pelo Instituto Brasileiro de Geografia e Estat\u00edstica (IBGE) para o ano de 2010.<br><br>Fonte:<br>Sistema Brasileiro de Monitoramento e Observa\u00e7\u00e3o de Impactos da Mudan\u00e7a Clim\u00e1tica - SISMOI",
		"value": 0.04
	}]
}
```
