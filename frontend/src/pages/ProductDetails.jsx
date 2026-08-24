import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getProduct } from "../../services/api";
import Loading from "../components/Loading";
import StatusBadge from "../components/StatusBadge";
import ConfidenceBadge from "../components/ConfidenceBadge";
import ClassificationCard from "../components/ClassificationCard";

export default function ProductDetails() {
    const { id } = useParams();

    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        load();
    }, [id]);

    async function load() {
        try {
            const data = await getProduct(id);
            setProduct(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }

    if (loading) {
        return <Loading text="Loading product..." />;
    }

    if (!product) {
        return (
            <div className="section-card">
                Product not found.
            </div>
        );
    }

    return (
        <>
            <Link to="/products" className="back-link">
                ← Back to products
            </Link>

            <div className="details-layout">
                <section className="section-card product-overview">
                    <div className="large-product-image">
                        {product.image ? (
                            <img src={product.image} alt={product.name} />
                        ) : (
                            <span>{product.name?.charAt(0)}</span>
                        )}
                    </div>

                    <div className="product-info">
                        <div className="eyebrow">PRODUCT</div>

                        <h2>{product.name}</h2>

                        <p>
                            {product.description ||
                                "No product description available."}
                        </p>

                        <div className="detail-tags">
                            <StatusBadge status={product.status} />

                            {product.classification && (
                                <ConfidenceBadge
                                    value={product.classification.confidence}
                                />
                            )}
                        </div>

                        <div className="info-list">
                            <div>
                                <span>Brand</span>
                                <strong>{product.brand || "—"}</strong>
                            </div>

                            <div>
                                <span>Product Type</span>
                                <strong>
                                    {product.product_type || "—"}
                                </strong>
                            </div>
                        </div>
                    </div>
                </section>

                {product.classification && (
                    <ClassificationCard
                        classification={product.classification}
                        productId={product.id}
                        onUpdate={(updatedProduct) => setProduct(updatedProduct)}
                    />
                )}
            </div>
        </>
    );
}