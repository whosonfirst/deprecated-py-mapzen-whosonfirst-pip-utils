# https://pythonhosted.org/setuptools/setuptools.html#namespace-packages
__import__('pkg_resources').declare_namespace(__name__)

import mapzen.whosonfirst.pip
import mapzen.whosonfirst.placetypes
import shapely.geometry
import logging

def append_hierarchy_and_parent_pip(feature, **kwargs):

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
        
    # see also : https://github.com/whosonfirst/go-whosonfirst-pip#wof-pip-server
    pip = mapzen.whosonfirst.pip.proxy()

    pt = mapzen.whosonfirst.placetypes.placetype(placetype)
    
    _hiers = []
    _rsp = []
    
    for parent in pt.parents():
        
        parent = str(parent)

        # TO DO: some kind of 'ping' to make sure the server is actually
        # there... (20151221/thisisaaronland)
        
        # print "%s : %s,%s" % (parent, lat, lon)

        try:
            rsp = pip.reverse_geocode(parent, lat, lon)
        except Exception, e:
            logging.warning("failed to reverse geocode %s @%s,%s" % (parent, lat, lon))
            continue

        if len(rsp):
            _rsp = rsp
            break

    for r in _rsp:
        id = r['Id']
        pf = mapzen.whosonfirst.utils.load(kwargs.get('data_root', ''), id)
        pp = pf['properties']
        ph = pp['wof:hierarchy']
            
        for h in ph:

            # k = "%s_id" % placetype
            # h[k] = wofid
            _hiers.append(h)

    if len(_rsp) == 0:
        logging.warning("Failed to reverse geocode any parents for %s, %s" % (lat, lon))
        return False

    if len(_rsp) > 1:  
        logging.warning("Multiple reverse geocoding possibilities %s, %s" % (lat, lon))
        return False

    if len(_hiers) == 0:
        return True

    parent_id = _rsp[0]['Id']
    props['wof:parent_id'] = parent_id
    
    props['wof:hierarchy'] = _hiers
    feature['properties'] = props

    return True
