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

#### Exemplo de retorno (um registro):

```json
{
  "complete_description": "Padrão de consumo do recurso hídrico e sua manutenção quanto à rede de distribuição de água. Informação resultante da composição de indicadores de perdas de água e consumo de água per capita.<br><br>Fonte:<br>Sistema Brasileiro de Monitoramento e Observação de Impactos da Mudança Climática - SISMOI",
  "equation": null,
  "id": 52,
  "indicator_id_master": 31,
  "level": 5,
  "name": "Eficiência no Uso da Água",
  "shortname": null,
  "simple_description": "Padrão de consumo do recurso hídrico e sua manutenção quanto à rede de distribuição",
  "title": " Eficiência no Uso da Água para a Chuva",
  "years": "2015"
}
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

jason contendo os . Há informações de projeção e uma propriedade chamada **features**, que contém propriedades para cada registro do mapa. 

#### Descição dos campos do json:

 - **id:** da feature.
 - **nome:** nome da feature.
 - **microrregi:** pode existir ou não, dependendo da resolução.
 - **mesorregia:** pode existir ou não, dependendo da resolução.

#### Exemplo de retorno (foram retiradas coordenadas geográficas desse exemplo):

```json
[
   {
      "type":"Feature",
      "properties":{
         "id":21,
         "nome":"Acara\u00fa",
         "geocod":2300200,
         "uf":"CE",
         "microrregi":266,
         "mesorregia":60
      },
      "geometry":{
         "type":"MultiPolygon",
         "coordinates":[
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
                     -40.331121,
                     -2.805455
                  ]
               ]
            ]
         ]
      }
   }
]
```

### c) getMapData

Retorna os dados associados aos polígonos.

#### Parâmetros:

 - **clipping:** recorte do mapa. Alternativas: "semiárido", "SE", "PE", "MG", "CE", "BA", "PI", "AL", "PB", "RN", "MA"
 - **resolution:** resolução do mapa. Alternativas: "microrregiao", "mesorregiao", "municipio", "estado"
 - **indicator_id:** id do indicador a ser exibido
 - **scenario_id:** cenário a ser selecionado, "O", "P" ou null quando o indicador não tiver.
 - **county_id:** no caso de mapa, será sempre **all** 
 - **year:** ano a ser filtrado

#### Exemplo de chamada:

```
curl -i http://127.0.0.1:5000/sismoi/getMapData/clipping=PE,resolution=municipio,indicator_id=2,scenario_id=null,county_id=all,year=2015
```

#### Retorno: 

jason contendo registros pesquisados. A estrutura varia de acordo com a resolução. Exemplo para 

#### Descição dos campos do json:

 - **id:** do valor.
 - **indicator_id:** id do indicador a ser exibido
 - **scenario_id:** cenário a ser selecionado, O, P ou null quando o indicador não tiver.
 - **county_id:** no caso de mapa, será sempre **all** 
 - **year:** ano a ser filtrado
 - **value:** valor do indicador

#### Exemplo de retorno (alguns registros de uma consulta):

```
[  
   {  
      "id":106758,
      "indicator_id":2,
      "scenario_id":null,
      "county_id":36,
      "year":2015,
      "value":0.416
   },
   {  
      "id":106872,
      "indicator_id":2,
      "scenario_id":null,
      "county_id":40,
      "year":2015,
      "value":0.416
   },
   {  
      "id":106986,
      "indicator_id":2,
      "scenario_id":null,
      "county_id":42,
      "year":2015,
      "value":0.416
   },
   {  
      "id":107100,
      "indicator_id":2,
      "scenario_id":null,
      "county_id":65,
      "year":2015,
      "value":0.416
   },
   {  
      "id":107214,
      "indicator_id":2,
      "scenario_id":null,
      "county_id":91,
      "year":2015,
      "value":0.416
   },
   {  
      "id":107328,
      "indicator_id":2,
      "scenario_id":null,
      "county_id":139,
      "year":2015,
      "value":0.416
   }
]
```
