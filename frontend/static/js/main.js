// ── Sales & Marketing Tracker — Global JavaScript ──

console.log('✅ Sales & Marketing Tracker — JavaScript loaded successfully');

/**
 * showAlert — displays a Bootstrap alert message inside any container
 *
 * How to use it later:
 *   showAlert('myDivId', 'Something went wrong!', 'danger')
 *   showAlert('myDivId', 'Saved successfully!', 'success')
 */
function showAlert(containerId, message, type = 'danger') {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
}
