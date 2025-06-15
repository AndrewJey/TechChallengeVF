/**
 * Results Component JavaScript
 * This file handles the results block functionality including:
 * - Loading results from results.json
 * - Implementing pagination
 * - Updating the number of items per page
 */

// Results state variables
let resultsData = [];
let currentPage = 1;
let itemsPerPage = 10;
let totalPages = 0;

/**
 * Initialize the results component
 */
function initResults() {
    // Load the results data
    loadResults();
    
    // Add event listeners for pagination
    setupPaginationListeners();
    
    console.log('Results component initialized');
}

/**
 * Load results from the JSON file
 */
function loadResults() {
    // Fetch results from the JSON file
    fetch('data/results.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load results');
            }
            return response.json();
        })
        .then(data => {
            // Store the results data
            resultsData = data;
            
            // Calculate total pages
            totalPages = Math.ceil(resultsData.length / itemsPerPage);
            
            // Display the first page of results
            displayResults(1);
            
            // Update pagination controls
            updatePaginationControls();
        })
        .catch(error => {
            console.error('Error loading results:', error);
            
            // Show error notification
            showNotification('Failed to load results. Please try again later.', 'error');
            
            // Display an error message in the results container
            const resultsContainer = document.getElementById('results-container');
            if (resultsContainer) {
                resultsContainer.innerHTML = `
                    <div class="col-12 text-center">
                        <p class="text-danger">Failed to load results. Please try again later.</p>
                    </div>
                `;
            }
        });
}

/**
 * Display a specific page of results
 * @param {number} page - The page number to display
 */
function displayResults(page) {
    // Validate the page number
    if (page < 1 || page > totalPages) {
        console.error('Invalid page number:', page);
        return;
    }
    
    // Update current page
    currentPage = page;
    
    // Calculate the start and end indices for the current page
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, resultsData.length);
    
    // Get the current page of results
    const currentResults = resultsData.slice(startIndex, endIndex);
    
    // Get the results container
    const resultsContainer = document.getElementById('results-container');
    if (!resultsContainer) {
        console.error('Results container not found');
        return;
    }
    
    // Clear the container
    resultsContainer.innerHTML = '';
    
    // Display the results
    currentResults.forEach(result => {
        // Create a card for each result
        const resultCard = document.createElement('div');
        resultCard.className = 'col-md-6 col-lg-4';
        resultCard.innerHTML = `
            <div class="card result-card">
                <div class="card-body">
                    <h5 class="card-title">${result.title}</h5>
                    <h6 class="card-subtitle mb-2 text-muted">${result.category}</h6>
                    <p class="card-text">${result.description}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">${formatDate(result.date)}</small>
                        <a href="#" class="btn btn-sm btn-primary">View Details</a>
                    </div>
                </div>
            </div>
        `;
        
        // Add the card to the container
        resultsContainer.appendChild(resultCard);
    });
    
    // Update pagination controls
    updatePaginationControls();
}

/**
 * Update the pagination controls based on the current state
 */
function updatePaginationControls() {
    // Get the pagination container
    const pagination = document.getElementById('pagination');
    if (!pagination) {
        console.error('Pagination container not found');
        return;
    }
    
    // Get the pagination list
    const paginationList = pagination.querySelector('ul.pagination');
    if (!paginationList) {
        console.error('Pagination list not found');
        return;
    }
    
    // Clear the pagination list except for the Previous and Next buttons
    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');
    
    // Remove all page number buttons
    Array.from(paginationList.children).forEach(item => {
        if (!item.id.includes('prev-page') && !item.id.includes('next-page')) {
            paginationList.removeChild(item);
        }
    });
    
    // Add page number buttons
    for (let i = 1; i <= totalPages; i++) {
        const pageItem = document.createElement('li');
        pageItem.className = `page-item ${i === currentPage ? 'active' : ''}`;
        pageItem.id = `page-${i}`;
        pageItem.innerHTML = `<a class="page-link" href="#">${i}</a>`;
        
        // Add click event listener
        pageItem.addEventListener('click', function(e) {
            e.preventDefault();
            displayResults(i);
        });
        
        // Insert before the Next button
        paginationList.insertBefore(pageItem, nextButton);
    }
    
    // Update Previous button state
    if (prevButton) {
        if (currentPage === 1) {
            prevButton.classList.add('disabled');
        } else {
            prevButton.classList.remove('disabled');
        }
    }
    
    // Update Next button state
    if (nextButton) {
        if (currentPage === totalPages) {
            nextButton.classList.add('disabled');
        } else {
            nextButton.classList.remove('disabled');
        }
    }
}

/**
 * Set up event listeners for pagination controls
 */
function setupPaginationListeners() {
    // Previous button click event
    const prevButton = document.getElementById('prev-page');
    if (prevButton) {
        prevButton.addEventListener('click', function(e) {
            e.preventDefault();
            if (currentPage > 1) {
                displayResults(currentPage - 1);
            }
        });
    }
    
    // Next button click event
    const nextButton = document.getElementById('next-page');
    if (nextButton) {
        nextButton.addEventListener('click', function(e) {
            e.preventDefault();
            if (currentPage < totalPages) {
                displayResults(currentPage + 1);
            }
        });
    }
}

/**
 * Update the number of items per page
 * @param {number} newItemsPerPage - The new number of items per page
 */
function updateItemsPerPage(newItemsPerPage) {
    // Update the items per page
    itemsPerPage = newItemsPerPage;
    
    // Recalculate total pages
    totalPages = Math.ceil(resultsData.length / itemsPerPage);
    
    // Adjust current page if needed
    if (currentPage > totalPages) {
        currentPage = totalPages;
    }
    
    // Display the current page with the new items per page
    displayResults(currentPage);
}