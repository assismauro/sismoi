### 1) Lista os valores da tabela values com seus relacionamentos

select c.name,c.state,i.id as idmaster,i.title as titlemaster,i.level as levelmaster,
       i2.id as iddetail,i2.title as titledetail,i2.level as leveldetail,
       v.scenario_id as scenario, year,v.value as indicator_value
from indicator_indicator ii
inner join indicator i
on ii.indicator_id_master = i.id
inner join indicator i2
on ii.indicator_id_detail = i2.id
left join value v
on ii.indicator_id_detail = v.indicator_id
left join county c
on v.county_id = c.id
--where cb.value is not null
order by i.id,i.level,i2.level,c.state,c.name,year,scenario_id

