import cv2
import numpy as np
from itertools import combinations
import random as rng
import matplotlib.pyplot as plt
import math


def listes_brutes (img, liste_des_premiers_pixels):
    
    c = len(img[1])
    l = len(img)
    
    Rinter = []
    
    plt.imshow(img)
    plt.show()
    
    for i in range (0,c-1) :
        
        j_min = 0
        j_max = l-1
        
        while img [j_min,i] == 0 and j_min < l-1 :
            j_min += 1
        while img [j_max,i] == 0 and j_max > 0 :
            j_max = j_max-1    
        
        if j_min < l-1:                
            Rinter += [(j_max-j_min)]
            
            if len(Rinter) == 3 :
                premier_pixel = i
                liste_des_premiers_pixels += [premier_pixel]
                        
    Zinter = [i for i in range (len(Rinter))]
        
    return (Rinter,Zinter, liste_des_premiers_pixels)


def listes_brutes_alter (img, numimg, cut, liste_des_premiers_pixels): #On coupe au milieu de la buse
    
    c = len(img[1])
    l = len(img)
    
    Rinter = []
    
    plt.imshow(img)
    plt.show()
    
    if numimg == 0 :
        
        cut_min = 0
        cut_max = l-1
        
        while img [cut_min,c-1] == 0 and cut_min < l-1 :
                cut_min += 1
        while img [cut_max,c-1] == 0 and cut_max > 0 :
                cut_max = cut_max-1       
        if cut_min < l-1:                
                cut = (cut_max+cut_min)//2
    
    plt.imshow(img[:cut])
    plt.show()
    plt.imshow(img[cut:])
    plt.show()
    
    for i in range (0,c-1) :
        
        j_min = cut
        j_max = l-1
        
        while img [j_min,i] == 0 and j_min < l-1 :
            j_min += 1
        while img [j_max,i] == 0 and j_max > cut :
            j_max = j_max-1    
        
        if j_min < l-1:                
            Rinter += [(j_max-j_min)]
            
            if len(Rinter) == 3 :
                premier_pixel = i
                liste_des_premiers_pixels += [premier_pixel]
                        
    Zinter = [i for i in range (len(Rinter))]
        
    return (Rinter, Zinter, liste_des_premiers_pixels, cut)


def listes_brutes_alter_2 (img, numimg, cut, liste_des_premiers_pixels): #On coupe au milieu du diamètre max
    
    c = len(img[1])
    l = len(img)
    
    Rinter = []
    Rinters = []
    
    plt.imshow(img)
    plt.show()
            
#            if len(Rinter) == 3 :
#                premier_pixel = i
#                liste_des_premiers_pixels += [premier_pixel]

        
    for i in range (0,c-1) :
    
        j_min = 0
        j_max = l-1
        
        while img [j_min,i] == 0 and j_min < l-1 :
            j_min += 1
        while img [j_max,i] == 0 and j_max > 0 :
            j_max = j_max-1    
                       
        Rinters += [(j_max-j_min)]
        
    indice_cut = Rinters.index(max(Rinters))
    cut_min = 0
    cut_max = l-1
    
    while img [cut_min,indice_cut] == 0 and cut_min < l-1 :
            cut_min += 1
    while img [cut_max,indice_cut] == 0 and cut_max > 0 :
            cut_max = cut_max-1       
    if cut_min < l-1:                
            cut = (cut_max+cut_min)//2
    
    plt.imshow(img[:cut])
    plt.show()
    plt.imshow(img[cut:])
    plt.show()
    
    for i in range (0,c-1) :
        
        j_min = 0
        j_max = cut
        
        while img [j_min,i] == 0 and j_min < cut :
            j_min += 1
        while img [j_max,i] == 0 and j_max > 0 :
            j_max = j_max-1    
        
        if j_min < cut:                
            Rinter += [(j_max-j_min)]
            
            if len(Rinter) == 3 :
                premier_pixel = i
                liste_des_premiers_pixels += [premier_pixel]
                    
    Zinter = [i for i in range (len(Rinter))]
        
    return (Rinter, Zinter, liste_des_premiers_pixels, cut)


def lissage_et_scaling (Rinter,Zinter,corresL,diam_buse,moy=20):
    
    Z = [Zinter[i]*corresL for i in range (len(Rinter))]
                       
    R = []
    
    for mi in range (len(Rinter)) :
        a = max(0,mi-moy)
        b = min(mi+moy,len(Rinter))
        c = min((mi-a),(b-mi))
        R += [np.mean(Rinter[mi-c:mi+c+1])*corresL/diam_buse]
        
    return (R, Z)


def corrections_R_et_Z_analyse (R, Z, pas = 10):
    
    #1 points tous les 10 en Z
    
    Zm = [Z[pas*i] for i in range (len(R)//pas)]
    Rm = [R[pas*i] for i in range (len(R)//pas)]
    
    #Inclusion du reste de goutte précédente
    
    V = 0
    i = 2

    while Rm[i]<max(Rm[2:-50]):
  
        V+=(Zm[i+1]-Zm[i])*Rm[i]**2*math.pi
        i+=1
    correc_Z=V/math.pi
    
    Zm_corrig = [0]
    Rm_corrig = [1]
    
    for j in range (i,len(Rm)):
        Zm_corrig += [(Zm[j]-Zm[i])+correc_Z]
        Rm_corrig += [Rm[j]]
            
    return(Rm_corrig,Zm_corrig)
    
 
def surface_tension (R,Z,diam_buse):

    Surface = 0
    
    for i in range (len(R)-1):
            
        Surface+=(Z[i+1]-Z[i])*R[i]*diam_buse/2*2*math.pi
    
    return (Surface)

def deformations (R):
    
    epsilon = -2*math.log(R)
    
    return(epsilon)
    
    

    
    
    
    
    
    
    
    



