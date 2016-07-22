# https://pythonhosted.org/setuptools/setuptools.html#namespace-packages
__import__('pkg_resources').declare_namespace(__name__)

import mapzen.whosonfirst.pip
import mapzen.whosonfirst.placetypes
import shapely.geometry
import logging

def reverse_geocoordinates(feature):

    props = feature['properties']

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

    return lat, lon

# please rename me
# test with 18.48361, -77.53057

def whereami(feature, **kwargs):

    raise Exception, "Please finish me"

    """
    lat, lon = reverse_geocoordinates(feature)    

    props = feature['properties']
    placetype = props['wof:placetype']

    # see also : https://github.com/whosonfirst/go-whosonfirst-pip#wof-pip-server
    pip = mapzen.whosonfirst.pip.proxy()

    pt = mapzen.whosonfirst.placetypes.placetype(placetype)

    for ancestor in pt.ancestors():

        ancestor = str(ancestor)

        # TO DO: some kind of 'ping' to make sure the server is actually
        # there... (20151221/thisisaaronland)
        
        # print "%s : %s,%s" % (parent, lat, lon)

        try:
            rsp = pip.reverse_geocode(ancestor, lat, lon)
        except Exception, e:
            logging.warning("failed to reverse geocode %s @%s,%s" % (parent, lat, lon))
            continue

        if len(rsp):
            _rsp = rsp
            break

        pass
    """

def append_hierarchy_and_parent_pip(feature, **kwargs):
    return append_hierarchy_and_parent(feature, **kwargs)

def append_hierarchy_and_parent(feature, **kwargs):

    props = feature['properties']
    placetype = props['wof:placetype']

    lat, lon = reverse_geocoordinates(feature)
 
    # see also : https://github.com/whosonfirst/go-whosonfirst-pip#wof-pip-server
    pip = mapzen.whosonfirst.pip.proxy()

    pt = mapzen.whosonfirst.placetypes.placetype(placetype)
    
    _hiers = []
    _rsp = []
    
    for parent in pt.parents():
        
        parent = str(parent)

        # TO DO: some kind of 'ping' to make sure the server is actually
        # there... (20151221/thisisaaronland)
        
        logging.debug("reverse geocode for %s w/ %s,%s" % (parent, lat, lon))

        print "reverse geocode for %s w/ %s,%s" % (parent, lat, lon)
        try:
            rsp = pip.reverse_geocode(parent, lat, lon)
        except Exception, e:
            logging.debug("failed to reverse geocode %s @%s,%s" % (parent, lat, lon))
            continue

        if len(rsp):
            _rsp = rsp
            break

    wofid = props.get('wof:id', None)

    possible = {}
    superseded = {}

    for r in _rsp:

        _id = r['Id']

        _feature = mapzen.whosonfirst.utils.load(kwargs.get('data_root', ''), _id)
        _props = _feature['properties']
        _superseded = _props['wof:superseded_by']

        if len(_superseded) == 0:
            possible[ _id ] = _feature
            continue

        # see this - there are two problems: 
        # 1. we are not checking for further superseded by
        # 2. we don't know whether the new record contains the point
        # 3. infinite loops

        for _sid in _superseded:
            _feature = mapzen.whosonfirst.utils.load(kwargs.get('data_root', ''), _sid)
            possible[ _sid ] = _feature

    import pprint

    print "superseded list"
    print pprint.pformat(superseded)

    print "possible results"
    print pprint.pformat(possible.keys())

    for _id, _superseded_by in superseded.items():

        for _sid in _superseded_by:

            print "%s has been superseded by %s - is it part of the result set" % (_id, _sid)
            if possible.has_key(_sid):
                print "YES"
                del(possible[_id])
                break

    print "possible results (after)"
    print pprint.pformat(possible.keys())

    for r in _rsp:
        id = r['Id']
        pf = mapzen.whosonfirst.utils.load(kwargs.get('data_root', ''), id)
        pp = pf['properties']
        ph = pp['wof:hierarchy']
            
        for h in ph:

            if wofid:
                h[ "%s_id" % placetype ] = wofid

            _hiers.append(h)

    parent_id = -1

    if len(_rsp) == 0:
        logging.debug("Failed to reverse geocode any parents for %s, %s" % (lat, lon))
    elif len(_rsp) > 1:  
        logging.debug("Multiple reverse geocoding possibilities %s, %s" % (lat, lon))
    else:
        parent_id = _rsp[0]['Id']

    props['wof:parent_id'] = parent_id
    
    props['wof:hierarchy'] = _hiers
    feature['properties'] = props

    return True
