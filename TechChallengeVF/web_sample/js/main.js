/**
 * Main JavaScript file for the Modern Dashboard
 * This file initializes the application and handles common functionality
 */

// Wait for the DOM to be fully loaded before executing any JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Application initialized');
    fetch("results.json")
        .then(response => response.json())
        .then(data => {
            console.log("Productos:", data);
            // Aquí actualizás el DOM con los datos
        });
    // Initialize all components
    initCalendar();
    initResults();
    initFiles();
    
    // Add event listeners for UI interactions
    addEventListeners();
});

/**
 * Add event listeners for UI interactions
 */
function addEventListeners() {
    // Items per page dropdown change event
    const itemsPerPageSelect = document.getElementById('items-per-page');
    if (itemsPerPageSelect) {
        itemsPerPageSelect.addEventListener('change', function() {
            // Update the number of items per page and refresh the results
            const itemsPerPage = parseInt(this.value);
            updateItemsPerPage(itemsPerPage);
        });
    }
}

/**
 * Show a notification message to the user
 * @param {string} message - The message to display
 * @param {string} type - The type of message (success, error, info, warning)
 */
function showNotification(message, type = 'info') {
    // You could implement a toast notification system here
    console.log(`${type.toUpperCase()}: ${message}`);
    
    // For now, we'll just use an alert for simplicity
    alert(message);
}

/**
 * Format a date for display
 * @param {Date} date - The date to format
 * @param {boolean} includeTime - Whether to include the time
 * @returns {string} The formatted date string
 */
function formatDate(date, includeTime = false) {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }
    
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric'
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return date.toLocaleDateString('en-US', options);
}

/**
 * Format a file size for display
 * @param {number} bytes - The file size in bytes
 * @returns {string} The formatted file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Get the appropriate icon for a file type
 * @param {string} fileType - The file type/extension
 * @returns {string} The icon class
 */
function getFileIcon(fileType) {
    // Map file extensions to Bootstrap icons
    const iconMap = {
        'pdf': 'bi-file-earmark-pdf',
        'doc': 'bi-file-earmark-word',
        'docx': 'bi-file-earmark-word',
        'xls': 'bi-file-earmark-excel',
        'xlsx': 'bi-file-earmark-excel',
        'ppt': 'bi-file-earmark-ppt',
        'pptx': 'bi-file-earmark-ppt',
        'txt': 'bi-file-earmark-text',
        'zip': 'bi-file-earmark-zip',
        'jpg': 'bi-file-earmark-image',
        'jpeg': 'bi-file-earmark-image',
        'png': 'bi-file-earmark-image',
        'gif': 'bi-file-earmark-image'
    };
    
    // Get the file extension (lowercase)
    const extension = fileType.toLowerCase();
    
    // Return the appropriate icon class or a default if not found
    return iconMap[extension] || 'bi-file-earmark';
}