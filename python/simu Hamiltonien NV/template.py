import numpy as np
from numpy import cos,sin,tan,arccos,arcsin,arctan,exp,sqrt,pi
from numpy.linalg import norm
import matplotlib.pyplot as plt
from qutip import *
from scipy.integrate import quad, dblquad, nquad


#theta=2*arccos(1/sqrt(3))

Sz=np.array([[1,0,0],[0,0,0],[0,0,-1]])
bnamez=['+','0','-']
Sx=1/sqrt(2)*np.array([[0,1,0],[1,0,1],[0,1,0]])
Sy=1/(sqrt(2)*1j)*np.array([[0,1,0],[-1,0,1],[0,-1,0]])
rho_0=np.array([[0,0,0],[0,1,0],[0,0,0]])
rho_s=1./3*np.array([[1,0,0],[0,1,0],[0,0,1]])



## Collaposologie
col_t1=np.array([[0,1,1],[1,0,1],[1,1,0]])
gamma_phonon=2E-4#5ms en unité MHz
col_laser=np.array([[0,0,0],[1,0,1],[0,0,0]])
gamma_las=1E-3 #Idem que l'autre

def ordre_numpy() : #Les matrices sont à rentrer ligne par ligne
	testM=np.array([[0,0,1],[0,0,0],[0,0,0]])
	testV=np.array([1,2,3])
	testV=testV.T #n'a pas d'influence

	print(testM.dot(testV)) #M.V
	print(testV.dot(testM)) #V.M

def Hamiltonian_0(B) :
	#Unité naturelle : MHz,Gauss
	D=2880
	gamma=2.8
	E=0.1 #E varie de 0.1 pour du bulk à 5 pour du nano
	H=D*Sz**2+gamma*(B[0]*Sx+B[1]*Sy+B[2]*Sz)+E*(Sx.dot(Sx)-Sy.dot(Sy))
	return H

def egvect(H) :
	val,vec=np.linalg.eigh(H) #H doit être Hermitienne
	return(val,vec)

def print_matrix(M,bname) :
	threshold=0.01
	with open('matrix.txt','w') as f:
		for name in bname :
			f.write('\t|'+name+'>\t')		
		for i in range(len (M[:,0])) :
			name=bname[i]
			f.write('\n')
			f.write('<'+name+'|')
			for v in M[i,:] :
				if np.linalg.norm(v)>threshold :
					f.write('\t%2.1f+%2.1fi'%(v.real,v.imag))
				else :
					f.write('\t\t')


def convolution(M1,M2,bname1,bname2) :
	bname=[]
	for name1 in bname1 :
		for name2 in bname2 :
			bname+=[name1+name2]
	l1=len(M1[:,0])
	l2=len(M2[:,0])
	l=l1*l2
	M=np.zeros((l,l),dtype=complex)
	for i1 in range(l1) :
		for j1 in range(l1) :
			for i2 in range(l2) :
				for j2 in range(l2) :
					i=i1*l2+i2
					j=j1*l2+j2
					M[i,j]=M1[i1,j1]*M2[i2,j2]
	return(M,bname)

def transpose_basepm(M) :
	#base : (+)=(+1)+(-1)/sqrt(2), 0=0 , (-)=(+1)-(-1)/sqrt(2)
	U=np.array([[1/sqrt(2),0,1/sqrt(2)],[0,1,0],[1/sqrt(2),0,-1/sqrt(2)]])
	return(np.matmul(U.T,np.matmul(M,U)))

def some_matrices() :
	transpose_pm=False # Transpose la matrice dans la base (0+-) au lieu de (0,+1,-1)
	matrice='hplus'
	if transpose_pm :
		Sxf=transpose_basepm(Sx)
		Syf=transpose_basepm(Sy)
		Szf=transpose_basepm(Sz)
	else :
		Sxf=Sx
		Syf=Sy
		Szf=Sz

	if matrice=='gplus' :
		M1,bname=convolution(Sxf,Sxf,bnamez,bnamez)
		M2,bname=convolution(Syf,Syf,bnamez,bnamez)
		print_matrix(M1+M2,bname)

	if matrice=='gmoins' :
		M1,bname=convolution(Sxf,Sxf,bnamez,bnamez)
		M2,bname=convolution(Syf,Syf,bnamez,bnamez)
		print_matrix(M1-M2,bname)

	if matrice=='hplus' :
		M1,bname=convolution(Sxf,Syf,bnamez,bnamez)
		M2,bname=convolution(Syf,Sxf,bnamez,bnamez)
		print_matrix(M1+M2,bname)

	if matrice=='hplus' :
		M1,bname=convolution(Sxf,Syf,bnamez,bnamez)
		M2,bname=convolution(Syf,Sxf,bnamez,bnamez)
		print_matrix(M1-M2,bname)

	if matrice=='SzSz' :
		M1,bname=convolution(Szf,Szf,bnamez,bnamez)
		print_matrix(M1,bname)

	if matrice=='SxSx' :
		M1,bname=convolution(Sxf,Sxf,bnamez,bnamez)
		print_matrix(M1,bname)

	if matrice=='SySy' :
		M1,bname=convolution(Syf,Syf,bnamez,bnamez)
		print_matrix(M1,bname)

	if matrice=='SxSy' :
		M1,bname=convolution(Sxf,Syf,bnamez,bnamez)
		print_matrix(M1,bname)

	if matrice=='SySx' :
		M1,bname=convolution(Syf,Sxf,bnamez,bnamez)
		print_matrix(M1,bname)
some_matrices()

def test_mesolve():
	H=Qobj(Hamiltonian_0([0,0,100])) #en ms
	c_op=Qobj(0.3*depop)
	rho=Qobj(rho_0)
	tlist=np.linspace(0,20,100)
	e_op=Qobj(rho_0)
	result=mesolve(H,rho,tlist,[],e_op)
	plt.plot(tlist,result[0])
	plt.show()

def make_collapse_list(gamma_las,gamma_t1) :
	col=[]
	for i in range(3) :
		for j in range(3) :
			if i!=j :
				single=np.zeros((3,3))
				single[i,j]=sqrt(gamma_t1)
				col+=[Qobj(single)]
	las=np.zeros((3,3))
	las[1,0]=sqrt(gamma_las)
	col+=[Qobj(las)]
	las=np.zeros((3,3))
	las[1,2]=sqrt(gamma_las)
	col+=[Qobj(las)]
	return col

def base_1():
	return [np.array([1,0,0]),np.array([0,1,0]),np.array([0,0,1])]
def base_2(phi=0):
	b1=base_1()
	theta=2*arccos(1/sqrt(3))
	T1=np.array([[1,0,0],[0,cos(theta),sin(theta)],[0,-sin(theta),cos(theta)]])
	T2=np.array([[cos(phi),sin(phi),0],[-sin(phi),cos(phi),0],[0,0,1]])
	b2=[]
	for v in b1 :
		v2=T2.dot(T1.dot(v))
		b2+=[v2]
	return b2




def Ham_dip(b1,b2,r): # b1
	r=np.array(r)
	S=[Qobj(spin) for spin in [Sx,Sy,Sz]]
	J=52/norm(r)**3 #MHz, r en nm
	H=tensor(qeye(3),qeye(3))-tensor(qeye(3),qeye(3)) #c'est con mais je peux pas faire de zéros rapidement
	u=r/norm(r)
	for i in range(3) :
		for j in range(3) :
			H=H-J*(3*b1[i].dot(u)*b2[j].dot(u)-b1[i].dot(b2[j]))*tensor(S[i],S[j])
	return H



def test_steady():
	t1_phonon=Qobj(col_t1*sqrt(gamma_phonon))
	laser_pump=Qobj(col_laser*sqrt(gamma_las))
	collapse=t1_phonon+laser_pump
	thetas=np.linspace(0,2*pi,10)
	Bs=np.linspace(0,1000,100)
	#thetas=[0,pi/2*0.99,0.9*pi,3*pi/2*0.99]
	rho_0=[]
	print(collapse)
	# for theta in thetas :
	# 	H=Qobj(Hamiltonian_0([100*sin(theta),0,100*cos(theta)]))
	# 	dm=steadystate(H,[t1_phonon,laser_pump])
	# 	rho_0+=[dm[1,1]]
	# 	print('theta=%f'%theta)
	# 	print(H)
	# 	print(dm)
	for B in Bs :
		H=Qobj(Hamiltonian_0([B*sin(pi/2),0,B*cos(pi/2)]))
		dm=steadystate(H,make_collapse_list(gamma_las,gamma_phonon))
		rho_0+=[dm[1,1]]
	plt.plot(Bs,rho_0)
	plt.show()

def steady_2_spins_1():
	thetas=np.linspace(0.6,0.64,100)
	
	fig,ax=plt.subplots(2)
	
	for gamma_f in [1,3,5,10] :
		rho_0_1=[]
		rho_0_2=[]
		for theta in thetas :
			H_0=Qobj(Hamiltonian_0([100*sin(theta),0,100*cos(theta)]))
			H_1=Qobj(Hamiltonian_0([100*sin(theta+2*arccos(1/sqrt(3))),0,100*cos(theta+2*arccos(1/sqrt(3)))]))
			H=tensor(H_0,qeye(3))+tensor(qeye(3),H_1)+Ham_dip(base_1(),base_2(),[5*cos(1.2),0,5*sin(1.2)])
			col_1=make_collapse_list(gamma_las,gamma_phonon)
			col_2=make_collapse_list(gamma_las,gamma_phonon*gamma_f)
			col_tot=[tensor(op,qeye(3)) for op in col_1]+[tensor(qeye(3),op) for op in col_2]
			dm=steadystate(H,col_tot)
			rho_0_1+=[dm.ptrace(0)[1,1]]
			rho_0_2+=[dm.ptrace(1)[1,1]]
		ax[0].plot(thetas,rho_0_1,label='gamma_f=%f'%gamma_f)
	for r in [10,13,15,20] :
		rho_0_1=[]
		rho_0_2=[]
		thetas=np.linspace(0.614,0.617,100)
		for theta in thetas :
			H_0=Qobj(Hamiltonian_0([100*sin(theta),0,100*cos(theta)]))
			H_1=Qobj(Hamiltonian_0([100*sin(theta+2*arccos(1/sqrt(3))),0,100*cos(theta+2*arccos(1/sqrt(3)))]))
			H=tensor(H_0,qeye(3))+tensor(qeye(3),H_1)+Ham_dip(base_1(),base_2(),[r*cos(1.2),0,r*sin(1.2)])
			col_1=make_collapse_list(gamma_las,gamma_phonon)
			col_2=make_collapse_list(gamma_las,gamma_phonon*5)
			col_tot=[tensor(op,qeye(3)) for op in col_1]+[tensor(qeye(3),op) for op in col_2]
			dm=steadystate(H,col_tot)
			rho_0_1+=[dm.ptrace(0)[1,1]]
			rho_0_2+=[dm.ptrace(1)[1,1]]
		ax[1].plot(thetas,rho_0_1,label='r=%f'%r)
	ax[0].legend()
	ax[1].legend()
	plt.show()

#steady_2_spins_1()

def double_quantum():
	Bs=np.linspace(0,100,100)
	fig,ax=plt.subplots(3)
	rho_0_1=[]
	rho_0_2=[]
	for B in Bs :
		H_0=Qobj(Hamiltonian_0([B,B,B]))
		H_1=Qobj(Hamiltonian_0([B,B,B]))
		H=tensor(H_0,qeye(3))+tensor(qeye(3),H_1)+Ham_dip(base_1(),base_1(),[10*cos(1.2),0,10*sin(1.2)])
		col_1=make_collapse_list(gamma_las,gamma_phonon)
		col_2=make_collapse_list(gamma_las,gamma_phonon*5)
		col_tot=[tensor(op,qeye(3)) for op in col_1]+[tensor(qeye(3),op) for op in col_2]
		dm=steadystate(H,col_tot)
		rho_0_1+=[dm.ptrace(0)[1,1]]
		rho_0_2+=[dm.ptrace(1)[1,1]]
	ax[0].plot(Bs,rho_0_1)
	ax[1].plot(Bs,rho_0_2)
	ax[2].plot(Bs,np.array(rho_0_2)+np.array(rho_0_1))
	plt.show()



def test_steady_2_levels(): ##j'ai pas séparé les collapses sur celui la, gaffe. En plus le hamiltonien dipolaire est peut-etre bien faux
	gamma_phonon=1E-4#5ms en unité MHz
	gamma_las=1E-3 #Idem que l'autre
	sx=sigmax()
	sy=sigmay()
	sz=sigmaz()
	J0=52 # MHz/nm3

	def Ham_up(B,theta) :
		#Unité naturelle : MHz,Gauss
		D=2880
		gamma=2.8
		H=np.array([[0,gamma*B*sin(theta)],[gamma*B*sin(theta),gamma*B*cos(theta)+D]])
		return(Qobj(H))
	def Ham_down(B,theta) :
		#Unité naturelle : MHz,Gauss
		D=2880
		gamma=2.8
		theta=theta+2*arccos(1/sqrt(3))
		H=np.array([[0,gamma*B*sin(theta)],[gamma*B*sin(theta),-gamma*B*cos(theta)+D]])
		return(Qobj(H))
	def Dip_same(r) :
		u=r/norm(r)
		return(-J0/norm(r)**3*(3*tensor(u[0]*sx+u[1]*sy+u[2]*sz,u[0]*sx+u[1]*sy+u[2]*sz)-(tensor(sx,sx)+tensor(sy,sy)+tensor(sz,sz))))


	def Dip_diff(r) :
		u=r/norm(r)
		theta=2*arccos(1/sqrt(3))
		sx2=cos(theta)*sx+sin(theta)*sz
		sz2=cos(theta)*sz-sin(theta)*sx
		return(-J0/norm(r)**3*(3*tensor(u[0]*sx+u[1]*sy+u[2]*sz,u[0]*sx2+u[1]*sy+u[2]*sz2)-(tensor(sx,sx2)+tensor(sy,sy)+tensor(sz,sz2))))

	laser=Qobj([[0,sqrt(gamma_las)],[0,0]])
	t1=Qobj([[0,sqrt(gamma_phonon)],[sqrt(gamma_phonon),0]])

	thetas=np.linspace(0,2*pi,100)
	Bs=np.linspace(0,1000,100)
	rho00=[]
	# for B in Bs :
	# 	H=Ham_up(B,pi/2)
	# 	rho=steadystate(H,[t1,laser])
	# 	rho00+=[rho[0,0]]
	# plt.plot(Bs,rho00)
	for theta in thetas :
		H=tensor(Ham_up(30,theta),qeye(2))+tensor(qeye(2),Ham_down(30,theta))+Dip_diff([5,0,5])
		laser2=tensor(laser,qeye(2))+tensor(qeye(2),laser)
		t12=tensor(t1,qeye(2))+tensor(qeye(2),t1)*2
		rho=steadystate(H,[t12,laser2])
		rho00+=[rho[0,0]+rho[1,1]]
	plt.plot(thetas,rho00)
	plt.show()

def gplus(theta,phi,alpha) :
	return(1/2*(3*sin(theta)*cos(phi)*(cos(alpha)*sin(theta)*cos(phi)+sin(alpha)*cos(theta))-cos(alpha)+3*(sin(theta)*sin(phi))**2-1))
def hmoins(theta,phi,alpha) :
	return(1/2*(3*sin(theta)*cos(phi)*(sin(theta)*sin(phi))-3*(sin(theta)*sin(phi))*(cos(alpha)*sin(theta)*cos(phi)+sin(alpha)*cos(theta))))

def gplus_same(theta,phi) :
	alpha=2*arccos(1/sqrt(3))
	return sqrt(gplus(theta,phi,alpha)**2+hmoins(theta,phi,alpha)**2)*sin(theta)/(4*pi)

def angular_average_manuel(f) : 
	N=100
	thetas=np.linspace(0,pi,N)
	phis=np.linspace(0,2*pi,N)
	dtheta=thetas[1]-thetas[0]
	dphi=phis[1]-phis[0]
	tot=0
	for theta in thetas[1:-1] :
		for phi in phis[1:-1] :
			tot+=f(theta,phi)*dtheta*dphi
		tot+=(f(theta,phis[0])+f(theta,phis[-1]))/2*dtheta*dphi
	for theta in (thetas[0],thetas[-1]) :
		for phi in phis[1:-1] :
			tot+=f(theta,phi)/2*dtheta*dphi
		tot+=(f(theta,phis[0])+f(theta,phis[-1]))/4*dtheta*dphi
	return(tot)

def angular_average(f) :
	return(dblquad(f,0,2*np.pi,lambda x:0,lambda x:np.pi))




print(angular_average_manuel(gplus_same))
print(2/(3*sqrt(3)))

#Le principal problème ici c'est que je considère tous les états comme étant |+1> et |-1>. Y'a peut-etre moyen de faire mieux mais on verra ca plus tard
#L'autre soucis c'est que je ne prend pas en compte l'élargissement inhomogène
def Lukin(B,gamma_las=1E-3,gamma_phonon=3E-4,gamma_f=1): #En Mhz
	B=np.array(B)
	PL=0
	Ci=[np.array([1,1,1])*1/np.sqrt(3),np.array([1,-1,-1])*1/np.sqrt(3),np.array([-1,1,-1])*1/np.sqrt(3),np.array([-1,-1,1])*1/np.sqrt(3)]
	Hi=[]
	egplus=[]
	egmoins=[]
	for i in range(4) :
		C=Ci[i]
		Bz=B.dot(C)
		B_rel=[np.sqrt(max(B.dot(B)-Bz**2,0)),0,Bz] #Il ai me pas les racines de nobres négatifs avec les arrondis
		H=Hamiltonian_0(B_rel)
		Hi+=[H]
		val,vec=egvect(H)
		egmoins+=[val[1]-val[0]]
		egplus+=[val[2]-val[0]]
	


