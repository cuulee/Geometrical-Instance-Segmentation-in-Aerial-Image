import numpy as np
import math, sys
import matplotlib.pyplot as plt
d = np.load('../DataPreparation/BuildingList%s.npy' % sys.argv[1]).item()
angles = []
for bid in d:
	polygon = d[bid]
	polygon = [((x - 8.43) * 100000, (y - 47.38) * 100000) for x, y in polygon]
	s = 0
	for (x1, y1), (x2, y2) in zip(polygon, polygon[1: ] + [polygon[0]]):
		s += x1 * y2 - x2 * y1
	if s < 0:
		polygon.reverse()
	for (x0, y0), (x1, y1), (x2, y2) in zip([polygon[-1]] + polygon[: -1], polygon, polygon[1: ] + [polygon[0]]):
		s = 0
		s += x0 * y1 - x1 * y0
		s += x1 * y2 - x2 * y1
		s += x2 * y0 - x0 * y2
		a, b = (x1 - x0, y1 - y0), (x2 - x1, y2 - y1)
		cos = min((a[0] * b[0] + a[1] * b[1]) / (math.sqrt(a[0] ** 2 + a[1] ** 2) * math.sqrt(b[0] ** 2 + b[1] ** 2)), 0.99999)
		if s >= 0:
			angle = 180 - math.degrees(math.acos(cos))
		else:
			angle = 180 + math.degrees(math.acos(cos))
		angles.append(angle)
angles.sort()
plt.hist(angles, bins = [i for i in range(0, 365, 5)])
plt.xlim(xmin = 0, xmax = 360)
plt.xlabel('Angle Degree', fontname = 'Arial')
plt.ylabel('Number of Angles', fontname = 'Arial')
plt.xticks(np.arange(0, 370, step = 30), fontname = 'Arial')
plt.yticks(fontname = 'Arial')
plt.title('Polygon Interior Angle Distribution in %s' % sys.argv[1], fontname = 'Arial')
plt.show()
