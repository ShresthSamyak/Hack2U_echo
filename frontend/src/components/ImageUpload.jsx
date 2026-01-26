import React from 'react';
import { Upload, Image as ImageIcon } from 'lucide-react';
import './ImageUpload.css';

const ImageUpload = ({ onImageSelect, disabled }) => {
  const [preview, setPreview] = React.useState(null);
  const [isDragging, setIsDragging] = React.useState(false);
  const fileInputRef = React.useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) processFile(file);
  };

  const processFile = (file) => {
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB');
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target.result);
    };
    reader.readAsDataURL(file);

    // Send to parent
    onImageSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  };

  return (
    <div className="image-upload-container">
      <div
        className={`upload-zone ${isDragging ? 'dragging' : ''} ${preview ? 'has-preview' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
      >
        {preview ? (
          <div className="preview-container">
            <img src={preview} alt="Room preview" className="preview-image" />
            <div className="preview-overlay">
              <Upload size={24} />
              <span>Click to change image</span>
            </div>
          </div>
        ) : (
          <div className="upload-prompt">
            <ImageIcon size={48} strokeWidth={1.5} />
            <h3>Upload Room Image</h3>
            <p>Drag & drop or click to select</p>
            <span className="upload-hint">For best results: show full room, good lighting</span>
          </div>
        )}
      </div>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        disabled={disabled}
        style={{ display: 'none' }}
      />
    </div>
  );
};

export default ImageUpload;
