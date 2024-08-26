MAIL_SENDER= 'xxx@gmail.com'
PASSWORD = 'xxx'
ADMIN_MAIL = 'xxxx@tttt.it'
IMAP_SERVER = 'imap.gmail.com'

SERVER = 'MOBILEMACHINE\\SQLEXPRESS2022'
DATABASE = 'RobotDatabase'
DB_USERNAME = 'sa'
DB_PASSWORD = 'xxxxxx'
TELEGRAM_TOKEN = '0000068000:AAG6HrufLX4vtLjTwAaIKyIsYelsPXXXXX'
TELEGRAM_MASTER_TARGET = 00000000

connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={DB_USERNAME};PWD={DB_PASSWORD};MARS_Connection=Yes'

TOP_MAIL_TOREAD = 10


PATH_FACE_REC_PEOPLE = "C://Dati//MiniPCKilobot//People"
PATH_TEST_VIDEO = "C:\Dati\MiniPCKilobot\Test_Videos\Test01.mp4"

PATH_OBJ_CLASS_configPath = 'c:/Dati/MiniPCKilobot/TrainedObjData/normalized_input_image_tensor.pbtxt'
PATH_OBJ_CLASS_weightsPath = 'c:/Dati/MiniPCKilobot/TrainedObjData/frozen_inference_graph.pb'
PATH_OBJ_CLASS_classFile = 'c:/Dati/MiniPCKilobot/TrainedObjData/coco_names.txt'

SOCKET_THIS_IS_SERVER_MACHINE = 1 #Set 1 it the server is running here, 0 if here is running only remote: in this case set SOCKET_SERVER_IP_FORCED
SOCKET_USE_LOCALHOST = 0 #Set 1 if all services are running in local machines, set 0 if a PCin LAN is acting as a server
SOCKET_SERVER_LOCALHOST_IP = '127.0.0.1'
SOCKET_SERVER_IP_REMOTE = ''
SOCKET_SERVER_PORT = 55555
SOCKET_BUFFER = 1024*2

ARDUINO_A_COM_PORT = "COM5"
ARDUINO_B_COM_PORT = "COM3"
LIDAR_COM_PORT = "COM10"
LIDAR_BOAD_RATE = 230400

THIS_MACHINE_NAME = "KILOBOT"

PYTHON_EXEC_PATH = 'C:/Users/user/AppData/Local/Programs/Python/Python311/python.exe'
PYTHON_CLIENT_DIR = "c:/Dati/MiniPCKilobot2/"
