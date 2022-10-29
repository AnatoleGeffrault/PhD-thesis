import cv2
import numpy as np

# Make sure that the box really contains the whole shape
def refine_box(box, img):

    # print("box in refine", box)
    bot_left_x = box[0][0]
    bot_left_y = box[0][1]
    top_right_x = box[1][0]
    top_right_y = box[1][1]


    threshold = 255*(top_right_x - bot_left_x) / 20
    # Refine top
    while np.sum(img[top_right_y, bot_left_x:top_right_x]) > threshold and top_right_y < img.shape[0]-1:
        top_right_y += 1 

    # Refine bottom
    while np.sum(img[bot_left_y, bot_left_x:top_right_x]) > threshold and bot_left_y > 1:
        bot_left_y -= 1 

    # Refine left
    while np.sum(img[bot_left_y:top_right_y, bot_left_x]) > threshold and bot_left_x > 1:
        bot_left_x -= 1 

    # Back up to original values if we reach image boundaries
    top_right_y = box[1][1] if top_right_y == img.shape[0]-1 else top_right_y
    bot_left_y  = box[0][1] if bot_left_y == 0 else bot_left_y
    bot_left_x  = box[0][0] if bot_left_x == 0  else bot_left_x

    return (bot_left_x, bot_left_y), (top_right_x, top_right_y)


# Add a margin to the considered box
def increase_box_size(box, img_shape, nb_pixels = 3):

    bot_left_x = int(max(box[0][0] - nb_pixels, 0))
    bot_left_y = int(max(box[0][1] - nb_pixels, 0))
    top_right_x = int(min(box[1][0] + nb_pixels, img_shape[1]))
    top_right_y = int(min(box[1][1] + nb_pixels, img_shape[0]))

    return ((bot_left_x, bot_left_y), (top_right_x, top_right_y))


### Final image data stuff

# Compute the maximum radius in the image and all the vertical radii
# Margin is the number of columns we don't want to consider in the right part of the image
def max_radius(img, margin = 10):

    # Compute radii for all x values
    radii = np.sum(img, axis = 0) // 255
    max_index = img.shape[1]-1

    print("in max radius", "len", radii.shape, "min", radii.min(), "mean", radii.mean(), "radii.max", radii.max())
    print("margin", margin)


    tmp_radii = radii.copy()
    tmp_img = img.copy()

    while max_index >= img.shape[1]-margin:

        if radii.shape[0] <= margin:
            return 0, np.array([]), img

        img = img[:, :img.shape[1]-margin]
        radii = radii[:radii.shape[0]-margin]
        max_index = np.argmax(radii)
        print("max index", max_index, "max_val", np.max(radii))

    max_value = radii[max_index]

    # Iterate to be sure we haven't cropped it too much
    end_img_index = radii.shape[0]-1
    while tmp_radii[end_img_index] <= max_value and end_img_index < tmp_radii.shape[0]:
        #print(str(end_img_index))
        end_img_index += 1

    print("next one", tmp_radii[end_img_index+1])
    img = tmp_img[:, :end_img_index]
    radii = tmp_radii[:end_img_index]

    # Check whether we have a black area within the box
    # If so, we have included two shapes
    for i in range(radii.size-1):
        if radii[i] - margin > 0 and radii[i+1] - margin < 0:
            return 0, np.array([]), img

    # Keep only non zero radii
    radii = radii[np.nonzero(radii)]
    max_index = np.argmax(radii)

    # Check whether the first radius is not too big, if so, the shape must be cut in half by the box
    if radii[0] > 0.4*radii[max_index]:
        return 0, np.array([]), img

    return max_index, radii, img


#############THE REAL THING###################"""

# From an image, detect and filter drop
# Returns the cropped and filtered image and its radii values
def crop_image_clean_video(img, debug = False, blur_kernel_size = 5, 
               black_and_white_threshold = 70, denoising_kernel_size = 70,
               nb_corners_to_detect = 10, margin = 10):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.fastNlMeansDenoising(gray, gray, h=10, templateWindowSize=denoising_kernel_size)
    (thresh, black_and_white_img) = cv2.threshold(gray, black_and_white_threshold, 255, cv2.THRESH_BINARY)

    # Select the most right-handed box
    final_box = [[0, 0], [black_and_white_img.shape[1]-1, black_and_white_img.shape[0]-1]]
    final_box = refine_box(final_box, black_and_white_img)
    final_box = increase_box_size(final_box, black_and_white_img.shape, nb_pixels = 5)
    # Crop the final image
    final_image = black_and_white_img[final_box[0][1]:final_box[1][1], final_box[0][0]:final_box[1][0]]
    final_image = gray[final_box[0][1]:final_box[1][1], final_box[0][0]:final_box[1][0]]

    if debug:
        cv2.rectangle(img, (final_box[0]), (final_box[1]), [0, 255, 255], 2) # Yellow

    # Filter image
    if blur_kernel_size:
        final_image = cv2.blur(final_image, (blur_kernel_size, blur_kernel_size))
    (thresh, final_image) = cv2.threshold(final_image, black_and_white_threshold, 255, cv2.THRESH_BINARY)

    # Get data on image and further refine the crop
    index_max, all_radii, final_image = max_radius(final_image, margin = margin)

    if debug:
        print("index max", index_max, "all_radii shape", all_radii.shape, "final image shape", final_image.shape)

    return final_image, all_radii