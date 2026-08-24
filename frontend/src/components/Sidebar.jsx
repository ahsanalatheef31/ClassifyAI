import { NavLink } from "react-router-dom";

const navigation = [
    {
        label: "Overview",
        items: [
            { name: "Dashboard", path: "/", icon: "⌂" },
            { name: "Products", path: "/products", icon: "▦" },
        ],
    },
    {
        label: "AI Workspace",
        items: [
            { name: "Classify Product", path: "/classify", icon: "✦" },
            { name: "Bulk Upload", path: "/bulk-upload", icon: "⇧" },
            { name: "Manual Review", path: "/review", icon: "✓" },
        ],
    },
];

export default function Sidebar({ mobileOpen, onClose }) {
    return (
        <aside className={`sidebar ${mobileOpen ? "sidebar-open" : ""}`}>
            <div className="brand">
                <div className="brand-mark">✦</div>

                <div>
                    <div className="brand-name">ClassifyAI</div>
                    <div className="brand-subtitle">Product Intelligence</div>
                </div>

                <button className="mobile-close" onClick={onClose}>
                    ×
                </button>
            </div>

            <div className="sidebar-content">
                {navigation.map((section) => (
                    <div className="nav-section" key={section.label}>
                        <div className="nav-label">{section.label}</div>

                        {section.items.map((item) => (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                onClick={onClose}
                                className={({ isActive }) =>
                                    `nav-item ${isActive ? "active" : ""}`
                                }
                            >
                                <span className="nav-icon">{item.icon}</span>
                                <span>{item.name}</span>
                            </NavLink>
                        ))}
                    </div>
                ))}
            </div>

            <div className="sidebar-bottom">
                <div className="system-status">
                    <span className="status-dot"></span>

                    <div>
                        <strong>AI Engine Online</strong>
                        <small>Qwen Vision · Local</small>
                    </div>
                </div>

                <div className="user-mini">
                    <div className="avatar">A</div>

                    <div>
                        <strong>Administrator</strong>
                        <small>Product Manager</small>
                    </div>
                </div>
            </div>
        </aside>
    );
}