import requests
from lxml import html
import random
from PIL import Image, ImageDraw
from os import listdir, remove
from os.path import isfile, join
from PIL.ImageChops import difference



def get_images(word):
    URL = "https://www.google.com/search?tbm=isch&q="
    SEARCH_WORD = word
    PAGE = "&start="
    current_count = 0
    FOLDER = "images/"
    for i in range(150):
        page = requests.get(URL + SEARCH_WORD + PAGE + str(current_count))
        doc = html.fromstring(page.content)
        for img in doc.xpath('//table[@class = "images_table"]//td//img[contains(@alt, "result for")]/@src'):
            with open(FOLDER + str(hash(img)) + ".jpg", 'wb') as f:
                f.write(requests.get(img).content)
        if current_count % 100 == 0:
            print(current_count)
        current_count += 20

def normalize_images(folder, size):
    images = listdir(folder)
    for img in images:
        image = Image.open(folder + img)
        n = min(image.size[0], image.size[1])
        image.resize((size, size)).crop((0, 0, size, size)).save("norm/" + img, "JPEG")


def calculate_signatures(imgs, folder):
    signatures = {}
    for path in images:
        path = folder + path
        img = Image.open(path).resize((1,1))
        if isinstance(img.getpixel((0,0)), int):
            continue
        sign = tuple(map(lambda x: x//10*10,img.getpixel((0,0))))
        if signatures.get(sign, -1) == -1:
            signatures[sign] = [path]
        else:
            signatures[sign].append(path)
    return signatures

def calculate_signatures2(imgs, folder):
    signatures = {}
    for path in images:
        path = folder + path
        img = Image.open(path)
        if isinstance(img.resize((1,1)).getpixel((0,0)), int):
            continue
        sign_v = sign(img)
        if signatures.get(sign_v, -1) == -1:
            signatures[sign_v] = [path]
        else:
            signatures[sign_v].append(path)
    return signatures

def sign(img):
    e = 30
    n = img.size[0]
    r, g, b = 0, 0, 0
    for i in range(n):
        for j in range(n):
            r += img.getpixel((i,j))[0]
            g += img.getpixel((i,j))[1]
            b += img.getpixel((i,j))[2]
    n = n ** 2
    return (int(r / n // e * e), int(g / n // e * e), int(b / n // e * e))

def make_puzzle(img_path, signatures):
    main_image = Image.open(img_path)
    main_image = main_image.resize((main_image.size[0] * 3, main_image.size[1] * 3))
    width = main_image.size[0] - main_image.size[0] % small_image_size
    height = main_image.size[1] - main_image.size[1] % small_image_size
    current_w, current_h = 0, 0
    res_image = Image.new("RGB", (width, height))
    for i in range(0, width, small_image_size):
        current_w = 0
        for j in range(0, height, small_image_size):
            box = (i, j, i + small_image_size, j + small_image_size)
            part = main_image.crop(box)
            #sig = tuple(map(lambda x: x//10*10, part.resize((1,1)).getpixel((0,0))))
            sig = sign(part)
            tmp = Image.new("RGB", part.size, sig)
            tmp = Image.open(random.choice(find_nearest(sig, signatures)))
            res_image.paste(tmp, box)
    res_image.save("res.jpg")

def delete_bad_images():
    images = listdir("images/")
    for i in images:
        if Image.open("images/" + i).mode != "RGB":
            remove("images/" + i)

def find_nearest(t, s):
    e = 3
    p = 10
    res = []
    i = 0
    while len(res) < 2:
        for j in range(2):
            res += s.get((t[0] + p, t[1], t[2]), [])
            res += s.get((t[0], t[1] + p, t[2]), [])
            res += s.get((t[0], t[1], t[2] + p), [])
            res += s.get((t[0] + p, t[1], t[2] + p), [])
            res += s.get((t[0] + p, t[1] + p, t[2]), [])
            res += s.get((t[0], t[1] + p, t[2] + p), [])
            res += s.get((t[0] + p, t[1] + p, t[2] + p), [])
            p *= -1
        i += 1
        p += 10
    return res

if __name__ == '__main__':
    small_image_size = 20
    FOLDER = "norm/"
    images = listdir(FOLDER)
    signatures = calculate_signatures2(images, FOLDER)
    make_puzzle("me.jpg", signatures)
    #normalize_images("images/", 20)
