#!/usr/bin/python
import shapefile
from math import sqrt
#2011 Statistical Local Areas
datafile = "data/1270055001_sa1_2011_aust_shape/SA1_2011_AUST"
# 2006 CCDs
#datafile = "1259030002_cd06aqld_shape/CD06aQLD"
#Australian Electorates
#datafile = "national-esri-16122011/COM20111216_ELB_region"

def build_data():
  sf = shapefile.Reader(datafile)
  records = sf.records()
  shapes = sf.shapes()

  return (records, shapes)

# Load the data once.
(records, shapes) = build_data()

def coord_in_poly(x, y, points):
  n = len(points)
  inside = False
  p1x,p1y = points[0]

  for i in range(0, n+1):
    p2x,p2y = points[i%n]
    if y > min(p1y,p2y):
      if y <= max(p1y, p2y):
        if x <= max(p1x, p2x):
          if p1y != p2y:
            xints = (y-p1y)*(p2x-p1y)/(p2y-p1y)+p1x
          if p1x == p2x or x <= xints:
            inside = not inside
    p1x,p1y = p2x,p2y

  return inside

def dist_from_centroid(x, y, shape):
  [x0, y0, x1, y1] = shape.bbox
  (xc, yc) = ((x0+x1)/2, (y0+y1)/2)

  ## Manhattan distance, because it's fast
  #return abs(x - xc) + abs(y - yc)
  (dx, dy) = (x-xc, y-yc)
  return sqrt(dx*dx + dy*dy)

def coord_in_shape(x, y, shape):
  try:
    [x0, y0, x1, y1] = shape.bbox
  except:
    [x0, y0, x1, y1] = 0,0,0,0
  if x < x0 or x > x1 or y < y0 or y > y1:
    return False

  return coord_in_poly(x, y, shape.points)

def coord_to_census(y, x):
  poss = [si for si in range(0, len(shapes))
        if coord_in_shape(x, y, shapes[si])]

  #print "{0} candidates.".format(len(poss))
  if len(poss) == 0:
    poss = list(range(0, len(shapes)))

  if len(poss) == 1:
    e_id = poss[0]
  else:
    print ("I couldn't figure it out")
    print (y)
    print (x)
    print (poss)
    return None
    # Failed to decide: pick the closest center
    #(dist, e_id) = min([(dist_from_centroid(x, y, shapes[poss[pi]]), poss[pi])
                      #for pi in range(0, len(poss))])
  return records[e_id][2],records[e_id][1]

#def main():
    #lat=-31.670811
    #lon=115.695396
    #result = coord_to_census(lat,lon)
    #print result

#main()
