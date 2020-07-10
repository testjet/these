import numpy as np
import matplotlib.pyplot as plt

with open('map_sumi4.txt','r') as f :
	c=f.read()
	c=c.split('\n\n\n')
	map=np.zeros((50,50,2))
	for k in range(len(c)-2):
		map_inter=c[k]
		map_inter=map_inter.split('\n')
		for i in range(len(map_inter)) :
			line=map_inter[i]
			line=line.split()
			#print(line)
			for j in range(len(line)) :				
				v=float(line[j])
				if (v>1e6) :
					v=v/2
				map[i,j,1]+=1
				map[i,j,0]=map[i,j,0]*(1-1./(map[i,j,1]))+v*(1./(map[i,j,1]))

theta=np.linspace(-6,6,50)
phi=np.linspace(-9,9,50)
map=map[1:,:,0]
map=map/np.amax(map)
fig,ax=plt.subplots()
c=ax.pcolormesh(theta,phi,map) #y'a une random ligne en y=0 que je comprend pas...
ax.set_xlabel(r'$\theta$ (°)')
ax.set_ylabel(r'$\phi$ (°)',rotation=0)
fig.colorbar(c,ax=ax)
plt.show()