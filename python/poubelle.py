import numpy as np
from numpy import exp,cos,sin
import matplotlib.pyplot as plt

sigma=1
gamma_las=0.1 #puissance laser
ratio_t1=0.5 #ratio de r1 venant de l'effet

def f1(x,ratio_t1):
	#return (1-ratio_t1)+ratio_t1*exp(-x**2/(2*sigma)**2)
	return (1-ratio_t1)+ratio_t1*1/(1+(x/sigma)**2)

def f2(x,gamma_las):
	return((x+gamma_las)/(2*x+gamma_las))

def width(x,y):
	hm=(max(y)+min(y))/2
	i=0
	while (y[i]-hm)*(y[i+1]-hm) > 0 :
		i+=1
	return x[i]

x=np.linspace(-10,10,100)
y=f1(x,ratio_t1)
z=f2(y,gamma_las)

def simple() :
	print(width(x,y),width(x,z))
	plt.plot(x,y/max(y),label='R1')
	plt.plot(x,z/max(z),label='PL')
	plt.legend()

def widths():
	n_x=1000
	n_gamma=1000
	ratios=[0.2,0.5,1]
	fig,ax=plt.subplots(2)
	x=np.linspace(-10,10,n_x)	
	for ratio_t1 in ratios :
		delta_width=[]	
		contraste=[]	
		gamma_range=np.linspace(0,5*ratio_t1,n_gamma)
		y=f1(x,ratio_t1)
		for gamma_las in gamma_range :		
			z=f2(y,gamma_las)
			delta_width+=[width(x,y)-width(x,z)]
			contraste+=[-(f2(f1(0,ratio_t1),gamma_las)-f2(f1(10,ratio_t1),gamma_las))/f2(f1(10,ratio_t1),gamma_las)]
		ax[0].plot(gamma_range/ratio_t1,delta_width,label='ratio=%f'%ratio_t1)
		ax[1].plot(gamma_range/ratio_t1,contraste,label='ratio=%f'%ratio_t1)
		ax[0].legend()
		ax[1].legend()
		ax[1].set_xlabel('Gamma_las')
		ax[0].set_ylabel('Width(PL)-Width(R1)')
		ax[1].set_ylabel('Contrast')



def lors():
	x=np.linspace(-20,20,1000)
	sigma1=0.05
	sigma2=5
	plt.plot(x,1/(1+(x/sigma1)**2)+1/(1+(x/sigma2)**2))
	plt.show()

lors()