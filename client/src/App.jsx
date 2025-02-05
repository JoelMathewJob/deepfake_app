import React, { useState } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import './App.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const App = () => {
  const [video, setVideo] = useState(null);
  const [videoURL, setVideoURL] = useState(null);
  const [loading, setLoading] = useState(false);
  const [predictions, setPredictions] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setVideo(file);
    setVideoURL(URL.createObjectURL(file));
  };

  const handleUpload = async () => {
    if (!video) {
      alert("Please select a video file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", video);

    setLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log("Upload response:", response.data);
      setPredictions(response.data);
    } catch (error) {
      console.error("Error uploading video:", error);
      alert("Failed to upload video. Please try again.");
    }

    setLoading(false);
  };

  return (
    <div className="App">
      <h1>Deepfake Detection</h1>

      {/* Video upload and preview */}
      <div className="upload-section">
        <input type="file" accept="video/*" onChange={handleFileChange} />
        {videoURL && <video width="500" controls src={videoURL} />}
        <button onClick={handleUpload} disabled={loading}>
          {loading ? "Uploading..." : "Upload Video"}
        </button>
      </div>

      {predictions && (
        <div className="results-section">
          {/* Frames with anomalies */}
          <h2>Frames with Anomalies (Fake `{'>'}` Real):</h2>
          <div className="anomaly-frames">
            {predictions.frames_with_anomalies.map((frame, index) => (
              <div key={index} className="frame">
                <p>Frame {frame.frame_index}: Real: {frame.real_score.toFixed(2)}, Fake: {frame.fake_score.toFixed(2)}</p>
                <img src={frame.frame_url} alt={`Frame ${frame.frame_index}`} width="200" />
              </div>
            ))}
          </div>

          {/* Final Results */}
          <h2>Final Results:</h2>
          <div className="final-results">
            <p>Total Frames: {predictions.final_scores.total_frames}</p>
            <p>Real Frames: {predictions.final_scores.real_count} ({predictions.final_scores.real_percentage.toFixed(2)}%)</p>
            <p>Fake Frames: {predictions.final_scores.fake_count} ({predictions.final_scores.fake_percentage.toFixed(2)}%)</p>
          </div>

          {/* Confidence Score Graph */}
          <h2>Confidence Score Graph:</h2>
          <div className="graph-container">
            <Bar
              data={{
                labels: predictions.frame_indices.map((idx) => `Frame ${idx}`),
                datasets: [
                  {
                    label: "Real Scores",
                    data: predictions.real_scores,
                    backgroundColor: "rgba(75, 192, 192, 0.6)",
                  },
                  {
                    label: "Fake Scores",
                    data: predictions.fake_scores,
                    backgroundColor: "rgba(255, 99, 132, 0.6)",
                  },
                ],
              }}
              options={{
                responsive: true,
                plugins: {
                  legend: { position: "top" },
                  title: { display: true, text: "Real vs Fake Confidence Scores" },
                },
                scales: {
                  x: { title: { display: true, text: "Frame Index" } },
                  y: { title: { display: true, text: "Confidence Score" } },
                },
              }}
            />
          </div>

          {/* Output Video */}
          {predictions.output_video_url && (
            <div className="output-video">
              <h2>Output Video:</h2>
              <video width="500" controls src={predictions.output_video_url} />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default App;