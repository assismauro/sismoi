from flask import Flask
from flask import jsonify
import psycopg2

try:
    conn = psycopg2.connect("dbname='sismoi' user='postgres' host='127.0.0.1' password='142857'")
    cur = conn.cursor()
except:
    print("I am unable to connect to the database")
    exit()

app = Flask(__name__)

@app.route("/sismoi/getHierarchy",methods=['GET'])
def getHierarchy():
    cur.execute("""select a.*,b.indicador_id_mestre from indicador a
                   left join indicador_indicador b
                   on b.indicador_id_detalhe = a.id""")
    return jsonify ([{'id': row[0], 'nome' : row[1], 'titulo' : row[2], 'sigla' : row[3], 'descricao_simples' : row[4],
                      'descricao_completa' : row[5], 'equacao' : row[6], 'anos' : row[7], 'nivel' : row[8], 'indicador_id_mestre' : row[9]} for row in cur.fetchall()])

# Teste de passagem de parâmetros no serviço
@app.route('/sismoi/getACity/<id>',methods=['GET'])
def getACity(id):
    cur.execute("""SELECT * from test_webservice where id = {0}""".format(id))
    return jsonify ([{'id': row[0], 'name' : row[1], 'value' : row[2]} for row in cur.fetchall()])

if __name__ == "__main__":
  app.run(host='127.0.0.1',port=5000, debug=True)
from flask import Flask
from flask import jsonify
import psycopg2

try:
    conn = psycopg2.connect("dbname='sismoi' user='postgres' host='127.0.0.1' password='142857'")
    cur = conn.cursor()
except:
    print("I am unable to connect to the database")
    exit()


