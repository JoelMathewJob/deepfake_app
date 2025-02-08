from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import os
from transformers import AutoImageProcessor, AutoModelForImageClassification, pipeline
from PIL import Image
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed_frames'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Ensure upload and processed directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Load the deepfake detection model and processor
processor = AutoImageProcessor.from_pretrained("prithivMLmods/Deep-Fake-Detector-Model")
model = AutoModelForImageClassification.from_pretrained("prithivMLmods/Deep-Fake-Detector-Model")
pipe = pipeline("image-classification", model=model, feature_extractor=processor)

def process_video(video_path, output_folder, confidence_threshold=0.5):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": "Could not open video"}

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Adaptive frame skipping strategy
    if total_frames <= 1000:
        frame_skip = max(1, total_frames // 100)  # Capture every 10th frame for small videos
    else:
        frame_skip = max(1, total_frames // 100)  # Capture exactly 100 frames for large videos

    frame_count = 0
    real_scores = []
    fake_scores = []
    frame_indices = []
    anomaly_frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_skip == 0:
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            result = pipe(pil_image)

            if result:
                real_score = next((x['score'] for x in result if x['label'] == 'Real'), 0)
                fake_score = next((x['score'] for x in result if x['label'] == 'Fake'), 0)

                real_scores.append(real_score)
                fake_scores.append(fake_score)
                frame_indices.append(frame_count)

                if fake_score > real_score:
                    frame_filename = f"frame_{frame_count}.jpg"
                    frame_path = os.path.join(output_folder, frame_filename)

                    cv2.putText(
                        frame,
                        f"Real: {real_score:.2f}, Fake: {fake_score:.2f}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255) if fake_score > real_score else (0, 255, 0),
                        2
                    )

                    cv2.imwrite(frame_path, frame)
                    anomaly_frames.append({
                        "frame_index": frame_count,
                        "real_score": real_score,
                        "fake_score": fake_score,
                        "frame_url": f"/processed_frames/{frame_filename}"
                    })

        frame_count += 1

    cap.release()

    output_video_path = os.path.join(output_folder, "output_video.mp4")
    create_output_video(output_folder, output_video_path)

    final_scores = calculate_final_scores(real_scores, fake_scores)

    return {
        "frames_with_anomalies": anomaly_frames,
        "real_scores": real_scores,
        "fake_scores": fake_scores,
        "frame_indices": frame_indices,
        "final_scores": final_scores,
        "output_video_url": f"/processed_frames/output_video.mp4"
    }


def create_output_video(output_folder, output_video_path, frame_rate=30):
    frame_files = sorted([f for f in os.listdir(output_folder) if f.endswith('.jpg')], key=lambda x: int(x.split('_')[1].split('.')[0]))
    if not frame_files:
        return None

    first_frame = cv2.imread(os.path.join(output_folder, frame_files[0]))
    height, width, _ = first_frame.shape

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, frame_rate, (width, height))

    for frame_file in frame_files:
        frame = cv2.imread(os.path.join(output_folder, frame_file))
        out.write(frame)

    out.release()
    return output_video_path

def calculate_final_scores(real_scores, fake_scores):
    total_frames = len(real_scores)  # real_scores and fake_scores have the same length
    real_count = sum(1 for score in real_scores if score > 0.5)
    fake_count = sum(1 for score in fake_scores if score > 0.5)

    real_percentage = (real_count / total_frames) * 100
    fake_percentage = (fake_count / total_frames) * 100

    return {
        "total_frames": total_frames,
        "real_count": real_count,
        "fake_count": fake_count,
        "real_percentage": real_percentage,
        "fake_percentage": fake_percentage
    }

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(video_path)

        # Check if the file was saved
        if not os.path.exists(video_path):
            return jsonify({"error": "Failed to save the file"}), 500

        # Process video and get predictions
        predictions = process_video(video_path, app.config['PROCESSED_FOLDER'])
        return jsonify(predictions)

    except Exception as e:
        traceback.print_exc()  # Log the error for debugging
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/processed_frames/<filename>')
def send_processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True) 