document.addEventListener("DOMContentLoaded", () => {
  // HEART RATE CHART
  const heartRateCanvas = document.getElementById("heartRateChart");
  if (heartRateCanvas) {
    const timestamps = JSON.parse(heartRateCanvas.dataset.timestamps || "[]");
    const heartRates = JSON.parse(heartRateCanvas.dataset.heartRates || "[]");

    // Read thresholds
    const hrNormalMin = parseFloat(heartRateCanvas.dataset.hrNormalMin);
    const hrNormalMax = parseFloat(heartRateCanvas.dataset.hrNormalMax);

    if (timestamps.length && heartRates.length) {
      new Chart(heartRateCanvas.getContext("2d"), {
        type: "line",
        data: {
          labels: timestamps,
          datasets: [{
            label: "Heart Rate (bpm)",
            data: heartRates,
            fill: false,
            segment: {
              borderColor: ctx => {
                const value = ctx.p1.parsed.y;
                if (value < hrNormalMin || value > hrNormalMax) return 'rgba(220, 38, 38, 0.9)'; 
                return 'rgba(37, 99, 235, 0.9)'; 
              }
            },
            pointBackgroundColor: ctx => {
              const value = ctx.parsed.y;
              if (value < hrNormalMin || value > hrNormalMax) return 'rgba(220, 38, 38, 1)'; 
              return 'rgba(37, 99, 235, 1)'; 
            },
            pointBorderColor: ctx => {
              const value = ctx.parsed.y;
              if (value < hrNormalMin || value > hrNormalMax) return 'rgba(153, 27, 27, 1)'; 
              return 'rgba(7, 61, 178, 1)'; 
            },
            pointBorderWidth: 2, 
            borderColor: (context) => { 
              if (heartRates.length > 0) {
                const firstValue = heartRates[0];
                if (firstValue < hrNormalMin || firstValue > hrNormalMax) return 'rgba(220, 38, 38, 0.9)'; 
                return 'rgba(37, 99, 235, 0.9)'; 
              }
              return 'rgba(37, 99, 235, 0.9)'; 
            },
            
            backgroundColor: "rgba(37, 99, 235, 0.7)", 
            tension: 0.3,
            pointRadius: 4,
            pointHoverRadius: 6,
            borderWidth: 2,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: true, position: "top" },
            tooltip: { mode: "index", intersect: false }
          },
          interaction: { mode: "nearest", intersect: false },
          scales: {
            x: {
              display: true,
              title: { display: true, text: "Date" },
              ticks: { maxRotation: 45, minRotation: 30 }
            },
            y: {
              display: true,
              title: { display: true, text: "Beats Per Minute (bpm)" },
              beginAtZero: false,
              suggestedMin: 50, 
              suggestedMax: 120,
              ticks: {
                stepSize: 10, 
                callback: v => Number.isInteger(v) ? v : ""
              }
            }
          }
        }
      });
    } else {
      console.warn("No heart rate data available.");
    }
  }

  // BLOOD PRESSURE CHART
  const bpCanvas = document.getElementById("bpChart");
  if (bpCanvas) {
    const timestamps = JSON.parse(bpCanvas.dataset.timestamps || "[]");
    const systolic = JSON.parse(bpCanvas.dataset.systolic || "[]"); // Original full data
    const diastolic = JSON.parse(bpCanvas.dataset.diastolic || "[]"); // Original full data

    // Read BP thresholds from dataset
    const bpNormalSystolicMax = parseFloat(bpCanvas.dataset.bpNormalSystolicMax);
    const bpNormalDiastolicMax = parseFloat(bpCanvas.dataset.bpNormalDiastolicMax);
    const bpElevatedSystolicMin = parseFloat(bpCanvas.dataset.bpElevatedSystolicMin);
    const bpElevatedSystolicMax = parseFloat(bpCanvas.dataset.bpElevatedSystolicMax);
    const bpElevatedDiastolicMax = parseFloat(bpCanvas.dataset.bpElevatedDiastolicMax);
    const bpStage1SystolicMin = parseFloat(bpCanvas.dataset.bpStage1SystolicMin);
    const bpStage1SystolicMax = parseFloat(bpCanvas.dataset.bpStage1SystolicMax);
    const bpStage1DiastolicMin = parseFloat(bpCanvas.dataset.bpStage1DiastolicMin);
    const bpStage1DiastolicMax = parseFloat(bpCanvas.dataset.bpStage1DiastolicMax);
    const bpStage2SystolicMin = parseFloat(bpCanvas.dataset.bpStage2SystolicMin);
    const bpStage2DiastolicMin = parseFloat(bpCanvas.dataset.bpStage2DiastolicMin);

    // Helper function for Systolic line/point color
    const getSystolicColor = (systolic_val, diastolic_val) => {
      // Stage 2 Hypertension
      if (systolic_val >= bpStage2SystolicMin || diastolic_val >= bpStage2DiastolicMin) {
        return 'rgba(220, 38, 38, 0.9)'; // Red (Critical)
      }
      // Elevated (now Yellow)
      else if (systolic_val >= bpElevatedSystolicMin && systolic_val <= bpElevatedSystolicMax) {
          return 'rgba(252, 211, 38, 0.9)'; // Yellow
      }
      // FIX: Stage 1 Hypertension (now Orange)
      else if ((systolic_val >= bpStage1SystolicMin && systolic_val <= bpStage1SystolicMax) ||
               (diastolic_val >= bpStage1DiastolicMin && diastolic_val <= bpStage1DiastolicMax)) {
          return 'rgba(249, 115, 22, 0.9)'; // Orange
      }
      // Normal
      else if (systolic_val < bpNormalSystolicMax && diastolic_val < bpNormalDiastolicMax) {
        return 'rgba(37, 99, 235, 0.9)'; // Blue (Normal Systolic)
      }
      // FIX: Default to Blue if no category matches (removed Gray fallback)
      return 'rgba(37, 99, 235, 0.9)'; // Default to Blue
    };

    // Helper function for Diastolic line/point color
    const getDiastolicColor = (systolic_val, diastolic_val) => {
      // Stage 2 Hypertension
      if (systolic_val >= bpStage2SystolicMin || diastolic_val >= bpStage2DiastolicMin) {
        return 'rgba(220, 38, 38, 0.9)'; // Red (Critical)
      }
      // FIX: Elevated (now Yellow)
      else if (
          systolic_val >= bpElevatedSystolicMin && // Systolic is elevated
          systolic_val <= bpElevatedSystolicMax && diastolic_val<=bpElevatedDiastolicMax
      ) {
          return 'rgba(252, 211, 38, 0.9)'; // Yellow
      }
      // FIX: Stage 1 Hypertension (now Orange)
      else if ((systolic_val >= bpStage1SystolicMin && systolic_val <= bpStage1SystolicMax) ||
               (diastolic_val >= bpStage1DiastolicMin && diastolic_val <= bpStage1DiastolicMax)) {
          return 'rgba(249, 115, 22, 0.9)'; // Orange
      }
      // // Normal
      // else if (systolic_val < bpNormalSystolicMax && diastolic_val < bpNormalDiastolicMax) {
      //   return 'rgba(16, 185, 129, 0.9)'; // Green (Normal Diastolic)
      // }
      // FIX: Default to Green if no category matches (removed Gray fallback)
      return 'rgba(16, 185, 129, 0.9)'; // Default to Green
    };


    if (timestamps.length && systolic.length && diastolic.length) {
      if (window.bpChartInstance) window.bpChartInstance.destroy(); // Keep destroy/create for filter changes

      window.bpChartInstance = new Chart(bpCanvas.getContext("2d"), {
        type: "line",
        data: {
          labels: timestamps,
          datasets: [
            {
              label: "Systolic (mmHg)",
              data: systolic, // This will be the filtered data after filter changes
              fill: false,
              // FIX: Removed top-level borderColor to let segment.borderColor control the line color
              // borderColor: (context) => { ... },
              segment: {
                // This is the primary driver for dynamic line coloring
                borderColor: ctx => getSystolicColor(ctx.p1.parsed.y, ctx.chart.data.datasets[1].data[ctx.p1.dataIndex]),
              },
              pointBackgroundColor: ctx => {
                const color = getSystolicColor(ctx.parsed.y, ctx.chart.data.datasets[1].data[ctx.dataIndex]);
                return color.replace(/0\.\d+/, "1"); // Make opaque
              },
              pointBorderColor: ctx => {
                const color = getSystolicColor(ctx.parsed.y, ctx.chart.data.datasets[1].data[ctx.dataIndex]);
                // Darker shades for point borders
                if (color.includes('220, 38, 38')) return 'rgba(153, 27, 27, 1)'; // Darker Red
                if (color.includes('252, 211, 38')) return 'rgba(202, 160, 0, 1)'; // Darker Yellow
                if (color.includes('249, 115, 22')) return 'rgba(194, 65, 12, 1)'; // Darker Orange
                if (color.includes('37, 99, 235')) return 'rgba(7, 61, 178, 1)'; // Darker Blue
                return 'rgba(75, 85, 99, 1)'; // Default Darker Gray (fallback if no match)
              },
              pointBorderWidth: 2,
              backgroundColor: "rgba(59,130,246,0.5)", // Default blue fill (if fill:true)
              tension: 0.3,
              borderWidth: 2,
              pointRadius: 4,
              pointHoverRadius: 6,
            },
            {
              label: "Diastolic (mmHg)",
              data: diastolic, // This will be the filtered data after filter changes
              fill: false,
              // FIX: Removed top-level borderColor to let segment.borderColor control the line color
              // borderColor: (context) => { ... },
              segment: {
                // This is the primary driver for dynamic line coloring
                borderColor: (ctx) => {
                  const systolicValueForDiastolicPoint = ctx.chart.data.datasets[0].data[ctx.p1.dataIndex];
                  return getDiastolicColor(systolicValueForDiastolicPoint, ctx.p1.parsed.y);
                },
              },
              pointBackgroundColor: (ctx) => {
                const systolicValueForDiastolicPoint = ctx.chart.data.datasets[0].data[ctx.dataIndex];
                const color = getDiastolicColor(systolicValueForDiastolicPoint, ctx.parsed.y);
                return color.replace(/0\.\d+/, "1"); // Make opaque
              },
              pointBorderColor: (ctx) => {
                const systolicValueForDiastolicPoint = ctx.chart.data.datasets[0].data[ctx.dataIndex];
                const color = getDiastolicColor(systolicValueForDiastolicPoint, ctx.parsed.y);
                // Darker shades for point borders
                if (color.includes('220, 38, 38')) return 'rgba(153, 27, 27, 1)'; // Darker Red
                if (color.includes('252, 211, 38')) return 'rgba(202, 160, 0, 1)'; // Darker Yellow
                if (color.includes('249, 115, 22')) return 'rgba(194, 65, 12, 1)'; // Darker Orange
                if (color.includes('16, 185, 129')) return 'rgba(10, 100, 70, 1)'; // Darker Green
                return 'rgba(75, 85, 99, 1)'; // Darker Gray
              },
              pointBorderWidth: 2,
              backgroundColor: "rgba(16,185,129,0.5)", // Default green fill (if fill:true)
              tension: 0.3,
              borderWidth: 2,
              pointRadius: 4,
              pointHoverRadius: 6,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: true, position: "top" },
            tooltip: { mode: "index", intersect: false },
          },
          interaction: { mode: "nearest", intersect: false },
          scales: {
            x: {
              title: { display: true, text: "Date" },
              ticks: { maxRotation: 45, minRotation: 30 },
            },
            y: {
              title: { display: true, text: "Blood Pressure (mmHg)" },
              min: 50,
              max: 150,
              ticks: { stepSize: 20 },
            },
          },
        },
      });
    } else {
      console.warn("No blood pressure data available.");
    }
  }

  // OXYGEN SATURATION (SpO2) CHART
  const spo2Ctx = document.getElementById("spO2Chart");
  if (spo2Ctx) {
    const spo2Timestamps = JSON.parse(spo2Ctx.dataset.timestamps || "[]");
    const spo2Values = JSON.parse(spo2Ctx.dataset.sp02values || "[]");

    // --- READ THRESHOLDS FROM DATA ATTRIBUTES ---
    const spo2Critical = parseFloat(spo2Ctx.dataset.spo2Critical);
    const spo2Caution = parseFloat(spo2Ctx.dataset.spo2Caution);
    // --- END READ THRESHOLDS ---

    if (spo2Timestamps.length && spo2Values.length) {
      new Chart(spo2Ctx.getContext("2d"), {
        type: "line",
        data: {
          labels: spo2Timestamps,
          datasets: [
            {
              label: "Oxygen Saturation (%)",
              data: spo2Values,
              // --- DYNAMIC COLORING BASED ON THRESHOLDS ---
              // This colors the line segments
              segment: {
                borderColor: ctx => {
                  const value = ctx.p1.parsed.y; // Value of the segment's end point
                  if (value < spo2Critical) return 'rgba(220, 38, 38, 0.9)'; // Red (Tailwind red-600 equivalent)
                  if (value >= spo2Critical && value < spo2Caution) return 'rgba(252, 211, 38, 0.9)'; // Yellow (Tailwind yellow-500 equivalent)
                  return 'rgba(37, 99, 235, 0.7)'; // Green (Tailwind green-700 equivalent)
                }
              },
              // This colors the individual data points
              pointBackgroundColor: ctx => {
                const value = ctx.parsed.y; // Value of the individual point
                if (value < spo2Critical) return 'rgba(220, 38, 38, 1)'; // Red
                if (value >= spo2Critical && value < spo2Caution) return 'rgba(252, 211, 38, 1)'; // Yellow
                return 'rgba(37, 99, 235, 0.7)'; // Green
              },
              pointBorderColor: ctx => { // This controls the border of the data point circle
                const value = ctx.parsed.y;
                if (value < spo2Critical) return 'rgba(153, 27, 27, 1)'; // Darker Red
                if (value >= spo2Critical && value < spo2Caution) return 'rgba(202, 160, 0, 1)'; // Darker Yellow
                return 'rgba(7, 61, 178, 0.7)'; // Darker Green
              },
              pointBorderWidth: 2, // <-- ADDED THIS LINE to make the border thicker
              borderColor: (context) => { // This is for the main line color, often overridden by segment
                if (spo2Values.length > 0) {
                  const firstValue = spo2Values[0];
                  if (firstValue < spo2Critical) return 'rgba(220, 38, 38, 0.9)'; // Red
                  if (firstValue >= spo2Critical && firstValue < spo2Caution) return 'rgba(252, 211, 38, 0.9)'; // Yellow
                  return 'rgba(37, 99, 235, 0.7)'; // Green
                }
                return 'rgba(37, 99, 235, 0.7)'; // Default if no data
              },
              // --- END DYNAMIC COLORING ---

              // Fallback borderColor and backgroundColor for overall dataset
              borderColor: "rgba(37, 99, 235, 0.7)", // Default green for overall line/points if dynamic fails
              backgroundColor: "rgba(7, 61, 178, 0.7)",

              tension: 0.3,
              borderWidth: 2,
              pointRadius: 4,
              pointHoverRadius: 6,
              fill: false,
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: true, position: "top" },
            tooltip: { mode: "index", intersect: false }
          },
          interaction: { mode: "nearest", intersect: false },
          scales: {
            x: {
              title: { display: true, text: "Date" },
              ticks: { maxRotation: 45, minRotation: 30 }
            },
            y: {
              title: { display: true, text: "SpO₂ (%)" },
              min: 80,
              max: 100,
              beginAtZero: false,
              ticks: {
                stepSize: 5,
                callback: function (value) {
                  return Number.isInteger(value) ? value : null;
                }
              }
            }
          }
        }
      });
    } else {
      console.warn("No SpO2 data available to render chart.");
    }
  }

  // WEIGHT CHART
  const weightCtx = document.getElementById("weightChart");
  if (weightCtx) {
    const weightTimestamps = JSON.parse(weightCtx.dataset.timestamps || "[]");
    const weightValues = JSON.parse(weightCtx.dataset.weights || "[]"); // This is the original, full data from HTML
    const weightDailyIncreaseCritical = parseFloat(weightCtx.dataset.weightDailyIncreaseCritical); // Read threshold

    // Helper function to get weight change color
    // It now relies on the context providing current and previous values directly.
    const getWeightChangeColor = (currentWeight, previousWeight) => {
      if (previousWeight === undefined || previousWeight === null) {
        return 'rgba(37, 99, 235, 0.9)'; // Default blue for first point
      }
      const change = currentWeight - previousWeight;

      // RED for critical increase
      if (change > weightDailyIncreaseCritical) {
        return 'rgba(220, 38, 38, 0.9)'; // Red if critical increase
      }
      // RED for critical decrease
      if (change < -weightDailyIncreaseCritical) { // If decrease is more than the critical amount (e.g., -3kg)
        return 'rgba(220, 38, 38, 0.9)'; // Red if critical decrease
      }

      return 'rgba(37, 99, 235, 0.9)'; // Blue otherwise (normal change within limits)
    };

    // Helper function to get darker color for point borders
    const getDarkerColor = (baseColor) => {
      return baseColor.replace(/,\s*0\.\d+\)/, ', 1)'); // Make opaque
    };


    if (weightTimestamps.length && weightValues.length) {
      new Chart(weightCtx.getContext("2d"), {
        type: "line",
        data: {
          labels: weightTimestamps,
          datasets: [{
            label: "Weight (kg)",
            data: weightValues, // This is the original data, filtered by the time period logic later
            fill: false,
            // --- DYNAMIC COLORING FOR WEIGHT ---
            segment: {
              borderColor: ctx => {
                const currentWeight = ctx.p1.parsed.y;
                const previousWeight = ctx.p0 ? ctx.p0.parsed.y : null; // Reliable from segment context
                return getWeightChangeColor(currentWeight, previousWeight);
              }
            },
            pointBackgroundColor: ctx => {
              const currentWeight = ctx.parsed.y;
              // For point coloring, we need the previous value from the *currently rendered* dataset.
              // ctx.dataset.data refers to the current (potentially filtered) data array.
              const previousWeight = ctx.dataIndex > 0 ? ctx.dataset.data[ctx.dataIndex - 1] : null;

              // console.log(`--- Point BG Color Debug for Index ${ctx.dataIndex} ---`); // Uncomment for debugging
              // console.log(`  Current Weight: ${currentWeight}`);
              // console.log(`  Previous Weight (from ctx.dataset.data): ${previousWeight}`);
              // console.log(`  Calculated Change: ${currentWeight - previousWeight}`);
              // console.log(`  Threshold: ${weightDailyIncreaseCritical}`);
              // console.log(`  Resulting Color: ${getWeightChangeColor(currentWeight, previousWeight)}`);
              // console.log('----------------------------------------------------');

              return getWeightChangeColor(currentWeight, previousWeight);
            },
            pointBorderColor: ctx => {
              const currentWeight = ctx.parsed.y;
              const previousWeight = ctx.dataIndex > 0 ? ctx.dataset.data[ctx.dataIndex - 1] : null;
              const baseColor = getWeightChangeColor(currentWeight, previousWeight);
              return getDarkerColor(baseColor);
            },
            pointBorderWidth: 2, // Make the border thicker
            borderColor: (context) => { // Main line color, based on first value or default
              // For the overall line color, use the first point of the currently rendered dataset.
              if (context.chart.data.datasets[0].data.length > 0) {
                const firstValue = context.chart.data.datasets[0].data[0];
                // The first point has no 'previous' for change calculation
                return getWeightChangeColor(firstValue, null);
              }
              return 'rgba(37, 99, 235, 0.9)'; // Default blue
            },
            // --- END DYNAMIC COLORING ---
            backgroundColor: "rgba(37, 99, 235, 0.7)", // Default blue fill
            tension: 0.3,
            pointRadius: 4,
            pointHoverRadius: 6,
            borderWidth: 2,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false, // Allow chart to fill container height
          plugins: {
            legend: { display: true, position: "top" },
            tooltip: { mode: "index", intersect: false }
          },
          interaction: { mode: "nearest", intersect: false },
          scales: {
            x: {
              display: true,
              title: { display: true, text: "Date" },
              ticks: { maxRotation: 45, minRotation: 30 }
            },
            y: {
              display: true,
              title: { display: true, text: "Weight (kg)" },
              min: 60,
              max: 100,
              beginAtZero: false,
              ticks: {
                stepSize: 10,
                callback: function (value) {
                  return value; // Display decimal values for weight
                }
              }
            }
          }
        }
      });
    } else {
      console.warn("No weight data available to render chart.");
    }
  }
  // BMI CHART
  const bmiCtx = document.getElementById("bmiChart");
  if (bmiCtx) {
    const bmiTimestamps = JSON.parse(bmiCtx.dataset.timestamps || "[]");
    const bmiValues = JSON.parse(bmiCtx.dataset.bmis || "[]");

    if (bmiTimestamps.length && bmiValues.length) {
      new Chart(bmiCtx.getContext("2d"), {
        type: "line",
        data: {
          labels: bmiTimestamps,
          datasets: [{
            label: "BMI",
            data: bmiValues,
            fill: false,
            borderColor: "rgba(37, 99, 235, 0.7)",
            backgroundColor: "rgba(37, 99, 235, 0.7)",
            tension: 0.3,
            pointRadius: 4,
            pointHoverRadius: 6,
            borderWidth: 2,
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: true, position: "top" },
            tooltip: { mode: "index", intersect: false }
          },
          interaction: { mode: "nearest", intersect: false },
          scales: {
            x: {
              display: true,
              title: { display: true, text: "Date" },
              ticks: { maxRotation: 45, minRotation: 30 }
            },
            y: {
              display: true,
              title: { display: true, text: "Body-Mass Index" },
              min: 15,
              max: 40,
              ticks: {
                stepSize: 5,
                callback: v => Number.isInteger(v) ? v : ""
              }
            }
          }
        }
      });
    } else {
      console.warn("No BMI data available to render chart.");
    }
  }
});
