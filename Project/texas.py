import shapefile
import pandas
import scipy
from bokeh.models.widgets import Button
from bokeh.io import output_file, show, vform
from bokeh.layouts import column,row,layout
from bokeh.io import show
from bokeh.plotting import *
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    GMapPlot, GMapOptions, Select,OpenURL,TapTool,TextInput, SaveTool,Legend,
    ColumnDataSource, Circle, DataRange1d, PanTool, WheelZoomTool, BoxSelectTool,Slider,CustomJS
)
from bokeh.plotting import figure
from bokeh.palettes import Viridis6 as palette
from bokeh.models import Label
from random import randint
import pickle


##get texas pieces

def getParts(shapeObj):
    points = []

    num_parts = len(shapeObj.parts)
    end = len(shapeObj.points) - 1
    segments = list(shapeObj.parts) + [end]

    for i in range(num_parts):
        points.append(shapeObj.points[segments[i]:segments[i + 1]])

    return points


# Return a dict with three elements
#        - state_name
#        - total_area
#        - list of list representing latitudes
#        - list of list representing longitudes
#
#  Input: State Name & ShapeFile Object

def getDict(city, shapefile):
    cityDict = {city: {}}
    rec = []
    shp = []
    points = []

    # Select only the records representing the
    # "city" and discard all other
    for i in shapefile.shapeRecords():
        if i.record[4].upper() == city:
            rec.append(i.record)
            shp.append(i.shape)
            #    total_area = sum( [float(i[0]) for i in rec] ) / (1000*1000)
    for j in shp:
        for i in getParts(j):
            points.append(i)
        #
        #	  # Prepare the dictionary
        #	  # Seperate the points into two separate lists of lists (easier for bokeh to consume)
        #	  #      - one representing latitudes
        #	  #      - second representing longitudes
        #
        lat = []
        lng = []
        for i in points:
            lat.append([j[0] for j in i])
            lng.append([j[1] for j in i])
        #
        #
        cityDict[city]['lat_list'] = lat
        cityDict[city]['lng_list'] = lng
    # stateDict[state_name]['total_area'] = total_area
    return cityDict


def texas():
    ## start by finding the states in Texas
    zipcodes = pandas.read_csv('zipcodes.csv')
    tx_city = list(set(zipcodes.City[zipcodes.State == 'TX']))
    return tx_city


def shapedata(city):
    ## read shape files and generate data
    dat = shapefile.Reader(r"C:\Users\qiann\Desktop\CO project Visuallization\\texas\\tl_2013_48_place")
    areas = {}
    tx_city = [city]
    for city in tx_city:
        data = getDict(city, dat)
        if data[city] != {}:
            areas[city] = {'lats': data[city]['lat_list'], 'lons': data[city]['lng_list'],
                                 'city': city}

    if areas != {}:
        import pickle
        output = open('texas_shape_'+city+'.txt', 'ab+')
        pickle.dump(areas, output)
        output.close()
    return areas

def plot(city,p):

    output = open('texas_shape_'+city+'.txt','rb')
    shp = pickle.load(output)
    output.close()
    shp = shp[city]


    #    City_names = [i['city'] for i in shp.values()]
    zip_code = [city for i in shp.values()]
    zip_lat = shp['lats']
    zip_lon  = shp['lons']
    x_c = (max(max(zip_lat))+min(min(zip_lat)))/2
    y_c = (max(max(zip_lon)) + min(min(zip_lon))) / 2
    r = len(palette)
    colors = [palette[randint(0,r-1)] for i in shp['lats']]
    source = ColumnDataSource(data=dict(x=zip_lat,y=zip_lon,zip_codes = zip_code, color = colors))
    p.patches('x', 'y', source=source,
    fill_color='black', fill_alpha=1,
    line_color="black", line_width=1)
    # cite = Label(x=x_c,y=y_c,x_units = 'data', text = city ,render_mode='css',
    #   border_line_color='white', border_line_alpha=1.0,
    #   background_fill_color='white', background_fill_alpha=1.0, text_font_size = "2pt")
    # p.add_layout(cite)

    ##plotting congress point
    # cr = p.circle(x = 30.274524,y = -97.740382,size=12,color='red')
    # toolss = ["pan,wheel_zoom,box_zoom,reset,previewsave"]
    return p




def create_plot(fn):
    output_file(fn+'.html',title='Austin Home Prices')
    map_options = GMapOptions(lat=30.29, lng=-97.73, map_type="roadmap", zoom=11)
    plot = GMapPlot(
        x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options, title="Austin",
        api_key='AIzaSyDfPR-VHUVIr3veDt-GKNZOpHyew6TER6Q'
    )
    return plot

def show_plot(p):
    show(p)

def shape_files():
    zipcodes = pandas.read_csv('zipcodes.csv')
    cities = list(set(zipcodes.City[zipcodes.State == 'TX']))
    for c in cities:
        try:
            shapedata(c)
        except IOError:
            print c+'not valid\n'
            pass

def plot_tx(p):
    from bokeh.sampledata.us_states import data as states
    xs = [states['TX']['lons']]
    ys = [states['TX']['lats']]
    source  = ColumnDataSource(data=dict(
        x=xs,
        y=ys
    ))
    p.patches('x','y',source = source, fill_color = 'black',fill_alpha=1,line_color = 'white', line_width=8)

    return p
def plot_circle(plot,city):

    source1 = read_sale_data(city)
    source2 = read_sale_data(city)

    callback = CustomJS(args=dict(s1=source1, s2=source2), code="""
            var data1 = s1.data;
            var data2 = s2.data;
            var f = rooms.value;
            var pri = prices.get('value');
            var bar = baths.get('value');
            var area = flarea.value;
            var max_area = marea.get('value')
            x1 = data1['xs'];
            y1 = data1['ys'];
            p1 = data1['price'];
            b1 = data1['beds'];
            z1 = data1['zips'];
            a1 = data1['adds'];
            cn1 = data1['city_name'];
            f1 = data1['floora'];
            ba1 = data1['bath'];
            c1 = data1['color'];
            leg1 = data1['leg'];
            x2 = [];
            y2 = [];
            p2 = [];
            b2 = [];
            z2 = [];
            a2 = [];
            cn2 = [];
            f2 = [];
            ba2 = [];
            c2  = [];
            leg2 = [];
            for (i = 0; i < x1.length; i++) {
                if (b1[i]>=f && p1[i]<=pri&&ba1[i]>=bar&&f1[i]>=area&&f1[i]<=max_area){
                  x2.push(x1[i]);
                  y2.push(y1[i]);
                  b2.push(b1[i]);
                  p2.push(p1[i]);
                  z2.push(z1[i]);
                  a2.push(a1[i]);
                  cn2.push(cn1[i]);
                  f2.push(f2[i]);
                  ba2.push(ba1[i]);
                  c2.push(c1[i]);
                  leg2.push(leg1[i]);
                }
            }

            data2['xs'] = x2;
            data2['ys'] = y2;
            data2['price'] = p2;
            data2['beds'] = b2;
            data2['color'] = c2;
            data2['zips'] = z2;
            data2['adds'] = a2;
            data2 ['city_name'] = cn2;
            data2 ['floora'] = f2;
            data2 ['bath'] = ba2;
            data2['leg'] = leg2
            s2.trigger('change');
        """)
    cr = Circle(x = 'xs',y =  'ys', fill_color='color', fill_alpha=0.8, size=6,line_color = 'white',line_alpha=0)
    circle = plot.add_glyph(source2, cr)
    # from bokeh.core.enums import LegendLocation
    # legend = Legend(items=[
    #     ("x: 300px, y: 150px (horizontal)", [circle]),
    # ], location=(300, 150), orientation="horizontal")
    # plot.add_layout(legend)

    # plot.add_glyph(source2, cr2)
    hover = HoverTool(tooltips="""
                <div>
                    <div>
                        <span style="font-size: 15px; color: #966;">Price</span>
                        <span style="font-size: 17px; font-weight: bold;">@price</span>
                    </div>
                    <div>
                        <span style="font-size: 15px; color: #966;">Address</span>
                        <span style="font-size: 17px; font-weight: bold;">@adds</span>
                    </div>
                    <div>
                        <span style="font-size: 15px; color: #966;">Bedrooms</span>
                        <span style="font-size: 17px; font-weight: bold;">@beds</span>
                    </div>
                    <div>
                        <span style="font-size: 15px; color: #966;">Bathrooms</span>
                        <span style="font-size: 17px; font-weight: bold;">@bath</span>
                    </div>
                    <div>
                        <span style="font-size: 15px; color: #966;">Area</span>
                        <span style="font-size: 17px; font-weight: bold;">@floora</span>
                    </div>
		    <div>
                        <span style="font-size: 15px; color: #966;">Color</span>
                        <span style="font-size: 17px; font-weight: bold;">@color</span>
                    </div>
                </div>
                """, point_policy='follow_mouse')
    pan = PanTool()
    wheel_zoom = WheelZoomTool()
    savet = SaveTool()
    plot.add_tools(hover,pan,wheel_zoom,savet)

    # room_slider = Slider(start=1, end=15, value=1, step=1, title="Minum Number of Bedrooms", callback=callback)
    # callback.args["rooms"] = room_slider
    room_select = Select(title='Minimum number of Bathrooms:', value='1',
                         options=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15'],
                         callback=callback)
    callback.args["rooms"] = room_select
    # price_slider = Slider(start=10000, end=20000000, value=1, step=100000, title="Max Prices", callback=callback)
    # callback.args["prices"] = price_slider
    price_input = TextInput(value="20000000", title="Max Price ($)", callback=callback)
    callback.args["prices"] = price_input
    bath_select = Select(title = 'Minimum number of Bathrooms:', value = '1', options = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15'],callback = callback)
    callback.args["baths"] = bath_select
    minarea_slider = Slider(start=100, end=10000, value=1, step=100, title="Min Floor Area (sqft):", callback=callback)
    callback.args["flarea"] = minarea_slider
    maxarea_slider = Slider(start=100, end=10000, value=10000, step=100, title="Max Floor Area (sqft):", callback=callback)
    callback.args["marea"] = maxarea_slider
    layouts = layout([room_select, bath_select,price_input],[maxarea_slider,minarea_slider],[plot])
    return layouts

def read_sale_data(city):##return a ColumnDataSource
    df= pandas.read_csv('sale.csv')
    df = df[df.city == city]
    cities = list(df.city.values)
    floorarea = list(df.floorarea.values)
    bathrooms = list(df.bathrooms.values)
    add = list(df.address.values)
    lat = list(df.latitude.values)
    lon = list(df.longitude.values)
    prices = list(df.price.values)
    p = []
    for i in prices:
        try:
            p.append(int(i))
        except ValueError:
            i = i.replace('K','000')
            p.append(int(i))
	
    prices = p
    bed = list(df.bedrooms.values)
    lzip = list(df.zipcode.values)
    color = []
    prange = []
    i=0
    while i < len(bed):
        if prices[i] <=900000:
            color.append('#6a6efc')
            prange.append('0~900000')
        elif prices[i]<=1200000:
            color.append('#383eff')
            prange.append('900000~1200000')
        elif prices[i]<=1400000:
            color.append('#6938ff')
            prange.append('1200000~1400000')
        elif prices[i]<=1600000:
            color.append('#dd38ff')
            prange.append('1400000~1600000')
        elif prices[i] <= 5000000:
            color.append('#ff388e')
            prange.append('1600000~50000000')
        else:
            color.append('#ff3838')
            prange.append('5000000+')
        i= i+1

    source = ColumnDataSource(data = dict(
        xs = lon,
        ys = lat,
        price = prices,
        beds = bed,
        zips = lzip,
        adds = add,
        city_name = cities,
        floora = floorarea,
        bath = bathrooms,
        color = color,
        leg = prange
    ))
    return source
def read_predict_data():
    df = pandas.read_csv('pred.csv')
    add = list(df.address.values)
    lat = list(df.latitude.values)
    lon = list(df.longitude.values)
    floora = list(df.floorarea.values)
    pri = list(df.price.values)
    est = list(df.pred.values)
    color = []
    alpha = []
    n = 0
    for i in range(len(lon)):
        if pri[i]-est[i]>=0:
            color.append('red')
            if abs(pri[i]-est[i])/pri[i] >= 0.2:
                n = n+1
                alpha.append(0.95)
            elif abs(pri[i]-est[i])/pri[i] >= 0.1:
                alpha.append(0.55)
            elif abs(pri[i]-est[i])/pri[i] >= 0.05:
                alpha.append(0.25)
            else:
                alpha.append(0.05)
        else:
            color.append('blue')
            if abs(pri[i] - est[i]) / pri[i] >= 0.2:
                n = n+1
                alpha.append(0.95)
            elif abs(pri[i] - est[i]) / pri[i] >= 0.1:
                alpha.append(0.55)
            elif abs(pri[i] - est[i]) / pri[i] >= 0.05:
                alpha.append(0.25)
            else:
                alpha.append(0.05)
    diff = []
    for i in range(len(pri)):
        diff.append(abs(pri[i] - est[i])/pri[i])



    source = ColumnDataSource(data = dict(
        xs = lon,
        ys = lat,
        floora = floora,
        price = pri,
        est = est,
        address = add,
        color = color,
        alpha = alpha,
        err = diff
    ))

    return source
def plot_pred(plot):

    source1 = read_predict_data()
    source2 = read_predict_data()

    callback = CustomJS(args=dict(s1=source1, s2=source2), code="""
            var data1 = s1.data;
            var data2 = s2.data;
            var pri = prices.get('value');
            var area = flarea.value;
            var max_area = marea.get('value')
            var ero = error.value;
            x1 = data1['xs'];
            y1 = data1['ys'];
            p1 = data1['price'];
            a1 = data1['address'];
            f1 = data1['floora'];
            es1 = data1['est'];
            c1 = data1['color'];
            al1 = data1['alpha']
            er1 = data1['err']
            x2 = [];
            y2 = [];
            p2 = [];
            a2 = [];
            f2 = [];
            es2 = []
            c2  = [];
            al2 = [];
            er2 = [];
            for (i = 0; i < x1.length; i++) {
                if (p1[i]<=pri&&f1[i]>=area&&f1[i]<=max_area&&er1[i]>=ero){
                  x2.push(x1[i]);
                  y2.push(y1[i]);
                  p2.push(p1[i]);
                  es2.push(es1[i]);
                  a2.push(a1[i]);
                  f2.push(f2[i]);
                  c2.push(c1[i]);
                  al2.push(al1[i]);
                  er2.push(er1[i]);
                }
            }

            data2['xs'] = x2;
            data2['ys'] = y2;
            data2['price'] = p2;
            data2['color'] = c2;
            data2['address'] = a2;
            data2 ['floora'] = f2;
            data2 ['est'] = es2;
            data2['alpha'] = al2;
            data2['err'] = er2;
            s2.trigger('change');
        """)
    cr = Circle(x = 'xs',y =  'ys', fill_color='color', fill_alpha='alpha', size=6,line_color = 'color',line_alpha='alpha')
    plot.add_glyph(source2, cr)
    hover = HoverTool(tooltips="""
                <div>
                    <div>
                        <span style="font-size: 15px; color: #966;">Address</span>
                        <span style="font-size: 17px; font-weight: bold;">@address</span>
                    </div>
                    <div>
                        <span style="font-size: 15px; color: #966;">Floor Area</span>
                        <span style="font-size: 17px; font-weight: bold;">@floora</span>
                    </div>
                    <div>
                        <span style="font-size: 15px; color: #966;">Price</span>
                        <span style="font-size: 17px; font-weight: bold;">@price</span>
                    </div>
                    <div>
                        <span style="font-size: 15px; color: #966;">Estimate</span>
                        <span style="font-size: 17px; font-weight: bold;">@est</span>
                    </div>
                    <div>
                        <span style="font-size: 15px; color: #966;">Error</span>
                        <span style="font-size: 17px; font-weight: bold;">@err</span>
                    </div>
                </div>
                """, point_policy='follow_mouse')
    pan = PanTool()
    wheel_zoom = WheelZoomTool()
    savet = SaveTool()
    plot.add_tools(hover,pan,wheel_zoom,savet)


    price_input = TextInput(value="20000000", title="Max Price ($)", callback=callback)
    callback.args["prices"] = price_input
    err_slider = Slider(start=0, end=1, value=0.2, step=0.05, title="Min Error:", callback=callback)
    callback.args["error"] = err_slider
    minarea_slider = Slider(start=100, end=10000, value=1, step=100, title="Min Floor Area (sqft):", callback=callback)
    callback.args["flarea"] = minarea_slider
    maxarea_slider = Slider(start=100, end=10000, value=10000, step=100, title="Max Floor Area (sqft):", callback=callback)
    callback.args["marea"] = maxarea_slider
    layouts = layout([ price_input,err_slider],[maxarea_slider,minarea_slider],[plot])
    return layouts

plots = create_plot('Ausin')
plots = plot_circle(plots,'Austin')
show(plots)
# plots = create_plot('Ausin Prediction')
# plots = plot_pred(plots)
# show(plots)

# lists= texas()
# lists.remove('NAS/JRB')
# for i in ['AUSTIN','HOUSTON','SAN ANTONIO','FORT WORTH','DALLAS','ARLINGTON','CORPUS CHRISTI','IRVING','GRAND PRAIRIE']:
# # for i in lists:
#     try:
#         plots = plot(i,plots)
#     except IOError:
#         print 'IO error'+i
#         pass


