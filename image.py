import os

from PIL import Image, ImageFile


class CustomImage:
    def __init__(self, path, folder="reduced"):
        self.path = path
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        self.image = Image.open(path)
        if self.image.mode in ("RGBA", "P"):
            self.image = self.image.convert('RGB')
        self.width, self.height = self.image.size
        self.reduced_path = os.path.join(os.path.dirname(self.path), folder, os.path.basename(self.path))
        
        
    def reduce_image(self, size=0.5, quality=75):
        new_width = round(self.width * size)
        new_height = round(self.height * size)
        self.image = self.image.resize((new_width,new_height))
        parent_dir = os.path.dirname(self.reduced_path)
        
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        
        self.image.save(self.reduced_path, format='JPEG',quality=quality)
        
        return os.path.exists(self.reduced_path)
         


   
if __name__ == "__main__":
    
    i = CustomImage(r"C:\Users\Jonat\Pictures\Screenshots\Gameboy.png")
    i.reduce_image(size=1,quality=75)
    