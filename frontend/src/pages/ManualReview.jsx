import { useEffect, useState } from "react";
import { getProducts, approveProductClassification } from "../../services/api";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";
import ConfidenceBadge from "../components/ConfidenceBadge";
import { Link } from "react-router-dom";

export default function ManualReview() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        load();
    }, []);

    async function load() {
        try {
            const data = await getProducts();

            const list = Array.isArray(data)
                ? data
                : data.results || [];

            setProducts(
                list.filter(
                    (product) =>
                        product.classification?.manual_review === true &&
                        product.classification?.approved !== true
                )
            );
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }

    async function handleQuickApprove(id) {
        try {
            await approveProductClassification(id, { approved: true });
            setProducts((prev) => prev.filter((p) => p.id !== id));
        } catch (err) {
            console.error("Failed to approve product", err);
        }
    }

    return (
        <section className="section-card">
            <div className="section-header">
                <div>
                    <div className="eyebrow">HUMAN-IN-THE-LOOP</div>
                    <h3>Manual Review</h3>
                    <p>
                        Products where the AI needs an additional human
                        decision.
                    </p>
                </div>
            </div>

            {loading ? (
                <Loading text="Finding products requiring review..." />
            ) : products.length === 0 ? (
                <EmptyState
                    icon="✓"
                    title="Everything looks good"
                    description="There are currently no products requiring manual review."
                />
            ) : (
                <div className="review-grid">
                    {products.map((product) => (
                        <div className="review-card" key={product.id}>
                            <div className="review-card-top">
                                <div className="review-product">
                                    <div className="table-product-placeholder">
                                        {product.name?.charAt(0)}
                                    </div>

                                    <div>
                                        <strong>{product.name}</strong>
                                        <span>
                                            {product.brand || "No brand"}
                                        </span>
                                    </div>
                                </div>

                                <ConfidenceBadge
                                    value={
                                        product.classification?.confidence
                                    }
                                />
                            </div>

                            <div className="review-category">
                                <span>Suggested category</span>
                                <strong>
                                    {product.classification?.category ||
                                        "Not available"}
                                </strong>
                            </div>

                            <div style={{ display: "flex", gap: "8px", marginTop: "12px" }}>
                                <button
                                    className="primary-button"
                                    style={{ flex: 1, padding: "8px 12px", fontSize: "0.85rem" }}
                                    onClick={() => handleQuickApprove(product.id)}
                                >
                                    ✓ Quick Approve
                                </button>
                                <Link
                                    to={`/products/${product.id}`}
                                    className="secondary-button"
                                    style={{ padding: "8px 12px", fontSize: "0.85rem" }}
                                >
                                    Review →
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </section>
    );
}