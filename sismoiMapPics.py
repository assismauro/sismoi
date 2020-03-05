import os
import psycopg2
from PIL import Image
import struct

import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from matplotlib.colors import ListedColormap

sqlvalues = '''
select a.geom,b.value,
                  case 
                  when c.pessimist = 0 then
	                   case
		                    when b.value >= 0.0 and b.value <= 0.2 then '#F40000'
		                    when b.value >  0.2 and b.value <= 0.4 then '#FF8300'
		                    when b.value >  0.4 and b.value <= 0.6 then '#FFCD00'
		                    when b.value >  0.6 and b.value <= 0.8 then '#A9DE00'
		                    when b.value >  0.8 and b.value <= 1.0 then '#02C650'
		                    else '#ffffff'
	                   end
                   else
	                   case
		                    when b.value >= 0.0 and b.value <= 0.2 then '#02C650'
		                    when b.value >  0.2 and b.value <= 0.4 then '#A9DE00'
		                    when b.value >  0.4 and b.value <= 0.6 then '#FFCD00'
		                    when b.value >  0.6 and b.value <= 0.8 then '#FF8300'
		                    when b.value >  0.8 and b.value <= 1.0 then '#F40000'
	                    	else '#ffffff'
                    	end
                    end as color
               from county a
               inner join value b
                 on a.id = b.county_id 
               inner join indicator c
                 on b.indicator_id = c.id
               where b.indicator_id = {0}
                 and scenario_id is null
'''

conn = psycopg2.connect(dbname="impactaclima", user="postgres", password="ebaeba18")

dpi = 12.8214
sismoi_colormap = ListedColormap(['#00cc00', '#aecc23', '#ffcc33', '#f18c2b', '#d7191b'], name='sismoi')

def crop(image_path, coords, saved_location):
    image_obj = Image.open(image_path)
    cropped_image = image_obj.crop(coords)
    cropped_image.save(saved_location)

def plotIndicadorSemiarido(indicator_id,title,pessimist):
    f, ax = plt.subplots(1, figsize=(20, 20), frameon=False)
    ax.set_axis_off()
    plt.axis('off')
    f.set_size_inches(160, 160)

    values=gpd.read_postgis(sqlvalues.format(indicator_id), conn,
                     geom_col='geom',
                     coerce_float=False)
    if len(values) == 0:
        return
    gpd.plotting.plot_polygon_collection(ax=ax, geoms=values['geom'], color=values['color'], linewidth=8.0,
                                     edgecolor='#d7d7d7')
    minx, miny, maxx, maxy = values.total_bounds
    r = 1.5
#    ax.set_title(title, fontsize=20)
#    f.suptitle(title, fontsize=20)
    dx = maxx - minx
    dy = maxy - miny
    ax.set_xlim(minx - dx / r, maxx + dx / r)
    ax.set_ylim(miny - dy / r, maxy + dy / r)

#    legenda = ax.get_legend()

#    ax.legend(title='Legenda')

    fname = r'd:\temp\sismoi\{2}-{0}_{1}.png'.format(title.replace(' ', '_').replace('/','_'),'1-verde' if pessimist == 0.0 else '1-vermelho',indicator_id)
    f.savefig(fname, facecolor='#8fc8ff', pad_inches=0, bbox_inches='tight', dpi=dpi)
    plt.close(f)
    print('{0} salvo.'.format(fname))
    crop(fname, (10, 225, 1500, 1175), fname)

if __name__ == '__main__':
    indicators = pd.read_sql('select id,title,pessimist from indicator where id > 0 order by id',conn)
    for index, row in indicators.iterrows():
        plotIndicadorSemiarido(row['id'],row['title'],row['pessimist'])
        print()
    conn.close()
    print('TheEnd')
