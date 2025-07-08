const PATIENT_API_URL = '/api/list-patients/';

const searchInput = document.getElementById('patient-search-input');
const resultsList = document.getElementById('patient-results-list');
const searchDropdownContainer = document.getElementById('patient-search-dropdown-container');


async function fetchPatients(searchTerm) {
    try {
        const url = searchTerm ? `${PATIENT_API_URL}?q=${encodeURIComponent(searchTerm)}` : PATIENT_API_URL;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data; 
    } catch (error) {
        console.error("Error fetching patients:", error);
        return [];
    }
}

function renderResults(filteredPatients) {
    resultsList.innerHTML = '';

    if (filteredPatients.length === 0 && searchInput.value.trim() !== '') {
        const noResultsDiv = document.createElement('div');
        noResultsDiv.className = 'px-4 py-2 text-gray-500 text-sm';
        noResultsDiv.textContent = 'No matching patients found.';
        resultsList.appendChild(noResultsDiv);
        resultsList.classList.remove('hidden');
    } else if (filteredPatients.length > 0) {
        filteredPatients.forEach(patient => {
            const resultItem = document.createElement('div');
            resultItem.className = 'px-4 py-2 cursor-pointer hover:bg-blue-50 hover:text-blue-700 rounded-md transition-colors duration-200 text-gray-800 text-sm';
            resultItem.innerHTML = `
                <div>${patient.first_name} ${patient.last_name}</div>
                <div class="text-xs text-gray-500">${patient.id || 'N/A'}</div>
            `;
            resultItem.dataset.patientId = patient.id; 

            resultItem.addEventListener('click', () => {
                const patientDetailUrl = `/${patient.id}/`;
                window.location.href = patientDetailUrl;

                searchInput.value = `${patient.first_name} ${patient.last_name} (ID: ${patient.id || 'N/A'})`;
                resultsList.classList.add('hidden');
            });
            resultsList.appendChild(resultItem);
        });
        resultsList.classList.remove('hidden');
    } else {
        resultsList.classList.add('hidden'); 
    }
}

searchInput.addEventListener('input', async (event) => {
    const searchTerm = event.target.value.toLowerCase().trim();

    if (searchTerm.length > 0) {
        const filteredPatients = await fetchPatients(searchTerm);
        renderResults(filteredPatients);
    } else {
        const allPatients = await fetchPatients(''); 
        renderResults(allPatients);
    }
});

document.addEventListener('click', (event) => {
    if (!searchDropdownContainer.contains(event.target)) {
        resultsList.classList.add('hidden');
    }
});

searchInput.addEventListener('focus', async () => {
    if (searchInput.value.trim() === '') {
        const allPatients = await fetchPatients('');
        renderResults(allPatients);
    }
});