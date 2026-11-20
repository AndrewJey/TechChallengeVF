/**
 * Files Component JavaScript
 * Safe DOM rendering and external link hygiene.
 */

function initFiles() {
    loadFiles();
}

function safeFileUrl(url) {
    if (!url || typeof url !== 'string') return '#';
    const trimmed = url.trim();
    if (/^(https?:\/\/|\/|files\/)/i.test(trimmed)) return trimmed;
    return '#';
}

function loadFiles() {
    fetch('data/files.json')
        .then(function (response) {
            if (!response.ok) throw new Error('Failed to load files');
            return response.json();
        })
        .then(function (data) {
            displayFiles(Array.isArray(data) ? data : []);
        })
        .catch(function (error) {
            console.error('Error loading files:', error);
            if (typeof showNotification === 'function') {
                showNotification('Failed to load files. Please try again later.', 'error');
            }
            const filesContainer = document.getElementById('files-container');
            if (filesContainer) {
                filesContainer.textContent = '';
                const p = document.createElement('p');
                p.className = 'text-danger text-center w-100';
                p.textContent = 'Failed to load files. Please try again later.';
                filesContainer.appendChild(p);
            }
        });
}

function displayFiles(files) {
    const filesContainer = document.getElementById('files-container');
    if (!filesContainer) return;
    filesContainer.textContent = '';

    if (!files || files.length === 0) {
        const p = document.createElement('p');
        p.className = 'text-muted text-center w-100';
        p.textContent = 'No files available';
        filesContainer.appendChild(p);
        return;
    }

    files.forEach(function (file) {
        const col = document.createElement('div');
        col.className = 'col-md-3 col-sm-6 mb-4';

        const filename = String(file.filename || 'file');
        const ext = filename.includes('.') ? filename.split('.').pop().toLowerCase() : '';
        const iconClass = typeof getFileIcon === 'function' ? getFileIcon(ext) : 'bi-file-earmark';
        const formattedSize = typeof formatFileSize === 'function' ? formatFileSize(file.size) : String(file.size || '');
        const url = safeFileUrl(file.url);

        const card = document.createElement('div');
        card.className = 'card file-card text-center h-100';
        const body = document.createElement('div');
        body.className = 'card-body';

        const icon = document.createElement('i');
        icon.className = 'bi ' + iconClass + ' file-icon';
        const h5 = document.createElement('h5');
        h5.className = 'file-name';
        h5.textContent = filename;
        const pType = document.createElement('p');
        pType.className = 'file-type';
        pType.textContent = file.type || ext.toUpperCase();
        const pSize = document.createElement('p');
        pSize.className = 'file-size';
        pSize.textContent = formattedSize;

        const dl = document.createElement('a');
        dl.href = url;
        dl.className = 'btn btn-sm btn-outline-primary';
        dl.target = '_blank';
        dl.rel = 'noopener noreferrer';
        dl.download = filename;
        dl.textContent = 'Download';

        body.append(icon, h5, pType, pSize, dl);
        if (isViewable(ext)) {
            const view = document.createElement('a');
            view.href = url;
            view.className = 'btn btn-sm btn-outline-secondary ms-2';
            view.target = '_blank';
            view.rel = 'noopener noreferrer';
            view.textContent = 'View';
            body.appendChild(view);
        }

        card.appendChild(body);
        col.appendChild(card);
        filesContainer.appendChild(col);
    });
}

function isViewable(fileExtension) {
    const viewableExtensions = ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'svg', 'txt', 'html', 'htm', 'mp4', 'webm', 'mp3', 'wav'];
    return viewableExtensions.includes(String(fileExtension || '').toLowerCase());
}
