""" reference
https://github.com/gboeing/urban-data-science/blob/master/20-Accessibility-Walkability/pandana-accessibility-demo-simple.ipynb"""

import pandana
import pandas
import matplotlib.pyplot as plt
from pandana.loaders import osm
bbox = [30.08, -98.02, 30.52, -97.56]
#lat-long bounding box for austin
amenity = 'supermarket' #accessibility to this type of amenity
distance = 10000 #max distance in meters
# first download the points of interest corresponding to the specified amenity type
pois = osm.node_query(bbox[0], bbox[1], bbox[2], bbox[3], tags='"shop"="{}"'.format(amenity))
pois[['shop', 'name', 'lat', 'lon']].tail()

# query the OSM API for the street network within the specified bounding box
network = osm.network_from_bbox(bbox[0], bbox[1], bbox[2], bbox[3])
# identify nodes that are connected to fewer than some threshold of other nodes within a given distance
# do nothing with this for now, but see full example in other notebook for more
lcn = network.low_connectivity_nodes(impedance=1000, count=10, imp_name='distance')

# precomputes the range queries (the reachable nodes within this maximum distance)
# so, as long as you use a smaller distance, cached results will be used
network.precompute(distance + 1)

# initialize the underlying C++ points-of-interest engine
network.init_pois(num_categories=1, max_dist=distance, max_pois=7)

# initialize a category for this amenity with the locations specified by the lon and lat columns
network.set_pois(category='my_amenity', x_col=pois['lon'], y_col=pois['lat'])

# search for the n nearest amenities to each node in the network
access = network.nearest_pois(distance=distance, category='my_amenity', num_pois=7)

# keyword arguments to pass for the matplotlib figure
bbox_aspect_ratio = (bbox[2] - bbox[0]) / (bbox[3] - bbox[1])
fig_kwargs = {'facecolor':'w',
              'figsize':(10, 10 * bbox_aspect_ratio)}

# keyword arguments to pass for scatter plots
plot_kwargs = {'s':5,
               'alpha':0.9,
               'cmap':'viridis_r',
               'edgecolor':'none'}

# plot the distance to the nth nearest amenity
n = 1
bmap, fig, ax = network.plot(access[n], bbox=bbox, plot_kwargs=plot_kwargs, fig_kwargs=fig_kwargs)
ax.set_axis_bgcolor('k')
ax.set_title('Walking distance (m) to nearest {} around Austin'.format(amenity), fontsize=15)
# fig.savefig('images/accessibility-supermarket.png', dpi=200, bbox_inches='tight')
# plt.show()

# add to previous data
house_df = pandas.read_csv('Aus1.csv')
house_df[amenity] = ''

for i in range(len(house_df)):
    id = ((network.nodes_df['x'] - house_df.ix[i]['longitude']) ** 2 +
            (network.nodes_df['y'] - house_df.ix[i]['latitude']) ** 2).idxmin(axis=1)
    house_df.loc[i, amenity] = access.ix[id][1]
del house_df['Unnamed: 0']
house_df.to_csv('Aus2.csv')


