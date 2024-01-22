import ultimateAlprSdk
import argparse
import json
import os.path
import cv2
import datetime
import psycopg2
import requests
import io
import base64
import numpy
from PIL import Image

MODE = 1
PLATE_LEN_MODE_0 = 10
PLATE_LEN_MODE_1 = 7
API_ENDPOINT = "http://192.168.212.190:1880/api/verbalization"
TAG = "[PythonRecognizer] "

REASON_PLATE = "Not authorized plate"
REASON_MODEL = "Invalid car model"

# Defines the default JSON configuration. More information at https://www.doubango.org/SDKs/anpr/docs/Configuration_options.html
JSON_CONFIG = {
    "debug_level": "error",
    "debug_write_input_image_enabled": False,
    "debug_internal_data_path": ".",

    "num_threads": -1,
    "gpgpu_enabled": True,
    "max_latency": -1,

    "klass_vcr_gamma": 1.5,

    "detect_roi": [0, 0, 0, 0],
    "detect_minscore": 0.1,

    "car_noplate_detect_min_score": 0.8,

    "pyramidal_search_enabled": True,
    "pyramidal_search_sensitivity": 0.28,
    "pyramidal_search_minscore": 0.3,
    "pyramidal_search_min_image_size_inpixels": 800,

    "recogn_rectify_enabled": True,
    "recogn_minscore": 0.3,
    "recogn_score_type": "min"
}

IMAGE_TYPES_MAPPING = {
        'RGB': ultimateAlprSdk.ULTALPR_SDK_IMAGE_TYPE_RGB24,
        'RGBA': ultimateAlprSdk.ULTALPR_SDK_IMAGE_TYPE_RGBA32,
        'L': ultimateAlprSdk.ULTALPR_SDK_IMAGE_TYPE_Y
}

# Connexion à la base de données PostgreSQL
conn = None

# Liste des plaques traitées
PLATE_DONE = []

# Function to handle frame conversion
def load_pil_image_from_frame(pil_image):
    if pil_image.mode in IMAGE_TYPES_MAPPING:
        imageType = IMAGE_TYPES_MAPPING[pil_image.mode]
    else:
        raise ValueError(TAG + "Invalid mode: %s" % pil_image.mode)

    return pil_image, imageType

# Fonction pour établir la connexion à la base de données
def connectBdd():
    try:
        conn = psycopg2.connect(
            dbname="bfc", 
            user="user", 
            password="password", 
            host="localhost"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

def process_result(result, current_frame):
    if result.isOK():
        result_json = json.loads(result.json())
        if "plates" in result_json:
            for plate in result_json["plates"]:
                cursor = conn.cursor()
                original_plate_text = plate["text"]
                plate_text = plate["text"].rstrip("*") 
                if len(plate_text) != (PLATE_LEN - 1):
                    continue
                
                if plate_text in PLATE_DONE:
                    continue
                    
                PLATE_DONE.append(plate_text)
                
                authorized = True
                reason = REASON_PLATE
                real_plate = plate_text
                    
                cursor.execute("SELECT plate, expiration, model FROM authorizations WHERE LOWER(plate) LIKE LOWER(%s)", (plate_text + '%',))
                auth = cursor.fetchone()
                if auth is None:
                    print(f"License Plate {original_plate_text} not authorized")
                    authorized = False
                else:
                    plateStr, expiration, model = auth
                    real_plate = plateStr
                    if expiration < datetime.datetime.now():
                        print(f"License Plate {real_plate} not authorization (expired)")
                        authorized = False
                    else:
                        if MODE == 1:
                            if "car" in plate:
                                if "makeModelYear" in plate["car"]:
                                    max_confidence_entry = max(plate["car"]["makeModelYear"], key=lambda x: x['confidence'])
                                    detected_model = max_confidence_entry['make']
                                    valid_model = detected_model == model
                                    if valid_model:
                                        print(f"License Plate {real_plate} is authorized (model: {detected_model} / valid: {valid_model})")
                                    else:
                                        print(f"License Plate {real_plate} is not authorization (model: {detected_model} / valid: {valid_model})")
                                        authorized = False
                                        reason = REASON_MODEL
                                else:
                                    print(f"License Plate {real_plate} is authorized")
                            else:
                                print(f"License Plate {real_plate} is authorized")
                        else:
                            print(f"License Plate {real_plate} is authorized")
                
                if MODE == 1 and authorized == False:
                    try:
                        # Encode the plate and reason for URL
                        plate_encoded = requests.utils.quote(real_plate)
                        reason_encoded = requests.utils.quote(reason)
                        # Convert the PIL image to OpenCV format and then to JPEG
                        open_cv_image = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)
                        retval, buffer = cv2.imencode('.jpg', open_cv_image)
                        jpg_as_text = io.BytesIO(buffer)
                        # Create the full URL with query parameters
                        full_url = f"{API_ENDPOINT}?plate={plate_encoded}&reason={reason_encoded}"
                        # Send the POST request with the image
                        response = requests.post(
                            full_url, 
                            files={"image": ("image.jpg", jpg_as_text, "image/jpeg")}
                        )
                        # Check if the request was successful
                        if response.status_code == 200:
                            print(f"Verbalization sended to the server")
                        else:
                            print(f"API Request failed with status code: {response.status_code}")
                    except requests.RequestException as e:
                        print(f"Error during API request: {e}")
                
        else:
            print("No plate detected")

# Entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    This is the recognizer sample using python language
    """)

    parser.add_argument("--video", required=True, help="Path to the video with ALPR data to recognize")
    parser.add_argument("--assets", required=False, default="../../../assets", help="Path to the assets folder")
    parser.add_argument("--charset", required=False, default="latin", help="Defines the recognition charset (a.k.a alphabet) value (latin, korean, chinese...)")
    parser.add_argument("--car_noplate_detect_enabled", required=False, default=False, help="Whether to detect and return cars with no plate")
    parser.add_argument("--ienv_enabled", required=False, default=False, help="Whether to enable Image Enhancement for Night-Vision (IENV). More info about IENV at https://www.doubango.org/SDKs/anpr/docs/Features.html#image-enhancement-for-night-vision-ienv. Default: true for x86-64 and false for ARM.")
    parser.add_argument("--openvino_enabled", required=False, default=True, help="Whether to enable OpenVINO. Tensorflow will be used when OpenVINO is disabled")
    parser.add_argument("--openvino_device", required=False, default="CPU", help="Defines the OpenVINO device to use (CPU, GPU, FPGA...). More info at https://www.doubango.org/SDKs/anpr/docs/Configuration_options.html#openvino-device")
    parser.add_argument("--npu_enabled", required=False, default=True, help="Whether to enable NPU (Neural Processing Unit) acceleration")
    parser.add_argument("--klass_lpci_enabled", required=False, default=False, help="Whether to enable License Plate Country Identification (LPCI). More info at https://www.doubango.org/SDKs/anpr/docs/Features.html#license-plate-country-identification-lpci")
    parser.add_argument("--klass_vcr_enabled", required=False, default=False, help="Whether to enable Vehicle Color Recognition (VCR). More info at https://www.doubango.org/SDKs/anpr/docs/Features.html#vehicle-color-recognition-vcr")
    parser.add_argument("--klass_vmmr_enabled", required=False, default=False, help="Whether to enable Vehicle Make Model Recognition (VMMR). More info at https://www.doubango.org/SDKs/anpr/docs/Features.html#vehicle-make-model-recognition-vmmr")
    parser.add_argument("--klass_vbsr_enabled", required=False, default=False, help="Whether to enable Vehicle Body Style Recognition (VBSR). More info at https://www.doubango.org/SDKs/anpr/docs/Features.html#vehicle-body-style-recognition-vbsr")
    parser.add_argument("--tokenfile", required=False, default="", help="Path to license token file")
    parser.add_argument("--tokendata", required=False, default="", help="Base64 license token data")
    parser.add_argument("--mode", required=True, default=0, help="Detection mode")
    args = parser.parse_args()

    # Check if video exist
    if not os.path.isfile(args.video):
        raise OSError(TAG + "File doesn't exist: %s" % args.video)
    
    MODE = int(args.mode)
    PLATE_LEN =  PLATE_LEN_MODE_0 if MODE == 0 else PLATE_LEN_MODE_1
    
    if MODE == 1:
        print("Started in verbalization mode")
    else:
        print("Started in information mode")

    # Update JSON options using values from the command args
    JSON_CONFIG["assets_folder"] = args.assets
    JSON_CONFIG["charset"] = args.charset
    JSON_CONFIG["car_noplate_detect_enabled"] = (
        args.car_noplate_detect_enabled == "True")
    JSON_CONFIG["ienv_enabled"] = (args.ienv_enabled == "True")
    JSON_CONFIG["openvino_enabled"] = (args.openvino_enabled == "True")
    JSON_CONFIG["openvino_device"] = args.openvino_device
    JSON_CONFIG["npu_enabled"] = (args.npu_enabled == "True")
    JSON_CONFIG["klass_lpci_enabled"] = (args.klass_lpci_enabled == "True")
    JSON_CONFIG["klass_vcr_enabled"] = (args.klass_vcr_enabled == "True")
    JSON_CONFIG["klass_vmmr_enabled"] = (MODE == 1)
    JSON_CONFIG["klass_vbsr_enabled"] = (args.klass_vbsr_enabled == "True")
    JSON_CONFIG["license_token_file"] = args.tokenfile
    JSON_CONFIG["license_token_data"] = args.tokendata

    # Initialize the engine
    ini_result = ultimateAlprSdk.UltAlprSdkEngine_init(json.dumps(JSON_CONFIG))
    if ini_result.isOK():
        print("Initialization done !")
    else:
        print("Initialization failed !")
        assert False

    conn = connectBdd()

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise Exception(TAG + "Could not open video file: %s" % args.video)

    # Get the original video frame rate
    fps = cap.get(cv2.CAP_PROP_FPS)
    # Calculate the interval for 12 fps
    frame_interval = fps
    # Process video frame by frame
    frame_count=0

    while cap.isOpened():
        ret, frame=cap.read()
        if not ret:
            break

        # Convert frame to PIL Image
        frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image=Image.fromarray(frame)

        frame_count += 1

        if frame_count % frame_interval != 0:
            continue

        # Process frame as before
        # Create a function to handle frame conversion
        image, imageType=load_pil_image_from_frame(pil_image)
        width, height=image.size

        result = ultimateAlprSdk.UltAlprSdkEngine_process(imageType, image.tobytes(), width, height, 0, 1)
        process_result(result, frame)

    # Release video capture
    cap.release()

    # DeInit the engine
    ultimateAlprSdk.UltAlprSdkEngine_deInit()
