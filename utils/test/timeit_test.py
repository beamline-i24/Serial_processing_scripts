import timeit
import itertools

def wrapper(func, *args, **kwargs):
    def wrapped():
	return func(*args, **kwargs)
    return wrapped

def function(list_of_x, list_of_y, list_of_z):
	list_xyz=[]
	for xyz in itertools.product(list_of_x, list_of_y,list_of_z):
    		list_xyz.append(xyz)
	return

list_of_x,list_of_y,list_of_z=range(100), range(100), range(100)
list_xyz=[]
for xyz in itertools.product(list_of_x, list_of_y,list_of_z):
    		list_xyz.append(xyz)
print len(list_xyz)
wrapped=wrapper(function, list_of_x, list_of_y, list_of_z)

print timeit.timeit(wrapped, number=1)
