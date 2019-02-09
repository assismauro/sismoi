## SISMOI
### Documentação de uso dos webservices do SISMOI

Abaixo a descrição dos webservices do SISMOI, seus parâmetros e retornos.

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
			[-40.331121, -2.805455]]]
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

```
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

```
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
     - **data:** conjunto de dados daquele ano e naquela classe de valor.
	- **id:** id da resolução (município, microrregião, mesorregião).
	- **name:** nome do objeto na resolução.
	- **value:** valor do indicador na resolução.
 
 #### Exemplo de retorno (Parte da hierarquia):

```
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
