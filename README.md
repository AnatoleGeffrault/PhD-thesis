# PhD-thesis
Codes for the image analyses of my PhD thesis

This code takes in entry a video of a filament being extruded from a nozzle and separating under the action of gravity. It allows for image analysis that extracts the profile of the filament with time and for profile analysis that extracts the elongational flow curve and other related datas.

# Install

I used the libraries OpenCV and numpy, that can be installed by typing, in the python shell :
"pip install opencv-python" and "pip install numpy"

You should then download the main code "main_EGR_english" together with the folder "Utils". The file "main_EGR_english" and the folder "Utils" should be in the same folder. 

# Run

Only the main code is to be run. 

I provided some videos as examples in the folder "Examples". The inputs of the code have to be changed according to the parameters of the extrusion. The inputs related to the exemples are given in the file "Inputs". You can play with the inputs to choose the output datas (write results as csv, write images, etc). I added a folder results for the emulsion video.

# Use your videos

Contrast : The videos are required to have a good contrast between the filament and the background. I used a black background with approximately white or non transparent materials (kaolin, emulsion), and a white screen with transparent or dark materials (carbopol gel, cement). 

Frame : The code was written to read videos where the nozzle is at the right of the video. The camera should be far enough from the filament to avoid distortion of the filament, but zoomed enough to have the best precision possible. You should avoid defects due to splashes or from other origin, and make sure the background is clean.


