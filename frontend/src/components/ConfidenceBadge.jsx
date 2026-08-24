export default function ConfidenceBadge({ value }) {
    const confidence = Number(value || 0);
    const percentage =
        confidence <= 1 ? Math.round(confidence * 100) : Math.round(confidence);

    let level = "low";

    if (percentage >= 80) {
        level = "high";
    } else if (percentage >= 60) {
        level = "medium";
    }

    return (
        <span className={`confidence-badge ${level}`}>
            {percentage}%
        </span>
    );
}