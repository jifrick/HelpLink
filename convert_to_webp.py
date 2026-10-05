from PIL import Image
import os

images = [
    "app/static/images/logo.png",
    "app/static/images/hero-artwork.png"
]

for img_path in images:
    if os.path.exists(img_path):
        webp_path = img_path.rsplit('.', 1)[0] + '.webp'
        print(f"Converting {img_path} to {webp_path}")
        with Image.open(img_path) as im:
            im.save(webp_path, format="webp", quality=90)
        # Optionally remove the original png
        os.remove(img_path)
    else:
        print(f"{img_path} not found")
