# https://pythonhosted.org/setuptools/setuptools.html#namespace-packages
__import__('pkg_resources').declare_namespace(__name__)

import mapzen.whosonfirst.pip
import mapzen.whosonfirst.placetypes
import shapely.geometry
import logging
import requests
import json
from mapzen.whosonfirst.utils import id2relpath

def append_hierarchy_and_parent_pip(feature, **kwargs):
    return append_hierarchy_and_parent(feature, **kwargs)

def append_hierarchy_and_parent(feature, **kwargs):

    props = feature['properties']
    placetype = props['wof:placetype']

    lat = props.get('lbl:latitude', None)
    lon = props.get('lbl:longitude', None)

    if not lat or not lon:
        lat = props.get('geom:latitude', None)
        lon = props.get('geom:longitude', None)

    if not lat or not lon:

        shp = shapely.geometry.asShape(feature['geometry'])
        coords = shp.centroid

        lat = coords.y
        lon = coords.x

    endpoint = kwargs.get('data_endpoint', 'https://whosonfirst.mapzen.com/data/')
    reverse_geocoded = get_reverse_geocoded(lat, lon, placetype)
    props['wof:parent_id'] = get_parent(reverse_geocoded, lat, lon)
    props['wof:hierarchy'] = get_hierarchy(reverse_geocoded, data_endpoint)

    feature['properties'] = props

    return True

def get_reverse_geocoded(lat, lon, placetype):

    # see also : https://github.com/whosonfirst/go-whosonfirst-pip#wof-pip-server
    pip = mapzen.whosonfirst.pip.server(hostname='pip.mapzen.com', scheme='https', port=443)

    pt = mapzen.whosonfirst.placetypes.placetype(placetype)

    _hiers = []
    _rsp = []

    for parent in pt.parents():

        parent = str(parent)

        # TO DO: some kind of 'ping' to make sure the server is actually
        # there... (20151221/thisisaaronland)

        # print "%s : %s,%s" % (parent, lat, lon)

        try:
            rsp = pip.reverse_geocode(lat, lon, parent)
        except Exception, e:
            logging.warning("failed to reverse geocode %s @%s,%s" % (parent, lat, lon))
            continue

        if len(rsp):
            _rsp = rsp
            break

    return _rsp

def get_parent(reverse_geocoded, lat, lon):

    parent_id = -1

    if len(reverse_geocoded) == 0:
        logging.warning("Failed to reverse geocode any parents for %s, %s" % (lat, lon))
    elif len(reverse_geocoded) > 1:
        logging.warning("Multiple reverse geocoding possibilities %s, %s" % (lat, lon))
    else:
        parent_id = reverse_geocoded[0]['Id']

    return parent_id

def get_hierarchy(reverse_geocoded, data_endpoint):

    _hiers = []

    for r in reverse_geocoded:
        id = r['Id']
        #pf = mapzen.whosonfirst.utils.load(kwargs.get('data_root', ''), id)
        rsp = requests.get(data_endpoint + id2relpath(id))
        pf = json.loads(rsp.content)
        pp = pf['properties']
        ph = pp['wof:hierarchy']
        placetype = pp['wof:placetype']

        for h in ph:

            h[ "%s_id" % placetype ] = id

            # k = "%s_id" % placetype
            # h[k] = wofid
            _hiers.append(h)

    return _hiers
