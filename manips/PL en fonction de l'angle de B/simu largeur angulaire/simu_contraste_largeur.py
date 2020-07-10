import numpy as np
from numpy import exp,cos,sin
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

sigma=1
gamma_las=0.1 #puissance laser
ratio_t1=0.5 #ratio de r1 venant de l'effet

def f1(x,ratio_t1):
	return (1-ratio_t1)+ratio_t1*exp(-x**2/(sigma)**2)
	#return (1-ratio_t1)+ratio_t1*1/(1+(x/sigma)**2)

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
	fig,ax=plt.subplots(3)
	x=np.linspace(-5,5,n_x)	
	for ratio_t1 in ratios :
		delta_width=[]	
		contraste=[]	
		gamma_range=np.linspace(0,10*ratio_t1,n_gamma)
		y=f1(x,ratio_t1)
		for gamma_las in gamma_range :		
			z=f2(y,gamma_las)
			delta_width+=[width(x,y)-width(x,z)]
			contraste+=[-(f2(f1(0,ratio_t1),gamma_las)-f2(f1(10,ratio_t1),gamma_las))/f2(f1(10,ratio_t1),gamma_las)/ratio_t1]
		ax[1].plot(gamma_range/ratio_t1,delta_width,label='ratio=%f'%ratio_t1)
		ax[2].plot(gamma_range/ratio_t1,contraste,label='ratio=%f'%ratio_t1)
		ax[0].plot(x,f1(x,ratio_t1),label='ratio=%f'%ratio_t1)
		ax[1].legend()
		ax[2].legend()
		ax[0].legend()
		ax[2].set_xlabel('Gamma_las')
		ax[1].set_ylabel('Width(PL)-Width(R1)')
		ax[2].set_ylabel('Contrast')
		ax[0].set_xlabel('Delta(E)')
		ax[0].set_ylabel('R1')
#widths()

def lor_fit(x,y,Amp=None,x0=None,sigma=None) :
	if not Amp :
		Amp=max(y)
	if not x0 :
		x0=x[int(len(x)/2)]
	if not sigma :
		sigma=x[int(len(x)/10)]-x[0]
	def f(x,Amp,x0,sigma) :
		return Amp*1/(1+((x-x0)/(2*sigma))**2)
	p0=[Amp,x0,sigma]
	popt, pcov = curve_fit(f, x, y, p0)
	return(x for x in popt)

def gauss_fit(x,y,Amp=None,x0=None,sigma=None) :
	if not Amp :
		Amp=max(y)
	if not x0 :
		x0=x[int(len(x)/2)]
	if not sigma :
		sigma=x[int(len(x)/10)]-x[0]

	def f(x,Amp,x0,sigma) :
		return Amp*np.exp(-((x-x0)/(2*sigma))**2)
	p0=[Amp,x0,sigma]
	popt, pcov = curve_fit(f, x, y, p0)
	return(x for x in popt)

x=np.linspace(-10,10,500)
y1=f1(x,ratio_t1=0.8)
y2=f2(y1,gamma_las)
y1=y1-min(y1)
y1=y1/max(y1)
plt.plot(x,y1,'r.')
Amp,x0,sigma=gauss_fit(x,y1)
y1fit=Amp*np.exp(-((x-x0)/(2*sigma))**2)
plt.plot(x,y1fit,'r')
y2=max(y2)-y2
y2=y2/max(y2)
Amp,x0,sigma=gauss_fit(x,y2)
y2fit=Amp*np.exp(-((x-x0)/(2*sigma))**2)
plt.plot(x,y2fit,'b')
plt.plot(x,y2,'b.')
plt.show()