######################Introduction#####################

#This code takes one video or several images as entries, and will deliver different .csv files containing :
#- the filament shapes as height(radius), at every time of the extrusion
#- the description of the solid domain as stress(strain) between 0 and the identified yield stress, at every time of the extrusion
#- the description of the liquid domain as stress(strain rate) between the identified yield stress and the stress corresponding to the minimum radius, at every time of the extrusion
#- the description of shear as shear stress over elongational stress vs shear rate over elongational rate 

#It is based on the theory developped in the article Extensional gravity rheometer for yield stress fluids


import cv2
import numpy as np
import matplotlib.pyplot as plt

from drop_detection_utils import *
from video_utils import *
from analysis_utils import *

if __name__ == "__main__":
    
    
    ####################INPUTS######################
 
    
    video_name = 'Emul88_1cm_0.36mms_4'
    folder_path = 'D:\Thèse_3a\Instron_gouttes'
    #video_path = "D:/Thèse_1a/Expériences/Instron_extrusion/Test/images_results/Emul88_2cm_0.036mms_1.MP4" # This could also be in a loop later
    video_path = folder_path+'/'+video_name+'.MP4'
    
    write_all_images = True
    debug = True
    right_margin = True
    left_margin = True
    upper_margin = True
    bottom_margin = True
    write_csv_files = False
    auto_scale = False
    Invert = False
    Only_pinch_off = True
    
    #Images treatment parameters
    denoising_kernel_size = 20 #Removes background noise
    blur_kernel_size = 3 #Slightly blurs for a better homogeneity
    black_and_white_threshold = 40 #Threshold value for turning Grey to B&W
    right_margin_value = 0 #Number of pixels cropped from the initial image (if asked for)
    left_margin_value = 200 #Number of pixels cropped from the initial image (if asked for)
    upper_margin_value = 300
    bottom_margin_value = 200
    margin = 60 #Number of pixels cropped from the initial image at each iteration to remove the nozzle from the image.
    #Its value should not have an impact an the cropped image
    cut = 0 #in case we cut a part of the image

    #Material and setup parameters
    diam_buse = 1 #cm
#    phi = 44.6 #Volume concentration in cement
#    density = 3100 #Kaolin density
#    rho = phi/100*density+(100-phi)/100*1000 #Suspension density
    rho = 780 #Emulsion density
#    rho = 1000 #Carbopol density
    g = 9.81 #m.s-2
    framerate = 60 #img/s
    scale = 943/4.5 #number of pixels for 1cm


    ####################IMAGES######################


    imgs = convert_video_to_image_sequence(video_path, Invert = Invert) #convert the video into a sequence of images
    
    if right_margin :     
        imgs = remove_right_margin(imgs, right_margin_value) #it might be difficult to find the limit between the nozzle and the filament
        #with iterations (from "get_several_images_to_crop"), so it can be done in a more "brutal" way ("remove_right_margin")
    if left_margin :     
        imgs = remove_left_margin(imgs, left_margin_value) 
        
    if bottom_margin :     
        imgs = remove_bottom_margin(imgs, bottom_margin_value)

    if upper_margin :     
        imgs = remove_upper_margin(imgs, upper_margin_value)

    imgs, steps = get_several_images_to_crop_2(imgs, denoising_kernel_size = denoising_kernel_size, debug = debug, black_and_white_threshold = black_and_white_threshold)
    #We first find the image(s) where the filament breaks, then we keep a selection (around 30 images for one complete extrusion)
    print (len(imgs), " detected") #Number of images that will be used in the following
          
    if write_all_images: #We can choose to write all the selected images, in RGB
        for i in range(len(imgs)):
            cv2.imwrite("img_" + str(i) + ".tif", imgs[i])
    
    
    ####################PROFILES######################
    
    
    #Lists for the study
    
    liste_des_R = [] #Complete list of radii (dimensionless)
    liste_des_Z = [] #Complete list of heights (cm)
    liste_des_r_adim = [] #Partial list of radii (dimensionless)
    liste_des_z = [] #Partial list of heights (cm)
    liste_des_N = [] #List of normal stresses
    liste_des_epsilon = [] #List of longitudinal strains
    liste_des_epsilon_point = [] #List of longitudinal rates of strain
    liste_des_acc = []  #List of acceleration
    liste_des_premiers_pixels = [] #List of heights of the first pixel of filament (from the left of the image)
    liste_des_epsilon_point_shear = [] #List of tangential rates of strain
    liste_des_N_shear = [] #List of tangential stresses
    if auto_scale == False :
        corresL = 1/scale
    
    for numimg in range(len(imgs)): 
        
        img, radii_drop = crop_image_clean_video(imgs[numimg],  blur_kernel_size = blur_kernel_size, 
                                                 black_and_white_threshold = black_and_white_threshold,
                                                 denoising_kernel_size = denoising_kernel_size, margin = margin, debug = debug) 
        #Detects the separation between the filament and the nozzle, and crops the image to keep only the filament in white, and the background in black
        
        print(str(numimg) + "th image processed")
        
        if write_all_images: #It can be useful to visualize all the cropped b&w images extracted from the video
            cv2.imwrite("img_bw_" + str(numimg) + ".tif", img)       
        
        Rinter, Zinter, liste_des_premiers_pixels = listes_brutes (img, liste_des_premiers_pixels) 
        #Get the list of diameters (Rinter), heights (Zinter) and height of first pixel of filament, in pixels
        
        
        if auto_scale == True :         
            if numimg == 0 : #We can set the scale in cm/pixel using the fact that the maximum radius of the filament
                #on the first image is exactly equal to the nozzle radius. It can be justified if the filament has 
                #negligible increase (swelling) or decrease of its radius when coming out of the nozzle
                diam_max = max(Rinter)
                corresL = diam_buse/diam_max #cm/pixel
        
        
        R, Z = lissage_et_scaling (Rinter,Zinter,corresL,diam_buse,moy=20) 
        #We smoothen the profile with a moving average, and we change the scale to cm
        liste_des_R.append(R) #Addition of the list of radii of this image to the complete list of all the images
        liste_des_Z.append(Z) #Addition of the list of heights of this image to the complete list of all the images
        
        #Plot of the profile of the drop
                
        plt.plot(Z,R,'-',color='red')
        plt.xlabel('Hauteur (cm)')
        plt.ylabel('Rayon adimensionné')
        plt.ylim((0,1.05))
        plt.show()
    
        
        ####################Theory######################
    

        Rm_corrig,Zm_corrig = corrections_R_et_Z_analyse (R, Z, pas = 10) 
        #We rewrite the bottom of the drop as a cylinder of radius R0 and not as a cone, to take its mass into account
         #but "forget" its shape, due to the breakage of the previous drop and therefore not explicitly provided for
         #by theory. We also take a step of 10 pixels in height, because it works better. I believe it's because
         #on 10 pixels in height, we have time to see an evolution of the radius, whereas on 1 pixel the radius really does not change.
        
        liste_des_r_adim.append(Rm_corrig) #Addition of the list of reduced radii of this image to the list of list for all the images
        liste_des_z.append(Zm_corrig) #Addition of the list of reduced heights of this image to the list of list for all the images
        
        
        if numimg > 1 : #We will now work on the expressions of strain, strain rate and stress. 
        #Tricky point here : to know the strain rate and stress of image i, i need to know the experimental datas of images i-1, i and i+1. 
        #Since i only know the experimental datas of images up to i, i will calculate the strain, strain rate and stress of image i-1, with
        #datas of images i-2, i-1 and i. Hence my calculations starting at numimg=2.
            
            Em = [] #list of strains in this image
            Epointm = [] #list of longitudinal strain rates in this image
            Epointshear = [] #list of tangential strain rates in this image
            Accel = [] #list of accelerations in this image
            Accel_part = []
            Accel_ref = []
            Nm = [] #list of normal stresses in this image
            Nshear = [] #list of tangential stresses in this image
            stepdown = (steps[numimg-1]-steps[numimg-2])/framerate #time step between current image (i-1) and last image (i-2)
            stepup = (steps[numimg]-steps[numimg-1])/framerate #time step between next image (i) and current image (i-1)
            step = (stepdown+stepup)/2 #mean time step
            
            for j in range (1, min(len(liste_des_r_adim[-1]),len(liste_des_r_adim[-2]),len(liste_des_r_adim[-3]))-1):
            #We cannot calculate the derivatives of of the extreme points at the bottom (z=0) and at the junction to the nozzle
                
                #For the calculation of the acceleration, we need to take the velocity values of the image i-2
                if j==1 :
                    Vdown = 0
                else :
                    Vdown = B*SumEj/stepdown/100 #m/s
                    
                #Longitudinal strain
                epsilon = deformations(Rm_corrig[j]) #defined in analysis_utils
                Em += [epsilon] #Strain at one height added to the list of the strains in this image
                
                #Longitudial strain rate : i separated the calculation into several parts. For derivation, i used a central difference.
                SumEj = 0
                coefE = 1/(stepup*liste_des_r_adim[-2][j])
                for k in range (j) :
                    SumEj += liste_des_r_adim[-2][k]*(liste_des_r_adim[-1][k]-liste_des_r_adim[-2][k])*(liste_des_z[-1][k]-liste_des_z[-2][k])
                A = liste_des_r_adim[-1][j]-liste_des_r_adim[-2][j]
                B = 2/(liste_des_r_adim[-2][j])**2
                C = liste_des_r_adim[-2][j+1]-liste_des_r_adim[-2][j-1]
                D = liste_des_z[-2][j+1]-liste_des_z[-2][j-1]
                Epointm += [-coefE*(A-B*C/D*SumEj)] #Strain rate at one height added to the list of the strain rates in this image
                
                #Tangential strain rate
                if j>2 :
                    Epointshear += [liste_des_r_adim[-2][j]*(Epointm[-1]-Epointm[-2])/(4*(liste_des_z[-2][j]-liste_des_z[-2][j-1]))]
                
                #Acceleration : it starts to be not negligible at times close to the breakage.
                Vup = B*SumEj/stepup/100 #m/s
#                accel_part = ((Vup-Vdown)/step+(Vup+Vdown)/2*(Vup-Vdown)/(-B*SumEj*2))/100
                delta_z_up = -(liste_des_premiers_pixels[-1]-liste_des_premiers_pixels[-2])*corresL/100 #m/s
                delta_z_down = -(liste_des_premiers_pixels[-2]-liste_des_premiers_pixels[-3])*corresL/100 #m/s
                Vuptot = delta_z_up/stepup + Vup #m/s
                Vdowntot = delta_z_down/stepdown + Vdown
                accel_ref = ((delta_z_up/stepup)-(delta_z_down/stepdown))/step
                accel = (Vuptot-Vdowntot)/step
                Accel += [accel]
#                Accel += [accel_part+accel_ref]
                Accel_part += [(accel-accel_ref)]
                Accel_ref += [accel_ref]
                
                #Normal stress 
                SumNj = 0
                coef = rho/((liste_des_r_adim[-2][j]*10**(-2))**2)
                for k in range (1,j) :
                    SumNj += (liste_des_r_adim[-2][k]*10**(-2))**2*(liste_des_z[-2][k]-liste_des_z[-2][k-1])*10**(-2)
                Nm += [coef*SumNj*(g-accel)]

                #Tangential stress
                Nshear += [-coef*SumNj*(g-accel)*C/D]
        
            liste_des_epsilon.append(Em)   #List of strains of this image added to the complete list of all images
            liste_des_epsilon_point.append(Epointm)  #List of strain rates of this image added to the complete list of all images        
            liste_des_N.append(Nm) #List of stresses of this image added to the complete list of all images
            liste_des_acc.append([Accel, Accel_ref, Accel_part])
            liste_des_epsilon_point_shear.append([0]+Epointshear+[0])
            liste_des_N_shear.append(Nshear)
            

    ####################Writing profiles######################
    
    if write_csv_files == True :
        
        #Creation of the .csv file for filament shapes
                        
        file1 =('filament_shape_'+video_name+'.csv')         
    
        shapes_table = open(file1,'w')
       
        #Filling the .csv file
        n = np.max([len(liste_des_R[i]) for i in range (len(liste_des_R))]) 
        for i in range (n) :
     
            for j in range (len(liste_des_R)):
                
                if i < len(liste_des_R[j]):
                    r_adim = str(liste_des_R[j][i])
                    z = str(liste_des_Z[j][i])
    
                else :
                    r_adim = ('')
                    z = ('')
    
                shapes_table.write(r_adim+";"+z+";")
            shapes_table.write("\n")
        shapes_table.close()  
    
    
    
    ####################Cleaning######################


    if Only_pinch_off == False :
         
        #We want to plot stress (strain rate) curves only for the part of the filament that is in its liquid (gravity-driven) regime.
        #And we want to plot stress (strain) curves only for the part of the filament that is in its solid (gravity-driven) regime.
        #It means we have to identify those regimes on the whole filament, and select the corresponding datas only
        
        
        l_sup = [] #List of the top borders for stress(strain rate) curves
        l_inf = [] #List of the bottom borders for stress(strain rate) curves (that are also the top borders of stress(strain curves))
        liste_des_N_liquid_clean = [] #List of stresses in the liquid regime
        liste_des_N_solid_clean = [] #List of stresses in the solid regime
        liste_des_N_shear_liquid_clean = [] #List of tangential stresses in the liquid regime
        liste_des_epsilon_clean = [] #List of strains in the solid regime
        liste_des_epsilon_point_clean = [] #List of strain rates in the liquid regime
        liste_des_epsilon_point_shear_clean = []
        
        for i in range (len(liste_des_N)):
        #We go through the whole filament and apply the adapted criteria to find the borders of solid and liquid domains
            
            #Upper limit : index of the minimum radius
            borne_sup = liste_des_r_adim[i+1].index(min(liste_des_r_adim[i+1]))-1
            l_sup.append(borne_sup)
            #Lower limit : index below which datas of stress (strain rate) are considered as noise  
            j = borne_sup
            while liste_des_epsilon_point[i][j-1] < liste_des_epsilon_point[i][j] and j>1:
                j = j-1
            error_eps = max(max(liste_des_epsilon_point[i][0:j]),0)
            k = borne_sup
            while liste_des_epsilon_point[i][k] > 2*error_eps and k>1:
                k = k-1
            borne_inf = k
            l_inf.append(borne_inf)
            
    
            liste_des_N_liquid_clean.append(liste_des_N[i][borne_inf:borne_sup]) #List of stresses in the liquid regime of all images
            liste_des_epsilon_point_clean.append(liste_des_epsilon_point[i][borne_inf:borne_sup]) #List of strain rates in the liquid regime of all images
            liste_des_N_solid_clean.append(liste_des_N[i][:borne_inf]) #List of stresses in the solid regime of all images
            liste_des_epsilon_clean.append(liste_des_epsilon[i][:borne_inf]) #List of strains in the solid regime of all images
            liste_des_epsilon_point_shear_clean.append(liste_des_epsilon_point_shear[i][borne_inf:borne_sup])
            liste_des_N_shear_liquid_clean.append(liste_des_N_shear[i][borne_inf:borne_sup]) #List of stresses in the liquid regime of all images



    if Only_pinch_off == True : #In the case we want the elongational datas from the pinch-off
        
        #We want to plot stress (strain rate) curves only for the part of the filament that is in its liquid (gravity-driven) regime.
        #And we want to plot stress (strain) curves only for the part of the filament that is in its solid (gravity-driven) regime.
        #It means we have to identify those regimes on the whole filament, and select the corresponding datas only
        
        l_sup = [] #List of the top borders for stress(strain rate) curves
        l_inf = [] #List of the bottom borders for stress(strain rate) curves (that are also the top borders of stress(strain curves))
        liste_des_N_liquid_clean = [] #List of stresses in the liquid regime
        liste_des_N_solid_clean = [] #List of stresses in the solid regime
        liste_des_N_liquid_final = [] #List of stresses at the pinch-off
        liste_des_epsilon_clean = [] #List of strains in the solid regime
        liste_des_epsilon_point_clean = [] #List of strain rates in the liquid regime
        liste_des_epsilon_point_shear_clean = []
        liste_des_epsilon_point_final = [] #List of strain rates at the pinch-off
        
        for i in range (len(liste_des_N)):
        #We go through the whole filament and apply the adapted criteria to find the borders of solid and liquid domains
            
            #Upper limit : index of the minimum radius
            borne_sup = len(liste_des_N[i])
            l_sup.append(borne_sup)
            #Lower limit : index below which datas of stress (strain rate) are considered as noise  
            borne_inter = min([liste_des_r_adim[i].index(min(liste_des_r_adim[i])),liste_des_r_adim[i+1].index(min(liste_des_r_adim[i+1]))])-1 #mal défini
            j = borne_inter
            while liste_des_epsilon_point[i][j-1] < liste_des_epsilon_point[i][j] and j>1:
                j = j-1
            error_eps = max(max(liste_des_epsilon_point[i][0:j]),0)
            k = borne_inter
            while liste_des_epsilon_point[i][k] > 2*error_eps and k>1:
                k = k-1
            borne_inf = k
            l_inf.append(borne_inf)
            
    
            liste_des_N_liquid_clean.append(liste_des_N[i][borne_inf:borne_sup]) #List of stresses in the liquid regime of all images
            liste_des_epsilon_point_clean.append(liste_des_epsilon_point[i][borne_inf:borne_sup]) #List of strain rates in the liquid regime of all images
            liste_des_N_solid_clean.append(liste_des_N[i][:borne_inf]) #List of stresses in the solid regime of all images
            liste_des_epsilon_clean.append(liste_des_epsilon[i][:borne_inf]) #List of strains in the solid regime of all images
            liste_des_epsilon_point_shear_clean.append(liste_des_epsilon_point_shear[i][borne_inf:borne_sup])
            liste_des_N_liquid_final.append(liste_des_N[i][borne_inter])
            liste_des_epsilon_point_final.append(liste_des_epsilon_point[i][borne_inter]) 
    

    ####################Writing liquid regime######################    
    
    if write_csv_files == True :
        
        if Only_pinch_off == False :
            
            #Creation of the .csv file for liquid regimes (flow curves)
                            
            file2 =('liquid_'+video_name+'.csv')
            liquid_table = open(file2,'w')
            
            #Filling the .csv file
            n = np.max(l_sup) 
            for i in range (n) :
                
                for j in range (len(liste_des_N_liquid_clean)):
                    
                    if i < len(liste_des_N_liquid_clean[j]):
                        strain_rate = str(liste_des_epsilon_point_clean[j][i])
                        stress = str(liste_des_N_liquid_clean[j][i])
                    else :
                        strain_rate = ('')
                        stress = ('')
        
                    liquid_table.write(strain_rate+";"+stress+";")
                liquid_table.write("\n")
            liquid_table.close()
            
        #Creation of the .csv file for shear vs elongation
                            
            file3 =('taus_vs_ds_'+video_name+'.csv')
            liquid_table = open(file3,'w')
            
            #Filling the .csv file
            n = np.max(l_sup) 
            for i in range (n) :
                
                for j in range (len(liste_des_epsilon_point_clean)):
                    
                    if i < len(liste_des_epsilon_point_clean[j]):
                        ds = str(liste_des_epsilon_point_shear_clean[j][i]/liste_des_epsilon_point_clean[j][i])
                        taus = str(liste_des_N_shear_liquid_clean[j][i]/liste_des_N_liquid_clean[j][i])
                    else :
                        ds = ('')
                        taus = ('')
        
                    liquid_table.write(ds+";"+taus+";")
                liquid_table.write("\n")
            liquid_table.close()
    
        if Only_pinch_off == True :
            
            #Creation of the .csv file for liquid regimes (flow curves)
                        
            file4 =('liquid_pinchoff_'+video_name+'.csv')
            liquid_table = open(file4,'w')
            
            #Filling the .csv file
                
            for i in range (len(liste_des_N_liquid_final)):
                    
                strain_rate = str(liste_des_epsilon_point_final[i])
                stress = str(liste_des_N_liquid_final[i])
                liquid_table.write(strain_rate+";"+stress+";")
                liquid_table.write("\n")
                
            liquid_table.close()
       
#    
#        ####################Writing solid regime######################    
#    
#
    if write_csv_files == True :
        
        if Only_pinch_off == False :
            
            #Creation of the .csv file for solid regimes
                             
            file5 =('solid_'+video_name+'.csv')         
            solid_table = open(file5,'w')
          
            #Filling the .csv file
            n = np.max(l_inf)
            for i in range (n) :
                
                for j in range (len(liste_des_N_solid_clean)):
                    
                    if i < len(liste_des_N_solid_clean[j]):
                        strain = str(liste_des_epsilon_clean[j][i])
                        stress = str(liste_des_N_solid_clean[j][i])
                    else :
                        strain = ('')
                        stress = ('')
        
                    solid_table.write(strain+";"+stress+";")
                solid_table.write("\n")
            solid_table.close()