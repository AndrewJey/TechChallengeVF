/**
 * Calendar Component JavaScript
 * This file handles the calendar functionality including:
 * - Initializing the FullCalendar component
 * - Loading events from events.json
 * - Handling event clicks to display details
 */

// Calendar instance variable
let calendar;

/**
 * Initialize the calendar component
 */
function initCalendar() {
    // Get the calendar container element
    const calendarEl = document.getElementById('calendar');
    
    if (!calendarEl) {
        console.error('Calendar container not found');
        return;
    }
    
    // Initialize FullCalendar
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        selectable: true,
        selectMirror: true,
        dayMaxEvents: true,
        weekNumbers: true,
        navLinks: true,
        
        // Event handling
        eventClick: handleEventClick,
        select: handleDateSelect,
        
        // Load events from JSON file
        events: loadCalendarEvents
    });
    
    // Render the calendar
    calendar.render();
    
    console.log('Calendar initialized');
}

/**
 * Load calendar events from the JSON file
 * @param {Object} info - Information about the current view
 * @param {Function} successCallback - Callback function to return events
 * @param {Function} failureCallback - Callback function for error handling
 */
function loadCalendarEvents(info, successCallback, failureCallback) {
    // Fetch events from the JSON file
    fetch('data/events.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load events');
            }
            return response.json();
        })
        .then(data => {
            // Process the events data
            const events = data.map(event => {
                // Convert event data to FullCalendar format if needed
                return {
                    id: event.id,
                    title: event.title,
                    start: event.start,
                    end: event.end,
                    allDay: event.allDay || false,
                    color: event.color || getEventColor(event.category),
                    extendedProps: {
                        description: event.description,
                        location: event.location,
                        category: event.category
                    }
                };
            });
            
            // Call the success callback with the events
            successCallback(events);
        })
        .catch(error => {
            console.error('Error loading events:', error);
            failureCallback(error);
            
            // Show error notification
            showNotification('Failed to load calendar events. Please try again later.', 'error');
        });
}

/**
 * Handle event click to display event details
 * @param {Object} info - Information about the clicked event
 */
function handleEventClick(info) {
    // Get the event details
    const event = info.event;
    const title = event.title;
    const start = formatDate(event.start, true);
    const end = event.end ? formatDate(event.end, true) : '';
    const description = event.extendedProps.description || 'No description available';
    const location = event.extendedProps.location || 'No location specified';
    
    // Create the HTML for the event details
    const eventDetailsHtml = `
        <div class="event-details-container">
            <h3 class="event-title">${title}</h3>
            <div class="event-time">
                <strong>Start:</strong> ${start}
                ${end ? `<br><strong>End:</strong> ${end}` : ''}
            </div>
            <div class="event-location">
                <strong>Location:</strong> ${location}
            </div>
            <div class="event-description">
                <strong>Description:</strong>
                <p>${description}</p>
            </div>
        </div>
    `;
    
    // Update the event details panel
    const eventDetailsPanel = document.getElementById('event-details');
    if (eventDetailsPanel) {
        eventDetailsPanel.innerHTML = eventDetailsHtml;
    }
    
    // Also update the modal if we want to show it
    const modalEventDetails = document.getElementById('modal-event-details');
    if (modalEventDetails) {
        modalEventDetails.innerHTML = eventDetailsHtml;
        
        // Show the modal
        const eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
        eventModal.show();
    }
}

/**
 * Handle date selection
 * @param {Object} info - Information about the selected date range
 */
function handleDateSelect(info) {
    // For this demo, we'll just log the selected date range
    console.log('Selected date range:', info.startStr, 'to', info.endStr);
    
    // In a real application, you might open a modal to create a new event
    // For now, we'll just show a notification
    showNotification(`Selected date range: ${formatDate(info.start)} to ${formatDate(info.end)}`, 'info');
    
    // Clear the selection
    calendar.unselect();
}

/**
 * Get a color for an event based on its category
 * @param {string} category - The event category
 * @returns {string} The color code
 */
function getEventColor(category) {
    // Map categories to colors
    const colorMap = {
        'meeting': '#4285F4',     // Blue
        'holiday': '#34A853',     // Green
        'important': '#EA4335',   // Red
        'personal': '#FBBC05',    // Yellow
        'conference': '#9C27B0',  // Purple
        'workshop': '#00ACC1',    // Cyan
        'deadline': '#FF6D00'     // Orange
    };
    
    // Return the appropriate color or a default if not found
    return colorMap[category] || '#4285F4';
}