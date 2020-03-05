import argparse
import sisCommons
import pandas as pd

def ProcessCmdLine():
    parser = argparse.ArgumentParser(description="SISMOI WebServices.")
    parser.add_argument("-host", "--host", help="Host IP", type=str, default="127.0.0.1")
    parser.add_argument("-p", "--port", type=str, help="Port to be used", default=5000)
    parser.add_argument("-dbip", "--databaseip", help="Database IP", type=str, default="127.0.0.1")
    parser.add_argument("-db", "--dbname", type=str, help="Database name", default='sismoi')
    parser.add_argument("-pwd", "--password", type=str, help="Database password")
    parser.add_argument("-u", "--user", type=str, help="Database user name")
    return parser.parse_args()

def executeSQL(sql):
    try:
        conn = sisCommons.connectDB()
        return pd.read_sql(sql,conn)
    except Exception as e:
        raise e

def getValue(sql):
    rows=executeSQL(sql)
    return None if len(rows) == 0 else rows.iloc[0][0]

if __name__ == "__main__":
    i=0
    try:
        args = ProcessCmdLine()
        f=open('validateImpactaClima.csv','w')
        f.write('i;indicator_id;indicator_name;county_id;county_name;year;scenario_id;level;len_components;value;value_calc\n')
        indicators=executeSQL("""select a.id,a.title,c.county_name, a.level as level_ind,a.pessimist,scenario_id,year,county_id,level 
                                        from indicator a
                                 left join (select distinct indicator_id,year,scenario_id from value) v
                                        on a.id = v.indicator_id
                                 left join (select id as county_id, name as county_name from county) c
                                        on 1 = 1
                                 where a.id > 0 and year is not null and level <= 5  
                                 --and a.name = 'Vulnerabilidade'
                                 order by id,year,scenario_id,county_id""")
        current_indicator = ""
        for i,indicator in indicators.iterrows():
            if indicator.id != 114:
                continue
            strvalue = """select value
                            from value v
                            where indicator_id = {0}
                            and (v.year  = {1})
                            and {2}
                            and county_id = {3}
                        """.format(indicator.id,
                indicator.year,
                'scenario_id is null' if int(indicator.year) <= sisCommons.currentYear\
                                                else 'scenario_id = {0}'.format(
                    indicator.scenario_id),
                indicator.county_id)
            value = getValue(strvalue)
            strcomps = '''select distinct i.id,i.pessimist,
                      first_value(title) over (partition by i.id order by year desc range between unbounded preceding and unbounded following) as title,
                      first_value(year) over (partition by i.id order by year desc range between unbounded preceding and unbounded following) as year,
                      first_value(value) over (partition by i.id order by year desc range between unbounded preceding and unbounded following) as value 
                      from indicator_indicator ii   
                      inner join indicator i
                    on ii.indicator_id_detail = i.id
            inner join value v
                    on v.indicator_id = ii.indicator_id_detail
                  where ii.indicator_id_master = {0}          
                    and ((v.year <= {1}) or (v.year = {2}))
                    and {3}
                    and v.county_id = {4}'''.format(
                indicator.id,
                sisCommons.currentYear,
                indicator.year,
                'scenario_id is null' if int(indicator.year) <= sisCommons.currentYear\
                                      else '((scenario_id = {0}) or (scenario_id is null))'.format(indicator.scenario_id),
                    indicator.county_id
                )
            components=executeSQL(strcomps)
            if len(components) == 0:
                f.write('{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10}\n'.format(i, indicator.id, indicator.title,
                                                                    indicator.county_id, indicator.county_name,
                                                                    indicator.year, indicator.scenario_id,
                                                                    indicator.level_ind,
                                                                    len(components),
                                                                    value, -1000))
            else:
                if (indicator.title == 'Índice de Vulnerabilidade'):
                    vcalc=(1-float((components[components.title.str.contains('Adaptativa')].value)-
                                   float(components[components.title.str.contains('Sensibilidade')].value)))/2
                else:
                    vcalc=components.value.median()
                if abs(vcalc-value) > 0.001:
                    f.write('{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10}\n'.format(i,indicator.id,indicator.title,
                                                                       indicator.county_id,indicator.county_name,
                                                                       indicator.year,indicator.scenario_id,indicator.level_ind,
                                                                        len(components),
                                                                        value,vcalc))
    #                print('Indicador {0}, ano {1}, cenário {2}, cidade {3}, tem valor = {4} e mediana = {5}'.format(
    #                    indicator.id,indicator.year,indicator.scenario_id,indicator.county_id,value,vcalc))
            if current_indicator != indicator[1]:
                current_indicator = indicator[1]
                print(current_indicator)
            if (i % 100) == 0:
                print(i,indicator.county_name,indicator.title,len(components),value,vcalc)
                f.close()
                f=open('validateImpactaClima.csv','a')
        errors=getValue("""select count(1) from
                          (
                            select i.id,i.title,year,scenario_id,count(1) from indicator i
                            left join value v
                            on i.id = v.indicator_id
                            group by i.id,i.title,year,scenario_id
                            having count(1) <> 1 and count(1) <> (select count(1) from county)
                            order by 1,3,4
                          ) foo""")
        if errors > 0:
            f.write("Existem {0} indicadores que tem número de valores (tabela value) inconsistentes.".format(errors))
        f.close()
    except Exception as e:
        print(e)
        print(i, indicator.county_name)
        print(e)
        exit(-1)
