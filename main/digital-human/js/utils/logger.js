// Log helper for the test harness UI.
export function log(message, type = 'info') {
    // Split multi-line messages so each line keeps a consistent prefix.
    const lines = message.split('\n');
    const now = new Date();
    // const timestamp = `[${now.toLocaleTimeString()}] `;
    const timestamp = `[${now.toLocaleTimeString()}.${now.getMilliseconds().toString().padStart(3, '0')}] `;

    // Fall back to the console if the log container does not exist.
    const logContainer = document.getElementById('logContainer');
    if (!logContainer) {
        console.log(`[${type.toUpperCase()}] ${message}`);
        return;
    }

    // Create a log entry for each line.
    lines.forEach((line, index) => {
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`;
        // Only the first line shows the timestamp.
        const prefix = index === 0 ? timestamp : ' '.repeat(timestamp.length);
        logEntry.textContent = `${prefix}${line}`;
        // logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        // Preserve leading spaces in wrapped lines.
        logEntry.style.whiteSpace = 'pre';
        if (type === 'error') {
            logEntry.style.color = 'red';
        } else if (type === 'debug') {
            logEntry.style.color = 'gray';
            return;
        } else if (type === 'warning') {
            logEntry.style.color = 'orange';
        } else if (type === 'success') {
            logEntry.style.color = 'green';
        } else {
            logEntry.style.color = 'black';
        }
        logContainer.appendChild(logEntry);
    });

    logContainer.scrollTop = logContainer.scrollHeight;
}
