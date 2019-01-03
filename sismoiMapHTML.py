import os
import folium
import branca.colormap as cm
# from folium.plugins import MiniMap
from folium.features import DivIcon
import json
from branca.element import Template, MacroElement

colorMap = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']

nomesIndicadores = [
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
]

colunasIndicadores = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r']

def getLegend(indicador,colorMap):
    return '''
        {{% macro html(this, kwargs) %}}

        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>SISMOI</title>
          <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

          <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
          <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>

          <script>
          $( function() {{
            $( "#maplegend" ).draggable({{
                            start: function (event, ui) {{
                                $(this).css({{
                                    right: "auto",
                                    top: "auto",
                                    bottom: "auto"
                                }});
                            }}
                        }});
        }});

          </script>
        </head>
        <body>


        <div id='maplegend' class='maplegend' 
            style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
             border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>

        <div class='legend-title'>{0}</div>
        <div class='legend-scale'>
          <ul class='legend-labels'>
            <li><span style='background:{1};opacity:0.7;'></span>Péssimo</li>
            <li><span style='background:{2};opacity:0.7;'></span>Ruim</li>
            <li><span style='background:{3};opacity:0.7;'></span>Médio</li>
            <li><span style='background:{4};opacity:0.7;'></span>Bom</li>
            <li><span style='background:{5};opacity:0.7;'></span>Muito bom</li>        
          </ul>
        </div>
        </div>

        </body>
        </html>

        <style type='text/css'>
          .maplegend .legend-title {{
            text-align: left;
            margin-bottom: 5px;
            font-weight: bold;
            font-size: 90%;
            }}
          .maplegend .legend-scale ul {{
            margin: 0;
            margin-bottom: 5px;
            padding: 0;
            float: left;
            list-style: none;
            }}
          .maplegend .legend-scale ul li {{
            font-size: 80%;
            list-style: none;
            margin-left: 0;
            line-height: 18px;
            margin-bottom: 2px;
            }}
          .maplegend ul.legend-labels li span {{
            display: block;
            float: left;
            height: 16px;
            width: 30px;
            margin-right: 5px;
            margin-left: 0;
            border: 1px solid #999;
            }}
          .maplegend .legend-source {{
            font-size: 80%;
            color: #777;
            clear: both;
            }}
          .maplegend a {{
            color: #777;
            }}
        </style>
        {{% endmacro %}}'''.format(indicador, *colorMap)


'''
def getColorPoly(feature):
    indicador = 'h'
    i = int(feature['properties'][indicador] * 10) % 5
    return colorMap[i]
'''

def map(pIndicador):
    indicador = pIndicador
    geo_json_data = json.load(open(r'G:\SISMOI\DADOS\vw_indicadores_ceara_simplified100_2.geojson'), encoding='utf8')


    # ,tiles='Stamen Terrain', tiles='OpenStreetMap'
    m = folium.Map([-5, -41], zoom_start=7, tiles='OpenStreetMap',
                   control_scale=True)

    folium.GeoJson(
        geo_json_data,
        style_function=lambda feature: {
            'fillColor':
            colorMap[0] if (feature['properties'][colunasIndicadores[indicador]] > 0.0 and feature['properties'][colunasIndicadores[indicador]] <= 0.2) else
            colorMap[1] if (feature['properties'][colunasIndicadores[indicador]] > 0.2 and feature['properties'][colunasIndicadores[indicador]] <= 0.4) else
            colorMap[2] if (feature['properties'][colunasIndicadores[indicador]] > 0.4 and feature['properties'][colunasIndicadores[indicador]] <= 0.6) else
            colorMap[3] if (feature['properties'][colunasIndicadores[indicador]] > 0.6 and feature['properties'][colunasIndicadores[indicador]] <= 0.8) else
            colorMap[4],
            'color': '#d7d7d7',
            'weight': 1
        }

    ).add_to(m)

    macro = MacroElement()
    s = getLegend(nomesIndicadores[indicador],colorMap)
    macro._template = Template(s)

    m.get_root().add_child(macro)
    '''
    folium.map.Marker(
        [-5, -41],
        icon=DivIcon(
            icon_size=(150,36),
            icon_anchor=(0,0),
            html='<div style="font-size: 24pt">Test</div>',
            )
        ).add_to(m)
    '''

    m

    m.save(r'C:\inetpub\wwwroot\sismoi.html')

map(10)
print('TheEnd')