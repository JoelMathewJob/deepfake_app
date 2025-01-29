import React from 'react';

function VideoUpload({ onUpload }) {
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      onUpload(file);
    }
  };

  return (
    <div>
      <input type="file" accept="video/*" onChange={handleFileChange} />
    </div>
  );
}

export default VideoUpload;
