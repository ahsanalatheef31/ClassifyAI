export default function StatusBadge({ status }) {
    const normalized = (status || "pending").toLowerCase();

    return (
        <span className={`status-badge ${normalized}`}>
            <span className="badge-dot"></span>
            {normalized}
        </span>
    );
}