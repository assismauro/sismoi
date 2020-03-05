import psycopg2
import argparse
import pandas as pd
import psycopg2.extras
import os
import math

indicatorsfname = 'indicadores.csv'
valuesfname = 'valores.csv'
indicrelationfname = 'composicoes.csv'
contribfname = 'proporcionalidades.csv'
indicatorstbname = 'indicator'
valuetbname = 'value'
indic_indictbname  = 'indicator_indicator'
contribtbname = 'contribution'
scenariotbname = 'scenario'

sismoiUser = 'postgres'

fpath = r'D:\Atrium\Projects\SISMOI\Dadosv2\proporcionalidades\csv'+'\\'

conn = None
curr = None

def executeSQL(sql,cursorFactory=None):
    try:
        conn = psycopg2.connect("dbname='{0}' user='{1}' host='{2}' password='{3}'".format(args.database,args.user,args.host,args.password))

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

def getDictResultset(sql):
    return dict(row for row in executeSQL(sql, psycopg2.extras.DictCursor))

def ProcessCmdLine():
    parser = argparse.ArgumentParser(description='SISMOI import data app.')
    parser.add_argument('-d', '--database', help='Database to use', type=str, default='sismoi')
    parser.add_argument('-host', '--host', help='Posgres host', type=str, default='127.0.0.1')
    parser.add_argument('-u', '--user', help='Database user', type=str, default=sismoiUser)
    parser.add_argument('-w', '--password', help='Database password', type=str, default='142857')
    parser.add_argument('-p', '--port', type=int, help='Posgres port', default=5432)
    parser.add_argument('-fp', '--filepath', type=str, help='CSV files path')
    parser.add_argument('-fn', '--filename', type=str, help='CSV file name')
    parser.add_argument('-dt', '--destination', help='Export destination', type=str, default='script')
    parser.add_argument('-sc', '--schema', help='Destination schema', type=str, default='xxxx')
    return parser.parse_args()

def connect(args):
    try:
        conn = psycopg2.connect("dbname='{0}' user='{1}' host='{2}' password='{3}' port={4}".format(args.database,args.user,args.host,args.password,args.port))
        cur = conn.cursor()
        return conn, cur
    except Exception as e:
        print('I am unable to connect to the database. Error: {0}'.format(str(e)))
        return None, None

'''
def createTables(cur):
    try:
        cur.execute(indicatorsCREATE.format(indicatorstbname,sismoiUser))
#        cur.execute(indic_indicCREATE.format(indic_indictbname,sismoiUser))
        cur.execute(valueCREATE.format(valuetbname, sismoiUser))
        cur.execute(scenarioCREATE.format(scenariotbname,sismoiUser))
        return True
    except Exception as e:
        print('Error creating tables. Error: {0}'.format(str(e)))
        return False

def dropTables(cur):
    try:
        cur.execute('DROP TABLE IF EXISTS {0}'.format(indicatorstbname))
#        cur.execute('DROP TABLE IF EXISTS {0}'.format(indic_indictbname))
        cur.execute('DROP TABLE IF EXISTS {0}'.format(valuetbname))
        cur.execute('DROP SEQUENCE IF EXISTS {0}_id_seq'.format(valuetbname))
        cur.execute('DROP TABLE IF EXISTS {0}'.format(scenariotbname))
        cur.execute('DROP SEQUENCE IF EXISTS {0}_id_seq'.format(scenariotbname))
        return True
    except Exception as e:
        print('Error dropping  tables. Error: {0}'.format(str(e)))
        return False
'''

def import_indicator(cur,indicators,indicatortbname,destination):
    if destination == 'csv':
        script="id;name;title;shortname;simple_description;complete_description;pessimist\r"
    else:
        script = ''
    for index, row in indicators.iterrows():
        if destination == 'csv':
            sql = "{0};{1};{2};{3};{4};{5};{6}".format(row['id'],
                                                                        row['nome'].replace("'",""),
                                                                        row['titulo'].replace("'",""),
                                                                        row['titulo'].replace("'",""),
                                                                        row['desc_simples'].replace("'","").strip(),
                                                                        row['desc_completa'].replace("'","").strip(),
                                                                        int(row['cor']) if row['cor'] == row['cor'] else 0)
        else:
            sql = """INSERT INTO {6}(id,name,title,simple_description,complete_description,optimist) 
                VALUES({0},'{1}','{2}','{3}','{4}',{5})""".format(row['id'],
                                                                        row['nome'].replace("'",""),
                                                                        row['titulo'].replace("'",""),
                                                                        row['desc_simples'].replace("'","").strip(),
                                                                        row['desc_completa'].replace("'","").strip(),
                                                                        row['cor'] if row['cor'] == row['cor'] else 'null',
                                                                            indicatortbname)
        if destination == 'sql' or destination == 'csv':
            script+=sql+'\r'
        else:
            cur.execute(sql)
    if destination == 'sql':
        script += sql + ';\r'
        with open(fpath+indicatorstbname+'.sql','w', encoding="utf-8") as f:
            f.write(script)
    elif destination == 'csv':
        with open(fpath + indicatorstbname + '.csv', 'w', encoding="utf-8") as f:
            f.write(script)
    else:
        conn.commit()

def import_relation(cur,relations,relationtbname):
    sql=''
    try:
        for index, row in relations.iterrows():
            sql="""INSERT INTO {2}(indicator_id_master,indicator_id_detail)
                VALUES({0},{1})""".format(row['indicator_id_master'], row['indicator_id_detail'],relationtbname)
            cur.execute(sql)
        conn.commit()
    except Exception as e:
        raise Exception('Erro na sentença {0}: {1}'.format(sql,e))

def import_value(cur,values,valuetable,destination):
    i=1
    j=1
    ids=pd.read_csv(fpath+'county_id_geocod.csv', sep=';', encoding='latin1', engine='python')
    script = ''
    for index, row in values.iterrows():
        try:
            county_id = int(ids.loc[ids['GEOCOD'] == int(row['GEOCOD'])]['ID'])
            for column in values.columns[3:]:
                parts = column.split('-')
                indicator_id = parts[0]
                year = parts[1]
                scenario_id = 'NULL' if len(parts) == 2 else 1 if parts[2] == 'O' else 2 if parts[2] == 'P' else -1
                if scenario_id == -1:
                    raise ValueError('Error in scenario_id: {0}'.format(column))
                value = row[column]
                if destination != 'csv':
                    sql="""INSERT INTO {5}(id,county_id,indicator_id,scenario_id,year,value)
                        VALUES({6},{0},{1},{2},{3},{4});""".format(county_id,indicator_id,
                                                                  scenario_id,year,value,
                                                                  valuetable,i)
                else:
                    sql="""{6},{0},{1},{2},{3},{4}""".format(county_id,indicator_id,
                                                             scenario_id,year,value,
                                                             valuetable,i)
                    if destination == 'script' or destination == 'csv':
                        script += sql + '\n'
                    else:
                        cur.execute(sql)
                i+=1
                if (i % 1000) == 0:
                    print(i)
                if (i % 5000000) == 0:
                    if destination == 'csv':
                        with open(fpath + indicatorstbname + '{0}.csv'.format(j), 'w', encoding="utf-8") as f:
                            f.write('id,county_id,indicator_id,scenario_id,year,value\n'+script)
                        j+=1
                        script=''
            if destination == 'sql':
                conn.commit()
        except Exception as e:
            print('Error in import_value. Error: {0}'.format(str(e)))
            return False
    if destination == 'script':
        with open(fpath + indicatorstbname + '.sql', 'w', encoding="utf-8") as f:
            f.write(script)
    elif destination == 'csv':
        with open(fpath + indicatorstbname + '__{0}.csv'.format(j), 'w', encoding="utf-8") as f:
            f.write('id,county_id,indicator_id,scenario_id,year,value\n' + script)
    else:
        conn.commit()
        return True

def import_contribution(cur, headercontrib, contributions, contribtbname,destination):
#    ids=getDictResultset('SELECT id,geocod FROM county')
    try:
        ids=pd.read_csv(fpath+'county_id_geocod.csv', sep=',', encoding='latin1', engine='python')
        script = 'id,county_id,master_indicator_id,detail_indicator_id,master_scenario_id,detail_scenario_id,master_year,detail_year,value\n'
        i=0
        j=0
        for index, row in contributions.iterrows():
            county_id = int(ids.loc[ids['GEOCOD'] == int(row['GEOCOD'])]['ID'])
            for i in range(3,len(contributions.columns)):
                if contributions.columns[i] == 'Cluster':
                    continue
                parts = contributions.columns[i].replace('.','-').split('-')
                detail_indicator_id = parts[0]
                detail_year = parts[1]
                detail_scenario_id = 'NULL' if len(parts) == 2 else 1 if parts[2] == 'O' else 2 if parts[2] == 'P' else 'NULL'
                if detail_scenario_id == -1:
                    raise ValueError('Error in scenario_id: {0}'.format(contributions.columns[i]))
                if isinstance(headercontrib[i][0],str):
                    partsh = headercontrib[i][0][headercontrib[i][0].rfind('(')+1:-1].split('-')
                master_indicator_id = partsh[0]
                master_year = partsh[1]
                master_scenario_id = 'NULL' if len(partsh) == 2 else 1 if partsh[2] == 'O' else 2 if partsh[2] == 'P' else 'NULL'
                if master_scenario_id == -1:
                   raise ValueError('Error in scenario_id: {0}'.format(headercontrib[i]))
                j+=1
                if destination != 'csv':
                    sql="""INSERT INTO {0} 
                            (county_id, master_indicator_id, detail_indicator_id, master_scenario_id, detail_scenario_id,
                            master_year, detail_year, value)  VALUES ({1},{2},{3},{4},{5},{6},{7},{8});"""\
                        .format(contribtbname,county_id, master_indicator_id, detail_indicator_id, master_scenario_id,
                                detail_scenario_id,master_year,detail_year,row[i])
                else:
                    sql="""{0},{1},{2},{3},{4},{5},{6},{7},{8}"""\
                        .format(j,county_id, master_indicator_id, detail_indicator_id, master_scenario_id,
                                detail_scenario_id,master_year,detail_year,row[i])
                if destination == 'script' or destination == 'csv':
                    script += sql + '\n'
                else:
                    cur.execute(sql)
            print(i,index)
        if destination == 'script' or destination == 'csv':
            with open(fpath + contribtbname + ('.sql' if destination == 'sql' else '.csv') , 'w', encoding="utf-8") as f:
                f.write(script)
        else:
            conn.commit()
        print(index,'   ************')
    except Exception as e:
        print('Error importing table. Error: {0}'.format(str(e)))

cur = None

if __name__ == '__main__':
    args=ProcessCmdLine()
#    conn, cur=connect(args)
#    if conn == None:
#        exit(-1)
    indicatorstbname = args.schema+'.'+indicatorstbname
    valuetbname = args.schema+'.'+valuetbname
    indic_indictbname = args.schema+'.'+indic_indictbname
    contribtbname = args.schema+'.'+contribtbname
    scenariotbname = args.schema+'.'+scenariotbname
    sep='\\' if os.name == 'nt' else '/'
    fpath=args.filepath+(sep if args.filepath[-1] != sep else '')
#    indicators = pd.read_csv(fpath+indicatorsfname, sep=';', encoding='utf-8', engine='python',header=0)
    values = pd.read_csv(fpath+valuesfname, sep=';', encoding='latin1', engine='python',header=0)
#    relations = pd.read_csv(fpath+indicrelationfname, sep=';', encoding='latin1', engine='python',header=0)
#    headercontrib = pd.read_csv(fpath+contribfname, sep=';', encoding='latin1', engine='python',header=None,nrows=1)
#    contributions = pd.read_csv(fpath+contribfname, sep=';', encoding='latin1', engine='python',header=1)
    '''
    if not(args.destination == 'csv') and not(dropTables(cur)):
        exit(-1)
    if not(args.destination == 'csv') and not(createTables(cur)):
        exit(-1)
    if not (args.destination == 'csv'):
        conn.commit()
    '''
    try:
#       import_indicator(cur, indicators, indicatorstbname,args.destination)
#       import_relation(cur, relations, indic_indictbname)
        import_value(cur, values, valuetbname, args.destination)
 #       import_contribution(None, headercontrib, contributions, contribtbname, args.destination)
    except Exception as e:
        print('Error importing table. Error: {0}'.format(str(e)))
#    conn.close()
    print('Done!')
