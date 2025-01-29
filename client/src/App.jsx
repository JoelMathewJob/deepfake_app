import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
  const [video, setVideo] = useState(null);
  const [videoURL, setVideoURL] = useState(null); // To preview the video
  const [loading, setLoading] = useState(false);
  const [predictions, setPredictions] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setVideo(file);
    setVideoURL(URL.createObjectURL(file)); // Create video preview URL
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
        }
      });

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
      <input type="file" accept="video/*" onChange={handleFileChange} />
      {videoURL && <video width="300" controls src={videoURL} />}

      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload Video"}
      </button>

      {predictions && (
        <div>
          {/* Display frames with anomalies */}
          <h2>Frames with Anomalies (Fake `{'>'}` Real):</h2>
          <ul>
            {predictions.frames_with_anomalies.map((frame, index) => (
              <li key={index}>
                Frame {frame.frame_index}: Real: {frame.real_score}, Fake: {frame.fake_score}
                {/* Show the actual frame preview */}
                <img src={frame.frame_url} alt={`Frame ${frame.frame_index}`} width="150" />
              </li>
            ))}
          </ul>

          {/* Final Results */}
          <h2>Final Results:</h2>
          <p>Total Frames: {predictions.final_scores.total_frames}</p>
          <p>Real Frames: {predictions.final_scores.real_count} ({predictions.final_scores.real_percentage}%)</p>
          <p>Fake Frames: {predictions.final_scores.fake_count} ({predictions.final_scores.fake_percentage}%)</p>

          {/* Confidence Score Graph */}
          <h2>Confidence Score Graph:</h2>
          <div id="graph-container">
            {/* You can use a library like Chart.js to display this */}
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
