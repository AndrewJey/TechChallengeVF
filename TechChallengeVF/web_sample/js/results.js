/**
 * Results Component JavaScript
 * Safe DOM rendering, filtering, pagination, and interactive detail preview.
 */

let allResultsData = [];
let resultsData = [];
let currentPage = 1;
let itemsPerPage = 10;
let totalPages = 1;

function safeHref(url) {
    if (!url || typeof url !== 'string') return '';
    const trimmed = url.trim();
    if (/^(https?:\/\/|\/|files\/)/i.test(trimmed)) return trimmed;
    return '';
}

function initResults() {
    ensureSearchBar();
    loadResults();
    setupPaginationListeners();
}

function ensureSearchBar() {
    const container = document.getElementById('results-container');
    if (!container || document.getElementById('results-search-input')) return;
    const bar = document.createElement('div');
    bar.className = 'mb-3';
    const input = document.createElement('input');
    input.id = 'results-search-input';
    input.type = 'search';
    input.className = 'form-control';
    input.placeholder = 'Filter results by title, category, or description...';
    input.setAttribute('aria-label', 'Filter results');
    input.addEventListener('input', function () {
        applyResultsFilter(this.value);
    });
    bar.appendChild(input);
    container.parentNode.insertBefore(bar, container);
}

function applyResultsFilter(query) {
    const q = String(query || '').trim().toLowerCase();
    resultsData = q
        ? allResultsData.filter(function (r) {
            return (
                String(r.title || '').toLowerCase().includes(q) ||
                String(r.category || '').toLowerCase().includes(q) ||
                String(r.description || '').toLowerCase().includes(q)
            );
        })
        : allResultsData.slice();
    totalPages = Math.max(1, Math.ceil(resultsData.length / itemsPerPage));
    displayResults(1);
}

function loadResults() {
    fetch('data/results.json')
        .then(function (response) {
            if (!response.ok) throw new Error('Failed to load results');
            return response.json();
        })
        .then(function (data) {
            allResultsData = Array.isArray(data) ? data : [];
            resultsData = allResultsData.slice();
            totalPages = Math.max(1, Math.ceil(resultsData.length / itemsPerPage));
            displayResults(1);
        })
        .catch(function (error) {
            console.error('Error loading results:', error);
            if (typeof showNotification === 'function') {
                showNotification('Failed to load results. Please try again later.', 'error');
            }
            const resultsContainer = document.getElementById('results-container');
            if (resultsContainer) {
                resultsContainer.textContent = '';
                const col = document.createElement('div');
                col.className = 'col-12 text-center';
                const p = document.createElement('p');
                p.className = 'text-danger';
                p.textContent = 'Failed to load results. Please try again later.';
                col.appendChild(p);
                resultsContainer.appendChild(col);
            }
        });
}

function displayResults(page) {
    const safeTotal = Math.max(1, totalPages);
    currentPage = Math.min(Math.max(1, page), safeTotal);

    const resultsContainer = document.getElementById('results-container');
    if (!resultsContainer) return;
    resultsContainer.textContent = '';

    if (resultsData.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'col-12 text-center text-muted py-4';
        empty.textContent = 'No matching results found.';
        resultsContainer.appendChild(empty);
        updatePaginationControls();
        return;
    }

    const startIndex = (currentPage - 1) * itemsPerPage;
    const currentResults = resultsData.slice(startIndex, startIndex + itemsPerPage);

    currentResults.forEach(function (result) {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4 mb-3';

        const card = document.createElement('div');
        card.className = 'card result-card h-100';

        const body = document.createElement('div');
        body.className = 'card-body d-flex flex-column';

        const title = document.createElement('h5');
        title.className = 'card-title';
        title.textContent = result.title || 'Untitled';

        const subtitle = document.createElement('h6');
        subtitle.className = 'card-subtitle mb-2 text-muted';
        subtitle.textContent = result.category || '';

        const desc = document.createElement('p');
        desc.className = 'card-text flex-grow-1';
        desc.textContent = result.description || '';

        const footer = document.createElement('div');
        footer.className = 'd-flex justify-content-between align-items-center mt-2';

        const small = document.createElement('small');
        small.className = 'text-muted';
        small.textContent = typeof formatDate === 'function' ? formatDate(result.date) : (result.date || '');

        const href = safeHref(result.url);
        let action;
        if (href) {
            action = document.createElement('a');
            action.href = href;
            action.target = '_blank';
            action.rel = 'noopener noreferrer';
            action.className = 'btn btn-sm btn-primary';
            action.textContent = 'Open Link';
        } else {
            action = document.createElement('button');
            action.type = 'button';
            action.className = 'btn btn-sm btn-outline-primary';
            action.textContent = 'View Details';
            action.addEventListener('click', function () {
                const detailsPanel = document.getElementById('event-details');
                if (detailsPanel) {
                    detailsPanel.textContent = '';
                    const h = document.createElement('h5');
                    h.textContent = result.title || 'Result Details';
                    const p = document.createElement('p');
                    p.textContent = (result.category ? result.category + ' — ' : '') + (result.description || '');
                    detailsPanel.append(h, p);
                }
            });
        }

        footer.append(small, action);
        body.append(title, subtitle, desc, footer);
        card.appendChild(body);
        col.appendChild(card);
        resultsContainer.appendChild(col);
    });

    updatePaginationControls();
}

function updatePaginationControls() {
    const pagination = document.getElementById('pagination');
    if (!pagination) return;
    const paginationList = pagination.querySelector('ul.pagination');
    if (!paginationList) return;

    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');

    Array.from(paginationList.children).forEach(function (item) {
        if (!item.id.includes('prev-page') && !item.id.includes('next-page')) {
            paginationList.removeChild(item);
        }
    });

    for (let i = 1; i <= totalPages; i++) {
        const pageItem = document.createElement('li');
        pageItem.className = 'page-item' + (i === currentPage ? ' active' : '');
        pageItem.id = 'page-' + i;
        const link = document.createElement('a');
        link.className = 'page-link';
        link.href = '#';
        link.textContent = String(i);
        pageItem.appendChild(link);
        pageItem.addEventListener('click', function (e) {
            e.preventDefault();
            displayResults(i);
        });
        paginationList.insertBefore(pageItem, nextButton);
    }

    if (prevButton) prevButton.classList.toggle('disabled', currentPage <= 1);
    if (nextButton) nextButton.classList.toggle('disabled', currentPage >= totalPages);
}

function setupPaginationListeners() {
    const prevButton = document.getElementById('prev-page');
    if (prevButton) {
        prevButton.addEventListener('click', function (e) {
            e.preventDefault();
            if (currentPage > 1) displayResults(currentPage - 1);
        });
    }
    const nextButton = document.getElementById('next-page');
    if (nextButton) {
        nextButton.addEventListener('click', function (e) {
            e.preventDefault();
            if (currentPage < totalPages) displayResults(currentPage + 1);
        });
    }
}

function updateItemsPerPage(newItemsPerPage) {
    itemsPerPage = Math.max(1, Number(newItemsPerPage) || 10);
    totalPages = Math.max(1, Math.ceil(resultsData.length / itemsPerPage));
    displayResults(Math.min(currentPage, totalPages));
}
