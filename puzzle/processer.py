import os
import cv2
import progressbar
import numpy as np
from random import choice
from ast import literal_eval
import pickle


def delete_bad_images(folder):
    if not folder or not os.path.exists(folder):
        return False
    images = os.listdir(folder)
    print("deleting bad images")
    with progressbar.ProgressBar(max_value=len(images), redirect_stdout=True) as bar:
        for img in images:
            tmp = cv2.imread(folder + '/' + img, 1)
            if str(type(tmp)) != "<class 'NoneType'>":
                min_size = min(tmp.shape[:2])
            if str(type(tmp)) == "<class 'NoneType'>":
                os.remove(folder + '/' + img)
            elif min_size < 100:
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
    return int(min_s / 100) * 100

def get_all_images(folder):
    if not folder or not os.path.exists(folder):
        return False
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

def calc_signatures(folder):
    if not folder or not os.path.exists(folder):
        return False
    images = get_all_images(folder)
    signatures = {}
    print("calculating signatures")
    with progressbar.ProgressBar(max_value=len(images), redirect_stdout=True) as bar:
        for i in images:
            image = cv2.imread(folder + "/" + i, 1)
            image = image[::2, ::2]
            color = calc_signature(image)
            signatures[color] = signatures[color] + [i] if color in signatures else [i]
            bar.update(bar.value + 1)
    with open('signatures', 'w') as out:
        for key, val in signatures.items():
            out.write('{}:{}\n'.format(key, val))


def calc_signature(image):
    fault = 15
    image = image[::2, ::2]
    if len(image) < 1:
        return (0,0,0)
    color = [0, 0, 0]
    count = 0
    for m in image:
        for j in m:
            color[0] += j[0]
            color[1] += j[1]
            color[2] += j[2]
            count += 1
    color[0] = int(color[0] / count / fault) * fault
    color[1] = int(color[1] / count / fault) * fault
    color[2] = int(color[2] / count / fault) * fault
    return tuple(color)

def get_signatures_from_file(file):
    res = {}
    with open(file) as inp:
        for i in inp.readlines():
            key, val = i.strip().split(':')
            r = int(key[key.index("(") + 1:key.index(",")])
            key = key[key.index(",") + 1:]
            g = int(key[:key.index(",")])
            b = int(key[key.index(",") + 1:-1])
            res[(r, g, b)] = literal_eval(val)
    return res

def find_nearest(signature, file, folder):
    fault = 5
    to_choose = []
    signatures = get_signatures_from_file(file)
    for d in range(15):
        for i in [-1, 1]:
            to_choose += signatures.get((signature[0] + fault * i * d, signature[1], signature[2]), [])
            to_choose += signatures.get((signature[0], signature[1] + fault * i * d, signature[2]), [])
            to_choose += signatures.get((signature[0], signature[1], signature[2] + fault * i * d), [])
            to_choose += signatures.get((signature[0] + fault * i * d, signature[1] + fault * i * d, signature[2]), [])
            to_choose += signatures.get((signature[0], signature[1] + fault * i * d, signature[2] + fault * i * d), [])
            to_choose += signatures.get((signature[0] + fault * i * d, signature[1], signature[2] + fault * i * d), [])
            to_choose += signatures.get((signature[0] + fault * i * d, signature[1] + fault * i * d, signature[2] + fault * i * d), [])

    return choice(to_choose) if len(to_choose) > 0 else choice(get_all_images(folder))

def make_puzzle(image, folder, file="signatures"):
    image = cv2.imread(image, 1)
    pre_size = 10
    height, width = image.shape[:2]
    height = int(height / pre_size) * pre_size
    width = int(width / pre_size) * pre_size
    image = image[0:height, 0:width]
    opt_size = find_optimal_size_for_images(folder, get_all_images(folder))
    new_w = int(width / pre_size * opt_size)
    new_h = int(height / pre_size * opt_size)
    puzzle = np.zeros((new_h, new_w, 3), np.uint8)

    with progressbar.ProgressBar(max_value=int(height / pre_size) * int(width / pre_size), redirect_stdout=True) as bar:
        for i in range(int(height / pre_size)):
             for j in range(int(width / pre_size)):
                 signature = calc_signature(image[pre_size * i:pre_size * (i + 1), pre_size * j:pre_size * (j + 1)])
                 new_part = cv2.imread(folder + '/' + find_nearest(signature, file, folder))
                 puzzle[opt_size * i:opt_size * (i + 1), opt_size * j:opt_size * (j + 1)] = new_part
                 bar.update(bar.value + 1)
    cv2.imwrite("puzzle.jpg", puzzle)