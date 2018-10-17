class Object_Category_Type():
    BACKGROUND = 'BACKGROUND'
    # VOC class ids
    AEROPLANE = 'AEROPLANE'
    BICYCLE = 'BICYCLE'
    BIRD = 'BIRD'
    BOAT = 'BOAT'
    BOTTLE = 'BOTTLE'
    BUS = 'BUS'
    CAR = 'CAR'
    CAT = 'CAT'
    CHAIR = 'CHAIR'
    COW = 'COW'
    DININGTABLE = 'DININGTABLE'
    DOG = 'DOG'
    HORSE = 'HORSE'
    MOTORBIKE = 'MOTORBIKE'
    PERSON = 'PERSON'
    POTTEDPLANT = 'POTTEDPLANT'
    SHEEP = 'SHEEP'
    SOFA = 'SOFA'
    TRAIN = 'TRAIN'
    TVMONITOR = 'TVMONITOR'
    # Pascal CONTEXT class ids
    BAG = 'BAG'
    BED = 'BED'
    BENCH = 'BENCH'
    BOOK = 'BOOK'
    BUILDING = 'BUILDING'
    CABINET = 'CABINET'
    CEILING = 'CEILING'
    CLOTHES = 'CLOTHES'
    COMPUTER = 'COMPUTER'
    CUP = 'CUP'
    DOOR = 'DOOR'
    FENCE = 'FENCE'
    FLOOR = 'FLOOR'
    FLOWER = 'FLOWER'
    FOOD = 'FOOD'
    GRASS = 'GRASS'
    GROUND = 'GROUND'
    KEYBOARD = 'KEYBOARD'
    LIGHT = 'LIGHT'
    MOUNTAIN = 'MOUNTAIN'
    MOUSE = 'MOUSE'
    CURTAIN = 'CURTAIN'
    PLATFORM = 'PLATFORM'
    SIGN = 'SIGN'
    PLATE = 'PLATE'
    ROAD = 'ROAD'
    ROCK = 'ROCK'
    SHELVES = 'SHELVES'
    SIDEWALK = 'SIDEWALK'
    SKY = 'SKY'
    SNOW = 'SNOW'
    BEDCLOTH = 'BEDCLOTH'
    TRACK = 'TRACK'
    TREEE = 'TREEE'
    TRUCK = 'TRUCK'
    WALL = 'WALL'
    WATER = 'WATER'
    WINDOW = 'WINDOW'
    WOOD = 'WOOD'

object_category_type_to_custom_id = {
    'BACKGROUND' : 0,
    'CAR' : 7,              # pascal mapping
    'BOAT' : 4,             # pascal mapping
    'PERSON' : 15,          # pascal mapping
    'FLOOR' : 33,           # pascal mapping
    'GRASS' : 36,           # pascal mapping
    'GROUND' : 37,          # pascal mapping
    'PLATFORM' : 43,        # pascal mapping
    'ROAD' : 46,            # pascal mapping
    'SIDEWALK' : 49,        # pascal mapping
    'TRACK' : 53            # pascal mapping

}
object_category_custom_id_to_type = {
    v: k for k, v in object_category_type_to_custom_id.iteritems()}

object_category_type_to_microsoft_coco_id = {
    'BACKGROUND' : 0,
    'PERSON' : 1,
    'BICYCLE' : 2,
    'CAR': 3,
    'MOTORCYCLE' : 4,
    'AIRPLANE' : 5,

    'BUS' : 6,
    'TRAIN' : 7,
    'TRUCK' : 8,
    'BOAT' : 9,
    'TRAFFIC LIGHT': 10,
    'FIRE HYDRANT' : 11,

    'STOP SIGN' : 12,
    'PARKING METER' : 13,
    'BENCH' : 14,
    'BIRD' : 15,
    'CAT' : 16,
    'DOG' : 17,
    'HORSE' : 18,

    'SHEEP' : 19,
    'COW' : 20,
    'ELEPHANT' : 21,
    'BEAR' : 22,
    'ZEBRA' : 23,
    'GIRAFFE' : 24,
    'BACKPACK' : 25,

    'UMBRELLA' : 26,
    'HANDBAG' : 27,
    'TIE' : 28,
    'SUITCASE' : 29,
    'FRISBEE' : 30,
    'SKIS' : 31,

    'SNOWBOARD' : 32,
    'SPORTS BALL' : 33,
    'KITE' : 34,
    'BASEBALL BAT' : 35,
    'BASEBALL GLOVE' : 36,

    'SKATEBOARD' : 37,
    'SURFBOARD' : 38,
    'TENNIS RACKET' : 39,
    'BOTTLE' : 40,
    'WINE GLASS' : 41,

    'CUP' : 42,
    'FORK' : 43,
    'KNIFE' : 44,
    'SPOON' : 45,
    'BOWL' : 46,
    'BANANNA' : 47,
    'APPLE' : 48,
    'SANDWICH' : 49,

    'ORANGE' : 50,
    'BROCCOLI' : 51,
    'CARROT' : 52,
    'HOT DOG' : 53,
    'PIZZA' : 54,
    'DONUT' : 55,
    'CAKE' : 56,

    'CHAIR' : 57,
    'COUCH' : 58,
    'POTTED PLANT' : 59,
    'BED' : 60,
    'DINING TABLE' : 61,
    'TOILET' : 62,
    'TV' : 63,

    'LAPTOP' : 64,
    'MOUSE' : 65,
    'REMOTE' : 66,
    'KEYBOARD' : 67,
    'CELL PHONE' : 68,
    'MICROWAVE' : 69,

    'OVEN' : 70,
    'TOASTER' : 71,
    'SINK' : 72,
    'REFRIGERATOR' : 73,
    'BOOK' : 74,
    'CLOCK' : 75,
    'VASE' : 76,

    'SCISSORS' : 77,
    'TEDDY BEAR': 78,
    'HAIR DRIER': 79,
    'TOOTH BRUSH' : 80
}

object_category_microsoft_coco_id_to_type = {
    v: k for k, v in object_category_type_to_microsoft_coco_id.iteritems()}

object_category_type_to_pascal_voc_id = {
    'BACKGROUND' : 0,
    # VOC class ids
    'AEROPLANE' : 1,
    'BICYCLE' : 2,
    'BIRD' : 3,
    'BOAT' : 4,
    'BOTTLE' : 5,
    'BUS' : 6,
    'CAR' : 7,
    'CAT' : 8,
    'CHAIR' : 9,
    'COW' : 10,
    'DININGTABLE' : 11,
    'DOG' : 12,
    'HORSE' : 13,
    'MOTORBIKE' : 14,
    'PERSON' : 15,
    'POTTEDPLANT' : 16,
    'SHEEP' : 17,
    'SOFA' : 18,
    'TRAIN' : 19,
    'TVMONITOR' : 20,
    # Pascal CONTEXT class ids
    'BAG' : 21,
    'BED' : 22,
    'BENCH' : 23,
    'BOOK' : 24,
    'BUILDING' : 25,
    'CABINET' : 26,
    'CEILING' : 27,
    'CLOTHES' : 28,
    'COMPUTER' : 29,
    'CUP' : 30,
    'DOOR' : 31,
    'FENCE' : 32,
    'FLOOR' : 33,
    'FLOWER' : 34,
    'FOOD' : 35,
    'GRASS' : 36,
    'GROUND' : 37,
    'KEYBOARD' : 38,
    'LIGHT' : 39,
    'MOUNTAIN' : 40,
    'MOUSE' : 41,
    'CURTAIN' : 42,
    'PLATFORM' : 43,
    'SIGN' : 44,
    'PLATE' : 45,
    'ROAD' : 46,
    'ROCK' : 47,
    'SHELVES' : 48,
    'SIDEWALK' : 49,
    'SKY' : 50,
    'SNOW' : 51,
    'BEDCLOTH' : 52,
    'TRACK' : 53,
    'TREEE' : 54,
    'TRUCK' : 55,
    'WALL' : 56,
    'WATER' : 57,
    'WINDOW' : 58,
    'WOOD' : 59
}

object_category_pascal_voc_id_to_type = {
    v: k for k, v in object_category_type_to_pascal_voc_id.iteritems()}