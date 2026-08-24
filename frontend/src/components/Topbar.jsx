
import { useLocation } from "react-router-dom";

const titles = {
    "/": ["Dashboard", "Overview of your product intelligence"],
    "/products": ["Products", "Manage and analyze your catalog"],
    "/classify": ["Classify Product", "Analyze a product with AI"],
    "/bulk-upload": ["Bulk Upload", "Classify hundreds of products at once"],
    "/review": ["Manual Review", "Review low-confidence classifications"],
};

export default function Topbar({ onMenu }) {
    const location = useLocation();

    const current = titles[location.pathname] || [
        "Product Details",
        "Product classification details",
    ];

    return (
        <header className="topbar">
            <button className="menu-button" onClick={onMenu}>
                ☰
            </button>

            <div>
                <h1>{current[0]}</h1>
                <p>{current[1]}</p>
            </div>

            <div className="topbar-right">
                <div className="ai-pill">
                    <span></span>
                    AI Online
                </div>

                <div className="top-avatar">A</div>
            </div>
        </header>
    );
}