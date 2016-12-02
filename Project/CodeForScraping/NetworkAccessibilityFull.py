""" Reference
https://github.com/gboeing/urban-data-science/blob/master/20-Accessibility-Walkability/pandana-accessibility-demo-full.ipynb"""

import pandana, time, os, pandas as pd, numpy as np
from pandana.loaders import osm

# configure search at a max distance of 1 km for up to the 10 nearest points-of-interest
amenities = ['restaurant', 'bar', 'school', 'hospital']
distance = 5000
num_pois = 10
num_categories = len(amenities) + 1 #one for each amenity, plus one extra for all of them combined

# bounding box as a list of llcrnrlat, llcrnrlng, urcrnrlat, urcrnrlng
bbox = [30.08, -98.02, 30.52, -97.56]  #lat-long bounding box for austin

# configure filenames to save/load POI and network datasets
bbox_string = '_'.join([str(x) for x in bbox])
net_filename = 'data/network_{}.h5'.format(bbox_string)
poi_filename = 'data/pois_{}_{}.csv'.format('_'.join(amenities), bbox_string)

# keyword arguments to pass for the matplotlib figure
bbox_aspect_ratio = (bbox[2] - bbox[0]) / (bbox[3] - bbox[1])
fig_kwargs = {'facecolor':'w',
              'figsize':(10, 10 * bbox_aspect_ratio)}

# keyword arguments to pass for scatter plots
plot_kwargs = {'s':5,
               'alpha':0.9,
               'cmap':'viridis_r',
               'edgecolor':'none'}

# network aggregation plots are the same as regular scatter plots, but without a reversed colormap
agg_plot_kwargs = plot_kwargs.copy()
agg_plot_kwargs['cmap'] = 'viridis'

# keyword arguments to pass for hex bin plots
hex_plot_kwargs = {'gridsize':60,
                   'alpha':0.9,
                   'cmap':'viridis_r',
                   'edgecolor':'none'}

# keyword arguments to pass to make the colorbar
cbar_kwargs = {}

# keyword arguments to pass to basemap
bmap_kwargs = {}

# color to make the background of the axis
bgcolor = 'k'
start_time = time.time()
if os.path.isfile(poi_filename):
    # if a points-of-interest file already exists, just load the dataset from that
    pois = pd.read_csv(poi_filename)
    method = 'loaded from CSV'
else:
    # otherwise, query the OSM API for the specified amenities within the bounding box
    osm_tags = '"amenity"~"{}"'.format('|'.join(amenities))
    pois = osm.node_query(bbox[0], bbox[1], bbox[2], bbox[3], tags=osm_tags)

    # using the '"amenity"~"school"' returns preschools etc, so drop any that aren't just 'school' then save to CSV
    pois = pois[pois['amenity'].isin(amenities)]
    pois.to_csv(poi_filename, index=False, encoding='utf-8')
    method = 'downloaded from OSM'

print('{:,} POIs {} in {:,.2f} seconds'.format(len(pois), method, time.time() - start_time))

start_time = time.time()
if os.path.isfile(net_filename):
    # if a street network file already exists, just load the dataset from that
    network = pandana.network.Network.from_hdf5(net_filename)
    method = 'loaded from HDF5'
else:
    # otherwise, query the OSM API for the street network within the specified bounding box
    network = osm.network_from_bbox(bbox[0], bbox[1], bbox[2], bbox[3])
    method = 'downloaded from OSM'

    # identify nodes that are connected to fewer than some threshold of other nodes within a given distance
    lcn = network.low_connectivity_nodes(impedance=1000, count=10, imp_name='distance')
    network.save_hdf5(net_filename, rm_nodes=lcn)  # remove low-connectivity nodes and save to h5

print('Network with {:,} nodes {} in {:,.2f} secs'.format(len(network.node_ids), method, time.time() - start_time))

# precomputes the range queries (the reachable nodes within this maximum distance)
# so, as long as you use a smaller distance, cached results will be used
network.precompute(distance + 1)

# initialize the underlying C++ points-of-interest engine
network.init_pois(num_categories=num_categories, max_dist=distance, max_pois=num_pois)

# initialize a category for all amenities with the locations specified by the lon and lat columns
network.set_pois(category='all', x_col=pois['lon'], y_col=pois['lat'])


# searches for the n nearest amenities (of all types) to each node in the network
all_access = network.nearest_pois(distance=distance, category='all', num_pois=num_pois)

# it returned a df with the number of columns equal to the number of POIs that are requested
# each cell represents the network distance from the node to each of the n POIs
print('{:,} nodes'.format(len(all_access)))

# initialize each amenity category with the locations specified by the lon and lat columns
for amenity in amenities:
    pois_subset = pois[pois['amenity']==amenity]
    network.set_pois(category=amenity, x_col=pois_subset['lon'], y_col=pois_subset['lat'])

# distance to the nearest restaurant
for amenity in amenities:
        access = network.nearest_pois(distance=distance, category=amenity, num_pois=num_pois)
        bmap, fig, ax = network.plot(access[1], bbox=bbox, plot_kwargs=plot_kwargs,
                                     fig_kwargs=fig_kwargs, bmap_kwargs=bmap_kwargs, cbar_kwargs=cbar_kwargs)
        ax.set_axis_bgcolor(bgcolor)
        ax.set_title('Walking distance (m) to nearest'+amenity+'around Austin', fontsize=15)
        fig.savefig('images/accessibility '+amenity+' austin1.png', dpi=200, bbox_inches='tight')

# add to previous data
house_df = pd.read_csv('Aus.csv')
for amenity in amenities:
    house_df[amenity] = ''
    access = network.nearest_pois(distance=distance, category=amenity, num_pois=num_pois)
    for i in range(len(house_df)):
        id = ((network.nodes_df['x'] - house_df.ix[i]['longitude']) ** 2 +
             (network.nodes_df['y'] - house_df.ix[i]['latitude']) ** 2).idxmin(axis=1)
        house_df.loc[i, amenity] = access.ix[id][1]
house_df.to_csv('Aus1.csv')




