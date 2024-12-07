from PIL import Image, ImageFilter, ImageDraw
import os
from sklearn.cluster import KMeans
from collections import Counter
import numpy as np
import time
os.environ['OMP_NUM_THREADS'] = '10'
def get_dominant_color(image):
    small_image = image.resize((50, 50))
    pixels = small_image.getdata()
    most_common_color = Counter(pixels).most_common(1)[0][0]
    return most_common_color
def get_main_colors(image, num_colors=3):
    image = image.resize((50, 50))
    pixels = np.array(image)
    colors = pixels.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_colors,n_init=10)
    kmeans.fit(colors)
    main_colors = kmeans.cluster_centers_.astype(int)
    main_colors = [tuple(color) for color in main_colors]
    return main_colors
def add_wite_border(image,width,height,new_width,new_height):
    dominant_color = (255, 255, 255)
    new_image = Image.new("RGB", (new_width, new_height),dominant_color)
    offset = ((new_width - width) // 2, (new_height - height) // 2)
    new_image.paste(image, offset)
    return new_image
def add_blured_background(image,width,height):
    blurred_image = image.filter(ImageFilter.GaussianBlur(40))
    new_image=blurred_image.resize((int(width*2), int(height*2)))
    temp_width,temp_height = new_image.size
    offset = ((temp_width - width) // 2, (temp_height - height) // 2)
    new_image.paste(image, offset)
    return new_image
def add_dominant_color_background(image,width,height,new_width,new_height):
    dominant_color = get_dominant_color(image)
    new_image = Image.new("RGB", (new_width, new_height),dominant_color)
    offset = ((new_width - width) // 2, (new_height - height) // 2)
    new_image.paste(image, offset)
    return new_image
def add_dominant_color_circle(image,width,height,new_width,new_height):
    main_colors = get_main_colors(image, num_colors=5)
    dominant_color = (255, 255, 255)
    new_image = Image.new("RGB", (new_width, new_height),dominant_color)
    draw = ImageDraw.Draw(new_image)
    radius = 250
    gap = 200
    center_x = new_width // 2
    center_y = new_height-200-radius
    for i, color in enumerate(main_colors):
        x = center_x - (radius*2 + gap) * (len(main_colors)//2-i)
        y = center_y
        draw.ellipse([(x - radius, y - radius), (x + radius, y + radius)], fill=color)
    offset = ((new_width - width) // 2, (new_height - height) // 2)
    new_image.paste(image, offset)
    return new_image
def add_watermark(image,watermark_path,new_width,new_height):
    watermark = Image.open(watermark_path)
    watermark_width, watermark_height = watermark.size
    new_watermark_size = (watermark_width // 4, watermark_height // 4)
    watermark = watermark.resize(new_watermark_size, Image.ANTIALIAS)
    watermark_x = (new_width - new_watermark_size[0]) // 2
    watermark_y = new_height - new_watermark_size[1] - 100
    watermark_position = (watermark_x, watermark_y)
    image.paste(watermark, watermark_position,watermark if watermark.mode == 'RGBA' else None)
    return image
def add_border(image_path, output_path,watermark_path='',background_kind='',new_width=6000,new_height=6000):
    image = Image.open(image_path)
    width, height = image.size
    
    if background_kind == 'dominant_color':
        new_image=add_dominant_color_background(image,width,height,new_width,new_height)
    elif background_kind == 'dominant_color_circle':
        new_image=add_dominant_color_circle(image,width,height,new_width,new_height)
    elif background_kind=='blured':
        new_image=add_blured_background(image,width,height)
    elif background_kind=='white':
        new_image=add_wite_border(image,width,height,new_width,new_height)
    temp_width,temp_height = new_image.size
    left = (temp_width - new_width) // 2
    top = (temp_height - new_height) // 2
    right = left + new_width
    bottom = top + new_height
    new_image = new_image.crop((left, top, right, bottom))
    if watermark_path:
        new_image=add_watermark(new_image,watermark_path,new_width,new_height)
    new_image.save(output_path,dpi=(240,240), lossless=True)
def process_images(input_folder, output_folder,watermark_path='',background='4',new_width=6000,new_height=6000,root=None,process_bar=None):
    '''
    :param input_folder: 输入文件夹路径
    :param output_folder: 输出文件夹路径
    :param watermark_path: 水印图片路径
    :param background: 背景类型，1:dominant_color,2:dominant_color_circle,3:blured,4:white
    :return:
    '''
    background_kind={'1':'dominant_color',
                     '2':'dominant_color_circle',
                     '3':'blured',
                     '4':'white'}
    star_time=time.time()
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for i, filename in enumerate(os.listdir(input_folder)):
        if filename.endswith((".jpg", ".jpeg", ".png")):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            add_border(input_path, output_path,watermark_path=watermark_path,background_kind=background_kind[background],new_width=new_width,new_height=new_height)
            if root and process_bar:
                process_bar['value']=(i + 1) * 100 // len([f for f in os.listdir(input_folder) if f.endswith((".jpg", ".jpeg", ".png"))])
                root.update_idletasks()
    end_time=time.time()
    print(f"time cost:{end_time-star_time}")
    print('finished')
if __name__ == "__main__":
#Define the input folder path
    input_folder = "2024.11.09Gold 200\ 去色罩"
#Define the output folder path
    output_folder = "2024.11.09Gold 200\加背景3"
#Define the watermark path
    watermark_path=""
#Define the new width of the image
    new_width = 6000#width+200#5800
#Define the new height of the image
    new_height = 6000#height+200#5800
    background_type=input('Choose the background type:\n1:dominant_color\n2:dominant_color_circle\n3:blured\n4:white\n')
    process_images(input_folder, output_folder,background=background_type,watermark_path=watermark_path,new_width=new_width,new_height=new_height)