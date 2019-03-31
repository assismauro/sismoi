from flask import Flask
from flask import request
import psycopg2
import psycopg2.extras
import argparse
import json
import numpy as np
import datetime
import zlib
from objsize import get_deep_size
import time
import sys
import os

resolutions = ['microrregiao','mesorregiao','municipio','estado']

classes = ['verylow','low','mid','high','veryhigh']

clippings = ['semiarido']

colorMap = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']

cache = {}
cacheType = -1

funcStats = {}

statsOff = False

currentYear = datetime.datetime.today().year

def startApp():
    app = Flask('sismoiWS')
    return app

app = startApp()

def ProcessCmdLine():
    parser = argparse.ArgumentParser(description="SISMOI WebServices.")
    parser.add_argument("-d", "--debug", help="Activate Flask debug mode", action='store_true')
    parser.add_argument("-l", "--log", help="Log calls to database", action='store_false')
    parser.add_argument("-so", "--statsoff", help="Deactivate stats monitoring", action='store_true')
    parser.add_argument("-host", "--host", help="Host IP", type=str, default="127.0.0.1")
    parser.add_argument("-p", "--port", type=str, help="Port to be used", default=5000)
    parser.add_argument("-dbip", "--databaseip", help="Database IP", type=str, default="127.0.0.1")
    parser.add_argument("-db", "--dbname", type=str, help="Database name", default='sismoi')
    parser.add_argument("-pwd", "--password", type=str, help="Database password")
    parser.add_argument("-u", "--user", type=str, help="Database user name")
    parser.add_argument("-c", "--cachetype", type=int, help="Cache type: 0 for no cache, 1 for plain, 2 for compressed",
                        default=1)
    return parser.parse_args()

def log(service,params,cache):
    if args.log:
        conn = psycopg2.connect("dbname='{0}' user='{1}' host='{2}' password='{3}'".format(args.dbname,args.user,args.databaseip,args.password))
        curr = conn.cursor()
        try:
            curr.execute(
                "insert into log(service,params,cache,date,script,iprequest) values ('{0}','{1}',{2},now(),'{3}','{4}')". \
                format(service, params, int(cache), os.path.basename(sys.argv[0]), request.environ['REMOTE_ADDR']))
            conn.commit()
        except:
            return

def updStats(label,fromCache=True):
    if not statsOff:
        key=label[:label.index('@')]
        elapsed = time.perf_counter() - funcStats[key]['start']
        if fromCache:
            funcStats[key]['elapsedwithcache'] += elapsed
            funcStats[key]['countwithcache'] += 1
        else:
            funcStats[key]['elapsedwocache'] += elapsed
            funcStats[key]['countwocache'] += 1

def toCache(label,value):
    updStats(label,False)
    if cacheType > 0:
        cache[label] = value if cacheType == 1 else zlib.compress(bytes(value,'utf-8'))

def fromCache(label):
    updStats(label,True)
    return cache[label] if cacheType == 1 else zlib.decompress(cache[label])

def inCache(label):
    global statsOff
    if not statsOff:
        key=label[:label.index('@')]
        if not(key in funcStats.keys()):
            funcStats[key]={'start' : time.perf_counter(),
                            'countwocache' : 0, 'elapsedwocache' : 0.0,
                            'countwithcache' : 0, 'elapsedwithcache' : 0.0}
        else:
            funcStats[key]['start']=time.perf_counter()
    return label in cache

@app.route("/sismoi/clearCache", methods=['GET'])
def clearCache():
    global funcStats
    global cache
    funcStats = {}
    cache = {}
    return 'Cache and stats cleared!\n'

def printDebug(line):
    if args.debug:
        print(line)

def executeSQL(sql,cursorFactory=None):
    try:
        conn = psycopg2.connect("dbname='{0}' user='{1}' host='{2}' password='{3}'".format(args.dbname,args.user,args.databaseip,args.password))

        if cursorFactory == None:
            curr = conn.cursor()
        else:
            curr = conn.cursor(cursor_factory = cursorFactory)
        curr.execute(sql)
        rows=curr.fetchall()
        conn.close()
        return rows
    except Exception as e:
        raise e

def getValue(sql):
    rows=executeSQL(sql)
    return None if rows == None else rows[0][0]

def getDictResultset(sql):
    resultset =executeSQL(sql, psycopg2.extras.DictCursor)
    return [dict(row) for row in resultset]

def getStates():
    return getDictResultset("select state from state")

def getIndicLevelYears():
    rows = executeSQL("""select i.id,level,i.pessimist,string_agg(year::character varying,',') as years 
                         from indicator i
                         left join
                         (select distinct indicator_id id,year from value) y
                           on i.id = y.id
                         group by i.id,level,i.pessimist
                         order by i.id""")
    return {id: {'level': level, 'pessimist': pessimist, 'years' : year.split(',') if year is not None else [0]} \
            for id,level,pessimist,year in rows}

def featureColor(value, pessimist):
    return (colorMap[0] if value >= 0.0 and value <= 0.2 else
            colorMap[1] if value >  0.2 and value <= 0.4 else
            colorMap[2] if value >  0.4 and value <= 0.6 else
            colorMap[3] if value >  0.6 and value <= 0.8 else
            colorMap[4]) if not pessimist else\
           (colorMap[4] if value >= 0.0 and value <= 0.2 else
            colorMap[3] if value >  0.2 and value <= 0.4 else
            colorMap[2] if value >  0.4 and value <= 0.6 else
            colorMap[1] if value >  0.6 and value <= 0.8 else
            colorMap[0])

def findElement(data,feature):
    for rec in data:
        if str(rec['id']) == str(feature['properties']['id']):
            return rec
    raise Exception("Element not found in findElement. keyfield: id Feature value: {0}".\
                    format(feature['properties']['id']))

def validateClippingResolution(sparams):
    errorMsg=''
    params = dict(token.split('=') for token in sparams.split(','))
    if not(params['resolution'] in resolutions):
        errorMsg='sismoiErr: Resolução errada: {0}.'.format(params['resolution'])
    '''
    if params['clipping'] not in clippings:
        errorMsg="sismoiErr: É necessário especificar clipping como 'semiarido' ou uma UF válida."
    '''
    return errorMsg,params

def validateParams(sparams):
    errorMsg,params=validateClippingResolution(sparams)
    if errorMsg != '':
        return errorMsg, params
    if not 'indicator_id' in params:
        errorMsg = "sismoiErr: É obrigatório especificar o indicador (indicator_id)."
    if str(params['indicator_id']) == '1':
        errorMsg = "sismoiErr: indicator_id deve ser maior que 1."
    elif not 'scenario_id' in params:
        errorMsg = "sismoiErr: É obrigatório especificar o cenário (scenario_id)."
    elif not params['scenario_id'] in ['1','2','null']:
        errorMsg='sismoiErr: Valor de scenario_id inválido, deve ser 1, 2 ou null.'
    elif ('year' in params):
        if not params['year'] in indicLevelYears[int(params['indicator_id'])]['years']:
            errorMsg='sismoiErr: Ano {0} não existe para o indicador {1}. Anos válidos: {2}'\
                .format(params['year'],
                        params['indicator_id'],
                        indicLevelYears[int(params['indicator_id'])]['years'])
        elif (params['scenario_id'] == 'null') and (int(params['year']) > currentYear):
            errorMsg='sismoiErr: É necessário especificar o cenário para ano maior que {0}.'.format(currentYear)
        elif (params['scenario_id'] != 'null') and (int(params['year']) <= currentYear):
            errorMsg='sismoiErr: Cenários não podem ser especificados para anos menores ou iguais a {0}.'.format(currentYear)
    elif params['scenario_id'] == 'null':
        errorMsg='sismoiErr: Se o ano não foi especificado, o cenário não pode ser nulo.'
    return errorMsg,params

def addFeatureColor(data):
    for rec in data:
        rec['valuecolor'] = featureColor(rec['value'],rec['pessimist'])
    return data

def toGroupedDict(data,pessimist):
    ret = {}
    for i in range(0,len(data)):
        if not(data[i]['year'] in ret.keys()):
            ret[data[i]['year']] = {}
            for _class,colorFake in zip(classes,np.arange(0.1,1.0,0.2)):
                ret[data[i]['year']].update({_class: {'data': [], 'count': 0,
                                                      'valuecolor': featureColor(colorFake,pessimist)},'count': 0})

        ret[data[i]['year']][data[i]['class']]['data'].append({'id':data[i]['id'],'name':data[i]['name'], 'value':data[i]['value']}
                                                              if 'id' in data[i] else
                                                              {'state':data[i]['state'],'value':data[i]['value']})
        ret[data[i]['year']][data[i]['class']]['count'] += 1
        ret[data[i]['year']]['count'] += 1
    return ret

def getIndicatorByState(params):
    data=getDictResultset('''select s.id, s.state, s.name, s.state, v.indicator_id, i.pessimist, v.scenario_id, year, round(avg(v.value)::numeric,2)::float as value
                               from value v
                              inner join indicator i
                                 on v.indicator_id = i.id
                              inner join county c
                                 on v.county_id = c.id
                              inner join state s
                                 on c.state = s.state                                    
                              where indicator_id = {0}
                                and scenario_id {1}
                                {2}
                                and year = {3}
                            group by s.id, s.state, s.name, v.indicator_id, i.pessimist, v.scenario_id,year
                             order by s.state, v.indicator_id, v.scenario_id,year
                          '''.format(params['indicator_id'],
                                     ' = ' +params['scenario_id'] if params['scenario_id'] != 'null' else 'is null',
                                     "and c.state = '{0}'".format(params['clipping']) if params['clipping'] != 'semiarido' else '',
                                     params['year'])
                          )
    return addFeatureColor(data)

def getIndicatorByMesoregion(params):
    data=getDictResultset('''select c.mesoregion_id as id, m.name, indicator_id, pessimist, v.scenario_id, year, round(avg(v.value)::numeric,2)::float as value
                               from value v
                              inner join indicator i
                                 on v.indicator_id = i.id
                              inner join county c
                                 on v.county_id = c.id 
                              inner join mesoregion m
                                 on c.mesoregion_id = m.id
                              where indicator_id = {0}
                                and scenario_id {1}
                                {2}
                                and year = {3}
                            group by  c.mesoregion_id, m.name, v.indicator_id, i.pessimist, v.year, v.scenario_id
                            order by                   m.name, v.year, v.scenario_id
                          '''.format(params['indicator_id'],
                                     ' = ' +params['scenario_id'] if params['scenario_id'] != 'null' else 'is null',
                                     "and c.state = '{0}'".format(params['clipping']) if params['clipping'] != 'semiarido' else '',
                                     params['year'])
                          )
    return addFeatureColor(data)

def getIndicatorByMicroregion(params):
    data=getDictResultset('''select c.microregion_id as id, m.name, indicator_id, i.pessimist, v.scenario_id,year, round(avg(v.value)::numeric,2)::float as value
                              from value v
                             inner join county c
                                on v.county_id = c.id 
                             inner join indicator i
                             on v.indicator_id = i.id
                             inner join microregion m
                                on c.microregion_id = m.id
                             where indicator_id = {0}
                               and scenario_id {1}
                               {2}
                               and year = {3}
                            group by  c.microregion_id, m.name, v.indicator_id, i.pessimist, v.year, v.scenario_id
                             order by                   m.name, v.year, v.scenario_id
                          '''.format(params['indicator_id'],
                                     ' = ' +params['scenario_id'] if params['scenario_id'] != 'null' else 'is null',
                                     "and c.state = '{0}'".format(params['clipping']) if params['clipping'] != 'semiarido' else '',
                                     params['year'])
                          )
    return addFeatureColor(data)

def getIndicatorByCounty(params):
    data=getDictResultset('''select v.county_id as id, c.name, v.indicator_id, v.year, v.scenario_id, i.pessimist, round(v.value::numeric,2)::float as value from value v 
                             inner join county c
                             on v.county_id = c.id
                             inner join indicator i
                             on v.indicator_id = i.id
                             where v.indicator_id = {0}
                               and v.scenario_id {1} 
                               {2}
                               and year = {3}
                             order by v.county_id, v.year, v.scenario_id
                          '''.format(params['indicator_id'],
                                     ' = ' +params['scenario_id'] if params['scenario_id'] != 'null' else 'is null',
                                     "and c.state = '{0}'".format(params['clipping']) if params['clipping'] != 'semiarido' else '',
                                     params['year'])
                          )
    return addFeatureColor(data)

def getTotalByState(params):
    rawdata=getDictResultset('''select s.id, s.state, s.name, year, 
                             case
                                when round(avg(v.value)::numeric,2) between 0   and 0.2 then 'verylow'
                                when round(avg(v.value)::numeric,2) between 0.2 and 0.4 then 'low'
                                when round(avg(v.value)::numeric,2) between 0.4 and 0.6 then 'mid'
                                when round(avg(v.value)::numeric,2) between 0.6 and 0.8 then 'high'
                                when round(avg(v.value)::numeric,2) > 0.8               then 'veryhigh'
                             end as class, round(avg(value)::numeric,2)::float as value
                                from 
                                value v
                                inner join county c
                                on v.county_id = c.id
                                inner join state s
                                on c.state = s.state
                                inner join indicator i
                                on v.indicator_id = i.id
                                inner join mesoregion m
                                on c.mesoregion_id = m.id
                                where indicator_id = {0}
                                {1}
                                {2} 
                                {3}                
                             group by s.id, s.state, s.name, year, i.pessimist
                                order by year {4}, s.state
                          '''.format(params['indicator_id'],
                             (' and (scenario_id = {0} or scenario_id is null)'.format(params['scenario_id'])) if params[ 'scenario_id'] != 'null' else '',
                              "and c.state = '{0}'".format(params['clipping']) if params['clipping'] != 'semiarido' else '',
                              'and v.year = {0}'.format(params['year']) if 'year' in params else '',
                              ('desc' if indicLevelYears[int(params['indicator_id'])]['level'] == 0 else '')
                             )
                          )
    data=toGroupedDict(rawdata,indicLevelYears[int(params['indicator_id'])]['level'])
    return data

def getTotalByMesoregion(params):
    rawdata=getDictResultset('''select c.mesoregion_id as id, m.name, year,
                             case
                                when round(avg(v.value)::numeric,2) between 0   and 0.2 then 'verylow'
                                when round(avg(v.value)::numeric,2) between 0.2 and 0.4 then 'low'
                                when round(avg(v.value)::numeric,2) between 0.4 and 0.6 then 'mid'
                                when round(avg(v.value)::numeric,2) between 0.6 and 0.8 then 'high'
                                when round(avg(v.value)::numeric,2) > 0.8               then 'veryhigh'
                             end as class, round(avg(value)::numeric,2)::float as value
                                from value v
                                inner join county c
                                on v.county_id = c.id
                                inner join indicator i
                                on v.indicator_id = i.id
                                inner join mesoregion m
                                on c.mesoregion_id = m.id
                                where indicator_id = {0}
                                {1}
                                {2}
                                {3}
                             group by year, mesoregion_id, m.name
                                order by year, value {4}, name
                          '''.format(params['indicator_id'],
                             (' and (scenario_id = {0} or scenario_id is null)'.format(params['scenario_id'])) if params[ 'scenario_id'] != 'null' else '',
                              "and c.state = '{0}'".format(params['clipping']) if params['clipping'] != 'semiarido' else '',
                              'and v.year = {0}'.format(params['year']) if 'year' in params else '',
                              ('desc' if indicLevelYears[int(params['indicator_id'])]['level'] == 0 else '')
                             )
                          )
    data=toGroupedDict(rawdata,indicLevelYears[int(params['indicator_id'])]['level'])
    return data

def getTotalByMicroregion(params):
    rawdata=getDictResultset('''select c.microregion_id as id, m.name, year, 
                             case
                                when round(avg(v.value)::numeric,2) between 0   and 0.2 then 'verylow'
                                when round(avg(v.value)::numeric,2) between 0.2 and 0.4 then 'low'
                                when round(avg(v.value)::numeric,2) between 0.4 and 0.6 then 'mid'
                                when round(avg(v.value)::numeric,2) between 0.6 and 0.8 then 'high'
                                when round(avg(v.value)::numeric,2) > 0.8               then 'veryhigh'
                             end as class, round(avg(value)::numeric,2)::float as value
                                from value v
                                inner join county c
                                on v.county_id = c.id
                                inner join indicator i
                                on v.indicator_id = i.id
                                inner join microregion m
                                on c.microregion_id = m.id
                                where indicator_id = {0}
                                {1}
                                {2}
                                {3}
                             group by year, c.microregion_id, m.name
                                order by year, value {4}, name
                          '''.format(params['indicator_id'],
                             (' and (scenario_id = {0} or scenario_id is null)'.format(params['scenario_id'])) if params[ 'scenario_id'] != 'null' else '',
                              "and c.state = '{0}'".format(params['clipping']) if params['clipping'] != 'semiarido' else '',
                              'and v.year = {0}'.format(params['year']) if 'year' in params else '',
                              ('desc' if indicLevelYears[int(params['indicator_id'])]['level'] == 0 else '')
                             )
                          )
    data=toGroupedDict(rawdata,indicLevelYears[int(params['indicator_id'])]['level'])
    return data

def getTotalByCounty(params):
    rawdata=getDictResultset('''select c.id, c.name, year, 
                                case
                                    when round(v.value::numeric,2) between 0   and 0.2 then 'verylow'
                                    when round(v.value::numeric,2) between 0.2 and 0.4 then 'low'
                                    when round(v.value::numeric,2) between 0.4 and 0.6 then 'mid'
                                    when round(v.value::numeric,2) between 0.6 and 0.8 then 'high'
                                    when round(v.value::numeric,2) > 0.8               then 'veryhigh'
                                end as class, round(value::numeric,2)::float as value
                                from value v
                                inner join county c
                                on v.county_id = c.id
                                inner join indicator i
                                on v.indicator_id = i.id
                                where indicator_id = {0}
                                {1}
                                {2}
                                {3}
                                order by year, value {4}, name
                          '''.format(params['indicator_id'],
                             (' and (scenario_id = {0} or scenario_id is null)'.format(params['scenario_id'])) if params[ 'scenario_id'] != 'null' else '',
                              "and c.state = '{0}'".format(params['clipping']) if params['clipping'] != 'semiarido' else '',
                              'and v.year = {0}'.format(params['year']) if 'year' in params else '',
                              ('desc' if indicLevelYears[int(params['indicator_id'])]['level'] == 0 else '')
                             )
                          )
    data=toGroupedDict(rawdata,indicLevelYears[int(params['indicator_id'])]['level'])
    return data

def getInfoByState(params):
    return {'nextlevel': getDictResultset(
        '''
    select distinct id,pessimist,
                first_value(title) over (partition by id order by year desc range between unbounded preceding and unbounded following) as title,
                first_value(year) over (partition by id order by year desc range between unbounded preceding and unbounded following) as year,
                round(first_value(value) over (partition by id order by year desc range between unbounded preceding and unbounded following)::numeric,2)::float as value 
    from 
    (
    select i.id,i.pessimist, title, year, avg(value) as VALUE
                from indicator_indicator ii   inner join indicator i
             on ii.indicator_id_detail = i.id
       inner join value v
               on v.indicator_id = ii.indicator_id_detail
       inner join county c
               on v.county_id = c.id
            where ii.indicator_id_master = {0}          
              and (v.year <= {1} or year = {2})
              and {3}
            and state_id = {4}
              and i.level = {5}
         group by i.id,i.pessimist, title, year
    ) A
    order by 5 desc'''.format(
            params['indicator_id'],
            params['year'] if int(params['year']) <= currentYear else currentYear,
            params['year'],
            'scenario_id is null' if int(params['year']) <= currentYear
            else '((scenario_id = {0}) or (scenario_id is null))'.format(params['scenario_id']),
            params['resolution_id'],
            indicLevelYears[int(params['indicator_id'])]['level'] + 1
        )),
        'lastlevel': getDictResultset(
        '''select distinct id,pessimist,
            first_value(title) over (partition by id order by year desc range between unbounded preceding and unbounded following) as title,
            first_value(year) over (partition by id order by year desc range between unbounded preceding and unbounded following) as year,
            round(first_value(value) over (partition by id order by year desc range between unbounded preceding and unbounded following)::numeric)::integer as value 
from 
(select i.id,i.pessimist,title,master_year as year,avg(value) as value
        from contribution ct
     INNER JOIN indicator i
             on i.id = ct.detail_indicator_id 
     inner join county c
           on ct.county_id = c.id
          where master_indicator_id = {0}          
            and (master_year <= {1} or master_year = {2})
            and {3}
            and state_id = {4}
       group by i.id,i.pessimist,title,master_year
) A
order by 5 desc'''.format(
            params['indicator_id'],
            params['year'] if int(params['year']) <= currentYear else currentYear,
            params['year'],
            'master_scenario_id is null' if int(params['year']) <= currentYear
            else '((master_scenario_id = {0}) or (master_scenario_id is null))'.format(params['scenario_id']),
            params['resolution_id']
        ))}

def getInfoByMesoregion(params):
    if indicLevelYears[int(params['indicator_id'])]['level'] == 6:
        raise Exception('sismoiErr: getInfo: o indicator_id = {0} é de nível 6'.format(params['indicator_id']))

    data = {'nextlevel': getDictResultset(
        '''
    select distinct id,pessimist,
                first_value(title) over (partition by id order by year desc range between unbounded preceding and unbounded following) as title,
                first_value(year) over (partition by id order by year desc range between unbounded preceding and unbounded following) as year,
                round(first_value(value) over (partition by id order by year desc range between unbounded preceding and unbounded following)::numeric,2)::float as value 
    from 
    (
    select i.id,i.pessimist, title, year, avg(value) as VALUE
                from indicator_indicator ii   inner join indicator i
             on ii.indicator_id_detail = i.id
       inner join value v
               on v.indicator_id = ii.indicator_id_detail
       inner join county c
               on v.county_id = c.id
            where ii.indicator_id_master = {0}          
              and (v.year <= {1} or year = {2})
              and {3}
            and mesoregion_id = {4}
              and i.level = {5}
         group by i.id,i.pessimist, title, year
    ) A
    order by 5 desc'''.format(
            params['indicator_id'],
            params['year'] if int(params['year']) <= currentYear else currentYear,
            params['year'],
            'scenario_id is null' if int(params['year']) <= currentYear
            else '((scenario_id = {0}) or (scenario_id is null))'.format(params['scenario_id']),
            params['resolution_id'],
            indicLevelYears[int(params['indicator_id'])]['level'] + 1
        )),
        'lastlevel': getDictResultset(
        '''select distinct id,pessimist,
            first_value(title) over (partition by id order by year desc range between unbounded preceding and unbounded following) as title,
            first_value(year) over (partition by id order by year desc range between unbounded preceding and unbounded following) as year,
            round(first_value(value) over (partition by id order by year desc range between unbounded preceding and unbounded following)::numeric)::integer as value 
from 
(select distinct i.id,i.pessimist,title,master_year as year,avg(value) as value
        from contribution ct
     INNER JOIN indicator i
             on i.id = ct.detail_indicator_id 
     inner join county c
           on ct.county_id = c.id
          where master_indicator_id = {0}          
            and (master_year <= {1} or master_year = {2})
            and {3}
            and mesoregion_id = {4}
       group by i.id,i.pessimist,title,master_year
) A
order by 5 desc'''.format(
            params['indicator_id'],
            params['year'] if int(params['year']) <= currentYear else currentYear,
            params['year'],
            'master_scenario_id is null' if int(params['year']) <= currentYear
            else '((master_scenario_id = {0}) or (master_scenario_id is null))'.format(params['scenario_id']),
            params['resolution_id']
        ))}
    return data

def getInfoByMicroregion(params):
    if indicLevelYears[int(params['indicator_id'])]['level'] == 6:
        raise Exception('sismoiErr: getInfo: o indicator_id = {0} é de nível 6'.format(params['indicator_id']))

    data = {'nextlevel':getDictResultset('''select distinct id,pessimist,
            first_value(title) over (partition by id order by year desc range between unbounded preceding and unbounded following) as title,
            first_value(year) over (partition by id order by year desc range between unbounded preceding and unbounded following) as year,
            round(first_value(value) over (partition by id order by year desc range between unbounded preceding and unbounded following)::numeric,2)::float as value 
from 
(
select i.id,i.pessimist, title, year, avg(value) as VALUE
            from indicator_indicator ii   inner join indicator i
         on ii.indicator_id_detail = i.id
   inner join value v
           on v.indicator_id = ii.indicator_id_detail
   inner join county c
           on v.county_id = c.id
        where ii.indicator_id_master = {0}          
          and (v.year <= {1} or year = {2})
          and {3}
          and c.microregion_id = 18
          and i.level = {5}
     group by i.id,i.pessimist, title, year
) A
order by 5 desc'''.format(
        params['indicator_id'],
        params['year'] if int(params['year']) <= currentYear else currentYear,
        params['year'],
        'scenario_id is null' if int(params['year']) <= currentYear
        else '((scenario_id = {0}) or (scenario_id is null))'.format(params['scenario_id']),
        params['resolution_id'],
        indicLevelYears[int(params['indicator_id'])]['level'] + 1
    )),
        'lastlevel':getDictResultset('''select distinct id,pessimist,
            first_value(title) over (partition by id order by year desc range between unbounded preceding and unbounded following) as title,
            first_value(year) over (partition by id order by year desc range between unbounded preceding and unbounded following) as year,
            round(first_value(value) over (partition by id order by year desc range between unbounded preceding and unbounded following)::numeric)::integer as value 
from 
(select i.id,i.pessimist,title,master_year as year,avg(value) as value
        from contribution ct
     INNER JOIN indicator i
             on i.id = ct.detail_indicator_id 
     inner join county c
           on ct.county_id = c.id
          where master_indicator_id = {0}          
            and (master_year <= {1} or master_year = {2})
            and {3}
            and microregion_id = {4}
       group by i.id,i.pessimist,title,master_year
) A
order by 5 desc'''.format(
            params['indicator_id'],
            params['year'] if int(params['year']) <= currentYear else currentYear,
            params['year'],
            'master_scenario_id is null' if int(params['year']) <= currentYear
            else '((master_scenario_id = {0}) or (master_scenario_id is null))'.format(params['scenario_id']),
            params['resolution_id']
        ))}
    return data

def getInfoByCounty(params):
    if indicLevelYears[int(params['indicator_id'])]['level'] == 6:
        raise Exception('sismoiErr: getInfo: o indicator_id = {0} é de nível 6'.format(params['indicator_id']))

    data={'nextlevel':getDictResultset(
      '''select distinct i.id,i.pessimist,
            first_value(title) over (partition by i.id order by year desc range between unbounded preceding and unbounded following) as title,
            first_value(year) over (partition by i.id order by year desc range between unbounded preceding and unbounded following) as year,
            round(first_value(value) over (partition by i.id order by year desc range between unbounded preceding and unbounded following)::numeric,2)::float as value 
            from indicator_indicator ii   inner join indicator i
         on ii.indicator_id_detail = i.id
   inner join value v
           on v.indicator_id = ii.indicator_id_detail
        where ii.indicator_id_master = {0}          
          and (v.year <= {1} or year = {2})
          and {3}
          and v.county_id = {4}
          and i.level = {5}
     order by 5 desc'''.format(
          params['indicator_id'],
          params['year'] if int(params['year']) <= currentYear else currentYear,
          params['year'],
          'scenario_id is null' if int(params['year']) <= currentYear
                                else '((scenario_id = {0}) or (scenario_id is null))'.format(params['scenario_id']),
          params['resolution_id'],
          indicLevelYears[int(params['indicator_id'])]['level']+1
    )),'lastlevel':getDictResultset(
        '''select distinct i.id,i.pessimist,
              first_value(title) over (partition by i.id order by master_year desc range between unbounded preceding and unbounded following) as title,
              first_value(master_year) over (partition by i.id order by master_year  desc range between unbounded preceding and unbounded following) as year,
              round(first_value(value) over (partition by i.id order by master_year desc range between unbounded preceding and unbounded following)::numeric)::integer as value 
        from contribution ct
     INNER JOIN indicator i
             on i.id = ct.detail_indicator_id 
          where master_indicator_id = {0}          
            and (master_year <= {1} or master_year = {2})
            and {3}
            and county_id = {4}
       order by 5 desc'''.format(
            params['indicator_id'],
            params['year'] if int(params['year']) <= currentYear else currentYear,
            params['year'],
            'master_scenario_id is null' if int(params['year']) <= currentYear
            else '((master_scenario_id = {0}) or (master_scenario_id is null))'.format(params['scenario_id']),
            params['resolution_id']
        ))}
    return data

def getStateGeometry(clipping):
    return getValue("""
    select
    row_to_json(fc)
    from
    (select 'FeatureCollection' as "type", array_to_json(array_agg(f)) as "features"
    from
       (select 'Feature' as "type",
                ST_AsGeoJSON(ST_Simplify(ST_Force_2D(geom), 0.0003), 4)::json as "geometry",
                (select json_strip_nulls(row_to_json(t))
        from
                (select
                 id,name,
                 state) t
       ) as "properties"
       from state
    {0}
    ) as f
    ) as fc""".format(("where state = '{0}'".format(clipping) if clipping != 'semiarido' else '')))

def getMesoregionGeometry(clipping):
    return getValue("""select
    row_to_json(fc)
    from
    (select 'FeatureCollection' as "type", array_to_json(array_agg(f)) as "features"
    from
       (select 'Feature' as "type",
                ST_AsGeoJSON(ST_Simplify(ST_Force_2D(geom), 0.0003), 4)::json as "geometry",
                (select json_strip_nulls(row_to_json(t))
        from
                (select
                 id,
                 name,
                 state) t
       ) as "properties"
       from mesoregion
       {0}
    ) as f
    ) as fc""".format(("where state = '{0}'".format(clipping ) if clipping != 'semiarido' else '')))

def getMicroregionGeometry(clipping):
    return getValue("""select
    row_to_json(fc)
    from
    (select 'FeatureCollection' as "type", array_to_json(array_agg(f)) as "features"
    from
       (select 'Feature' as "type",
                ST_AsGeoJSON(ST_Simplify(ST_Force_2D(geom), 0.0003), 4)::json as "geometry",
                (select json_strip_nulls(row_to_json(t))
        from
                (select
                 id,
                 name,
                 state) t
       ) as "properties"
       from microregion
       {0}
    ) as f
    ) as fc""".format(("where state = '{0}'".format(clipping ) if clipping != 'semiarido' else '')))

def getCountyGeometry(clipping):
    return getValue("""select
    row_to_json(fc)
    from
    (select 'FeatureCollection' as "type", array_to_json(array_agg(f)) as "features"
    from
       (select 'Feature' as "type",
                ST_AsGeoJSON(ST_Simplify(ST_Force_2D(geom), 0.0003), 4)::json as "geometry",
                (select json_strip_nulls(row_to_json(t))
        from
                (select
                 id,
                 name,
                 state) t
       ) as "properties"
       from county
       {0}
    ) as f
    ) as fc""".format(("where state = '{0}'".format(clipping ) if clipping != 'semiarido' else '')))

@app.route("/sismoi/getHierarchy", methods=['GET'])
def getHierarchy():
    incache=inCache('getHierarchy@')
    log('getHieararchy', '', incache)
    if incache:
        return fromCache('getHierarchy@')
    try:
        data=getDictResultset("""select a.id,a.name,a.title,a.shortname,
                                        a.simple_description,a.complete_description,
                                        a.equation,a.level,a.pessimist,
                                        string_agg(distinct b.indicator_id_master::character varying,',') as indicator_id_master, 
                                        string_agg(distinct year::character varying,',') as years 
                                        from indicator a
                                 left join indicator_indicator b
                                        on b.indicator_id_detail = a.id
                                 left join (select distinct indicator_id,year from value) v
                                        on a.id = v.indicator_id
                                     where level = 1 or indicator_id_master is not null
                                  group by a.id,a.name,a.title,a.shortname,a.simple_description,a.complete_description,
                                           a.equation,a.level,a.pessimist
                                  order by level,id
                              """)
        ret = json.dumps(data)
        toCache('getHierarchy@',ret)
        return ret
    except Exception as e:
        return str(e)

@app.route('/sismoi/getGeometry/<sparams>', methods=['GET'])
def getGeometry(sparams):
    errorMsg, params = validateClippingResolution(sparams)
    if (errorMsg != ''):
        raise Exception('sismoiErr: getGeometry: ' + errorMsg + '\nParams: '+sparams)
    # special cache for maps
    cacheName='getGeometry@resolution={0},clipping={1}'.format(params['resolution'],params['clipping'])
    incache=inCache(cacheName)
    log('getGeometry',cacheName.split('@')[1],incache)
    map = None
    if incache:
        return fromCache(cacheName)
    if params['resolution'] == 'estado':
        map=getStateGeometry(params['clipping'])
    elif params['resolution'] == 'municipio':
        map=getCountyGeometry(params['clipping'])
    elif params['resolution'] == 'microrregiao':
        map = getMicroregionGeometry(params['clipping'])
    elif params['resolution'] == 'mesorregiao':
        map = getMesoregionGeometry(params['clipping'])
    ret=json.dumps(map)
    toCache(cacheName,ret)
    return ret

@app.route('/sismoi/getMapData/<sparams>', methods=['GET'])
def getMapData(sparams):
    incache=inCache('getMapData@'+sparams)
    log('getMapData',sparams,incache)
    if incache:
        return fromCache('getMapData@'+sparams)
    errorMsg, params = validateParams(sparams)
    if (errorMsg != ''):
        raise Exception('getMapData: ' + errorMsg)
    data = None
    if params['resolution'] == 'municipio':
        data = getIndicatorByCounty(params)
    elif params['resolution'] == 'microrregiao':
        data = getIndicatorByMicroregion(params)
    elif params['resolution'] == 'mesorregiao':
        data = getIndicatorByMesoregion(params)
    elif params['resolution'] == 'estado':
        data = getIndicatorByState(params)
    '''
    if len(data) == 0:
        raise Exception('sismoiErr: getMapData: Não existem dados para esses parâmetros: {0}'.format(sparams))
    '''
    ret=json.dumps(data)
    toCache('getMapData@'+sparams,ret)
    return ret

@app.route('/sismoi/getGeometryAndData/<sparams>', methods=['GET'])
def getGeometryAndData(sparams):
    incache=inCache('getGeometryAndData@'+sparams)
    log('getGeometryAndData',sparams,incache)
    if incache:
        return fromCache('getGeometryAndData@'+sparams)
    errorMsg, params = validateParams(sparams)
    if (errorMsg != ''):
        raise Exception('getGeometryAndData: ' + errorMsg)
    geometry = json.loads(getGeometry(sparams))
    mapdata = json.loads(getMapData(sparams))

    if geometry['features'] == None:
        return json.dumps(geometry)
    for feature in geometry['features']:
        row = findElement(mapdata, feature)
        feature['properties']['name'] = row['name']
        feature['properties']['value'] = float(row['value'])
        feature['properties']['style'] = {'color': '#d7d7d7',
                                          'fillcolor': featureColor(float(row['value']), row['pessimist']), 'weight': 1}
    ret=json.dumps(geometry)
    toCache('getGeometryAndData@'+sparams,ret)
    return ret

@app.route('/sismoi/getTotal/<sparams>', methods=['GET'])
def getTotal(sparams):
    incache=inCache('getTotal@'+sparams)
    log('getTotal',sparams,incache)
    if incache:
        return fromCache('getTotal@'+sparams)
    errorMsg, params = validateParams(sparams)
    if (errorMsg != ''):
        return 'sismoiErr: getTotal: ' + errorMsg
    if params['resolution'] == 'municipio':
        data = getTotalByCounty(params)
    elif params['resolution'] == 'microrregiao':
        data = getTotalByMicroregion(params)
    elif params['resolution'] == 'mesorregiao':
        data = getTotalByMesoregion(params)
    elif params['resolution'] == 'estado':
        data = getTotalByState(params)
    else:
        raise Exception('sismoiErr: Parâmetro resolution inválido: {0}',params['resolution'])
    ret=json.dumps(data)
    toCache('getTotal@'+sparams,ret)
    return ret

# clipping=semiarido,resolution=municipio,indicator_id=2,scenario_id=1,year=2030
@app.route('/sismoi/getInfo/<sparams>', methods=['GET']) # 'clipping=semiarido,resolution=municipio,indicator_id=2,scenario_id=1,year=2030'
def getInfo(sparams):
    incache=inCache('getInfo@'+sparams)
    log('getInfo',sparams,incache)
    if incache:
        return fromCache('getInfo@'+sparams)
    errorMsg,params=validateClippingResolution(sparams)
    if errorMsg == '' and (not 'indicator_id' in params):
        errorMsg = "sismoiErr: É obrigatório especificar o indicador (indicator_id)."
    if 'resolution_id' not in params.keys():
        errorMsg = "sismoiErr: É obrigatório especificar o id na resolução indicada."
    if errorMsg != '':
        return errorMsg, params
    if params['resolution'] == 'municipio':
        data=getInfoByCounty(params)
    elif params['resolution'] == 'microrregiao':
        data=getInfoByMicroregion(params)
    elif params['resolution'] == 'mesorregiao':
        data = getInfoByMesoregion(params)
    elif params['resolution'] == 'estado':
        data=getInfoByState(params)
    ret=json.dumps(data)
    toCache('getInfo@'+sparams,ret)
    return ret

# indicator_id=2
@app.route('/sismoi/getIndicatorData/<sparams>', methods=['GET'])
def getIndicatorData(sparams):
    incache = inCache('getIndicatorData@'+sparams)
    log('getIndicatorData',sparams,incache)
    if incache:
        return fromCache('getIndicatorData@'+sparams)
    if inCache('getIndicatorData@'+sparams):
        return fromCache('getIndicatorData@'+sparams)
    params = dict(token.split('=') for token in sparams.split(','))
    if not 'indicator_id' in params:
        raise Exception("sismoiErr: É obrigatório especificar o indicador (indicator_id).")
    try:
        data=getDictResultset("""select a.id,a.name,a.title,a.shortname,
                                        a.simple_description,a.complete_description,
                                        a.equation,a.level,a.pessimist,
                                        string_agg(distinct year::character varying,',') as years 
                                        from indicator a
                                 left join (select distinct indicator_id,year from value) v
                                        on a.id = v.indicator_id
                                     where a.id = {0}
                                  group by a.id,a.name,a.title,a.shortname,a.simple_description,a.complete_description,
                                           a.equation,a.level,a.pessimist
                              """.format(params['indicator_id']))
        ret = json.dumps(data)
        toCache('getIndicatorData@' + sparams, ret)
        return ret
    except Exception as e:
        return str(e)

@app.route('/sismoi/getStats', methods=['GET'])
def getStats():
    cacheHits=0
    accesses=0
    line=('='*84)+'\n'
    s=['                                   SISMOI Stats\n',
       line,
        "{:<22} {:<6} {:<12} {:<15} {:<17} {:<10}\n".format('Function', 'Calls', 'Cache Hits', 'W/O Cache(s)', 'With Cache(ms)','Ratio'),
       line]
    for func, values  in funcStats.items():
        withoutcache=str(round(values['elapsedwocache']/values['countwocache'],3)) if values['countwocache'] > 0 \
            else '-'
        withcache=str(round(values['elapsedwithcache']*1000/values['countwithcache'],6)) if values['countwithcache'] > 0 \
            else '-'
        s.append("{:<22} {:<6} {:<12} {:<15} {:<17} {:<10}\n".format(func, values['countwocache']+
                                                                           values['countwithcache'],
                                                              values['countwithcache'],
                                                              withoutcache,
                                                              withcache,
                                                              int(float(withoutcache)/float(withcache)*1000)
                                                                  if (withoutcache != '-')
                                                                     and (withcache != '-')
                                                                     and (withcache != '0.0') else '-'
                                                              ))
        cacheHits+=values['countwithcache']
        accesses+=values['countwocache']+values['countwithcache']
    return '''
{0}{6}
Accesses: {1}
Cache Type: {2}
Cache Hits: {3}
Cache Hits Efficiency: {7}%
Cache Length: {4}
Cache Size: {5} kbytes
Log: {8}
'''.format(''.join(s),accesses,cacheType,cacheHits,len(cache),int(get_deep_size(cache)/1024),line,
           round((cacheHits/accesses*100 if accesses > 0 else 0.0),2),args.log)

if __name__ == "__main__":
    try:
        args = ProcessCmdLine()
        clippings = clippings + getStates()
        indicLevelYears = getIndicLevelYears()
        cacheType=args.cachetype

        cacheType = 0
        args.log = True

        statsOff = args.statsoff

        app.run(host=args.host, port=args.port, debug=args.debug)
    except Exception as e:
        print(e)
        exit(-1)
