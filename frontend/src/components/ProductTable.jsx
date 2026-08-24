import { Link } from "react-router-dom";
import StatusBadge from "./StatusBadge";
import ConfidenceBadge from "./ConfidenceBadge";

export default function ProductTable({ products = [] }) {
    return (
        <div className="table-wrapper">
            <table className="product-table">
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Status</th>
                        <th>Category</th>
                        <th>Confidence</th>
                        <th>Review</th>
                        <th></th>
                    </tr>
                </thead>

                <tbody>
                    {products.map((product) => (
                        <tr key={product.id}>
                            <td>
                                <div className="product-cell">
                                    {product.image ? (
                                        <img
                                            src={product.image}
                                            alt=""
                                            className="table-product-image"
                                        />
                                    ) : (
                                        <div className="table-product-placeholder">
                                            {product.name?.charAt(0) || "P"}
                                        </div>
                                    )}

                                    <div>
                                        <strong>{product.name}</strong>

                                        <span>
                                            {product.brand || "No brand"}
                                        </span>
                                    </div>
                                </div>
                            </td>

                            <td>
                                <StatusBadge status={product.status} />
                            </td>

                            <td>
                                <div className="category-cell">
                                    {product.classification?.category || (
                                        <span className="muted">Processing...</span>
                                    )}
                                </div>
                            </td>

                            <td>
                                {product.classification ? (
                                    <ConfidenceBadge
                                        value={product.classification.confidence}
                                    />
                                ) : (
                                    <span className="muted">—</span>
                                )}
                            </td>

                            <td>
                                {product.classification?.manual_review ? (
                                    <span className="review-required">Required</span>
                                ) : (
                                    <span className="review-ok">Clear</span>
                                )}
                            </td>

                            <td>
                                <Link
                                    className="view-link"
                                    to={`/products/${product.id}`}
                                >
                                    View →
                                </Link>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}