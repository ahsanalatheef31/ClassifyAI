import { useEffect, useRef, useState } from "react";
import { getJob, getJobs, uploadBulkFile } from "../../services/api";
import StatusBadge from "../components/StatusBadge";
import { Link } from "react-router-dom";

export default function BulkUpload() {
    const [file, setFile] = useState(null);
    const [job, setJob] = useState(null);
    const [allJobs, setAllJobs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const inputRef = useRef(null);

    // Initial load: Fetch jobs and restore active/latest job
    useEffect(() => {
        loadJobs();
    }, []);

    async function loadJobs() {
        try {
            const data = await getJobs();
            const jobsList = Array.isArray(data) ? data : data.results || [];
            setAllJobs(jobsList);

            if (jobsList.length > 0) {
                // Look for an ongoing processing/pending job first
                const ongoing = jobsList.find(
                    (j) => j.status === "processing" || j.status === "pending"
                );
                const targetJob = ongoing || jobsList[0];
                setJob(targetJob);

                if (targetJob.status === "processing" || targetJob.status === "pending") {
                    setLoading(true);
                }
            }
        } catch (err) {
            console.error("Failed to fetch jobs list:", err);
        }
    }

    function selectFile(e) {
        const selected = e.target.files?.[0];

        if (!selected) return;

        const valid =
            selected.name.toLowerCase().endsWith(".csv") ||
            selected.name.toLowerCase().endsWith(".xlsx");

        if (!valid) {
            setError("Please upload a CSV or XLSX file.");
            return;
        }

        setError("");
        setFile(selected);
    }

    async function handleUpload() {
        if (!file) return;

        setLoading(true);
        setError("");

        try {
            const data = new FormData();
            data.append("file", file);

            const result = await uploadBulkFile(data);

            const newJob = {
                id: result.job_id,
                status: result.status || "pending",
                total_products: 0,
                processed_products: 0,
                failed_products: 0,
            };

            localStorage.setItem("active_job_id", result.job_id);
            setJob(newJob);
            setFile(null);
            loadJobs();
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.error ||
                "Bulk upload failed."
            );
            setLoading(false);
        }
    }

    // Active Polling Loop
    useEffect(() => {
        if (!job?.id) return;

        let active = true;

        async function poll() {
            try {
                const data = await getJob(job.id);

                if (!active) return;

                setJob(data);

                // Refresh jobs list to sync history
                setAllJobs((prev) =>
                    prev.map((j) => (j.id === data.id ? data : j))
                );

                if (
                    data.status === "completed" ||
                    data.status === "failed"
                ) {
                    setLoading(false);
                    return;
                }

                setTimeout(poll, 2000);
            } catch (error) {
                console.error(error);
                if (active) {
                    setError("Unable to retrieve job status.");
                    setLoading(false);
                }
            }
        }

        poll();

        return () => {
            active = false;
        };
    }, [job?.id]);

    const total = job?.total_products || 0;
    const processed = job?.processed_products || 0;
    const failed = job?.failed_products || 0;

    const progress =
        total > 0
            ? Math.round(((processed + failed) / total) * 100)
            : 0;

    return (
        <div className="bulk-page">
            <section className="section-card upload-card">
                <div className="section-header">
                    <div>
                        <div className="eyebrow">BULK INTELLIGENCE</div>
                        <h3>Classify your catalog</h3>
                        <p>
                            Upload a CSV or XLSX file and let the AI process
                            your entire product catalog asynchronously.
                        </p>
                    </div>
                </div>

                <div
                    className={`bulk-dropzone ${file ? "selected" : ""}`}
                    onClick={() => inputRef.current?.click()}
                >
                    <div className="bulk-icon">⇧</div>

                    {file ? (
                        <>
                            <strong>{file.name}</strong>
                            <span>
                                {(file.size / 1024 / 1024).toFixed(2)} MB
                            </span>
                        </>
                    ) : (
                        <>
                            <strong>Drop your catalog here</strong>
                            <span>
                                CSV or XLSX files · Click to browse
                            </span>
                        </>
                    )}

                    <input
                        ref={inputRef}
                        type="file"
                        accept=".csv,.xlsx"
                        hidden
                        onChange={selectFile}
                    />
                </div>

                {error && (
                    <div className="error-message" style={{ marginTop: "12px" }}>
                        {error}
                    </div>
                )}

                <div className="form-actions">
                    <button
                        className="secondary-button"
                        onClick={() => setFile(null)}
                    >
                        Clear
                    </button>

                    <button
                        className="primary-button"
                        disabled={!file || loading}
                        onClick={handleUpload}
                    >
                        {loading ? "Processing Upload..." : "Start Classification"}
                    </button>
                </div>
            </section>

            {job && (
                <section className="section-card job-card" style={{ marginTop: "24px" }}>
                    <div className="job-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <div>
                            <div className="eyebrow">
                                CLASSIFICATION JOB #{job.id}
                            </div>
                            <h3>Job Progress & Details</h3>
                        </div>

                        <StatusBadge status={job.status} />
                    </div>

                    <div className="progress-area" style={{ margin: "20px 0" }}>
                        <div className="progress-label" style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                            <span>Classification progress</span>
                            <strong>{progress}% ({processed + failed} / {total} products)</strong>
                        </div>

                        <div className="progress-track" style={{ background: "#e2e8f0", height: "10px", borderRadius: "5px", overflow: "hidden" }}>
                            <div
                                className="progress-fill"
                                style={{
                                    width: `${progress}%`,
                                    background: job.status === "failed" ? "#ef4444" : "#2563eb",
                                    height: "100%",
                                    transition: "width 0.3s ease"
                                }}
                            />
                        </div>
                    </div>

                    <div className="job-stats" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px", background: "#f8fafc", padding: "16px", borderRadius: "8px" }}>
                        <div>
                            <span style={{ fontSize: "0.85rem", color: "#64748b" }}>Total Products</span>
                            <strong style={{ display: "block", fontSize: "1.4rem" }}>{total}</strong>
                        </div>

                        <div>
                            <span style={{ fontSize: "0.85rem", color: "#64748b" }}>Completed</span>
                            <strong style={{ display: "block", fontSize: "1.4rem", color: "#10b981" }}>{processed}</strong>
                        </div>

                        <div>
                            <span style={{ fontSize: "0.85rem", color: "#64748b" }}>Failed</span>
                            <strong style={{ display: "block", fontSize: "1.4rem", color: "#ef4444" }}>{failed}</strong>
                        </div>
                    </div>

                    {job.status === "completed" && (
                        <div className="success-message" style={{ marginTop: "16px", background: "#ecfdf5", color: "#065f46", padding: "12px", borderRadius: "6px" }}>
                            ✓ Catalog classification completed successfully. <Link to="/products" style={{ color: "#059669", fontWeight: 600, marginLeft: "8px" }}>View Products →</Link>
                        </div>
                    )}

                    {job.status === "failed" && (
                        <div className="error-message" style={{ marginTop: "16px", background: "#fef2f2", color: "#991b1b", padding: "12px", borderRadius: "6px" }}>
                            {job.error_message || "Classification job failed."}
                        </div>
                    )}
                </section>
            )}

            {allJobs.length > 0 && (
                <section className="section-card" style={{ marginTop: "24px" }}>
                    <div className="section-header">
                        <div>
                            <h3>Bulk Upload Jobs History</h3>
                            <p>Recent catalog classification jobs and progress</p>
                        </div>
                    </div>

                    <div className="jobs-list" style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "16px" }}>
                        {allJobs.map((j) => {
                            const jTotal = j.total_products || 0;
                            const jDone = (j.processed_products || 0) + (j.failed_products || 0);
                            const jPct = jTotal > 0 ? Math.round((jDone / jTotal) * 100) : 0;

                            return (
                                <div
                                    key={j.id}
                                    style={{
                                        display: "flex",
                                        justifyContent: "space-between",
                                        alignItems: "center",
                                        padding: "12px 16px",
                                        background: j.id === job?.id ? "#f0f9ff" : "#ffffff",
                                        border: j.id === job?.id ? "1px solid #0284c7" : "1px solid #e2e8f0",
                                        borderRadius: "8px",
                                    }}
                                >
                                    <div>
                                        <strong style={{ fontSize: "0.95rem" }}>Job #{j.id}</strong>
                                        <span style={{ fontSize: "0.85rem", color: "#64748b", marginLeft: "12px" }}>
                                            {j.created_at ? new Date(j.created_at).toLocaleString() : ""}
                                        </span>
                                        <div style={{ fontSize: "0.85rem", color: "#334155", marginTop: "4px" }}>
                                            {jPct}% complete ({jDone}/{jTotal} products)
                                        </div>
                                    </div>

                                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                                        <StatusBadge status={j.status} />
                                        {j.id !== job?.id && (
                                            <button
                                                className="secondary-button"
                                                style={{ fontSize: "0.8rem", padding: "4px 10px" }}
                                                onClick={() => setJob(j)}
                                            >
                                                Inspect
                                            </button>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </section>
            )}
        </div>
    );
}