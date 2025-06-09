const PATIENT_API_URL = '/api/list-patients/'; // Adjusted to your actual API endpoint

const searchInput = document.getElementById('patient-search-input');
const resultsList = document.getElementById('patient-results-list');
const searchDropdownContainer = document.getElementById('patient-search-dropdown-container');

/**
 * Fetches patient data from the API based on a search term.
 * @param {string} searchTerm - The term to search for (name or ID).
 * @returns {Promise<Array<Object>>} A promise that resolves to an array of patient objects.
 */
async function fetchPatients(searchTerm) {
    try {
        // Construct the URL with a query parameter for the search term
        const url = searchTerm ? `${PATIENT_API_URL}?q=${encodeURIComponent(searchTerm)}` : PATIENT_API_URL;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data; // Assuming your API returns an array of patient objects
    } catch (error) {
        console.error("Error fetching patients:", error);
        // Return an empty array to prevent further errors in rendering
        return [];
    }
}

/**
 * Renders the filtered list of patients into the results dropdown.
 * @param {Array<Object>} filteredPatients - An array of patient objects to display.
 */
function renderResults(filteredPatients) {
    resultsList.innerHTML = ''; // Clear previous results

    if (filteredPatients.length === 0 && searchInput.value.trim() !== '') {
        // Display "No results" message if no matches and input is not empty
        const noResultsDiv = document.createElement('div');
        noResultsDiv.className = 'px-4 py-2 text-gray-500 text-sm';
        noResultsDiv.textContent = 'No matching patients found.';
        resultsList.appendChild(noResultsDiv);
        resultsList.classList.remove('hidden');
    } else if (filteredPatients.length > 0) {
        filteredPatients.forEach(patient => {
            const resultItem = document.createElement('div');
            resultItem.className = 'px-4 py-2 cursor-pointer hover:bg-blue-50 hover:text-blue-700 rounded-md transition-colors duration-200 text-gray-800 text-sm';
            // Ensure patient.id exists and is displayed
            resultItem.innerHTML = `
                <div>${patient.first_name} ${patient.last_name}</div>
                <div class="text-xs text-gray-500">${patient.id || 'N/A'}</div>
            `;
            resultItem.dataset.patientId = patient.id; // Store patient ID

            resultItem.addEventListener('click', () => {
                // Simulate Django's `location = this.value` behavior
                // Updated to match your urls.py: path("patients/<str:patient_id>/", patient_detail, name="patient_detail"),
                const patientDetailUrl = `/patients/${patient.id}/`; // Replace with your actual URL pattern
                window.location.href = patientDetailUrl;

                // Optionally, update the input field with the selected patient's name and ID
                searchInput.value = `${patient.first_name} ${patient.last_name} (ID: ${patient.id || 'N/A'})`;
                resultsList.classList.add('hidden'); // Hide results after selection
            });
            resultsList.appendChild(resultItem);
        });
        resultsList.classList.remove('hidden'); // Show the results list
    } else {
        resultsList.classList.add('hidden'); // Hide if no input or no results
    }
}

// Event listener for input changes on the search box
searchInput.addEventListener('input', async (event) => {
    const searchTerm = event.target.value.toLowerCase().trim();

    if (searchTerm.length > 0) {
        // Fetch filtered patients from the API
        const filteredPatients = await fetchPatients(searchTerm);
        renderResults(filteredPatients);
    } else {
        // If search term is empty, fetch all patients (or a default set)
        const allPatients = await fetchPatients(''); // Fetch all or initial set
        renderResults(allPatients);
    }
});

// Event listener to hide results when clicking outside the search/dropdown container
document.addEventListener('click', (event) => {
    if (!searchDropdownContainer.contains(event.target)) {
        resultsList.classList.add('hidden');
    }
});

// Event listener to show all patients when input is focused and empty
searchInput.addEventListener('focus', async () => {
    if (searchInput.value.trim() === '') {
        const allPatients = await fetchPatients(''); // Fetch all or initial set
        renderResults(allPatients);
    }
});