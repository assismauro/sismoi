## SISMOI
### Documentação de uso dos webservices do SISMOI

Abaixo a descrição dos webservices do SISMOI, seus parâmetros e retornos.

### a) getHierarchy

Retorna a lista de todos os indicadores do SISMOI, bem como a hierarquia existente entre eles.

#### Parâmetros:
Nenhum

#### Retorno: 

jason contendo um registro para cada indicador. 

#### Descição dos campos do json:

**complete description:** descrição completa do indicador.

**equation:** equação de ponderação do valor do indicador (null, por enquanto)

**id:** id do indicador.

**indicator_id_master:** id do indicador master (indicador do qual este estará pendente na hierarquia.

**level:** nível do indicador.

**name:** nome do indicador.

**shorname:** sigla do indicador, a ser usado na equação de ponderação (null por enquanto).

**simple_description:** descrição simples do indicador.

**title:** título do indicador.

**years:** lista de anosem que o indicador ocorre.

#### Exemplo de retorno:

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
