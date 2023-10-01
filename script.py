#!/usr/bin/env python3

import re
import sys
from pygeodesy import ellipsoidalVincenty as ev
import sys

def decimal_to_dms(decimal, direction):
    degrees = int(decimal)
    minutes = int((decimal - degrees) * 60)
    seconds = round(((decimal - degrees) * 60 - minutes) * 60, 2)
    return f"{direction}{degrees:03d}.{minutes:02d}.{seconds:06.3f}"


def coord2es(tuple):
    lat = decimal_to_dms(tuple[0], 'N' if tuple[0] >= 0 else 'S')
    lon = decimal_to_dms(tuple[1], 'E' if tuple[1] >= 1 else 'W')
    return f"{lat}:{lon}"

def eprint(*args, **kwargs):
  pass
  #print(*args, file=sys.stderr, **kwargs)

fmt = re.compile(r"^([\d\.]+),\s+([\d\.]+)$")

def run(file, delta):
  source_points = []
  # The wanted distance between the tracer points in meters
  point_distance = float(delta) * 1852
  
  eprint(f"Point distance: {point_distance}")

  with open(file) as f:
    for line in f.readlines():
      coords = fmt.match(line).groups()
      source_points.append(ev.LatLon(float(coords[0]), float(coords[1])))

  source_points.reverse()

  source_point_count = len(source_points)
  # Tracer starts at the beginning
  tracer = source_points[0]
  # How much distance do we need to cover before putting down another point?
  remaining_point_distance = point_distance
  points = []
  lines = []
  current_line = [source_points[0]]
  drawing = False

  for next_index, source_point in enumerate(source_points, start=1):
    if next_index >= source_point_count:
      break
    
    next_source_point = source_points[next_index]
    bearing_to_next_source = source_point.initialBearingTo(next_source_point)
    distance_to_next_source = source_point.distanceTo(next_source_point)
    
    eprint(f"Next point: {next_index}, distance: {distance_to_next_source}, bearing: {bearing_to_next_source}")
    
    # Track distance travelled on current source point pair
    remaining_distance_to_next_source = distance_to_next_source
    while remaining_distance_to_next_source >= 0:
      eprint(f"Remaining distance to next: {remaining_distance_to_next_source}")
      
      if remaining_distance_to_next_source < remaining_point_distance:
        eprint("Remaining distance not sufficient on current segment, switching points.")
        tracer = next_source_point
        current_line.append(tracer)
        remaining_point_distance = remaining_point_distance - remaining_distance_to_next_source
        break
      
      # Travel distance to next source point, or wanted support point distance, whichever is smaller
      distance_to_go = min(distance_to_next_source, remaining_point_distance)
      tracer = tracer.destination(distance_to_go, bearing_to_next_source)
      # Note the travelled distance along the current source point's bearing
      remaining_distance_to_next_source = remaining_distance_to_next_source - distance_to_go
      
      # Did we travel far enough to warrant putting a point? If yes, tracer is our new point, reset remaining distance
      if distance_to_go >= remaining_point_distance:
        points.append(tracer)
        current_line.append(tracer)
        remaining_point_distance = point_distance

        # If the current line was to be drawn, save it, otherwise discard
        if drawing:
          lines.append(current_line)
        
        current_line = [tracer]
        drawing = not drawing
      else:
        # If not, mark the travelled distance as travelled
        remaining_point_distance = remaining_point_distance - distance_to_go

  #for point in points:
  #  lat, lon = point.latlon
  #  print (f"{lat}, {lon}")
  for line in lines:
    count = len(line)

    for idx, point in enumerate(line):
      if idx == count - 1:
        break

      print(f"LINE:{coord2es((point.lat, point.lon))}:{coord2es((line[idx + 1].lat, line[idx + 1].lon))}")


if __name__ == '__main__':
  run(sys.argv[1], sys.argv[2])