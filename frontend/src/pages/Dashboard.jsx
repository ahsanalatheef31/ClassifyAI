import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getProducts } from "../../services/api";
import StatCard from "../components/StatCard";
import ProductTable from "../components/ProductTable";
import Loading from "../components/Loading";
import EmptyState from "../components/EmptyState";

export default function Dashboard() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadProducts();
    }, []);

    async function loadProducts() {
        try {
            const data = await getProducts();
            setProducts(Array.isArray(data) ? data : data.results || []);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }

    const completed = products.filter(
        (p) => p.status === "completed"
    ).length;

    const processing = products.filter(
        (p) => p.status === "processing"
    ).length;

    const pending = products.filter(
        (p) => p.status === "pending"
    ).length;

    const failed = products.filter(
        (p) => p.status === "failed"
    ).length;

    const review = products.filter(
        (p) => p.classification?.manual_review
    ).length;

    return (
        <>
            <section className="hero-section">
                <div>
                    <div className="eyebrow">PRODUCT INTELLIGENCE</div>

                    <h2>
                        Turn your catalog into
                        <span> structured intelligence.</span>
                    </h2>

                    <p>
                        Automatically understand products, map them to Shopify
                        taxonomy, and identify classifications that need human
                        review.
                    </p>
                </div>

                <Link to="/classify" className="primary-button">
                    <span>✦</span>
                    Classify Product
                </Link>
            </section>

            <section className="stats-grid">
                <StatCard
                    title="Total Products"
                    value={products.length}
                    description="Products in catalog"
                    icon="▦"
                />

                <StatCard
                    title="Completed"
                    value={completed}
                    description="Successfully classified"
                    icon="✓"
                    variant="green"
                />

                <StatCard
                    title="Processing"
                    value={processing}
                    description="Currently analyzing"
                    icon="◌"
                    variant="purple"
                />

                <StatCard
                    title="Failed"
                    value={failed}
                    description="Failed processing"
                    icon="✕"
                    variant="red"
                />

                <StatCard
                    title="Manual Review"
                    value={review}
                    description="Requires attention"
                    icon="!"
                    variant="orange"
                />
            </section>

            <section className="section-card">
                <div className="section-header">
                    <div>
                        <h3>Recent Products</h3>
                        <p>Your latest classification activity</p>
                    </div>

                    <Link to="/products" className="secondary-button">
                        View all
                    </Link>
                </div>

                {loading ? (
                    <Loading text="Loading products..." />
                ) : products.length ? (
                    <ProductTable products={products.slice(0, 8)} />
                ) : (
                    <EmptyState
                        icon="✦"
                        title="No products yet"
                        description="Start by classifying your first product."
                    />
                )}
            </section>
        </>
    );
}