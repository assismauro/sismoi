import psycopg2 as pg
from pandas._libs.properties import cache_readonly


def createTable(cursor):
    cursor.execute('DROP TABLE IF EXISTS cadastroimoveis')
    cursor.execute('''CREATE TABLE "public"."cadastroimoveis" ( 
        "uf" integer );
        ALTER TABLE cadastroimoveis ADD COLUMN id BIGSERIAL PRIMARY KEY;
        SELECT AddGeometryColumn ('cadastroimoveis','geom',5880,'POINT',2);
    ''')

def dms2dd(coord):
    degrees, minutes, seconds, direction = coord.split()
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
    if direction == 'O' or direction == 'S':
        dd *= -1
    return dd;

if __name__ == '__main__':
    conn=pg.connect(host='127.0.0.1',user='sismoi',password='142857',database='sismoi')
    i=0
    j=0
    cur = conn.cursor()
    createTable(cur)
    error=[]
    with open(r'G:\SISMOI\DADOS\CadastroNacionalEnderecos\Cadastro_Nacional_de_Enderecos_Fins_Estatisticos\Cadastro_Nacional_de_Enderecos_Fins_Estatisticos.txt', encoding="ISO-8859-1") as infile:
        for line in infile:
            try:
                i+=1
                sLat=line[321:336].strip()
                sLong=line[336:351].strip()
                if (sLat != '') or (sLong != ''):
                    uf=int(line[0:2])
                    lat=dms2dd(sLat)
                    long=dms2dd(sLong)
                    sql='INSERT INTO cadastroimoveis(uf,geom) VALUES ({2},ST_Transform(ST_SetSRID(ST_MakePoint({0}, {1}), 4326),5880))'.format(long,lat,uf)
                    cur.execute(sql)
                    if (j % 50000) == 0:
                        conn.commit()
                    j+=1
                if (i % 50000) == 0:
                    print(i,j)
            except Exception as e:
                error.append(e)
    conn.commit()
    print(error)
    print(i,j)
