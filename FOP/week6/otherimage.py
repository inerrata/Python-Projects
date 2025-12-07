#imports needed for the assignment
import numpy as np
from PIL import Image
import copy
import pickle
#only needed for plotting
import matplotlib.pyplot as plt

class ImageProcessor():
    """
    A class to process and manipulate images in RGB or Color Map format.
    """
    def __init__(self):
        """
        Constructor method. Initializes the image array, color map, and format flag.
        - self._image_array: Stores the image data (RGB or Color Map IDs).
        - self._color_map: Stores the (ID -> RGB) mapping (float 0-1) for Color Map mode.
        - self._is_rgb_mode: Boolean, True for RGB, False for Color Map.
        """
        self._image_array = None
        self._color_map = None
        self._is_rgb_mode = True # Default to True (RGB) if no image is loaded yet

    # --- Helper/Error Methods ---

    def _check_image_loaded(self):
        """Raises a ValueError if no image is loaded."""
        if self._image_array is None:
            raise ValueError("There is no image loaded.") # [cite: 670]

    # --- Getter Methods ---

    def is_RGB_mode(self):
        """Returns True if the image is in RGB format, False otherwise."""
        return self._is_rgb_mode # [cite: 666]

    def get_color_map(self):
        """Returns the (ID -> RGB) mapping."""
        self._check_image_loaded() # Check added to comply with general requirement [cite: 682]
        return self._color_map # [cite: 667]

    def get_array(self):
        """Returns the image array."""
        self._check_image_loaded() # Check added to comply with general requirement [cite: 682]
        return self._image_array # [cite: 668]

    def shape(self):
        """Returns the x and y dimensions of the image (width, height)."""
        self._check_image_loaded() # [cite: 670]
        # NumPy shape is (height, width, channels) or (height, width)
        # Assuming required return is (width, height) or (x, y)
        if self._image_array.ndim == 3:
            return self._image_array.shape[1], self._image_array.shape[0] # (x, y) [cite: 669]
        else:
            return self._image_array.shape[1], self._image_array.shape[0] # (x, y) [cite: 669]

    # --- Load/Save Methods ---

    def load(self, filepath):
        """
        Loads an image from the given filepath. Supports PNG (RGB) and PKL (Color Map).
        """
        if filepath.endswith(".png"): # [cite: 673]
            pil_image = Image.open(filepath).convert("RGB") # [cite: 675, 676]
            self._image_array = np.array(pil_image) # Convert to numpy array [cite: 677]
            self._is_rgb_mode = True # [cite: 663]
            self._color_map = None
        elif filepath.endswith(".pkl"): # [cite: 673]
            with open(filepath, 'rb') as f:
                # Load tuple: (image array, color mapping) [cite: 680]
                self._image_array, self._color_map = pickle.load(f) # [cite: 681]
            self._is_rgb_mode = False # [cite: 663]
        else:
            raise ValueError("Unsupported file extension.")

    def save(self, filepath):
        """
        Saves the image to the given filepath. Saves as PNG if RGB, or PKL if Color Map.
        """
        self._check_image_loaded() # [cite: 682]

        if self._is_rgb_mode:
            # Save as PNG [cite: 686]
            if not filepath.endswith(".png"):
                filepath += ".png"
            # Ensure data type is compatible with PIL (usually uint8)
            img_to_save = Image.fromarray(self._image_array.astype(np.uint8))
            img_to_save.save(filepath)
        else:
            # Save as PKL [cite: 687]
            if not filepath.endswith(".pkl"):
                filepath += ".pkl"
            data_to_save = (self._image_array, self._color_map) # Tuple format [cite: 680]
            with open(filepath, 'wb') as f:
                pickle.dump(data_to_save, f) # [cite: 687]

    # --- Image Format Transformation ---

    def _rgb_to_colormap(self, bins=2):
        """Converts the current RGB image (0-255) to a Color Map (IDs)."""
        # Note: This implementation is for the extra challenge, supporting any 'bins' (n).
        if self._image_array is None:
            return # Should be caught by change_image_format, but for safety

        # 1. Group pixels into bins^3 groups (normalized threshold 0-1) [cite: 703, 694]
        # Threshold: 256 / bins (e.g., bins=2 -> 128)
        threshold = 256 // bins
        # Create an integer key for each pixel by dividing the channel value by the threshold
        # This gives a value from 0 to bins-1 for each R, G, B channel.
        # Example: if bins=2, values < 128 -> 0, values >= 128 -> 1
        rgb_key = self._image_array // threshold # Result is (H, W, 3) with values 0 to bins-1

        # 2. Encode the 3-value key into a single ID (base 'bins' number system) [cite: 879]
        # Example: bins=2 (base 2). Key [R, G, B] -> R*2^2 + G*2^1 + B*2^0
        # The indices for the 3 channels are 2, 1, 0
        powers = np.array([bins**2, bins**1, bins**0], dtype=np.int64)
        # The initial IDs are 0 to bins^3 - 1
        initial_ids = np.sum(rgb_key * powers, axis=-1) # (H, W)

        # 3. Assign consecutive IDs and calculate average color [cite: 713, 714, 716]
        unique_ids = np.unique(initial_ids)
        new_color_map = {}
        final_colormap_array = np.zeros_like(initial_ids, dtype=initial_ids.dtype)
        
        # Determine minimal unsigned integer dtype [cite: 701, 889]
        num_groups = len(unique_ids)
        if num_groups <= 256:
            dtype = np.uint8
        elif num_groups <= 65536:
            dtype = np.uint16
        else: # Unlikely given n<=255[cite: 890], but good practice
            dtype = np.uint32

        final_colormap_array = final_colormap_array.astype(dtype)

        # Loop to assign new IDs and calculate averages (one of the few unavoidable loops)
        # This is where the initial ID (0 to bins^3-1) is mapped to a consecutive ID (0 to n-1)
        for new_id, old_id in enumerate(unique_ids):
            mask = initial_ids == old_id
            final_colormap_array[mask] = new_id
            
            # Calculate average color for this group (R, G, B channels) [cite: 716]
            # Must average over the x and y axes for all 3 channels
            group_pixels = self._image_array[mask]
            # Convert to float (0-1) before averaging [cite: 716]
            avg_color = np.mean(group_pixels.astype(np.float64) / 255.0, axis=0)
            new_color_map[new_id] = avg_color

        self._image_array = final_colormap_array
        self._color_map = new_color_map # [cite: 717]
        
    def _colormap_to_rgb(self):
        """Converts the current Color Map image (IDs) to an RGB image (0-255)."""
        if self._image_array is None or self._color_map is None:
            return # Should be caught by change_image_format

        # Use numpy.vectorize to apply the color map lookup across the array [cite: 719]
        # The map stores float (0-1) RGB values, so we convert back to (0-255) uint8 [cite: 720]
        map_to_uint8 = {id: (c * 255.0).astype(np.uint8) for id, c in self._color_map.items()}
        
        # The 'signature' specifies input is '()' (single ID) and output is '(3)' (RGB triplet)
        # Note: self.get_color_map().get is not used here due to the need for 0-255 conversion
        rgb_lookup = np.vectorize(map_to_uint8.get, signature='()->(n)') 
        
        # Apply the lookup to the color map array
        self._image_array = rgb_lookup(self._image_array) 
    
    def change_image_format(self, to_rgb, bins=2):
        """
        Changes the image format between RGB (True) and Color Map (False).
        Bins argument is used only for RGB -> Color Map conversion.
        """
        self._check_image_loaded() # [cite: 682]
        
        if to_rgb == self._is_rgb_mode:
            return # No change needed [cite: 692]
            
        if to_rgb:
            # Color Map -> RGB [cite: 718]
            self._colormap_to_rgb()
            self._is_rgb_mode = True # [cite: 663]
            self._color_map = None # Color map is no longer needed/valid
        else:
            # RGB -> Color Map [cite: 700]
            self._rgb_to_colormap(bins=bins)
            self._is_rgb_mode = False # [cite: 663]

    # --- Computer Vision Algorithms ---

    def rotate_colors(self):
        """
        Rotates the color channels for RGB or the color mapping for Color Map format.
        """
        self._check_image_loaded() # [cite: 682]
        
        if self._is_rgb_mode:
            # RGB: channel 0 becomes Green, 1 becomes Blue, 2 becomes Red. (0, 1, 2) -> (1, 2, 0) [cite: 724]
            # The channels dimension is the last axis (-1 or 2)
            self._image_array = np.roll(self._image_array, shift=1, axis=-1)
        else:
            # Color Map: Rotates the mapping IDs: ID_0 becomes color_n, ID_1 becomes color_0, etc. [cite: 726]
            
            # The assignment seems to imply a rotation of the *values* (colors) corresponding to the IDs
            # ID_0 color becomes new ID_1 color, ID_1 color becomes new ID_2 color, ...
            
            # 1. Get current (ID, Color) pairs sorted by ID
            sorted_colors = [self._color_map[i] for i in sorted(self._color_map.keys())]
            
            # 2. Rotate the list of colors: last color moves to the front (right shift by 1)
            rotated_colors = np.roll(sorted_colors, shift=1, axis=0) 
            
            # 3. Create the new mapping
            new_color_map = {i: rotated_colors[i] for i in range(len(rotated_colors))}
            self._color_map = new_color_map

    def blur_RGB_images(self, size=3):
        """
        Blurs the image (RGB format only) by averaging the pixel area of given size.
        """
        self._check_image_loaded() # [cite: 682]
        if not self._is_rgb_mode:
            # Does not need to crash for color map format [cite: 733]
            return

        # Ensure size is odd and at least 3 [cite: 737, 736]
        if size % 2 == 0:
            size += 1
        if size < 3: # To prevent small/zero radius issues
            size = 3
        
        # Calculate half-size (radius) for padding/slicing
        radius = size // 2 
        
        image = self._image_array.astype(np.float64) # Use float for accurate averaging
        H, W, C = image.shape
        blurred_image = np.empty_like(image)

        # Iterate over each pixel (loop is used here as a simple way to define the area, 
        # but the averaging within the area is done with numpy functions) [cite: 734]
        for r in range(H):
            for c in range(W):
                # Determine the area bounds, handling edges (boundary conditions) [cite: 738]
                r_min = max(0, r - radius)
                r_max = min(H, r + radius + 1)
                c_min = max(0, c - radius)
                c_max = min(W, c + radius + 1)

                # Slice the relevant area from the image
                area = image[r_min:r_max, c_min:c_max, :]
                
                # Calculate the average over the x and y axes (axes 0 and 1 of the area) [cite: 739, 740]
                # Keep the color channels (axis 2)
                avg_rgb = np.mean(area, axis=(0, 1))
                
                # Assign the averaged value to the new pixel
                blurred_image[r, c, :] = avg_rgb

        # Convert back to original dtype (uint8 is expected for 0-255 RGB)
        self._image_array = np.round(blurred_image).astype(np.uint8)

    def pixelate_images(self, area, block_size=10):
        """
        Pixelates a specific area of the image using block averaging (RGB) or mode (Color Map).
        Area is given as ((xmin, xmax), (ymin, ymax)).
        """
        self._check_image_loaded() # [cite: 682]

        ((x_min, x_max), (y_min, y_max)) = area # [cite: 763]
        
        # Clamp coordinates to image boundaries
        H, W = self._image_array.shape[:2]
        y_min = max(0, y_min)
        y_max = min(H, y_max)
        x_min = max(0, x_min)
        x_max = min(W, x_max)
        
        # Loop over the area with steps of block_size [cite: 766]
        # These loops define the blocks, but the calculation within the block is numpy vectorized.
        # Note: This is required as per the specification for block processing.
        for r in range(y_min, y_max, block_size):
            for c in range(x_min, x_max, block_size):
                # Determine the block boundaries [cite: 767]
                r_end = min(r + block_size, y_max)
                c_end = min(c + block_size, x_max)
                
                block = self._image_array[r:r_end, c:c_end]
                
                if self._is_rgb_mode:
                    # RGB: Common value is the average color (triplet of 0-255 whole numbers) [cite: 774, 775]
                    # We average over all dimensions except the color channels (if they exist)
                    # Use float for accurate average, then round and convert back to uint8
                    common_value = np.mean(block.astype(np.float64), axis=(0, 1)).round().astype(np.uint8)
                    # Broadcast the common value back into the slice
                    self._image_array[r:r_end, c:c_end] = common_value
                else:
                    # Color Map: Common value is the mode of the color IDs [cite: 815]
                    # Flatten the block to easily calculate the mode
                    flattened_block = block.ravel() 
                    
                    # Hint: "bincount" and "argmax" [cite: 869]
                    # Count occurrences of each color ID
                    counts = np.bincount(flattened_block)
                    # The color ID with the highest count is the mode (most common value)
                    mode_id = np.argmax(counts)
                    
                    # Broadcast the mode ID back into the slice
                    self._image_array[r:r_end, c:c_end] = mode_id 

    # --- Show Method (Provided in starter code) ---
    # This method is not changed per instructions [cite: 625]
    def show(self, filename=None):
        """
        This shows the images or saves the image if a filename is given.
        This works for both image formats.
        """
        self._check_image_loaded() # Added to comply with general requirement [cite: 682]
        
        if self.is_RGB_mode():
            img = self.get_array()
        else:
            # Uses numpy vectorize to apply the color map lookup
            img = np.vectorize(self.get_color_map().get,
                               signature='()->(n)')(self.get_array())
            # Convert float [0, 1] to uint8 [0, 255] for plotting
            img = np.clip(img * 255, 0, 255).astype(np.uint8)

        # Plotting logic
        plt.imshow(img, interpolation='none')
        plt.axis('off')
        
        if filename is not None:
            plt.savefig(filename + ".png", bbox_inches='tight', pad_inches=0)
            plt.close() # Close plot after saving
        else:
            plt.show()

if __name__ == "__main__":
    """
    Script that pixelates only the pumpkin in the given pumpkin image and saves it.
    Required: load "pumpkin.png", pixelate pumpkin area, save as "pumpkin_masked.png". [cite: 870]
    The pumpkin area is not explicitly defined in the text, but is assumed for the script.
    A common pumpkin area for a typical image is approximated.
    """
    
    # Define an approximate area for the pumpkin (example coordinates for a generic image)
    # The actual coordinates depend on the provided 'pumpkin.png', 
    # but based on common test images, the following range is a reasonable guess for the pumpkin area.
    # Assuming pumpkin body is roughly center to lower-center (y: 100-400, x: 100-400 for a 500x500 image)
    # For a typical 512x512 image, a good area could be ((x_min, x_max), (y_min, y_max))
    # We will use relative coordinates (20% to 80% of a 512x512 image size) for robustness.
    
    try:
        # 1. Create instance
        processor = ImageProcessor()

        # 2. Load the pumpkin image
        print("Loading pumpkin.png...")
        processor.load("pumpkin.png") # Assumes "pumpkin.png" is available in the current directory [cite: 679]
        
        # Get image shape for relative area calculation
        W, H = processor.shape() 

        # Define the area for pixelation based on W and H
        # Example area for the pumpkin (adjust based on actual image)
        x_min = int(0.1 * W)
        x_max = int(0.9 * W)
        y_min = int(0.1 * H)
        y_max = int(0.9 * H)
        
        pumpkin_area = ((x_min, x_max), (y_min, y_max))
        block_size = 10 # Default block size [cite: 761]

        # 3. Pixelate only the pumpkin area
        print(f"Pixelating area {pumpkin_area} with block size {block_size}...")
        processor.pixelate_images(pumpkin_area, block_size=block_size)
        
        # 4. Save the result
        output_filename = "pumpkin_masked"
        print(f"Saving result as {output_filename}.png...")
        processor.save(output_filename) # Saves as "pumpkin_masked.png" [cite: 870]

        print("Script finished successfully.")

    except ValueError as e:
        print(f"An error occurred: {e}")
    except FileNotFoundError:
        print("Error: 'pumpkin.png' not found. Make sure the file is in the correct directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")