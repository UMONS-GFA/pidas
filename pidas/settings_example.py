DATA_FILE = 'data.csv'
DATA_HEADER = "sensorID,value,timestamp"
NB_SENSOR = 8   # Number of fake sensors generated
MEASURE_INTERVAL = 60
LOG_DIR = 'logs/'
PIDAS_DIR = '/home/USERNAME/pidas/pidas'
SIMULATION_MODE = 0
CSV_HEADER = ["sensorID", "sensorName", "value", "timestamp"]
REMOTE_SAVING = True

DATABASE = {
    'HOST': '127.0.0.1',
    'PORT': 8086,
    'USER': '',
    'PASSWORD': '',
    'NAME': ''
}

# messages logging configuration
LOGGING_CONFIG = {
    'debug_mode': False,
    'logging_to_console': False,
    'file_name': 'pidas_log',
    'max_bytes': 262144,
    'backup_count': 30,
    'when': 'D',
    'interval': 1
}

# data logging configuration
DATA_LOGGING_CONFIG = {
    'file_name': 'data_log',
    'max_bytes': 1048576,
    'backup_count': 1024,
    # Settings period to minute overwrite data_log rotating file !!
    'when': 'H',
    'interval': 1,
    'influxdb_logging': True
}


