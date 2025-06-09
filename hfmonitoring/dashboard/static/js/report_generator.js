document.addEventListener('DOMContentLoaded', function () {

    const openReportModalBtn = document.getElementById('openReportModalBtn');
    const datePickerModal = document.getElementById('datePickerModal');
    const reportModal = document.getElementById('reportModal');
    
    if (!openReportModalBtn || !datePickerModal || !reportModal) {
        console.error("Report generator elements were not found. The script will not run.");
        return;
    }
    
    const closeDatePickerModalBtn = document.getElementById('closeDatePickerModalBtn');
    const reportLast2WeeksBtn = document.getElementById('report-last-2-weeks');
    const reportLast1MonthBtn = document.getElementById('report-last-1-month');
    const closeReportModalBtn = document.getElementById('closeReportModalBtn');
    const reportContent = document.getElementById('reportContent');
    const reportTitle = document.getElementById('report-title'); // Get the title element

    openReportModalBtn.addEventListener('click', function() {
        datePickerModal.classList.remove('hidden');
    });

    closeDatePickerModalBtn.addEventListener('click', function() {
        datePickerModal.classList.add('hidden');
    });

    reportLast2WeeksBtn.addEventListener('click', function() {
        const today = new Date();
        const startDate = new Date();
        startDate.setDate(today.getDate() - 14);
        fetchReportForPeriod(startDate, today);
    });

    reportLast1MonthBtn.addEventListener('click', function() {
        const today = new Date();
        const startDate = new Date();
        startDate.setMonth(today.getMonth() - 1);
        fetchReportForPeriod(startDate, today);
    });
    
    closeReportModalBtn.addEventListener('click', function () {
        reportModal.classList.add('hidden');
    });

    function fetchReportForPeriod(startDate, endDate) {
        datePickerModal.classList.add('hidden');
        reportModal.classList.remove('hidden');
        reportContent.innerHTML = '<p class="text-center text-gray-500">Generating report...</p>';
        
        // --- UPDATED: This section now sets your desired title ---
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        const formattedStartDate = startDate.toLocaleDateString('en-US', options);
        const formattedEndDate = endDate.toLocaleDateString('en-US', options);
        if (reportTitle) {
            reportTitle.textContent = `Patient's Health Report from ${formattedStartDate} to ${formattedEndDate}`;
        }
        
        const pathParts = window.location.pathname.split('/');
        const patientId = pathParts[2];

        if (!patientId) {
            reportContent.innerHTML = `<p class="text-center text-red-500">Error: Could not find patient ID in the URL.</p>`;
            return;
        }

        const startDateStr = startDate.toISOString().split('T')[0];
        const endDateStr = endDate.toISOString().split('T')[0];
        const url = `/api/patients/${patientId}/generate-abnormal-report/?start_date=${startDateStr}&end_date=${endDateStr}`;

        fetch(url)
            .then(response => {
                if (!response.ok) { return response.json().then(err => { throw new Error(err.error || 'Server error'); }); }
                return response.json();
            })
            .then(data => {
                displayComprehensiveReport(data.report_data);
            })
            .catch(error => {
                console.error('Error fetching report data:', error);
                reportContent.innerHTML = `<p class="text-center text-red-500">Failed to generate report: ${error.message}</p>`;
            });
    }

    function displayComprehensiveReport(reportData) {
        if (!reportData || reportData.length === 0) {
            reportContent.innerHTML = '<p class="text-center text-gray-600 font-medium">No vitals data found for this patient in the selected date range.</p>';
            return;
        }

        let html = '';
        const patientReport = reportData[0];
        const info = patientReport.patient_info;
        const stats = patientReport.stats;

        html += `
        <div class="p-4 border border-gray-200 rounded-lg">
            <div class="mb-4">
                <h3 class="text-xl font-bold text-blue-700">${info.name}</h3>
                <div class="flex flex-wrap text-sm text-gray-600 gap-x-4 gap-y-1">
                    <span><strong>ID:</strong> ${info.id}</span>
                    <span><strong>DOB:</strong> ${info.dob}</span>
                    <span><strong>Sex:</strong> ${info.sex}</span>
                </div>
            </div>
            <div class="mb-4">
                <h4 class="font-semibold text-gray-800 mb-2">Summary Statistics (Avg / Min / Max)</h4>
                <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 text-center">
                    <div class="p-2 bg-gray-50 rounded"><p class="text-xs font-medium text-gray-500">Systolic BP</p><p class="text-md font-bold text-gray-800 whitespace-nowrap">${stats.systolic_bp.avg} / ${stats.systolic_bp.min} / ${stats.systolic_bp.max}</p></div>
                    <div class="p-2 bg-gray-50 rounded"><p class="text-xs font-medium text-gray-500">Diastolic BP</p><p class="text-md font-bold text-gray-800 whitespace-nowrap">${stats.diastolic_bp.avg} / ${stats.diastolic_bp.min} / ${stats.diastolic_bp.max}</p></div>
                    <div class="p-2 bg-gray-50 rounded"><p class="text-xs font-medium text-gray-500">Heart Rate</p><p class="text-md font-bold text-gray-800 whitespace-nowrap">${stats.heart_rate.avg} / ${stats.heart_rate.min} / ${stats.heart_rate.max}</p></div>
                    <div class="p-2 bg-gray-50 rounded"><p class="text-xs font-medium text-gray-500">SpO2</p><p class="text-md font-bold text-gray-800 whitespace-nowrap">${stats.oxygen_saturation.avg} / ${stats.oxygen_saturation.min} / ${stats.oxygen_saturation.max}</p></div>
                    <div class="p-2 bg-gray-50 rounded"><p class="text-xs font-medium text-gray-500">Weight (kg)</p><p class="text-md font-bold text-gray-800 whitespace-nowrap">${stats.weight.avg} / ${stats.weight.min} / ${stats.weight.max}</p></div>
                    <div class="p-2 bg-gray-50 rounded"><p class="text-xs font-medium text-gray-500">BMI</p><p class="text-md font-bold text-gray-800 whitespace-nowrap">${stats.bmi.avg} / ${stats.bmi.min} / ${stats.bmi.max}</p></div>
                </div>
            </div>`;
            
        if (patientReport.abnormal_instances && patientReport.abnormal_instances.length > 0) {
            html += `
            <div>
                <h4 class="font-semibold text-gray-800 mb-2">Abnormal Readings</h4>
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50"><tr><th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date & Time</th><th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Metric</th><th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Value</th></tr></thead>
                    <tbody class="bg-white divide-y divide-gray-200">`;
            patientReport.abnormal_instances.forEach(instance => {
                for (const [key, value] of Object.entries(instance.details)) {
                     html += `<tr><td class="px-4 py-2 whitespace-nowrap text-sm text-gray-600">${instance.date}</td><td class="px-4 py-2 whitespace-nowrap text-sm text-gray-800 font-semibold">${key}</td><td class="px-4 py-2 whitespace-nowrap text-sm text-red-600 font-bold">${value}</td></tr>`;
                }
            });
            html += `</tbody></table></div>`;
        } else {
            html += `
            <div>
                <h4 class="font-semibold text-gray-800 mb-2">Abnormal Readings</h4>
                <div class="text-center p-4 border-2 border-dashed rounded-lg">
                    <p class="text-gray-600 font-medium">No abnormal instances found in this period.</p>
                </div>
            </div>`;
        }
        html += `</div>`;
        reportContent.innerHTML = html;
    }
});
