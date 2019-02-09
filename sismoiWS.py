from flask import Flask
import psycopg2
import psycopg2.extras
import argparse
import json
from flask_compress import Compress

conn,cur = None,None

resolutions = ['microrregiao','mesorregiao','municipio','estado']

classes = ['verylow','low','mid','high','veryhigh']

states = []

clippings = ['semiarido']

colorMap = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']

compress = Compress()

def startApp():
    app = Flask(__name__)
    compress.init_app(app)
    return app

app = startApp()

def ProcessCmdLine():
    parser = argparse.ArgumentParser(description="SISMOI WebServices.")
    parser.add_argument("-d", "--debug", help="Activate Flask debug mode", action='store_true')
    parser.add_argument("-host", "--host", help="Host IP", type=str, default="127.0.0.1")
    parser.add_argument("-p", "--port", type=str, help="Port to be used", default=5000)
    return parser.parse_args()

def shortJson(json):
    return json.replace('\t','').replace('\n')

def connect():
    conn = psycopg2.connect("dbname='sismoi' user='sismoi' host='200.133.39.41' password='142857'")
    cur = conn.cursor()
    return conn, cur

def getValue(sql):
    cur.execute(sql)
    row=cur.fetchone()
    if row != None:
        return row[0]
    else:
        return None

def findElement(data,keyfield, feature):
    for rec in data:
        if rec[keyfield] == feature['properties'][keyfield]:
            return rec
    raise Exception('Element not found in findElement. keyfield: {0} Feature: \n {1}'.format(keyfield,feature))

def getDictResultset(sql):
    dictcur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    dictcur.execute(sql)
    resultset =dictcur.fetchall()
    dictResult = []
    for row in resultset:
        dictResult.append(dict(row))
    return dictResult

def getStates():
    cur.execute("select distinct state from county where state is not null")
    return([token[0] for token in cur.fetchall()])

def featureColor(value, optimist):
    value = value if optimist else 1 - value
    return colorMap[0] if (value >= 0.0 and value <= 0.2) else\
           colorMap[1] if (value > 0.2 and value <= 0.4) else\
           colorMap[2] if (value > 0.4 and value <= 0.6) else\
           colorMap[3] if (value > 0.6 and value <= 0.8) else\
           colorMap[4]

def validateClippingResolution(params):
    errorMsg=''
    if not(params['resolution'] in resolutions):
        errorMsg='Resolução errada: {0}.'.format(params['resolution'])
    if params['clipping'] not in clippings:
        errorMsg="É necessário especificar clipping como 'semiarido' ou uma UF válida."
    return errorMsg

def validateGetGeometryParams(sparams):
    errorMsg = ''
    params=dict(token.split('=') for token in sparams.split(','))
    if len(params) < 2:
        return 'São esperados no mínimo dois parâmetros.', None
    errorMsg=validateClippingResolution(params)
    if errorMsg == '':
        return errorMsg,params

def validateIndicatorParams(sparams):
    errorMsg = ''
    params=dict(token.split('=') for token in sparams.split(','))
    if len(params) < 5:
        errorMsg='São esperados no mínimo cinco parâmetros.'
    errorMsg=validateClippingResolution(params)
    return errorMsg,params

def validateTotalParams(sparams,nparamsexpected):
    errorMsg = ''
    params=dict(token.split('=') for token in sparams.split(','))
    if len(params) < nparamsexpected:
        errorMsg='São esperados {0} parâmetros.'.format(nparamsexpected)
    elif params['clipping'] not in clippings:
        errorMsg = "É necessário especificar clipping como 'semiarido' ou uma UF válida."
    elif not('scenario_id' in params) and not('year' in params):
        errorMsg = "É necessário especificar o ano ou o cenário."
    return errorMsg,params

def addFeatureColor(data):
    for rec in data:
        rec['valuecolor'] = featureColor(rec['value'],rec['optimist'])
    return data

def toGroupedDict(data):
    ret = {}
    for i in range(0,len(data)):
        colorFake = 0.0
        if not(data[i]['year'] in ret.keys()):
            ret[data[i]['year']] = {}
            for _class in classes:
                ret[data[i]['year']].update({_class: {'data': [], 'count': 0, 'valuecolor': featureColor(colorFake,data[i]['optimist'])},'count': 0})
                colorFake+=0.2
        if 'id' in data[i]:
            ret[data[i]['year']][data[i]['class']]['data'].append({'id':data[i]['id'],
                'name':data[i]['name'], 'value:':data[i]['value']})
        else:
            ret[data[i]['year']][data[i]['class']]['data'].append({'state':data[i]['state'],
                'value:':data[i]['value']})
        ret[data[i]['year']][data[i]['class']]['count']+=1
        ret[data[i]['year']]['count']+=1
    return ret

def getIndicatorByCounty(params):
    data=getDictResultset('''select v.county_id as id, v.indicator_id, v.year, v.scenario_id, i.optimist, v.value from value v 
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

def getIndicatorByMicroregion(params):
    data=getDictResultset('''select c.microregion_id as id, m.name, indicator_id, i.optimist, v.scenario_id,year, avg(v.value) as value
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
                            group by  c.microregion_id, m.name, v.indicator_id, i.optimist, v.year, v.scenario_id
                             order by                   m.name, v.year, v.scenario_id
                          '''.format(params['indicator_id'],
                                     ' = ' +params['scenario_id'] if params['scenario_id'] != 'null' else 'is null',
                                     "and state = '{0}'".format(params['clipping']) if params['clipping'] != 'semiarido' else '',
                                     params['year'])
                          )
    return addFeatureColor(data)

def getIndicatorByMesoregion(params):
    data=getDictResultset('''select c.mesoregion_id as id, m.name, indicator_id, optimist, v.scenario_id, year, avg(v.value) as value
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
                            group by  c.mesoregion_id, m.name, v.indicator_id, i.optimist, v.year, v.scenario_id
                            order by                   m.name, v.year, v.scenario_id
                          '''.format(params['indicator_id'],
                                     ' = ' +params['scenario_id'] if params['scenario_id'] != 'null' else 'is null',
                                     "and state = '{0}'".format(params['clipping']) if params['clipping'] != 'semiarido' else '',
                                     params['year'])
                          )
    return addFeatureColor(data)

def getIndicatorByState(params):
    data=getDictResultset('''select c.state,v.indicator_id, i.optimist, v.scenario_id, year, avg(v.value) as value
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
                            group by  c.state, v.indicator_id, i.optimist, v.scenario_id,year
                             order by c.state, v.indicator_id, v.scenario_id,year
                          '''.format(params['indicator_id'],
                                     ' = ' +params['scenario_id'] if params['scenario_id'] != 'null' else 'is null',
                                     "and state = '{0}'".format(params['clipping']) if params['clipping'] != 'semiarido' else '',
                                     params['year'])
                          )
    return addFeatureColor(data)

def getTotalByState(params):
    optimist = getValue('select optimist from indicator where id = {0}'.format(params['indicator_id']))
    rawdata=getDictResultset('''select c.state, year, i.optimist, 
                             case
                                when value between 0   and 0.2 then 'verylow'
                                when value between 0.2 and 0.4 then 'low'
                                when value between 0.4 and 0.6 then 'mid'
                                when value between 0.6 and 0.8 then 'high'
                                when value > 0.8               then 'veryhigh'
                             end as class, avg(v.value) as value
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
                             group by state, year, i.optimist, class 
                                order by year {4}, state
                          '''.format(params['indicator_id'],
                                     (' and (scenario_id = {0}'.format(params['scenario_id'] if params['scenario_id'] != 'null' else '') +
                                      (' or scenario_id is null)' if (not 'year' in params) else ')')),
                                      "and c.state = '{0}'".format(params['clipping']) if params['clipping'] != 'semiarido' else '',
                                      'and v.year = {0}'.format(params['year']) if 'year' in params else '',
                                      ('desc' if optimist == 0 else '')
                                     )
                          )
    data=toGroupedDict(rawdata)
    return data

def getTotalByMesoregion(params):
    optimist = getValue('select optimist from indicator where id = {0}'.format(params['indicator_id']))
    rawdata=getDictResultset('''select c.mesoregion_id as id, m.name, year, i.optimist, 
                             case
                                when value between 0   and 0.2 then 'verylow'
                                when value between 0.2 and 0.4 then 'low'
                                when value between 0.4 and 0.6 then 'mid'
                                when value between 0.6 and 0.8 then 'high'
                                when value > 0.8               then 'veryhigh'
                             end as class, avg(v.value) as value
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
                             group by year, class,  mesoregion_id, m.name, i.optimist
                                order by year, value {4}, name
                          '''.format(params['indicator_id'],
                                     (' and (scenario_id = {0}'.format(params['scenario_id'] if params['scenario_id'] != 'null' else '') +
                                      (' or scenario_id is null)' if (not 'year' in params) else ')')),
                                      "and c.state = '{0}'".format(params['clipping']) if params['clipping'] != 'semiarido' else '',
                                      'and v.year = {0}'.format(params['year']) if 'year' in params else '',
                                      ('desc' if optimist == 0 else '')
                                     )
                          )
    data=toGroupedDict(rawdata)
    return data

def getTotalByMicroregion(params):
    optimist = getValue('select optimist from indicator where id = {0}'.format(params['indicator_id']))
    rawdata=getDictResultset('''select c.microregion_id as id, m.name, year, i.optimist, 
                             case
                                when value between 0   and 0.2 then 'verylow'
                                when value between 0.2 and 0.4 then 'low'
                                when value between 0.4 and 0.6 then 'mid'
                                when value between 0.6 and 0.8 then 'high'
                                when value > 0.8               then 'veryhigh'
                             end as class, avg(v.value) as value
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
                             group by year, class, c.microregion_id, m.name, i.optimist
                                order by year, value {4}, name
                          '''.format(params['indicator_id'],
                                     (' and (scenario_id = {0}'.format(params['scenario_id'] if params['scenario_id'] != 'null' else '') +
                                      (' or scenario_id is null)' if (not 'year' in params) else ')')),
                                      "and c.state = '{0}'".format(params['clipping']) if params['clipping'] != 'semiarido' else '',
                                      'and v.year = {0}'.format(params['year']) if 'year' in params else '',
                                      ('desc' if optimist == 0 else '')
                                     )
                          )
    data=toGroupedDict(rawdata)
    return data

def getTotalByCounty(params):
    optimist = getValue('select optimist from indicator where id = {0}'.format(params['indicator_id']))
    rawdata=getDictResultset('''select c.id, c.name, year, i.optimist, v.value,
                             case
                                when value between 0   and 0.2 then 'verylow'
                                when value between 0.2 and 0.4 then 'low'
                                when value between 0.4 and 0.6 then 'mid'
                                when value between 0.6 and 0.8 then 'high'
                                when value > 0.8               then 'veryhigh'
                             end as class
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
                                     (' and (scenario_id = {0}'.format(params['scenario_id'] if params['scenario_id'] != 'null' else '') +
                                      (' or scenario_id is null)' if (not 'year' in params) else ')')),
                                      "and c.state = '{0}'".format(params['clipping']) if params['clipping'] != 'semiarido' else '',
                                      'and v.year = {0}'.format(params['year']) if 'year' in params else '',
                                      ('desc' if optimist == 0 else '')
                                     )
                          )
    data=toGroupedDict(rawdata)
    return data

@app.route("/sismoi/getHierarchy", methods=['GET'])
def getHierarchy():
    try:
        data=getDictResultset("""select a.*,b.indicator_id_master from indicator a
                       left join indicator_indicator b
                       on b.indicator_id_detail = a.id
                       where level = 1 or indicator_id_master is not null
                       order by level,id""")
        return json.dumps(data)
    except Exception as e:
        return str(e)

@app.route('/sismoi/getGeometry/<sparams>', methods=['GET'])
def getGeometry(sparams):
#    return sparams
    errorMsg, params = validateGetGeometryParams(sparams)
    if (errorMsg != ''):
        raise Exception('getGeometry: ' + errorMsg + '\nParams: '+sparams)
    # force reasolution == 'municipio' of there´s state clipping.
    realresolution = (params['resolution'] if params['clipping'] == 'semiarido' else 'municipio')
    cur.execute("SELECT geojson FROM geojson WHERE name = '{0}'".format(realresolution))
    smap = cur.fetchone()[0]
    if realresolution == 'municipio':
        map=json.loads(smap)
        try:
            i=0
            while i < len(map['features']):
                if (params['clipping'] != 'semiarido') and (params['clipping'] != map['features'][i]['properties']['uf']):
                    del map['features'][i]
                else:
                    del map['features'][i]['properties']['uf']
                    i+=1
        except Exception as e:
            print(e)
        return json.dumps(map)
    else:
        return smap
    return map

@app.route('/sismoi/getMapData/<sparams>', methods=['GET'])
def getMapData(sparams):
    errorMsg, params = validateIndicatorParams(sparams)
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
    return json.dumps(data)

@app.route('/sismoi/getGeometryAndData/<sparams>', methods=['GET'])
def getGeometryAndData(sparams):
    errorMsg, params = validateIndicatorParams(sparams)
    if (errorMsg != ''):
        raise Exception('getGeometryAndData: ' + errorMsg)
    geometry = json.loads(getGeometry(sparams))
    mapdata = json.loads(getMapData(sparams))
    keyfield = 'state' if params['resolution'] == 'estado' else 'id'
    for feature in geometry['features']:
        row = findElement(mapdata, keyfield, feature)
        feature['properties']['value'] = float(row['value'])
        feature['properties']['style'] = {'color': '#d7d7d7',
                                          'fillcolor': featureColor(float(row['value']), row['optimist']), 'weight': 1}
    return json.dumps(geometry)

@app.route('/sismoi;getTotal/<sparams>', methods=['GET'])
def getTotal(sparams):
    errorMsg, params = validateTotalParams(sparams,3)
    if (errorMsg != ''):
        raise Exception('getTotal: ' + errorMsg)
    if params['resolution'] == 'municipio':
        data = getTotalByCounty(params)
    elif params['resolution'] == 'microrregiao':
        data = getTotalByMicroregion(params)
    elif params['resolution'] == 'mesorregiao':
        data = getTotalByMesoregion(params)
    elif params['resolution'] == 'estado':
        data = getTotalByState(params)
    else:
        raise Exception('Parâmetro resolution inválido: {0}',params['resolution'])
    return json.dumps(data)

if __name__ == "__main__":
    try:
        conn, cur = connect()
        states = getStates()
        clippings = clippings + states
        args = ProcessCmdLine()
        app.run(host=args.host, port=args.port, debug=args.debug)
    except Exception as e:
        print(e)
