import React, { useEffect, useState, useRef } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

// ✅ --- PDF.js fixed ESM import ---
import * as pdfjsLib from 'pdfjs-dist/build/pdf';
import pdfjsWorker from 'pdfjs-dist/build/pdf.worker.entry';
pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker;

// ✅ --- URL.parse Polyfill ---
if (typeof URL !== 'undefined' && !URL.parse) {
  URL.parse = (urlStr) => new URL(urlStr, window.location.origin);
}

const API_URL = 'http://127.0.0.1:8000/api/v1';
const MAX_PREVIEW_SIZE_BYTES = 5 * 1024 * 1024; // 5 MB

const getPreviewInfo = (filename) => {
  if (!filename) return { type: 'unsupported' };
  const ext = filename.split('.').pop().toLowerCase();
  const syntaxExts = [
    'js', 'py', 'css', 'html', 'md', 'java', 'cpp', 'c', 'h', 'cs',
    'go', 'rb', 'rs', 'swift', 'txt', 'log', 'json', 'lock'
  ];
  if (syntaxExts.includes(ext))
    return { type: 'syntax', language: ext === 'lock' ? 'json' : ext };
  if (ext === 'pdf') return { type: 'pdf' };
  if (['png', 'jpg', 'jpeg', 'gif', 'webp'].includes(ext)) return { type: 'image' };
  return { type: 'unsupported' };
};

function FilePreviewer({ fileId, fileName, onClose }) {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pdfDoc, setPdfDoc] = useState(null);
  const [numPages, setNumPages] = useState(null);

  const [pageNumberInput, setPageNumberInput] = useState("1");
  const [rotation, setRotation] = useState(0); 

  const canvasRefs = useRef([]);

  const fileUrl = fileId && fileName ? `${API_URL}/get/${fileId}/${fileName}` : null;
  const { type: previewType, language } = getPreviewInfo(fileName);

  // --- Load syntax/text files ---
  useEffect(() => {
    if (previewType !== 'syntax' || !fileUrl) return;
    setContent('');
    setError(null);
    setLoading(true);

    fetch(fileUrl)
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to fetch: ${res.status}`);
        const length = res.headers.get('Content-Length');
        if (length && parseInt(length, 10) > MAX_PREVIEW_SIZE_BYTES)
          throw new Error('File too large to preview (limit: 5MB).');
        return res.text();
      })
      .then((data) => {
        setContent(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [fileUrl, previewType]);

  // --- Load PDF safely ---
  useEffect(() => {
    if (previewType !== 'pdf' || !fileUrl) return;

    setPdfDoc(null);
    setNumPages(null);
    setPageNumberInput("1");
    setRotation(0); 
    setError(null);
    setLoading(true);

    const loadPdf = async () => {
      try {
        const response = await fetch(fileUrl);
        if (!response.ok) throw new Error(`Failed to fetch PDF (${response.status})`);
        const arrayBuffer = await response.arrayBuffer();
        const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
        const pdf = await loadingTask.promise;
        setPdfDoc(pdf);
        setNumPages(pdf.numPages);
        setLoading(false);
      } catch (err) {
        console.error('PDF load error:', err);
        setError(`Error loading PDF: ${err.message}`);
        setLoading(false);
      }
    };
    loadPdf();
  }, [fileUrl, previewType]);

  // --- Render ALL PDF pages ---
  useEffect(() => {
    if (!pdfDoc) return;

    const renderAllPages = async () => {
      canvasRefs.current = canvasRefs.current.slice(0, pdfDoc.numPages);

      for (let i = 1; i <= pdfDoc.numPages; i++) {
        const canvas = canvasRefs.current[i - 1];
        if (!canvas) continue; 

        try {
          const page = await pdfDoc.getPage(i);
          const viewport = page.getViewport({ scale: 1.5, rotation });
          const context = canvas.getContext('2d');
          canvas.height = viewport.height;
          canvas.width = viewport.width;
          await page.render({ canvasContext: context, viewport }).promise;
        } catch (e) {
          console.error(`Error rendering page ${i}:`, e);
          setError(`Error rendering page ${i}: ${e.message}`);
        }
      }
    };

    renderAllPages();
  }, [pdfDoc, rotation]);

  const handleOpenExternally = () => {
    if (fileUrl && window.mirixApi?.openFile) {
      window.mirixApi.openFile(fileUrl);
    } else {
      window.open(fileUrl, '_blank');
    }
  };

  const handlePageJump = () => {
    const pageNum = parseInt(pageNumberInput, 10);
    if (!pageNum || pageNum < 1 || pageNum > numPages) {
      setPageNumberInput("1");
      canvasRefs.current[0]?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    canvasRefs.current[pageNum - 1]?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const handleRotate = () => setRotation(prev => (prev + 90) % 360);

  const renderContent = () => {
    if (!fileUrl) return <p>No preview available.</p>;
    if (loading) return <p>Loading file...</p>;
    if (error) return <p style={{ color: 'red', padding: '1rem' }}>{error}</p>;

    switch (previewType) {
      case 'syntax':
        return (
          <div className="preview-code-block-wrapper">
            <SyntaxHighlighter language={language} style={vscDarkPlus} showLineNumbers>
              {content}
            </SyntaxHighlighter>
          </div>
        );
      case 'image':
        return (
          <div className="preview-image-wrapper">
            <img src={fileUrl} alt={fileName} />
          </div>
        );
      case 'pdf':
        return (
          <div className="pdf-viewer-container">
            <div className="pdf-controls">
              <button onClick={handleRotate} className="pdf-rotate-btn" title="Rotate 90°">↻</button>
              <div className="pdf-page-indicator">
                <span>Page 1 of {numPages || '...'}</span>
              </div>
              <div className="pdf-page-jump">
                <input
                  type="number"
                  min="1"
                  max={numPages || 1}
                  value={pageNumberInput}
                  onChange={(e) => setPageNumberInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handlePageJump()}
                />
                <button onClick={handlePageJump}>Go</button>
              </div>
            </div>
            <div className="pdf-canvas-wrapper">
              {Array.from({ length: numPages || 0 }, (_, index) => (
                <canvas key={`pdf-page-${index + 1}`} ref={el => canvasRefs.current[index] = el} className="pdf-page-canvas" />
              ))}
            </div>
          </div>
        );
      default:
        return (
          <div className="preview-fallback">
            <p>Preview not supported for this file type.</p>
            <button onClick={handleOpenExternally}>Open Externally</button>
          </div>
        );
    }
  };

  return (
    <>
      <div className="file-preview-overlay" onClick={onClose}></div>
      <div className="file-preview-panel" onClick={(e) => e.stopPropagation()}>
        <div className="preview-header">
          <strong>{fileName}</strong>
          <div className="preview-header-buttons">
            <button className="external-open-btn" onClick={handleOpenExternally}>Open Externally</button>
            <button className="close-btn" onClick={onClose}>&times;</button>
          </div>
        </div>
        <div className="preview-content">{renderContent()}</div>
      </div>
    </>
  );
}

export default FilePreviewer;
