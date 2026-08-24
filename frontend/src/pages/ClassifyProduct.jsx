import { useEffect, useRef, useState } from "react";
import { createProduct, getProduct } from "../../services/api";
import ClassificationCard from "../components/ClassificationCard";
import Loading from "../components/Loading";

export default function ClassifyProduct() {
    const [form, setForm] = useState({
        name: "",
        description: "",
        brand: "",
        product_type: "",
    });

    const [image, setImage] = useState(null);
    const [preview, setPreview] = useState("");
    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const inputRef = useRef(null);

    function handleChange(e) {
        setForm({
            ...form,
            [e.target.name]: e.target.value,
        });
    }

    function handleImage(e) {
        const file = e.target.files?.[0];

        if (!file) return;

        setImage(file);
        setPreview(URL.createObjectURL(file));
    }

    async function handleSubmit(e) {
        e.preventDefault();

        setError("");
        setProduct(null);
        setLoading(true);

        try {
            const data = new FormData();

            data.append("name", form.name);
            data.append("description", form.description);
            data.append("brand", form.brand);
            data.append("product_type", form.product_type);

            if (image) {
                data.append("image", image);
            }

            const created = await createProduct(data);

            let current = created;

            setProduct(current);

            while (
                current.status !== "completed" &&
                current.status !== "failed"
            ) {
                await new Promise((resolve) =>
                    setTimeout(resolve, 2500)
                );

                current = await getProduct(created.id);

                setProduct(current);
            }

            if (current.status === "failed") {
                setError(
                    current.error_message ||
                    "Product classification failed."
                );
            }
        } catch (err) {
            console.error(err);

            setError(
                err.response?.data?.error ||
                "Unable to connect to the backend."
            );
        } finally {
            setLoading(false);
        }
    }

    function reset() {
        setForm({
            name: "",
            description: "",
            brand: "",
            product_type: "",
        });

        setImage(null);
        setPreview("");
        setProduct(null);
        setError("");
    }

    return (
        <div className="workspace-grid">
            <section className="section-card form-card">
                <div className="section-header">
                    <div>
                        <div className="eyebrow">AI WORKSPACE</div>
                        <h3>Classify a Product</h3>
                        <p>
                            Give the AI some product information and let it
                            determine the best Shopify category.
                        </p>
                    </div>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="form-grid">
                        <div className="field full">
                            <label>Product name *</label>
                            <input
                                name="name"
                                value={form.name}
                                onChange={handleChange}
                                placeholder="e.g. Brown Casual Shoes"
                                required
                            />
                        </div>

                        <div className="field">
                            <label>Brand</label>
                            <input
                                name="brand"
                                value={form.brand}
                                onChange={handleChange}
                                placeholder="e.g. Nike"
                            />
                        </div>

                        <div className="field">
                            <label>Product type</label>
                            <input
                                name="product_type"
                                value={form.product_type}
                                onChange={handleChange}
                                placeholder="e.g. Shoes"
                            />
                        </div>

                        <div className="field full">
                            <label>Description</label>
                            <textarea
                                name="description"
                                value={form.description}
                                onChange={handleChange}
                                placeholder="Describe the product..."
                                rows="5"
                            />
                        </div>

                        <div className="field full">
                            <label>Product image</label>

                            <div
                                className={`image-upload ${preview ? "has-image" : ""
                                    }`}
                                onClick={() => inputRef.current?.click()}
                            >
                                {preview ? (
                                    <div className="preview-container">
                                        <img src={preview} alt="Preview" />
                                        <div>
                                            <strong>{image?.name}</strong>
                                            <span>Click to replace image</span>
                                        </div>
                                    </div>
                                ) : (
                                    <>
                                        <div className="upload-icon">↑</div>
                                        <strong>Upload product image</strong>
                                        <span>
                                            PNG, JPG or JPEG · Click to browse
                                        </span>
                                    </>
                                )}

                                <input
                                    ref={inputRef}
                                    type="file"
                                    accept="image/png,image/jpeg,image/jpg"
                                    onChange={handleImage}
                                    hidden
                                />
                            </div>
                        </div>
                    </div>

                    {error && (
                        <div className="error-message">
                            {error}
                        </div>
                    )}

                    <div className="form-actions">
                        <button
                            type="button"
                            className="secondary-button"
                            onClick={reset}
                        >
                            Reset
                        </button>

                        <button
                            type="submit"
                            className="primary-button"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <span className="button-spinner"></span>
                                    Analyzing...
                                </>
                            ) : (
                                <>
                                    <span>✦</span>
                                    Classify Product
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </section>

            <section>
                {loading && (
                    <div className="section-card">
                        <Loading text="AI is analyzing the product..." />

                        <div className="analysis-steps">
                            <div className="analysis-step active">
                                <span>01</span>
                                Understanding product
                            </div>

                            <div className="analysis-step">
                                <span>02</span>
                                Searching taxonomy
                            </div>

                            <div className="analysis-step">
                                <span>03</span>
                                Ranking categories
                            </div>
                        </div>
                    </div>
                )}

                {!loading && product?.classification && (
                    <ClassificationCard
                        classification={product.classification}
                    />
                )}

                {!loading && !product && (
                    <div className="ai-preview">
                        <div className="ai-orb">✦</div>
                        <h3>AI Classification</h3>
                        <p>
                            Your classification result will appear here after
                            the product has been analyzed.
                        </p>
                    </div>
                )}
            </section>
        </div>
    );
}