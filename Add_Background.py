from PIL import Image, ImageFilter, ImageDraw,ExifTags,ImageFont, ImageOps
from collections import defaultdict
from fractions import Fraction
from datetime import datetime, timezone, timedelta
import re
import os
from sklearn.cluster import KMeans
from collections import Counter
import numpy as np
import time
import math
os.environ['OMP_NUM_THREADS'] = '10'
def parse_iso8601(date_str):
    try:
        return datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
    except ValueError:
        pass
    iso_regex = re.compile(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d+)?(Z|[+-]\d{2}:\d{2})?$')
    match = iso_regex.match(date_str)
    
    if match:
        year, month, day, hour, minute, second, fraction, tz_info = match.groups()
        fraction = fraction or '0'
        fraction = int(fraction)
        new_date_str = f"{year}-{month:02}-{day:02}T{hour:02}:{minute:02}:{second:02}.{fraction:03}"
        if tz_info:
            new_date_str += tz_info
        
        return datetime.fromisoformat(new_date_str).replace(tzinfo=timezone.utc if tz_info is None else None)
    
    raise ValueError("Invalid ISO 8601 format")
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
def add_blured_background(image,width,height, corner_radius=120, shadow_offset=(60, 60), shadow_blur=15):

    blurred_image = image.filter(ImageFilter.GaussianBlur(40))
    new_image = blurred_image.resize((int(width * 2), int(height * 2)))
    temp_width, temp_height = new_image.size

    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        [(0, 0), image.size], corner_radius, fill=255
    )
    rounded_image = ImageOps.fit(image, image.size, centering=(0.5, 0.5))
    rounded_image.putalpha(mask)

    shadow = Image.new("RGBA", (image.width + shadow_offset[0], image.height + shadow_offset[1]), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        [(shadow_blur, shadow_blur), (image.width, image.height)],
        corner_radius,
        fill=(0, 0, 0, 180)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))


    offset = ((temp_width - width) // 2, (temp_height - height) // 2)
    new_image.paste(shadow, (offset[0] + shadow_offset[0] // 2, offset[1] + shadow_offset[1] // 2), shadow)
    new_image.paste(rounded_image, offset, rounded_image)
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
def get_img_xmp(image):
    img_xmp = image.getxmp()
    # print(img_xmp)
    paremeterdic={}
    xmp_data=img_xmp['xmpmeta']['RDF']['Description']
    paremeterdic['LensModel']=xmp_data['LensModel']
    paremeterdic['Model']=xmp_data['Model']
    paremeterdic['FocalLength']=float(Fraction(xmp_data['FocalLength']))
    paremeterdic['FNumber']=float(Fraction(xmp_data['FNumber']))
    paremeterdic['ExposureTime']=float(Fraction(xmp_data['ExposureTime']))
    paremeterdic['ISOSpeedRatings']=int(xmp_data['ISOSpeedRatings']['Seq']['li'])
    paremeterdic['Make']=xmp_data['Make']
    date_str=xmp_data['DateTimeOriginal']
    # try:
    #     date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")
    # except:
    date_obj = parse_iso8601(date_str)
    paremeterdic['DateTimeOriginal']=date_obj.strftime('%Y:%m:%d %H:%M:%S')
    return paremeterdic
def get_img_exif(image):
    img_exif = image._getexif()
    if not img_exif:
        result_dict=get_img_xmp(image)
        return result_dict
    result_dict=defaultdict(str)
    for key, val in img_exif.items():
        if key in ExifTags.TAGS:
            result_dict[ExifTags.TAGS[key]]=val
    return result_dict
def add_Parameter(image):
    parameter_dict=get_img_exif(image)
    width, height = image.size
    lowest_len=min(width,height)
    # self_adative_roit=math.ceil(width*height/(3000*6000)*0.4)
    self_adative_roit=min(width,height)/3500
    watermark = Image.new('RGB', (width, int(lowest_len*0.1)), color=(255, 255, 255))
    watermark_width, watermark_height = watermark.size
    draw = ImageDraw.Draw(watermark)

    Boldfont = ImageFont.truetype("fonts\Roboto-Bold.ttf", int(90*self_adative_roit))
    Lightfont = ImageFont.truetype("fonts\Roboto-Light.ttf", int(70*self_adative_roit))
    #lens
    text = parameter_dict["LensModel"]
    text_position = (int(watermark_height*0.2), int(watermark_height*0.2))
    draw.text(text_position, text, font=Boldfont, fill='black')
    
    #Camera
    text = parameter_dict["Model"]
    text_position = (int(watermark_height*0.2), int(watermark_height)//2+int(10*self_adative_roit)) 
    draw.text(text_position, text, font=Lightfont, fill='gray')
    
    #Parameter
    focal_length=parameter_dict['FocalLength']
    f_number=parameter_dict['FNumber']
    exposure_time = Fraction(parameter_dict['ExposureTime']).limit_denominator() if parameter_dict['ExposureTime'] else 'NA'
    iso=parameter_dict['ISOSpeedRatings']
    para='  '.join([str(focal_length) + 'mm', 'f/' + str(f_number), str(exposure_time)+'s','ISO' + str(iso)])
    _, _, text_width, text_height = Boldfont.getbbox(para)
    text_position = (watermark_width - text_width - int(watermark_height*0.2), int(watermark_height*0.2)) 
    draw.text(text_position, para, font=Boldfont, fill='black') 
    
    #Time
    date=datetime.strptime(parameter_dict['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
    date=date.strftime( '%Y-%m-%d %H:%M')
    text_position = (watermark_width - text_width - int(watermark_height*0.2), int(watermark_height)//2+int(10*self_adative_roit))  # 在图像顶部居中
    draw.text(text_position, date, font=Lightfont, fill='gray')
    
    # Gray line
    draw.line([(watermark_width - text_width - int(50*self_adative_roit) -int(watermark_height*0.2), int(50*self_adative_roit)), (width - text_width - int(50*self_adative_roit) -int(watermark_height*0.2), int(watermark_height)-int(50*self_adative_roit))], fill=(128, 128, 128), width=10)
      
    # logo
    brand=parameter_dict['Make']
    logo_height=int(watermark_height*0.7)
    logo=get_logo(brand)
    logo=resize_image_with_height(logo,logo_height)
    logo_position = (watermark_width - text_width - int(70*self_adative_roit) -logo.size[0]-int(watermark_height*0.2), int((watermark_height-logo.size[1])//2))  # 在图像顶部居中
    watermark.paste(logo, logo_position)
    
    new_img=Image.new('RGB', (width, int(height+watermark_height)), color=(255, 255, 255))
    new_img.paste(image, (0, 0))
    new_img.paste(watermark, (0, height))
    temp_width,temp_height=new_img.size
    new_background=Image.new('RGB', (int(temp_width*1.05), int(temp_height*1.025)), color=(255, 255, 255))
    new_background.paste(new_img, (int(temp_width*0.025), int(temp_height*0.025)))
    return new_background
def resize_image_with_height(image, height):
    width, old_height = image.size

    scale = height / old_height
    new_width = round(width * scale)

    resized_image = image.resize((new_width, height), Image.LANCZOS)
    image.close()

    return resized_image
def get_logo(brand):
    file='logos\\'+brand.lower().split(' ')[0]+'.png'
    logo=Image.open(file)
    return logo
def add_border(image_path, output_path,watermark_path='',background_kind='',new_width=6000,new_height=6000):
    image = Image.open(image_path)
    width, height = image.size
    
    if background_kind == 'dominant_color':
        new_image=add_dominant_color_background(image,width,height,new_width,new_height)
    elif background_kind == 'dominant_color_circle':
        new_image=add_dominant_color_circle(image,width,height,new_width,new_height)
    elif background_kind=='blured':
        new_image=add_blured_background(image,width,height)
        temp_width,temp_height = new_image.size
        left = (temp_width - new_width) // 2
        top = (temp_height - new_height) // 2
        right = left + new_width
        bottom = top + new_height
        new_image = new_image.crop((left, top, right, bottom))
    elif background_kind=='white':
        new_image=add_wite_border(image,width,height,new_width,new_height)
    elif background_kind=='parameter':
        new_image=add_Parameter(image)
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
                     '4':'white',
                     '5':'parameter'}
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