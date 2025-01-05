const imageUploader = document.getElementById('imageUploader');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const borderSizeInput = document.getElementById('borderSize');
const borderColorInput = document.getElementById('borderColor');
const borderRadiusInput = document.getElementById('borderRadius');
var parameterDict;

var borderSize=100;
var borderColor="#ffffff";
var borderRadius=40;
borderSizeInput.addEventListener('input', () => {
    borderSize = Number(borderSizeInput.value) || 100; 
});

borderColorInput.addEventListener('input', () => {
    borderColor = borderColorInput.value || "#ffffff"; 
});
  borderRadiusInput.addEventListener('input', () => {
    borderRadius = Number(borderRadiusInput.value);
  });
let img = new Image();
const resetImage = () => {
    if (img.src) {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
    }
  };
imageUploader.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            img.src = e.target.result;
            img.onload = async () => {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                parameterDict= await getImgExif(img);
                console.log(parameterDict);
                if (parameterDict.DateTimeOriginal) {
                    const dateParts = parameterDict.DateTimeOriginal.split(' '); // 拆分日期和时间
                    if (dateParts.length === 2) {
                        const [date, time] = dateParts;
                        const formattedDate = date.replace(/:/g, '-'); // 替换日期中的冒号为短横线
                        parameterDict.DateTimeOriginal = `${formattedDate}T${time}`;
                    } else {
                        parameterDict.DateTimeOriginal = null; // 如果解析失败，设置为 null
                    }
                }
                document.getElementById('lensModel').value = parameterDict.LensModel;
                document.getElementById('model').value = parameterDict.Model;
                document.getElementById('focalLength').value = parameterDict.FocalLength;
                document.getElementById('fNumber').value = parameterDict.FNumber;
                document.getElementById('exposureTime').value = parameterDict.ExposureTime;
                document.getElementById('isoSpeedRatings').value = parameterDict.ISOSpeedRatings;
                document.getElementById('make').value = parameterDict.Make;
                document.getElementById('dateTimeOriginal').value = parameterDict.DateTimeOriginal;
            };
        };
        reader.readAsDataURL(file);
        
    }
    
});

document.getElementById('addWhiteBorder').addEventListener('click', () => {
    addWhiteBorder();
});

document.getElementById('addBlurredBackground').addEventListener('click', () => {
    addBlurredBackground();
});

document.getElementById('addDominantColor').addEventListener('click', () => {
    addDominantColorBackground();
});

document.getElementById('saveImage').addEventListener('click', () => {
    const link = document.createElement('a');
    link.download = 'processed_image.png';
    link.href = canvas.toDataURL();
    link.click();
});

function addWhiteBorder() {
    resetImage()
    const newWidth = canvas.width + borderSize;
    const newHeight = canvas.height + borderSize;

    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');
    tempCanvas.width = newWidth;
    tempCanvas.height = newHeight;

    tempCtx.fillStyle = borderColor;
    tempCtx.fillRect(0, 0, newWidth, newHeight);
    tempCtx.drawImage(canvas, borderSize/2, borderSize/2);

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    canvas.width = newWidth;
    canvas.height = newHeight;
    ctx.drawImage(tempCanvas, 0, 0);
}

function addBlurredBackground() {
    resetImage()
    const originWidth = canvas.width;
    const originalHeight = canvas.height;
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');
    tempCanvas.width = canvas.width * 2;
    tempCanvas.height = canvas.height * 2;

    tempCtx.filter = `blur(${borderRadius}px)`;
    tempCtx.drawImage(canvas, 0, 0, tempCanvas.width, tempCanvas.height);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    canvas.width = tempCanvas.width;
    canvas.height = tempCanvas.height;
    ctx.drawImage(tempCanvas, 0, 0);
    ctx.drawImage(img, (tempCanvas.width-originWidth) / 2, (tempCanvas.height-originalHeight) / 2);
    
}


function addDominantColorBackground() {
    resetImage()
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const pixels = imageData.data;
    const colorCounts = {};

    for (let i = 0; i < pixels.length; i += 4) {
        const rgb = `${pixels[i]},${pixels[i + 1]},${pixels[i + 2]}`;
        colorCounts[rgb] = (colorCounts[rgb] || 0) + 1;
    }

    const dominantColor = Object.keys(colorCounts).reduce((a, b) => (colorCounts[a] > colorCounts[b] ? a : b)).split(',');
    const [r, g, b] = dominantColor.map(Number);

    const newWidth = canvas.width + borderSize;
    const newHeight = canvas.height + borderSize;

    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');
    tempCanvas.width = newWidth;
    tempCanvas.height = newHeight;

    tempCtx.fillStyle = `rgb(${r},${g},${b})`;
    tempCtx.fillRect(0, 0, newWidth, newHeight);
    tempCtx.drawImage(canvas, borderSize/2, borderSize/2);

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    canvas.width = newWidth;
    canvas.height = newHeight;
    ctx.drawImage(tempCanvas, 0, 0);
}
async function getImgExif(imageFile) {
    return new Promise((resolve) => {
        EXIF.getData(imageFile, function () {
            const exifData = EXIF.getAllTags(this);
            console.log(exifData);
            resolve({
                LensModel: exifData.LensModel,
                Model: exifData.Model,
                FocalLength: exifData.FocalLength ? `${exifData.FocalLength}` : "N/A",
                FNumber: exifData.FNumber,
                ExposureTime: exifData.ExposureTime,
                ISOSpeedRatings: exifData.ISOSpeedRatings,
                Make: exifData.Make,
                DateTimeOriginal: exifData.DateTimeOriginal,
            });
        });
    });
}
function generateImage() {
    resetImage()
    const form = document.getElementById('parameterForm');
    const formData = new FormData(form);

    const parameters = {
        LensModel: formData.get('lensModel'),
        Model: formData.get('model'),
        FocalLength: parseFloat(formData.get('focalLength')),
        FNumber: parseFloat(formData.get('fNumber')),
        ExposureTime: parseFloat(formData.get('exposureTime')),
        ISOSpeedRatings: parseInt(formData.get('isoSpeedRatings')),
        Make: formData.get('make'),
        DateTimeOriginal: formData.get('dateTimeOriginal'),
    };


    const width = canvas.width;
    const height = canvas.height;
    const watermarkHeight = Math.ceil(Math.min(width, height) * 0.1);
    const self_adative_roit=Math.ceil(width*height/(3000*6000)*0.4)
    canvas.width = width;
    canvas.height = height + watermarkHeight;

    // Draw original image
    ctx.drawImage(img, 0, 0);

    // Draw watermark background
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, height, width, watermarkHeight);

    // Draw text parameters
    const boldFont = "bold 100px Arial";
    const regularFont = "80px Arial";
    ctx.font = boldFont;
    ctx.fillStyle = 'black';

    ctx.fillText(parameters.LensModel, Math.floor(watermarkHeight*0.2), height +  Math.floor(watermarkHeight*0.35));
    const shooting_parameter=`${parameters.FocalLength}mm f/${parameters.FNumber} ${parameters.ExposureTime}s ISO${parameters.ISOSpeedRatings}`;
    const shooting_parameter_text_width= ctx.measureText(shooting_parameter).width
    ctx.fillText(
        shooting_parameter,
        width-shooting_parameter_text_width-Math.floor(watermarkHeight*0.2),
        Math.floor(  height +  watermarkHeight*0.35)
    );

    ctx.font = regularFont;
    ctx.fillStyle = 'gray';
    ctx.fillText(parameters.Model, Math.floor(watermarkHeight*0.2), height + watermarkHeight/1.5+ 10* self_adative_roit);
    const shooting_time_text_width= ctx.measureText(parameters.DateTimeOriginal).width
    ctx.fillText(
        parameters.DateTimeOriginal, 
        width-shooting_time_text_width-Math.floor(watermarkHeight*0.2), 
        height + watermarkHeight/1.5+ 10* self_adative_roit);

    // Example logo (Replace with dynamic logo handling if needed)
    const logo = new Image();
    logo.src = '..\\logos\\nikon.png'; // Placeholder logo
    logo.onload = () => {
        const scale = watermarkHeight * 0.6 / logo.height;
        const logoWidth = logo.width * scale;
        const logoHeight = logo.height * scale;
    
        ctx.drawImage(logo, width - shooting_parameter_text_width - Math.floor(70*self_adative_roit) -Math.floor(watermarkHeight*0.9), height + Math.floor(watermarkHeight *0.2) , logoWidth, logoHeight);
    };
    // await new Promise((resolve) => {
    //     logo.onload = resolve;
    // });
    // const scale = watermarkHeight * 0.6 / logo.height;
    // const logoWidth = logo.width * scale;
    // const logoHeight = logo.height * scale;
    // ctx.drawImage(logo, width - shooting_parameter_text_width - Math.floor(70*self_adative_roit) -Math.floor(watermarkHeight*0.9), height + Math.floor(watermarkHeight *0.2) , logoWidth, logoHeight);
}





