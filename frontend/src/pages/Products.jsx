import { useEffect, useState } from "react";
import { getProducts } from "../../services/api";
import ProductTable from "../components/ProductTable";
import Loading from "../components/Loading";
import EmptyState from "../components/EmptyState";

export default function Products() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [status, setStatus] = useState("all");

    useEffect(() => {
        load();
    }, []);

    async function load() {
        try {
            const data = await getProducts();
            setProducts(
                Array.isArray(data) ? data : data.results || []
            );
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }

    const filtered = products.filter((product) => {
        const matchesSearch =
            product.name
                ?.toLowerCase()
                .includes(search.toLowerCase()) ||
            product.brand
                ?.toLowerCase()
                .includes(search.toLowerCase());

        const matchesStatus =
            status === "all" || product.status === status;

        return matchesSearch && matchesStatus;
    });

    return (
        <>
            <div className="toolbar">
                <div className="search-box">
                    <span>⌕</span>
                    <input
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search products..."
                    />
                </div>

                <select
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                >
                    <option value="all">All statuses</option>
                    <option value="completed">Completed</option>
                    <option value="processing">Processing</option>
                    <option value="pending">Pending</option>
                    <option value="failed">Failed</option>
                </select>
            </div>

            <section className="section-card">
                <div className="section-header">
                    <div>
                        <h3>All Products</h3>
                        <p>{filtered.length} products found</p>
                    </div>
                </div>

                {loading ? (
                    <Loading text="Loading products..." />
                ) : filtered.length ? (
                    <ProductTable products={filtered} />
                ) : (
                    <EmptyState
                        icon="⌕"
                        title="No products found"
                        description="Try changing your search or filter."
                    />
                )}
            </section>
        </>
    );
}