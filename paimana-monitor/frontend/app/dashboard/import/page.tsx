"use client";

import { useState, useRef, useEffect } from "react";
import { uploadFile, getImportStatus, type ImportRecord } from "@/lib/api";
import clsx from "clsx";

export default function ImportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");
  const [importId, setImportId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<ImportRecord | null>(null);
  // Optional filename if we got it from the upload response (uploadFile returns ImportRecord, wait, I need to check uploadFile return type in api.ts)
  const [filename, setFilename] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Polling for job status
  useEffect(() => {
    if (!importId || jobStatus?.status === "completed" || jobStatus?.status === "failed") {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const res = await getImportStatus(importId);
        setJobStatus(res);
        if (res.status === "completed" || res.status === "failed") {
          setIsUploading(false);
        }
      } catch (err) {
        console.error("Status polling failed", err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [importId, jobStatus?.status]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      if (selected.size > 20 * 1024 * 1024) {
        setError("File size exceeds 20MB limit.");
        setFile(null);
      } else {
        setError("");
        setFile(selected);
        setJobStatus(null);
        setImportId(null);
        setFilename(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setError("");
    setJobStatus(null);
    setImportId(null);

    try {
      // Note: uploadFile actually returns { import_id, filename, status, message }
      // based on the fastAPI code, but api.ts says it returns ImportRecord.
      // We will cast it.
      const res: any = await uploadFile(file);
      const newImportId = res.import_id || res.id;
      setImportId(newImportId);
      setFilename(res.filename || file.name);
      setJobStatus({
        id: newImportId,
        document_id: res.filename || file.name,
        status: "pending",
        rows_found: 0,
        rows_processed: 0,
        rows_rejected: 0,
        duplicates: 0,
        new_projects: 0,
        updated_projects: 0,
        created_at: new Date().toISOString(),
      });
    } catch (err: any) {
      setError(err.message || "Upload failed");
      setIsUploading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setImportId(null);
    setJobStatus(null);
    setFilename(null);
    setError("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const progressPct = jobStatus && jobStatus.rows_found > 0
    ? Math.min(100, Math.round(((jobStatus.rows_processed + jobStatus.rows_rejected) / jobStatus.rows_found) * 100))
    : 0;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-100">Data Ingestion</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Upload PAIMANA flash reports (PDF, CSV, Excel) to update portfolio data and run risk assessments.
        </p>
      </div>

      <div className="card p-6">
        <h2 className="text-lg font-semibold text-slate-200 mb-4">Upload File</h2>

        <div className="border-2 border-dashed border-slate-700 rounded-xl p-8 text-center bg-slate-900/50 hover:bg-slate-800/50 transition-colors">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".csv, .xlsx, .xls, .pdf"
            className="hidden"
            id="file-upload"
          />
          <div className="mx-auto w-12 h-12 bg-blue-500/10 rounded-full flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <div className="text-sm font-medium text-slate-300 mb-1">
            {file ? file.name : "Drag and drop or click to select"}
          </div>
          <div className="text-xs text-slate-500 mb-4">
            {file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : "Supports PDF, CSV, Excel (up to 20MB)"}
          </div>
          <div className="flex gap-3 justify-center">
            <button
              className="btn-secondary text-sm"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
            >
              {file ? "Change File" : "Select File"}
            </button>
            {file && !isUploading && !jobStatus && (
              <button className="btn-primary text-sm" onClick={handleUpload}>
                Start Import
              </button>
            )}
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* Progress Tracker */}
        {jobStatus && (
          <div className="mt-6 p-4 bg-slate-900 border border-slate-700 rounded-lg space-y-4">
            <div className="flex justify-between items-center text-sm">
              <span className="font-semibold text-slate-200">Importing: {filename || jobStatus.document_id}</span>
              <span className={clsx(
                "uppercase tracking-wider font-bold text-[10px] px-2 py-0.5 rounded",
                jobStatus.status === "completed" ? "bg-green-500/20 text-green-400" :
                jobStatus.status === "failed" ? "bg-red-500/20 text-red-400" :
                jobStatus.status === "processing" ? "bg-blue-500/20 text-blue-400" :
                "bg-slate-700 text-slate-400"
              )}>
                {jobStatus.status}
              </span>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-xs text-slate-400">
                <span>{
                  jobStatus.status === "completed" ? "Ingestion complete" :
                  jobStatus.status === "failed" ? "Ingestion failed" :
                  jobStatus.status === "processing" ? "Processing..." : "Pending..."
                }</span>
                <span>{progressPct}%</span>
              </div>
              <div className="progress-bar">
                <div
                  className={clsx(
                    "progress-fill",
                    jobStatus.status === "failed" ? "bg-red-500" :
                    jobStatus.status === "completed" ? "bg-green-500" :
                    "bg-blue-500"
                  )}
                  style={{ width: `${progressPct}%` }}
                />
              </div>
            </div>

            {/* Results */}
            {jobStatus.status === "completed" && (
              <div className="p-3 bg-slate-800 rounded text-sm text-slate-300">
                <div className="font-medium mb-2">Import Summary</div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>Rows Processed: {jobStatus.rows_processed}</div>
                  <div>Rows Rejected: {jobStatus.rows_rejected}</div>
                  <div>New Projects: {jobStatus.new_projects}</div>
                  <div>Updated Projects: {jobStatus.updated_projects}</div>
                </div>
                <div className="mt-4">
                  <button className="btn-secondary py-1 px-3 text-xs" onClick={handleReset}>
                    Upload Another File
                  </button>
                </div>
              </div>
            )}

            {jobStatus.status === "failed" && jobStatus.error_message && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded text-sm text-red-400">
                <div className="font-semibold mb-1">Error:</div>
                <div className="text-xs">{jobStatus.error_message}</div>
                {!!jobStatus.error_details && Array.isArray(jobStatus.error_details) && (
                  <ul className="list-disc pl-4 text-xs space-y-1 mt-2">
                    {(jobStatus.error_details as any[]).map((err, i) => (
                      <li key={i}>{typeof err === 'string' ? err : JSON.stringify(err)}</li>
                    ))}
                  </ul>
                )}
                <div className="mt-4">
                  <button className="btn-secondary py-1 px-3 text-xs" onClick={handleReset}>
                    Try Again
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
