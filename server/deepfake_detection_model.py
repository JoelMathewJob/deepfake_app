import cv2
import os
import matplotlib.pyplot as plt
from transformers import AutoImageProcessor, AutoModelForImageClassification, pipeline
from PIL import Image

# Load the deepfake detection model and processor
processor = AutoImageProcessor.from_pretrained("prithivMLmods/Deep-Fake-Detector-Model")
model = AutoModelForImageClassification.from_pretrained("prithivMLmods/Deep-Fake-Detector-Model")
pipe = pipeline("image-classification", model=model, feature_extractor=processor)

def process_video(video_path, output_folder, frame_skip=100, confidence_threshold=0.5):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
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

                if real_score >= confidence_threshold or fake_score >= confidence_threshold:
                    real_scores.append(real_score)
                    fake_scores.append(fake_score)
                    frame_indices.append(frame_count)

                    if fake_score > real_score:
                        anomaly_frames.append({
                            "frame_index": frame_count,
                            "real_score": real_score,
                            "fake_score": fake_score
                        })

        frame_count += 1

    cap.release()

    # Plot the scores (for the graph)
    print(real_score)
    plot_scores(real_scores, fake_scores, frame_indices)

    # Calculate the final results
    final_scores = calculate_final_scores(real_scores, fake_scores)

    return {
        "frames_with_anomalies": anomaly_frames,
        "real_scores": real_scores,
        "fake_scores": fake_scores,
        "frame_indices": frame_indices,
        "final_scores": final_scores
    }

def plot_scores(real_scores, fake_scores, frame_indices):
    plt.figure(figsize=(12, 6))
    plt.plot(frame_indices, real_scores, label="Real", marker="o", color="green", linestyle="--")
    plt.plot(frame_indices, fake_scores, label="Fake", marker="x", color="red", linestyle="--")
    plt.title("Deepfake Detection Scores Across Video Frames")
    plt.xlabel("Frame Index")
    plt.ylabel("Confidence Score")
    plt.legend()
    plt.grid()
    plt.show()

def calculate_final_scores(real_scores, fake_scores):
    total_frames = len(real_scores) + len(fake_scores)
    if total_frames == 0:
        return {"error": "No frames with valid scores detected."}

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
