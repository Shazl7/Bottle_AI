
# Bottle AI — YOLOv8 Inspection Module

**Real-time bottle inspection using Python, YOLOv8, OpenCV, and optional Blynk IoT integration.**

## Project overview

Bottle AI is the **computer-vision part** of a larger automated bottle-filling and capping system. The complete project covers three areas:

| Module | Role |
| --- | --- |
| Computer Vision | Inspect bottle images with YOLOv8 and report predicted classes. |
| Embedded Software | Coordinate bottle detection, filling, transfer, capping, counting, and safety logic. |
| IoT | Use an ESP32 and Blynk Cloud for machine monitoring and control. |

**Repository scope:** This repository contains the Python inspection application, **not** the complete machine firmware or embedded controller software.

The project presentation describes the categories **Full Bottle**, **Empty Bottle**, and **Bottle Without Cap**. The exact available labels depend on the trained weights (`best.pt`).

## What the Python program does

- Captures frames from a webcam (default camera index: `0`) or a configurable camera stream.
- Runs a custom YOLOv8 object-detection model on each frame.
- Displays bounding boxes, a predicted class, and the confidence score.
- Reports the **highest-confidence detection** when multiple objects are visible.
- Optionally updates three Blynk virtual pins:

| Blynk pin | Data |
| --- | --- |
| `V10` | Predicted class, or `No Detection` |
| `V11` | Confidence as a percentage (0–100) |
| `V12` | Camera status (`Online`, `Offline`, or `Stopped`) |

To reduce repeated requests, `V10` and `V11` are updated **when the predicted class changes**, not on every frame. Blynk integration is optional; without a token, video detection still works locally.

## Repository layout

```text
Bottle_AI/
├── live_webcam_blynk.py   # Main vision application
├── requirements.txt       # Python dependencies
├── .env.example           # Example configuration (no real secrets)
├── .gitignore             # Excludes secrets, datasets and model weights
├── README.md              # This documentation
└── models/
    └── README.txt         # Put best.pt in this folder locally
```

The developer's `train/`, `valid/`, `test/`, `runs/`, and `yolo_env/` folders are excluded from Git by default. A local `data.yaml` can be shared separately after verifying its paths and dataset rights.

## Quick start (Windows / PowerShell)

**1. Clone and enter the repository**

```powershell
git clone https://github.com/Shazl7/Bottle_AI.git
cd Bottle_AI
```

**2. Set up Python** (Python 3.10+ recommended)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**3. Add the trained model**

Copy the trained YOLOv8 `best.pt` from your training output (for example, `runs/detect/train/weights/best.pt`) into:

```text
models/best.pt
```

Model weights are **not** committed to this repository. If published and permitted by their license, download the matching `best.pt` from the project's GitHub Releases page and place it in `models/`.

**4. Configure the camera and Blynk**

```powershell
Copy-Item .env.example .env
```

Edit `.env`:

```dotenv
MODEL_PATH=models/best.pt
CAMERA_SOURCE=0
CONFIDENCE=0.55
BLYNK_SERVER=https://blynk.cloud
BLYNK_AUTH_TOKEN=
```

Use a **new** Blynk token obtained from your own device: paste it after `BLYNK_AUTH_TOKEN=` in the local `.env` file. To run locally without Blynk, leave `BLYNK_AUTH_TOKEN` blank. For an ESP32-CAM HTTP stream, set `CAMERA_SOURCE` to its accessible stream URL instead of `0`.

**5. Start inspection**

```powershell
python live_webcam_blynk.py
```

Press **Q** to close the live detection window.

## Dataset and model training

The computer-vision project presentation describes a custom dataset with approximately **120–150 images per class**, gathered using varied lighting, backgrounds, and camera angles. Its workflow covers collection, annotation, train/validation/test splitting, data augmentation, YOLOv8 training, and evaluation.

Metrics described in the presentation include precision, recall, mAP50, F1 score, loss curves, and a confusion matrix. **No numerical evaluation results are claimed here**, because the training outputs were not supplied for verification.

## Publication and security

- **Never publish your Blynk device authentication token.** Use a local `.env` file, which is ignored by Git.
- **Regenerate any token previously copied into messages or source files before public release.**
- Review `data.yaml` for private local paths before publishing it.
- Keep raw images, local virtual environments, and training output out of the main repository unless intentionally distributing them.
- Share a trained model separately through a GitHub Release only after checking the rights and license for the model and data.
- If a secret has already been committed, removing it from the latest source file is **not enough**: rotate it and address Git history.

## Limitations

- Only the highest-confidence detected object is reported to Blynk, even if several bottles are in view.
- Confidence updates are sent when the **class changes**, not continuously.
- Model accuracy and processing speed depend on the camera, training data, weights, and computer hardware.
- This repository does not include the firmware for the filling, conveyor, capping, and protection functions.


## Blynk IoT Configuration

To enable real-time monitoring through Blynk:

1. Go to [Blynk Cloud](https://blynk.cloud).
2. Sign in and create or select your device.
3. Copy your device's Auth Token.
4. Open `live_webcam_blynk.py`.
5. Find the following line:

   `BLYNK_TOKEN = ""`

6. Insert your Auth Token between the quotation marks.
7. Configure the following Blynk Datastreams:

| Virtual Pin | Description |
|---|---|
| V10 | Detected Bottle Class |
| V11 | Detection Confidence (%) |
| V12 | Camera Status |

8. Save the file and run the application.

**Security Note:** Never publish your real Blynk Auth Token on GitHub. Keep the token in your local copy only.