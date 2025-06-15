/**
 * Files Component JavaScript
 * This file handles the files section functionality including:
 * - Loading file metadata from files.json
 * - Displaying file cards with appropriate icons
 * - Handling file download/view actions
 */

/**
 * Initialize the files component
 */
function initFiles() {
    // Load the files data
    loadFiles();
    
    console.log('Files component initialized');
}

/**
 * Load files from the JSON file
 */
function loadFiles() {
    // Fetch files from the JSON file
    fetch('data/files.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load files');
            }
            return response.json();
        })
        .then(data => {
            // Display the files
            displayFiles(data);
        })
        .catch(error => {
            console.error('Error loading files:', error);
            
            // Show error notification
            showNotification('Failed to load files. Please try again later.', 'error');
            
            // Display an error message in the files container
            const filesContainer = document.getElementById('files-container');
            if (filesContainer) {
                filesContainer.innerHTML = `
                    <div class="col-12 text-center">
                        <p class="text-danger">Failed to load files. Please try again later.</p>
                    </div>
                `;
            }
        });
}

/**
 * Display the files in the files container
 * @param {Array} files - The array of file objects
 */
function displayFiles(files) {
    // Get the files container
    const filesContainer = document.getElementById('files-container');
    if (!filesContainer) {
        console.error('Files container not found');
        return;
    }
    
    // Clear the container
    filesContainer.innerHTML = '';
    
    // Check if there are any files
    if (!files || files.length === 0) {
        filesContainer.innerHTML = `
            <div class="col-12 text-center">
                <p class="text-muted">No files available</p>
            </div>
        `;
        return;
    }
    
    // Add Bootstrap Icons CSS if not already included
    if (!document.querySelector('link[href*="bootstrap-icons"]')) {
        const iconsCss = document.createElement('link');
        iconsCss.rel = 'stylesheet';
        iconsCss.href = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css';
        document.head.appendChild(iconsCss);
    }
    
    // Display the files
    files.forEach(file => {
        // Create a card for each file
        const fileCard = document.createElement('div');
        fileCard.className = 'col-md-3 col-sm-6 mb-4';
        
        // Get the file extension from the filename
        const fileExtension = file.filename.split('.').pop().toLowerCase();
        
        // Get the appropriate icon for the file type
        const iconClass = getFileIcon(fileExtension);
        
        // Format the file size
        const formattedSize = formatFileSize(file.size);
        
        // Create the file card HTML
        fileCard.innerHTML = `
            <div class="card file-card text-center h-100">
                <div class="card-body">
                    <i class="bi ${iconClass} file-icon"></i>
                    <h5 class="file-name">${file.filename}</h5>
                    <p class="file-type">${file.type}</p>
                    <p class="file-size">${formattedSize}</p>
                    <a href="${file.url}" class="btn btn-sm btn-outline-primary" 
                       target="_blank" download="${file.filename}">
                        Download
                    </a>
                    ${isViewable(fileExtension) ? 
                        `<a href="${file.url}" class="btn btn-sm btn-outline-secondary ms-2" 
                           target="_blank">View</a>` : ''}
                </div>
            </div>
        `;
        
        // Add click event to the card (excluding the buttons)
        fileCard.querySelector('.card').addEventListener('click', function(e) {
            // Only trigger if the click was not on a button
            if (!e.target.closest('a.btn')) {
                // Show file details or trigger download
                handleFileCardClick(file);
            }
        });
        
        // Add the card to the container
        filesContainer.appendChild(fileCard);
    });
}

/**
 * Handle click on a file card
 * @param {Object} file - The file object
 */
function handleFileCardClick(file) {
    // Get the file extension
    const fileExtension = file.filename.split('.').pop().toLowerCase();
    
    // If the file is viewable, open it in a new tab
    if (isViewable(fileExtension)) {
        window.open(file.url, '_blank');
    } else {
        // Otherwise, trigger download
        const link = document.createElement('a');
        link.href = file.url;
        link.download = file.filename;
        link.click();
    }
}

/**
 * Check if a file is viewable in the browser
 * @param {string} fileExtension - The file extension
 * @returns {boolean} Whether the file is viewable
 */
function isViewable(fileExtension) {
    // List of file extensions that can be viewed in the browser
    const viewableExtensions = [
        'pdf', 'jpg', 'jpeg', 'png', 'gif', 'svg', 'txt', 'html', 'htm', 'mp4', 'webm', 'mp3', 'wav'
    ];
    
    return viewableExtensions.includes(fileExtension.toLowerCase());
}