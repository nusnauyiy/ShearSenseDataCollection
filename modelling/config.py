from modelling.util import ascii_to_gesture

SEED_CONSTANT = 23
CLASSES_LIST = ascii_to_gesture.values()
NUM_CLASSES = len(CLASSES_LIST)

IMG_HEIGHT = 60
IMG_WIDTH = 60
MAX_IMGS_PER_CLASS = 1000
DATA_DIR = "video_data"

NUM_EPOCHS = 30
BATCH_SIZE = 8
