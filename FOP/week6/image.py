# imports needed for the assignment
import numpy as np
from PIL import Image
import pickle


class ImageProcessor():
    def __init__(self):
        self._image_array = None
        self._color_map = None
        self._is_rgb_mode = None

    def _check_image_loaded(self):
        """Raises a ValueError if no image is currently loaded."""
        if self._image_array is None:
            raise ValueError("There is no image loaded.")

    #   Getter Methods

    def is_RGB_mode(self):
        """Returns True for RGB format, False for color map format."""
        return self._is_rgb_mode

    def get_color_map(self):
        """Returns the (ID->RGB) mapping"""
        return self._color_map

    def get_array(self):
        """Returns the image array."""
        return self._image_array

    def shape(self):
        """Returns the (width, height) dimensions (x, y) of the image."""
        self._check_image_loaded()
        # Shape is (height, width, channels) or (height, width)
        return (self._image_array.shape[:2])

    # Load/Save Methods

    def load(self, filepath):
        filepath_lower = filepath.lower()
        if filepath_lower.endswith('.png'):
            img_pil = Image.open(filepath).convert("RGB")
            self._image_array = np.array(img_pil)
            self._is_rgb_mode = True
            self._color_map = None
        elif filepath_lower.endswith('.pkl'):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            if not isinstance(data, tuple) or len(data) != 2:
                raise TypeError(
                    "Pickle file does not contain the expected "
                    "(image_array, color_map) tuple."
                )
            self._image_array, self._color_map = data
            self._is_rgb_mode = False
        else:
            raise ValueError(
                f"Unsupported file extension. "
                f"Must end with .png or .pkl: {filepath}"
            )

    def save(self, filepath):
        """Saves the current image (PNG for RGB, PKL for color map)."""
        self._check_image_loaded()
        if self.is_RGB_mode():
            img_to_save = Image.fromarray(self._image_array.astype(np.uint8))
            img_to_save.save(filepath + ".png")
        else:
            data_to_save = (self._image_array, self._color_map)
            with open(filepath + ".pkl", 'wb') as f:
                pickle.dump(data_to_save, f)

    # Transformation Methods
    
    def _rgb_to_colormap(self, bins=2):
        rgb_array = self._image_array
        num_groups = bins ** 3
        if num_groups <= 256:
            id_dtype = np.uint8
        elif num_groups <= 65536:
            id_dtype = np.uint16
        else:
            id_dtype = np.uint32

        step = 256 / bins
        bin_indices = (rgb_array // step).astype(np.uint8)

        cube_ids_full_range = (
            bin_indices[..., 0] * (bins ** 2) +
            bin_indices[..., 1] * bins +
            bin_indices[..., 2]
        ).astype(id_dtype)
        unique_cube_ids = np.unique(cube_ids_full_range)

        colormap_image = np.searchsorted(
            unique_cube_ids,
            cube_ids_full_range
        ).astype(id_dtype)

        color_map = {}
        for new_id, old_id in enumerate(unique_cube_ids):
            mask = (cube_ids_full_range == old_id)
            avg_color = np.mean(
                rgb_array[mask].astype(np.float64),
                axis=0
            ) / 255.0
            avg_color = np.round(avg_color, 6)
            color_map[new_id] = avg_color

        self._image_array = colormap_image
        self._color_map = color_map
        self._is_rgb_mode = False

    def _colormap_to_rgb(self):
        ids = self._image_array
        color_map = self._color_map

        H, W = ids.shape
        rgb = np.zeros((H, W, 3), dtype=np.uint8)

        for id_val, color in color_map.items():
            mask = (ids == id_val)
            rgb[mask] = np.floor(np.array(color) * 255).astype(np.uint8)

        self._image_array = rgb
        self._color_map = None
        self._is_rgb_mode = True

    def change_image_format(self, to_rgb, bins=2):
        """Transforms the image between RGB and color map format."""
        self._check_image_loaded()
        if to_rgb == self.is_RGB_mode():
            return

        if to_rgb:
            self._colormap_to_rgb()
        else:
            self._rgb_to_colormap(bins=bins)

    # Computer Vision Methods
    
    def rotate_colors(self):
        """
        Rotates the color channels (RGB) or rotates color_map values
        (color map mode).
        """
        self._check_image_loaded()

        if self.is_RGB_mode():
            # Rotate with -1 instead of 1 to match assignment needs
            self._image_array = np.roll(self._image_array, shift=-1, axis=2)
        else:
            # Colormap: rotate values in dictionary
            old_map = self._color_map
            keys = sorted(old_map.keys())
            n = len(keys)

            new_map = {}
            for i, k in enumerate(keys):
                new_key = keys[(i + 1) % n]  # rotate forward
                new_map[new_key] = old_map[k]

            self._color_map = new_map

    def blur_RGB_images(self, size=3):
        """Blurs RGB image by averaging area around each pixel (RGB only)."""
        self._check_image_loaded()
        if not self.is_RGB_mode():
            return

        if size % 2 == 0:
            size += 1  # make it odd

        H, W, C = self._image_array.shape
        radius = size // 2

        # Convert to int32 to prevent overflow during summation
        img_int = self._image_array.astype(np.int32)

        # Create output array
        result = np.zeros((H, W, C), dtype=np.int32)

        # Use sliding window WITHOUT padding - only average existing pixels
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                # Calculate valid slice ranges
                y_start = max(0, dy)
                y_end = min(H, H + dy)
                x_start = max(0, dx)
                x_end = min(W, W + dx)

                # Corresponding slice in source image
                src_y_start = max(0, -dy)
                src_y_end = min(H, H - dy)
                src_x_start = max(0, -dx)
                src_x_end = min(W, W - dx)

                # Add the shifted slice to the accumulator
                result[y_start:y_end, x_start:x_end] += \
                    img_int[src_y_start:src_y_end, src_x_start:src_x_end]

        # Compute the number of pixels averaged for each position
        count = np.zeros((H, W), dtype=np.int32)
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                y_start = max(0, dy)
                y_end = min(H, H + dy)
                x_start = max(0, dx)
                x_end = min(W, W + dx)
                count[y_start:y_end, x_start:x_end] += 1

        # Divide by count for each channel (integer division)
        self._image_array = (result // count[:, :, np.newaxis]).astype(
            np.uint8
        )

    def pixelate_images(self, area, block_size=10):
        """Pixelates a specific area of the image."""
        self._check_image_loaded()
        ((x_start, x_end), (y_start, y_end)) = area
        if block_size < 1:
            return

        # Use .copy() for a mutable array
        current_array = self._image_array.copy()

        # Loops iterate over the blocks
        for y in range(y_start, y_end, block_size):
            for x in range(x_start, x_end, block_size):
                y_e = min(y + block_size, y_end)
                x_e = min(x + block_size, x_end)
                block = self._image_array[y:y_e, x:x_e]

                if block.size == 0:
                    continue

                if self.is_RGB_mode():
                    # RGB: Common value is the average color
                    common_value = np.mean(
                        block.astype(np.float32),
                        axis=(0, 1)
                    ).astype(np.uint8)
                else:
                    # Color Map: Common value is the mode
                    common_value = np.argmax(np.bincount(block.ravel()))

                # Apply the common value to the block in the copy
                current_array[y:y_e, x:x_e] = common_value

        self._image_array = current_array

# Main Script

if __name__ == "__main__":
    ip = ImageProcessor()

    try:
        ip.load("pumpkin.png")
    except FileNotFoundError:
        print("Error: 'pumpkin.png' not found. Cannot run script.")

    # Determine the area of the pumpkin to pixelate.
    width, height = ip.shape()

    x_min_p = width // 4
    x_max_p = width * 3 // 4
    y_min_p = height // 4
    y_max_p = height * 3 // 4

    pumpkin_area = ((x_min_p, x_max_p), (y_min_p, y_max_p))

    # Pixelate the determined area (the pumpkin) with default block size (10)
    ip.pixelate_images(pumpkin_area)

    # Save the result as "pumpkin_masked.png"
    ip.save("pumpkin_masked")
    print("Successfully generated and saved 'pumpkin_masked.png'.")
