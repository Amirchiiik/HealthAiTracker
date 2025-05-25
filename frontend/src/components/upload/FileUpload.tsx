import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { uploadService } from '../../services/uploadService';
import { UploadProgress } from '../../types';
import { LoadingSpinner } from '../common/LoadingSpinner';

interface FileUploadProps {
  onUploadComplete: (filename: string) => void;
  onUploadError: (error: string) => void;
  disabled?: boolean;
  maxFiles?: number;
}

interface UploadingFile {
  file: File;
  progress: UploadProgress;
  status: 'uploading' | 'completed' | 'error';
  error?: string;
  filename?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onUploadComplete,
  onUploadError,
  disabled = false,
  maxFiles = 5,
}) => {
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (disabled) return;

      // Validate each file
      const validFiles: File[] = [];
      for (const file of acceptedFiles) {
        const validation = uploadService.validateFile(file);
        if (!validation.isValid) {
          onUploadError(`${file.name}: ${validation.error}`);
          continue;
        }
        validFiles.push(file);
      }

      if (validFiles.length === 0) return;

      // Check max files limit
      if (uploadingFiles.length + validFiles.length > maxFiles) {
        onUploadError(`Maximum ${maxFiles} files allowed`);
        return;
      }

      // Initialize uploading files
      const newUploadingFiles: UploadingFile[] = validFiles.map((file) => ({
        file,
        progress: { loaded: 0, total: file.size, percentage: 0 },
        status: 'uploading',
      }));

      setUploadingFiles((prev) => [...prev, ...newUploadingFiles]);

      // Upload each file
      for (let i = 0; i < validFiles.length; i++) {
        const file = validFiles[i];
        const fileIndex = uploadingFiles.length + i;

        try {
          const result = await uploadService.uploadFile(file, (progress) => {
            setUploadingFiles((prev) => {
              const updated = [...prev];
              if (updated[fileIndex]) {
                updated[fileIndex].progress = progress;
              }
              return updated;
            });
          });

          // Mark as completed
          setUploadingFiles((prev) => {
            const updated = [...prev];
            if (updated[fileIndex]) {
              updated[fileIndex].status = 'completed';
              updated[fileIndex].filename = result.filename;
            }
            return updated;
          });

          onUploadComplete(result.filename);
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Upload failed';
          
          setUploadingFiles((prev) => {
            const updated = [...prev];
            if (updated[fileIndex]) {
              updated[fileIndex].status = 'error';
              updated[fileIndex].error = errorMessage;
            }
            return updated;
          });

          onUploadError(`${file.name}: ${errorMessage}`);
        }
      }
    },
    [disabled, maxFiles, uploadingFiles.length, onUploadComplete, onUploadError]
  );

  const removeFile = (index: number) => {
    setUploadingFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    disabled,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/webp': ['.webp'],
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
    },
    maxFiles,
  });

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'uploading':
        return <Loader className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-success-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-error-500" />;
      default:
        return <File className="w-5 h-5 text-gray-400" />;
    }
  };

  return (
    <div className="w-full">
      {/* Upload Zone */}
      <div
        {...getRootProps()}
        className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors duration-200 ${
          isDragActive
            ? 'border-primary-400 bg-primary-50 dark:bg-primary-900/20'
            : 'border-gray-300 hover:border-gray-400 dark:border-gray-600'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className={`p-3 rounded-full ${
            isDragActive ? 'bg-primary-100 dark:bg-primary-800' : 'bg-gray-100 dark:bg-gray-700'
          }`}>
            <Upload className={`w-8 h-8 ${
              isDragActive ? 'text-primary-600' : 'text-gray-400'
            }`} />
          </div>
          
          <div>
            <p className="text-lg font-medium text-gray-900 dark:text-white">
              {isDragActive ? 'Drop files here' : 'Upload medical files'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Drag & drop files here, or click to select
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
              Supports JPEG, PNG, WebP, PDF, TXT (max 10MB each)
            </p>
          </div>
        </div>
      </div>

      {/* File List */}
      {uploadingFiles.length > 0 && (
        <div className="mt-6 space-y-3">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white">
            Files ({uploadingFiles.length})
          </h3>
          
          <div className="space-y-2">
            {uploadingFiles.map((uploadingFile, index) => (
              <div
                key={index}
                className="flex items-center space-x-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
              >
                {getStatusIcon(uploadingFile.status)}
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {uploadingFile.file.name}
                  </p>
                  <div className="flex items-center space-x-2 mt-1">
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {formatFileSize(uploadingFile.file.size)}
                    </p>
                    {uploadingFile.status === 'uploading' && (
                      <span className="text-xs text-blue-500">
                        {uploadingFile.progress.percentage}%
                      </span>
                    )}
                    {uploadingFile.status === 'error' && uploadingFile.error && (
                      <span className="text-xs text-error-500">
                        {uploadingFile.error}
                      </span>
                    )}
                    {uploadingFile.status === 'completed' && (
                      <span className="text-xs text-success-500">
                        Uploaded successfully
                      </span>
                    )}
                  </div>
                  
                  {/* Progress Bar */}
                  {uploadingFile.status === 'uploading' && (
                    <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                      <div
                        className="bg-primary-600 h-1.5 rounded-full transition-all duration-300"
                        style={{ width: `${uploadingFile.progress.percentage}%` }}
                      />
                    </div>
                  )}
                </div>
                
                <button
                  onClick={() => removeFile(index)}
                  className="p-1 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
                  disabled={uploadingFile.status === 'uploading'}
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload; 