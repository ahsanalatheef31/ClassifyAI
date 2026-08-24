import { useState } from "react";
import ConfidenceBadge from "./ConfidenceBadge";
import { approveProductClassification } from "../../services/api";

export default function ClassificationCard({ classification, productId, onUpdate }) {
    if (!classification) return null;

    const [loading, setLoading] = useState(false);
    const [customCat, setCustomCat] = useState("");
    const [showCustomInput, setShowCustomInput] = useState(false);
    const [msg, setMsg] = useState("");

    const ai = classification.ai_analysis || {};
    const isApproved = classification.approved === true;

    async function handleApprove(categoryToApprove = null, gidToApprove = null) {
        if (!productId) return;
        setLoading(true);
        setMsg("");

        try {
            const payload = {
                approved: true,
            };
            if (categoryToApprove) {
                payload.category = categoryToApprove;
                payload.shopify_gid = gidToApprove || "";
            }

            const updatedProduct = await approveProductClassification(productId, payload);
            setMsg(categoryToApprove ? "Category updated and approved!" : "Classification approved!");
            if (onUpdate) {
                onUpdate(updatedProduct);
            }
        } catch (err) {
            console.error(err);
            setMsg("Failed to update approval status.");
        } finally {
            setLoading(false);
        }
    }

    async function handleReject() {
        if (!productId) return;
        setLoading(true);
        setMsg("");

        try {
            const updatedProduct = await approveProductClassification(productId, { approved: false });
            setMsg("Marked for review.");
            if (onUpdate) {
                onUpdate(updatedProduct);
            }
        } catch (err) {
            console.error(err);
            setMsg("Failed to update status.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="classification-result">
            <div className="result-header">
                <div>
                    <div className="eyebrow">AI CLASSIFICATION</div>
                    <h2>Classification Result</h2>
                </div>

                <div className="status-badges-group" style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                    {isApproved ? (
                        <span className="badge badge-success" style={{ background: "#10b981", color: "#fff", padding: "4px 10px", borderRadius: "12px", fontSize: "0.85rem", fontWeight: 600 }}>
                            ✓ Approved
                        </span>
                    ) : (
                        <span className="badge badge-warning" style={{ background: "#f59e0b", color: "#fff", padding: "4px 10px", borderRadius: "12px", fontSize: "0.85rem", fontWeight: 600 }}>
                            ⚠️ {classification.manual_review ? "Manual Review Required" : "Pending Approval"}
                        </span>
                    )}

                    <ConfidenceBadge value={classification.confidence} />
                </div>
            </div>

            <div className="category-result">
                <span>Current Shopify Category</span>
                <strong style={{ fontSize: "1.2rem", color: "#111827" }}>{classification.category || "—"}</strong>

                {classification.shopify_gid && (
                    <small style={{ color: "#6b7280", marginTop: "4px" }}>{classification.shopify_gid}</small>
                )}
            </div>

            {/* APPROVAL / UPDATE ACTION CONTROLS */}
            {productId && (
                <div className="approval-action-box" style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: "8px", padding: "16px", margin: "16px 0" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
                        <div>
                            <strong style={{ display: "block", fontSize: "0.95rem" }}>Is this classification correct?</strong>
                            <span style={{ fontSize: "0.85rem", color: "#64748b" }}>Approve current recommendation or choose an alternative below.</span>
                        </div>

                        <div style={{ display: "flex", gap: "8px" }}>
                            <button
                                className="primary-button"
                                style={{ background: isApproved ? "#059669" : "#2563eb", padding: "8px 16px" }}
                                disabled={loading}
                                onClick={() => handleApprove()}
                            >
                                {isApproved ? "✓ Classification Approved" : "Approve Classification"}
                            </button>

                            {isApproved && (
                                <button
                                    className="secondary-button"
                                    style={{ padding: "8px 16px" }}
                                    disabled={loading}
                                    onClick={handleReject}
                                >
                                    Unapprove / Mark for Review
                                </button>
                            )}
                        </div>
                    </div>

                    {msg && (
                        <div style={{ marginTop: "10px", fontSize: "0.85rem", color: "#059669", fontWeight: 500 }}>
                            {msg}
                        </div>
                    )}
                </div>
            )}

            <div className="result-grid">
                <div className="result-item">
                    <span>Product Type</span>
                    <strong>{ai.product_type || "—"}</strong>
                </div>

                <div className="result-item">
                    <span>Specific Type</span>
                    <strong>{ai.specific_type || "—"}</strong>
                </div>

                <div className="result-item">
                    <span>Intended Use</span>
                    <strong>{ai.intended_use || "—"}</strong>
                </div>

                <div className="result-item">
                    <span>Manual Review</span>
                    <strong>
                        {classification.manual_review ? "Required" : "Not Required"}
                    </strong>
                </div>
            </div>

            {classification.ranking_reason && (
                <div className="reason-box">
                    <span>Why this category?</span>
                    <p>{classification.ranking_reason}</p>
                </div>
            )}

            {/* ALTERNATIVES SELECTION */}
            {classification.alternatives?.length > 0 && (
                <div className="alternatives" style={{ marginTop: "20px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                        <span style={{ fontWeight: 600 }}>Alternative Category Suggestions</span>
                        <span style={{ fontSize: "0.8rem", color: "#6b7280" }}>Click any alternative to select & approve</span>
                    </div>

                    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                        {classification.alternatives.map((item, index) => {
                            const catPath = typeof item === "string" ? item : item.category || item.path || JSON.stringify(item);
                            const catGid = typeof item === "object" ? item.shopify_gid || item.gid : "";
                            const isCurrent = catPath === classification.category;

                            return (
                                <div
                                    key={index}
                                    className="alternative-item"
                                    style={{
                                        display: "flex",
                                        justify: "space-between",
                                        alignItems: "center",
                                        padding: "10px 14px",
                                        background: isCurrent ? "#ecfdf5" : "#ffffff",
                                        border: isCurrent ? "1px solid #10b981" : "1px solid #e5e7eb",
                                        borderRadius: "6px",
                                        gap: "12px"
                                    }}
                                >
                                    <div style={{ flex: 1 }}>
                                        <strong style={{ display: "block", fontSize: "0.9rem", color: "#1f2937" }}>{catPath}</strong>
                                        {catGid && <small style={{ color: "#9ca3af" }}>{catGid}</small>}
                                    </div>

                                    {productId && !isCurrent && (
                                        <button
                                            className="secondary-button"
                                            style={{ padding: "6px 12px", fontSize: "0.8rem" }}
                                            disabled={loading}
                                            onClick={() => handleApprove(catPath, catGid)}
                                        >
                                            Select & Approve →
                                        </button>
                                    )}

                                    {isCurrent && (
                                        <span style={{ fontSize: "0.8rem", color: "#059669", fontWeight: 600 }}>
                                            Selected
                                        </span>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* CUSTOM CATEGORY OVERRIDE */}
            {productId && (
                <div style={{ marginTop: "16px", paddingTop: "12px", borderTop: "1px dashed #e2e8f0" }}>
                    {!showCustomInput ? (
                        <button
                            className="secondary-button"
                            style={{ fontSize: "0.85rem", padding: "6px 12px" }}
                            onClick={() => setShowCustomInput(true)}
                        >
                            + Specify Custom Category
                        </button>
                    ) : (
                        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                            <input
                                type="text"
                                value={customCat}
                                onChange={(e) => setCustomCat(e.target.value)}
                                placeholder="Enter full Shopify Category path (e.g. Apparel & Accessories > Shoes)"
                                style={{ flex: 1, padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.85rem" }}
                            />
                            <button
                                className="primary-button"
                                style={{ padding: "8px 14px", fontSize: "0.85rem" }}
                                disabled={loading || !customCat.trim()}
                                onClick={() => {
                                    handleApprove(customCat.trim());
                                    setShowCustomInput(false);
                                }}
                            >
                                Apply & Approve
                            </button>
                            <button
                                className="secondary-button"
                                style={{ padding: "8px 12px", fontSize: "0.85rem" }}
                                onClick={() => setShowCustomInput(false)}
                            >
                                Cancel
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}