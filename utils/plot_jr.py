import matplotlib.pyplot as plt
import pandas as pd

columns = ['fast_axis_x','fast_axis_y', 'fast_axis_z', 'slow_axis_x', 'slow_axis_y', 'slow_axis_z' ]
index = ['battle','igypop','weezer']
df = pd.DataFrame(index=index, columns=columns)
df['fast_axis_x'] = [0.9999977550623774, 0.9999982600652912, 0.9999983227108509]
df['fast_axis_y'] = [0,0,0]
df['fast_axis_z']=[-0.0021189313829052536,-0.001865439999153693,-0.001831550022519978]
df['slow_axis_x']=[-3.865162696186718e-06,-3.0765268416627177e-06, -3.4478783685469325e-06]
df['slow_axis_y']=[-0.9999983363110279, -0.9999986400305672, -0.9999982281102588]
#df['slow_axis_z']=

print df
for key in columns:
	plt.plot(df[key])
        plt.show()
