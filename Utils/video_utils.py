import cv2



def convert_video_to_image_sequence(video_path, Invert = False):

    imgs = []
    capture = cv2.VideoCapture(video_path)

    while True:
        ret, frame = capture.read()
        if frame is None:
            break
        if Invert == True :
            frame = cv2.bitwise_not(frame)
        imgs.append(frame)

    capture.release()

    return imgs

def get_black_image(img, denoising_kernel_size = 3, blur_kernel_size = 3, black_and_white_threshold = 30):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if blur_kernel_size:
        gray = cv2.blur(gray, (blur_kernel_size, blur_kernel_size))


    (thresh, black_and_white_img) = cv2.threshold(gray, black_and_white_threshold, 255, cv2.THRESH_BINARY)

    return black_and_white_img

# Assumed to be a black and white image
def compute_number_of_shapes(black_and_white_img, noise_size = 70, debug_img = None):

    contours, hierarchy = cv2.findContours(black_and_white_img, 1, 2)
    nb_shapes = 0

    for contour in contours:
        area = cv2.contourArea(contour)
        if cv2.contourArea(contour) > noise_size**2:
            nb_shapes += 1

            if debug_img is not None:
                cv2.drawContours(debug_img, contour,0,(0,0,255),2)

    return nb_shapes

#######GET IMAGES#########

def get_several_images_to_crop_2(imgs, black_and_white_threshold = 30, denoising_kernel_size = 70, debug = False):

    imgs_background_only = []
    imgs_drop = []

    # Cut all images and convert them in black and white
    for img in imgs:
        black_img = get_black_image(img, denoising_kernel_size = denoising_kernel_size, black_and_white_threshold = black_and_white_threshold)
        imgs_background_only.append(black_img)

    # Get frames where the drop fall
    # for img in imgs:
    prev_nb_shapes = compute_number_of_shapes(imgs_background_only[0])
    cur_nb_shapes = compute_number_of_shapes(imgs_background_only[1])
    count = [0]
    steps =[]

    for i in range(1, len(imgs_background_only)-1):
        next_nb_shapes = compute_number_of_shapes(imgs_background_only[i+1])
        if cur_nb_shapes > prev_nb_shapes and next_nb_shapes >= cur_nb_shapes and  i > 1 :        
            for h in range (1,10):
                step0 = count[-1]+(i-125-count[-1])*h//10
                if count[-1]<step0:
                    print ("step0=",step0)
                    steps.append(step0)
                    imgs_drop.append(imgs[step0])
            for j in range (0,10):
                step1 = i-125+10*j
                if count[-1]<step1:
                    print ("step1=",step1)
                    steps.append(step1)
                    imgs_drop.append(imgs[step1])
            for k in range (0,5):
                step2 = i-25+3*k
                if count[-1]<step2:
                    print ("step2=",step2)
                    steps.append(step2)
                    imgs_drop.append(imgs[step2])
            for l in range (0,10):
                step3 = i-10+l
                if count[-1]<step3:
                    print ("step3=",step3)
                    steps.append(step3)
                    imgs_drop.append(imgs[step3])
                
            if debug:
                print("nb_shapes change", next_nb_shapes, cur_nb_shapes, prev_nb_shapes)
                cv2.imwrite("detect_" + str(i) + ".tif", cv2.hconcat([imgs_background_only[i-1], imgs_background_only[i], imgs_background_only[i+1]]))
            count.append(i)
        prev_nb_shapes = cur_nb_shapes
        cur_nb_shapes = next_nb_shapes

    return imgs_drop, steps


def remove_right_margin(imgs, right_margin_value):
    for i in range(len(imgs)):
        imgs[i] = imgs[i][:, 0:-right_margin_value-1]

    return imgs

def remove_left_margin(imgs, left_margin_value):
    for i in range(len(imgs)):
        imgs[i] = imgs[i][:, left_margin_value:]

    return imgs

def remove_upper_margin(imgs, upper_margin_value):
    for i in range(len(imgs)):
        imgs[i] = imgs[i][upper_margin_value:, :]

    return imgs

def remove_bottom_margin(imgs, bottom_margin_value):
    for i in range(len(imgs)):
        imgs[i] = imgs[i][0:-bottom_margin_value-1, :]

    return imgs