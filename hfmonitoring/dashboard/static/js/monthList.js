document.addEventListener("DOMContentLoaded", () => {
    const timestampSources = [
        document.getElementById("bmiChart"),
        document.getElementById("bpChart"),
        document.getElementById("heartRateChart"),
        document.getElementById("weightChart"),
        document.getElementById("spO2Chart"),
    ].filter(Boolean);

    let allTimestamps = [];
    const chartMap = {};
    const originalChartData = {};

    timestampSources.forEach(el => {
        const chartId = el.id;
        const chartInstance = Chart.getChart(chartId);

        if (chartInstance) {
            chartMap[chartId] = chartInstance;
            originalChartData[chartId] = {
                labels: [...chartInstance.data.labels],
                datasets: chartInstance.data.datasets.map(ds => ({ ...ds, data: [...ds.data] }))
            };
            JSON.parse(el.dataset.timestamps || "[]").forEach(dateStr => {
                const [day, month, year] = dateStr.split('-');
                allTimestamps.push(new Date(year, month - 1, day));
            });
        }
    });

    const timePeriodSelect = document.getElementById("time-period-select");

    if (timePeriodSelect) {
        timePeriodSelect.innerHTML = '<option value="" disabled selected>Select Period</option>';

        const periodOptions = [
            { value: '7d', text: 'Last 1 Week' },
            { value: '14d', text: 'Last 2 Weeks' },
            { value: '30d', text: 'Last 1 Month' }
        ];

        periodOptions.forEach(({ text, value }) => { 
            const option = document.createElement("option");
            option.value = value;
            option.textContent = text; 
            timePeriodSelect.appendChild(option);
        });

        const defaultOption = timePeriodSelect.querySelector('option[value="7d"]');
        if (defaultOption) {
            defaultOption.selected = true;
            setTimeout(() => {
                timePeriodSelect.dispatchEvent(new Event("change"));
            }, 0);
        }

        timePeriodSelect.addEventListener("change", function () {
            const selectedPeriod = this.value;
            const now = new Date();
            let filterStartDate = null;

            const nowForCalc = new Date(now); 

            if (selectedPeriod === '7d') {
                filterStartDate = new Date(nowForCalc.setDate(nowForCalc.getDate() - 7));
            } else if (selectedPeriod === '14d') {
                filterStartDate = new Date(nowForCalc.setDate(nowForCalc.getDate() - 14));
            } else if (selectedPeriod === '30d') {
                filterStartDate = new Date(nowForCalc.setMonth(nowForCalc.getMonth() - 1));
            } 
            
            if (filterStartDate) {
                filterStartDate.setHours(0, 0, 0, 0); 
            }

            Object.entries(chartMap).forEach(([chartId, chart]) => {
                const original = originalChartData[chartId];
                const newLabels = [];
                const newDatasetsData = original.datasets.map(() => []);

                original.labels.forEach((labelStr, i) => {
                    const [day, month, year] = labelStr.split('-');
                    const labelDate = new Date(year, month - 1, day); 
                    labelDate.setHours(0, 0, 0, 0);

                    let normalizedFilterStartDate = filterStartDate; 

                    if (normalizedFilterStartDate === null || labelDate >= normalizedFilterStartDate) {
                        newLabels.push(labelStr);
                        original.datasets.forEach((ds, idx) => {
                            newDatasetsData[idx].push(ds.data[i]);
                        });
                    }
                });

                chart.data.labels = newLabels;
                chart.data.datasets.forEach((ds, idx) => {
                    ds.data = newDatasetsData[idx];
                });

                chart.update();
            });
        });
    }
});