import os
import psycopg2
from PIL import Image
import struct

import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.colors import ListedColormap

nomesIndicadores = (
    'Índice de Impacto das Mudanças Climáticas (2015)',
    'Índice de Impacto das Mudanças Climáticas (2030) - Cenário Otimista',
    'Índice de Impacto das Mudanças Climáticas (2030) - Cenário Pessimista',
    'Índice de Impacto das Mudanças Climáticas (2050) - Cenário Otimista',
    'Índice de Impacto das Mudanças Climáticas (2050) - Cenário Pessimista',
    'Índice de Vulnerabilidade às Mudanças Climáticas (2015)',
    'Índice de Exposição às Mudanças Climáticas (2015)', 'Índice Climático de Seca (2015)',
    'Índice Climático de Seca (2030) - Cenário Otimista',
    'Índice Climático de Seca (2030) - Cenário Pessimista', 'Índice Climático de Seca (2050) - Cenário Otimista',
    'Índice Climático de Seca (2050) - Cenário Pessimista', 'Índice de Sensibilidade às Mudanças Climáticas (2015)',
    'Índice de Capacidade de Resposta às Mudanças Climáticas (2015)', 'Eficiência no uso da água (2015)',
    'Reuso da água (2013)', 'Índice de perdas na distribuição do sistema de abastecimento de água (2010)',
    'Consumo médio per capita de água (2010)'
)

colunasIndicadores = ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r')

conn = psycopg2.connect(dbname="sismoi", user="sismoi", password="142857")
f, ax = plt.subplots(1, figsize=(20, 20), frameon=False)
ax.set_axis_off()
plt.axis('off')
dpi = 12.8214
sismoi_colormap = ListedColormap(['#00cc00', '#aecc23', '#ffcc33', '#f18c2b', '#d7191b'], name='sismoi')

f.set_size_inches(160, 160)

def plotAmericadoSul():
    sa = gpd.read_postgis(
        "select * from americadosul", conn,
        geom_col='geom',
        coerce_float=False)
    cmap = ListedColormap(['#cccccc'], name='gray')
    sa.plot(cmap=cmap, ax=ax)

def plotBrasil():
    brasil = gpd.read_postgis(
        "select * from brasil", conn,
        geom_col='geom',
        coerce_float=False)
    cmap = ListedColormap(['#e4e4e4'], name='gray')
    brasil.plot(cmap=cmap, ax=ax)

def crop(image_path, coords, saved_location):
    image_obj = Image.open(image_path)
    cropped_image = image_obj.crop(coords)
    cropped_image.save(saved_location)

def start():
    plotAmericadoSul()
    plotBrasil()

def plotSemiArido():
    start()
    semiarido = gpd.read_postgis(
        'select * from municipio_ibge_2010 where semiarido',
        conn,
        geom_col='geom5880',
        coerce_float=False)
    semiarido.plot(color='white',
               linewidth=3.0, edgecolor='#d7d7d7',
               categorical=False, ax=ax)
    minx, miny, maxx, maxy = semiarido.total_bounds
    r = 1.5
    dx = maxx - minx
    dy = maxy - miny
    ax.set_xlim(minx - dx / r, maxx + dx / r)
    ax.set_ylim(miny - dy / r, maxy + dy / r)

    fname = r'G:\temp\sismoi\semiarido.png'
    f.savefig(fname, facecolor='#8fc8ff', pad_inches=0, bbox_inches='tight', dpi=dpi)
    print('{0} salvo.'.format(fname))
    crop(fname, (10, 225, 1500, 1175), fname)

def plotBorderCeara():
    ce = gpd.read_postgis(
        'select * from ceara_borda', conn,
        geom_col='geom',
        coerce_float=False)
    ce.plot(facecolor="none",
            edgecolor='#999999', lw=10, ax=ax)

def plotCearaFortaleza():
    start()
    ceara = gpd.read_postgis(
        'select geom from vw_indicadores_ceara',
        conn,
        geom_col='geom',
        coerce_float=False)
    fortaleza = gpd.read_postgis(
        "select geom5880 from vw_indicadores_ceara where nm_municip = 'FORTALEZA'",
        conn,
        geom_col='geom5880',
        coerce_float=False)
    ceara.plot(color='white',
               linewidth=3.0, edgecolor='#d7d7d7',
               categorical=False, ax=ax)
    fortaleza.plot(color='#2c7bb6',
               linewidth=3.0,edgecolor='#d7d7d7',
               categorical=False, ax=ax)
    plotBorderCeara()
    minx, miny, maxx, maxy = ceara.total_bounds
    r = 1.5
    dx = maxx - minx
    dy = maxy - miny
    ax.set_xlim(minx - dx / r, maxx + dx / r)
    ax.set_ylim(miny - dy / r, maxy + dy / r)
    fname = r'G:\temp\sismoi\cearafortaleza.png'
    f.savefig(fname, facecolor='#8fc8ff', pad_inches=0, bbox_inches='tight', dpi=dpi)
    print('{0} salvo.'.format(fname))
    crop(fname, (10, 225, 1500, 1175), fname)

def plotIndicadoresMunicipiosCeara():
    start()
    for nome, coluna in zip(nomesIndicadores, colunasIndicadores):
        plotBorderCeara()
        sql='''select nm_municip,
             case 
                when {0} >= 0.0 and {0} <= 0.2 then 1
                when {0} >  0.2 and {0} <= 0.4 then 2
                when {0} >  0.4 and {0} <= 0.6 then 3
                when {0} >  0.6 and {0} <= 0.8 then 4
                when {0} >  0.8 and {0} <= 0.2 then 5
                else -1
               end as value,
               case
                when {0} >= 0.0 and {0} <= 0.2 then '#00cc00'
                when {0} >  0.2 and {0} <= 0.4 then '#aecc23'
                when {0} >  0.4 and {0} <= 0.6 then '#ffcc33'
                when {0} >  0.6 and {0} <= 0.8 then '#f18c2b'
                when {0} >  0.8 and {0} <= 0.2 then '#d7191b'
                else '#ffffff'
               end as color, geom, {1}
               from vw_indicadores_ceara --where {0} <= 0.4'''.format(coluna if coluna != 'p' else '1-{0}'.format(coluna),coluna)
        indic = gpd.read_postgis(sql, conn,
            geom_col='geom',
            coerce_float=False)
#        gpd.plotting.plot_polygon_collection(ax=ax, geoms=indic['geom'], color=indic['color'], linewidth=8.0, edgecolor='#d7d7d7')
        gpd.plotting.plot_polygon_collection(ax=ax, geoms=indic['geom'], color=indic['color'], linewidth=8.0, edgecolor='#d7d7d7')

        indic.apply(lambda x: ax.annotate(s=x[coluna], xy=x.geom.centroid.coords[0], ha='center', fontsize=40), axis=1)

        minx, miny, maxx, maxy = indic.total_bounds
        r = 1.5
        dx=maxx - minx
        dy=maxy - miny
        ax.set_xlim(minx-dx/r, maxx+dx/r)
        ax.set_ylim(miny-dy/r, maxy+dy/r)
#        cbar = f.colorbar(ax, ticks=[0, 0.2, 0.4, 0.6, 0.8, 1.0], orientation='horizontal')

        fname = r'G:\temp\sismoi\{0}.png'.format(nome.replace(' ', '_'))
        f.savefig(fname, facecolor='#8fc8ff', pad_inches=0, bbox_inches='tight', dpi=dpi)
        print('{0} salvo.'.format(fname))
        crop(fname, (10, 225, 1500, 1175), fname)
        break

if __name__ == '__main__':
    plotIndicadoresMunicipiosCeara()
#    plotSemiArido()
#    plotCearaFortaleza()
    conn.close()
    print('TheEnd')

