export default function Loading({ text = "Loading..." }) {
    return (
        <div className="loading-state">
            <div className="spinner"></div>
            <span>{text}</span>
        </div>
    );
}
