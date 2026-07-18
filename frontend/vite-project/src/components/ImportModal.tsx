import { useRef, useState } from 'react';
import { api, ApiError } from '../api';

interface ImportModalProps {
  onClose: () => void;
  onImported: (count: number) => void;
}

export default function ImportModal({ onClose, onImported }: ImportModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async () => {
    if (!file) {
      setError('Please choose a PDF file.');
      return;
    }
    setError(null);
    setUploading(true);
    try {
      const res = await api.importProducts(file);
      if (res.count === 0) {
        // Keep the modal open so the user can try a different file.
        setError(res.message || 'No products could be recognised in this PDF.');
        return;
      }
      onImported(res.count);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.errors?.file?.[0] || err.message);
      } else {
        setError('Import failed.');
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={uploading ? undefined : onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        {uploading && (
          <div className="modal-loading">
            <div className="spinner" />
            <p className="modal-loading-title">Importing your catalogue…</p>
            <p className="modal-loading-sub">
              Parsing the PDF and extracting products &amp; images. This can take
              several seconds for large files — please keep this window open.
            </p>
          </div>
        )}

        <div className="modal-header">
          <h2>Import products from PDF</h2>
          <button
            className="modal-close"
            onClick={onClose}
            aria-label="Close"
            disabled={uploading}
          >
            ×
          </button>
        </div>

        <p className="modal-hint">
          Upload a catalogue PDF. Products are parsed and added (or updated by SKU).
        </p>

        {error && <div className="alert alert-error">{error}</div>}

        <div
          className={`dropzone ${file ? 'dropzone-filled' : ''}`}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept="application/pdf,.pdf"
            hidden
            onChange={(e) => {
              setError(null);
              setFile(e.target.files?.[0] ?? null);
            }}
          />
          {file ? (
            <span className="dropzone-file">📄 {file.name}</span>
          ) : (
            <span>Click to select a PDF file</span>
          )}
        </div>

        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={onClose} disabled={uploading}>
            Cancel
          </button>
          <button
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={uploading || !file}
          >
            {uploading ? 'Importing…' : 'Import'}
          </button>
        </div>
      </div>
    </div>
  );
}
