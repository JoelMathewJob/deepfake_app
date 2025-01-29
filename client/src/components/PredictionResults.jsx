import React from 'react';

function PredictionResults({ predictions }) {
  return (
    <div>
      <h2>Predictions:</h2>
      <ul>
        {predictions.frames.map((frame, index) => (
          <li key={index}>
            Frame {frame.index}: {frame.label} (Confidence: {frame.confidence})
          </li>
        ))}
      </ul>
      <div>
        <p>Total Real Frames: {predictions.realCount}</p>
        <p>Total Fake Frames: {predictions.fakeCount}</p>
      </div>
    </div>
  );
}

export default PredictionResults;
