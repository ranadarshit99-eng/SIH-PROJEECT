import React, { useState, useRef, useEffect } from 'react';
import { Camera, X, Check, RefreshCw, AlertCircle, ShieldCheck } from 'lucide-react';

const DocumentScannerModal = ({ isOpen, onClose, onCapture, title = "Scan Document Certificate" }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [stream, setStream] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [cameraError, setCameraError] = useState('');
  const [isStarting, setIsStarting] = useState(false);

  // Start Camera Stream when modal opens
  useEffect(() => {
    if (isOpen) {
      startCamera();
    } else {
      stopCamera();
    }
    return () => {
      stopCamera();
    };
  }, [isOpen]);

  const startCamera = async () => {
    setCameraError('');
    setCapturedImage(null);
    setIsStarting(true);
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1920 }, height: { ideal: 1080 } },
        audio: false
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      console.warn("Camera access warning:", err);
      // Fallback to basic video constraint
      try {
        const fallbackStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        setStream(fallbackStream);
        if (videoRef.current) {
          videoRef.current.srcObject = fallbackStream;
        }
      } catch (err2) {
        setCameraError("Unable to access live webcam/camera. Please ensure camera permissions are granted.");
      }
    } finally {
      setIsStarting(false);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.92);
    setCapturedImage(dataUrl);
  };

  const handleRetake = () => {
    setCapturedImage(null);
  };

  const handleConfirm = () => {
    if (!capturedImage) return;

    // Convert dataUrl to File object for backend upload
    fetch(capturedImage)
      .then(res => res.blob())
      .then(blob => {
        const filename = `scan_${Date.now()}.jpg`;
        const file = new File([blob], filename, { type: 'image/jpeg' });
        onCapture(file, capturedImage);
        stopCamera();
        onClose();
      });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-xl w-full overflow-hidden shadow-2xl border border-slate-200 flex flex-col">
        
        {/* Modal Header */}
        <div className="bg-slate-900 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
              <Camera size={18} />
            </div>
            <div>
              <h3 className="text-sm font-bold">{title}</h3>
              <p className="text-[10px] text-slate-400">Live Camera Document & Certificate Scanner</p>
            </div>
          </div>
          <button
            onClick={() => { stopCamera(); onClose(); }}
            className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-slate-300 hover:text-white transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 flex-1 flex flex-col items-center justify-center min-h-[360px] bg-slate-50 relative">
          {cameraError ? (
            <div className="text-center p-6 text-rose-700 bg-rose-50 border border-rose-200 rounded-2xl max-w-md">
              <AlertCircle size={36} className="mx-auto mb-2 text-rose-600" />
              <p className="text-xs font-bold">{cameraError}</p>
              <button
                onClick={startCamera}
                className="mt-4 px-4 py-2 bg-rose-600 text-white text-xs font-bold rounded-xl shadow"
              >
                Retry Camera Connection
              </button>
            </div>
          ) : capturedImage ? (
            /* Snapshot Preview Mode */
            <div className="relative w-full max-h-[360px] rounded-2xl overflow-hidden border-2 border-emerald-500 shadow-md">
              <img src={capturedImage} alt="Captured Document Scan" className="w-full h-full object-contain bg-black" />
              <div className="absolute top-3 right-3 bg-emerald-600 text-white text-[10px] font-bold px-3 py-1 rounded-full shadow flex items-center gap-1">
                <ShieldCheck size={14} />
                <span>High Res Scan Captured</span>
              </div>
            </div>
          ) : (
            /* Live Camera Feed */
            <div className="relative w-full max-h-[360px] rounded-2xl overflow-hidden border-2 border-slate-300 bg-black flex items-center justify-center">
              {isStarting && (
                <div className="text-white text-xs font-bold flex items-center gap-2">
                  <RefreshCw size={18} className="animate-spin text-blue-400" />
                  <span>Initializing Camera Scanner...</span>
                </div>
              )}
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="w-full h-full object-cover"
              />
              <canvas ref={canvasRef} className="hidden" />

              {/* Viewfinder Target Guidelines */}
              <div className="absolute inset-8 border-2 border-dashed border-white/50 rounded-xl pointer-events-none flex items-center justify-center">
                <span className="text-[10px] font-bold text-white/70 bg-black/50 px-3 py-1 rounded-full uppercase tracking-wider">
                  Align Document / Certificate within Frame
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Modal Controls Footer */}
        <div className="p-4 bg-white border-t border-slate-200 flex items-center justify-between">
          <button
            type="button"
            onClick={() => { stopCamera(); onClose(); }}
            className="px-4 py-2 text-xs font-bold text-slate-600 hover:text-slate-900 bg-slate-100 rounded-xl"
          >
            Cancel
          </button>

          {capturedImage ? (
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleRetake}
                className="px-4 py-2 text-xs font-bold text-slate-700 bg-slate-200 hover:bg-slate-300 rounded-xl flex items-center gap-1.5"
              >
                <RefreshCw size={14} />
                <span>Retake Photo</span>
              </button>

              <button
                type="button"
                onClick={handleConfirm}
                className="px-5 py-2 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-md flex items-center gap-1.5"
              >
                <Check size={16} />
                <span>Use Scanned Photo</span>
              </button>
            </div>
          ) : (
            <button
              type="button"
              disabled={!stream}
              onClick={capturePhoto}
              className="px-6 py-2.5 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-xl shadow-md flex items-center gap-2"
            >
              <Camera size={16} />
              <span>Capture Document Photo</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentScannerModal;
