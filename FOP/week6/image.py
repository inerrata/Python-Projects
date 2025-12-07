# imports needed for the assignment
import numpy as np
from PIL import Image
import copy
import pickle

# only needed for plotting
import matplotlib.pyplot as plt

class ImageProcessor():
    # Your methods here
    
    # Constructor
    def __init__(self):
        self.image = None
        self.colour_map = None
        self.rgb_mode = True

    # Getter
    def is_RGB_mode(self):
        return self.rgb_mode
    
    def get_colour_map(self):
        return self.colour_map
    
    def get_array(self):
        self.image
        
    def shape(self):
        if self.image is None:  # If there is no image, tell user there is no image
            return ValueError("No image loaded")
        return self.image.shape
    
    # Load 
    def load(self, filepath):
        if filepath.endswith(".png"):
            img = Image.open(filepath).convert("RGB")
            self.image = np.array(img)
            self.colour_map = None
            self.rgb_mode = True
        
        elif filepath.endswith(".pkl"):
            with open(filepath, "rb") as f:
                data = pickle.load(f)
            self.image, self.colour_map = data
            self.rgb_mode = False
        
        else:
            raise ValueError("Unsupported file format")
        
    # Save
    def save(self, filepath):
        self.__assert_loaded()
        
        if self.rgb_mode:
            # Making sure the image has a .png
            if not filepath.endwith(".png"):
                filepath += ".png"
            Image.fromarray(self.image.astype(np.uint8)).save(filepath)
        
        else:
            if not filepath.endswith(".pkl"):
                filepath += ".pkl"
            with open(filepath, "wb") as f:
                pickle.dump((self.image, self.colour_map, f))
            
    # Change Format
    def change_image_format(self, to_rgb, bins=2):
        self.__assert_loaded()
        
        # Nothing to do
        if to_rgb == self.rgb_mode:
            return
        
        # CMAP to RGB
        if to_rgb and not self.rgb_mode:
            vec = np.vectorize(self.colour_map.get, signature='(()->(n))')
            self.image = vec(self.image).astype(np.uint8)
            self.colour_map = None
            self.rgb_mode = True
            return
        
        # RGB to CMAP
        
    def show(self, filename=None):
        """
        This shows the images or saves the image if an filename is given.
        This works for both image formats.
        """
        if self.is_RGB_mode():
            img = self.get_array()
        else:
            img = np.vectorize(self.get_color_map().get, signature='()->(n)')(self.get_array())

        plt.imshow(img, interpolation='none')
        plt.axis('off')
        if filename is not None:
            plt.savefig(filename + ".png", bbox_inches='tight', pad_inches=0)
        else:
            plt.show()

if __name__ == "__main__":
    # Script code here
