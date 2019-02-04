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

 - **clipping:** recorte do mapa. Alternativas: "semiárido", "SE", "PE", "MG", "CE", "BA", "PI", "AL", "PB", "RN", "MA"
 - **resolution:** resolução do mapa. Alternativas: "microrregiao", "mesorregiao", "municipio", "estado"

#### Exemplo de chamada:

```
curl -i http://127.0.0.1:5000/sismoi/getGeometry/clipping=SE,resolution=microrregiao
```

#### Retorno: 

jason contendo os dados. Há informações de projeção e uma propriedade chamada **features**, que contém propriedades para cada registro do mapa. 

#### Descição dos campos do json:

 - **id:** da feature.
 - **name:** nome da feature.

#### Exemplo de retorno (2 registros, resolucao "municipio". Foram retiradas algumas coordenadas geográficas por razões de espaço):

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
        "nome": "Acaraú",
      },
      "geometry": {
        "type": "MultiPolygon",
        "coordinates": [
          [
            [
              [
                -40.331121,
                -2.805455
              ],
              [
                -40.216206,
                -2.8167
              ],
              [
                -40.188748,
                -2.812914
              ],
              [
                -40.147872,
                -2.839507
              ],
              [
                -40.124927,
                -2.823793
              ],
              [
                -40.086645,
                -2.831316
              ]
            ]
          ]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "id": 3991,
        "nome": "Potiretama",
      },
      "geometry": {
        "type": "MultiPolygon",
        "coordinates": [
          [
            [
              [
                -38.203981,
                -5.634789
              ],
              [
                -38.168162,
                -5.645658
              ],
              [
                -38.171772,
                -5.651755
              ],
              [
                -38.14854,
                -5.659175
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
 - **scenario_id:** cenário a ser selecionado, "O", "P" ou null quando o indicador não tiver.
 - **year:** ano a ser filtrado

#### Exemplo de chamada:

```
curl -i http://127.0.0.1:5000/sismoi/getMapData/clipping=PE,resolution=municipio,indicator_id=2,scenario_id=null,year=2015
```

#### Retorno: 

jason contendo registros pesquisados. A estrutura varia de acordo com a resolução. Exemplo para 

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
