import shapefile
#I'm putting my_ before all my variable names because I don't know what names were used in shapefile and
#I don't want to create a naming conflict

#here I create my list of points from a chosen shapefile
my_fileName = raw_input("name of shapefile containing points: ")
my_sf = shapefile.Reader(my_fileName)
my_shapes = my_sf.shapes()
my_points = []
for i in my_shapes:
	my_points.append(i.points[0])

#here I selected the upper, far left, bottom, and far right points

#until proven otherwise I will just assume that the first point is all of these
my_upperPoint = my_points[0]
my_leftPoint = my_points[0]
my_bottomPoint = my_points[0]
my_rightPoint = my_points[0]

#upper
for i in range(len(my_points)):
	if my_points[i][1] > my_upperPoint[1]:
		my_upperPoint = my_points[i]

#left
for i in range(len(my_points)):
	if my_points[i][0] < my_leftPoint[0]:
		my_leftPoint = my_points[i]

#bottom
for i in range(len(my_points)):
	if my_points[i][1] < my_bottomPoint[1]:
		my_bottomPoint = my_points[i]

#right
for i in range(len(my_points)):
	if my_points[i][0] > my_rightPoint[0]:
		my_rightPoint = my_points[i]

#script will start at upper and work its way through the list till it connects with itself
my_targets = []
my_targets.append(my_leftPoint)
my_targets.append(my_bottomPoint)
my_targets.append(my_rightPoint)
my_targets.append(my_upperPoint)

#now I create a list of pairs of points to be joined, going counter clockwise using the points I just found.
#if the two points connect and there is nothing on the right then they are a valid pair, otherwise try the
#points that would be cut off, starting with the point closest to the second point.

#takes the start point, the end point and the point to test, returns true if cuttof
def determineCutoff(my_pointA, my_pointB, my_pointC):
	#if any of the points are the same don't bother doing anything
	if my_pointA == my_pointB or my_pointA == my_pointC or my_pointB == my_pointC:
		return 0
	#if line is vertical I don't need to use a function I can just check if C is to the left or right of A
	if my_pointA[0] == my_pointB[0]:
		#if line is going down
		if my_pointA[1] > my_pointB[1]:
			if my_pointC[0] < my_pointA[0]:
				return 1
		#if line is going up
		if my_pointA[1] < my_pointB[1]:
			if my_pointC[0] > my_pointA[0]:
				return 1
		else:
			return 0			

	#slope 
	my_m = ((my_pointB[1] - my_pointA[1])/(my_pointB[0] - my_pointA[0]))
	#constant to add	
	my_s = (my_pointA[1] - (my_m * my_pointA[0]))
	#determines whether the right hand side is above or below the function y = (my_m * x) + my_s
	above = -1
	#check for above	
	if my_pointB[0] < my_pointA[0]:
		above = 1
	if my_pointB[0] > my_pointA[0]:
		above = 0
	if above == 1:
		if (my_pointC[1] > ((my_m * my_pointC[0]) + my_s)):
			return 1
	if above == 0:
		if (my_pointC[1] < ((my_m * my_pointC[0]) + my_s)):
			return 1
	#assuming nothing has returned 1 yet that means there is no cuttof
	return 0

my_border = []
my_border.append(my_upperPoint)

#choose cutoff it a recursive funtion that whittles away the list of cuttofs until it = 0
#takes the from point and a list of the points it cuts off and finds a point it doesn't cut off
def chooseCutoff(my_pointA, my_cutoffs):
	#starts by pulling off the first cutoff and making it the target and checking what it cuts off	
	my_tempTarget = my_cutoffs.pop(0)
	my_moreCutoffs = []
	for i in my_cutoffs:
		if determineCutoff(my_pointA, my_tempTarget, i):
			my_moreCutoffs.append(i)
	if len(my_moreCutoffs) == 0:
		return my_tempTarget
	else:
		return chooseCutoff(my_pointA, my_moreCutoffs)

#attaches the next item to border and if that item is the current target that target is removed from the list
def attachNext(my_points, my_border, my_target): 
	my_cutoffList = []	
	for i in my_points:		
		if determineCutoff(my_border[len(my_border)-1], my_targets[0], i):
			my_cutoffList.append(i)
	if len(my_cutoffList) == 0:
		my_border.append(my_target[0])
		del my_target[0]
	else:
		my_border.append(chooseCutoff(my_border[len(my_border)-1], my_cutoffList))

while len(my_targets) > 0:
	attachNext(my_points, my_border, my_targets)

my_listToWrite = []
my_listToWrite.append(my_border)
w = shapefile.Writer(shapefile.POLYLINE)
w.poly(parts=my_listToWrite)
w.field('Line','C','40')
w.record('1')
my_fileName = raw_input("save convex hull as: ")
w.save(my_fileName)
