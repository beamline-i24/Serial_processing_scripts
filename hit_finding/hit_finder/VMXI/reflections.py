from dials.util.options import flatten_reflections
from dials.util.phil import ReflectionTableConverters
import os

converter = ReflectionTableConverters()

def get_num_reflections(strong,  directory):
    strong_reflections=flatten_reflections(get_reflection_list(directory, strong))
    strong_val=sum_list(strong_reflections)
    return float(strong_val) 

def get_reflection_list(directory, file_name):
    reflection_list=[]
    reflection_list.append(converter.from_string(os.path.join(directory,file_name)))
    return reflection_list

def flatten_list(reflection_list):
    return flatten_reflections(reflection_list)

def sum_list(reflections):
    length_list= [len(rlist) for rlist in reflections] 
    return float(sum(length_list))

