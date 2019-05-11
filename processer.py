import os
import cv2
import progressbar


def delete_bad_images(folder):
    if not folder or not os.path.exists(folder):
        return False
    images = os.listdir(folder)
    print("deleting bad images")
    with progressbar.ProgressBar(max_value=len(images), redirect_stdout=True) as bar:
        for img in images:
            tmp = cv2.imread(folder + '/' + img, 1)
            min_size = min(tmp.shape[:2])
            if str(type(tmp)) == "<class 'NoneType'>":
                os.remove(folder + '/' + img)
            elif min_size < 300:
                os.remove(folder + '/' + img)
            bar.update(bar.value + 1)


def find_optimal_size_for_images(folder, images):
    if not folder or not os.path.exists(folder):
        return False
    tmp = cv2.imread(folder + '/' + images[0], 1)
    min_s = min(tmp.shape[:2])
    print("finding optimal size for images")
    with progressbar.ProgressBar(max_value=len(images), redirect_stdout=True) as bar:
        for i in images:
            tmp = cv2.imread(folder + '/' + i, 1)
            height, width = tmp.shape[:2]
            min_s = min(width, height) if min_s > min(width, height) else min_s
            bar.update(bar.value + 1)
    return min_s

def get_all_images(folder):
    return os.listdir(folder)


def process_all_images(folder):
    if not folder or not os.path.exists(folder):
        return False
    images = get_all_images(folder)
    opt_size = find_optimal_size_for_images(folder, images)
    print("processing all images")
    with progressbar.ProgressBar(max_value=len(images), redirect_stdout=True) as bar:
        for i in images:
            image = cv2.imread(folder + '/' + i, 1)
            new_size = min(image.shape[:2])
            image = image[0:new_size, 0:new_size]
            image = cv2.resize(image, (opt_size, opt_size))
            cv2.imwrite(folder + '/' + i, image)
            bar.update(bar.value + 1)


folder = "imgs"
delete_bad_images(folder)
process_all_images(folder)
