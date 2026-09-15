/**
 * CardioMetrics - Heart Disease Analytics Dashboard Client
 * Handles asynchronous API orchestration, Chart.js visualizations,
 * correlation heatmap matrix, dynamic filtering, hypothesis test display,
 * and paginated/searchable patient data exploration.
 */

document.addEventListener("DOMContentLoaded", () => {
    // Lucide Icon Initializer
    if (window.lucide) {
        lucide.createIcons();
    }

    // Application State
    const state = {
        filters: {
            gender: "all",
            age_group: "all",
            outcome: "all",
            cp: "all"
        },
        activeClinicalVar: "thalach",
        patients: {
            page: 1,
            per_page: 10,
            search: "",
            sort: "patient_id",
            order: "asc",
            total: 0,
            pages: 1
        },
        charts: {
            diseaseDist: null,
            ageDist: null,
            genderDist: null,
            chestPainDist: null,
            clinicalHist: null
        },
        clinicalDataCache: null
    };

    // Color Palette Constants for Chart.js
    const PALETTE = {
        disease: "#e11d48",         // Rose
        noDisease: "#059669",       // Emerald
        diseaseBg: "rgba(225, 29, 72, 0.8)",
        noDiseaseBg: "rgba(5, 150, 105, 0.8)",
        borderLight: "#e2e8f0",
        textPrimary: "#0f172a",
        textMuted: "#64748b"
    };

    // DOM Element References
    const elements = {
        filterGender: document.getElementById("filterGender"),
        filterAgeGroup: document.getElementById("filterAgeGroup"),
        filterOutcome: document.getElementById("filterOutcome"),
        filterChestPain: document.getElementById("filterChestPain"),
        resetFiltersBtn: document.getElementById("resetFiltersBtn"),
        emptyStateResetBtn: document.getElementById("emptyStateResetBtn"),
        filterRecordCount: document.getElementById("filterRecordCount"),
        emptyFilterState: document.getElementById("emptyFilterState"),

        // KPIs
        kpiTotalPatients: document.getElementById("kpiTotalPatients"),
        kpiDiseaseCases: document.getElementById("kpiDiseaseCases"),
        kpiDiseasePrevalence: document.getElementById("kpiDiseasePrevalence"),
        kpiAverageAge: document.getElementById("kpiAverageAge"),
        kpiAvgChol: document.getElementById("kpiAvgChol"),
        kpiAvgMaxHr: document.getElementById("kpiAvgMaxHr"),
        kpiAvgBp: document.getElementById("kpiAvgBp"),

        // Notes
        noteDiseaseDist: document.getElementById("noteDiseaseDist"),
        noteGenderDist: document.getElementById("noteGenderDist"),

        // Clinical Tab elements
        clinicalTabsNav: document.getElementById("clinicalTabsNav"),
        clinicalVarName: document.getElementById("clinicalVarName"),
        clinicalVarUnit: document.getElementById("clinicalVarUnit"),
        clinicalDisMean: document.getElementById("clinicalDisMean"),
        clinicalDisMedian: document.getElementById("clinicalDisMedian"),
        clinicalDisIqr: document.getElementById("clinicalDisIqr"),
        clinicalDisStd: document.getElementById("clinicalDisStd"),
        clinicalNoDisMean: document.getElementById("clinicalNoDisMean"),
        clinicalNoDisMedian: document.getElementById("clinicalNoDisMedian"),
        clinicalNoDisIqr: document.getElementById("clinicalNoDisIqr"),
        clinicalNoDisStd: document.getElementById("clinicalNoDisStd"),
        clinicalVarNote: document.getElementById("clinicalVarNote"),

        // Heatmap & Tables
        heatmapContainer: document.getElementById("heatmapContainer"),
        hypothesisTestBody: document.getElementById("hypothesisTestBody"),

        // Patient Explorer
        patientSearchInput: document.getElementById("patientSearchInput"),
        perPageSelect: document.getElementById("perPageSelect"),
        patientsTableBody: document.getElementById("patientsTableBody"),
        pageInfoText: document.getElementById("pageInfoText"),
        pageCurrentPill: document.getElementById("pageCurrentPill"),
        prevPageBtn: document.getElementById("prevPageBtn"),
        nextPageBtn: document.getElementById("nextPageBtn"),
        sortableHeaders: document.querySelectorAll("#patientsTable th.sortable"),

        // Insights & Nav
        insightsGrid: document.getElementById("insightsGrid"),
        mobileNavToggle: document.getElementById("mobileNavToggle"),
        sidebar: document.getElementById("sidebar"),
        navItems: document.querySelectorAll(".sidebar-nav .nav-item")
    };

    /**
     * Build URL query parameter string from active filters
     */
    function buildQueryString(extraParams = {}) {
        const params = new URLSearchParams({
            gender: state.filters.gender,
            age_group: state.filters.age_group,
            outcome: state.filters.outcome,
            cp: state.filters.cp,
            ...extraParams
        });
        return params.toString();
    }

    /**
     * Update active navigation link on scroll
     */
    function setupScrollSpy() {
        const sections = document.querySelectorAll("section[id]");
        window.addEventListener("scroll", () => {
            let current = "";
            sections.forEach(sec => {
                const top = sec.offsetTop - 120;
                if (window.scrollY >= top) {
                    current = sec.getAttribute("id");
                }
            });

            elements.navItems.forEach(item => {
                item.classList.remove("active");
                if (item.getAttribute("href") === `#${current}`) {
                    item.classList.add("active");
                }
            });
        });
    }

    /**
     * Mobile sidebar toggle
     */
    if (elements.mobileNavToggle && elements.sidebar) {
        elements.mobileNavToggle.addEventListener("click", () => {
            elements.sidebar.classList.toggle("open");
        });
    }

    // -------------------------------------------------------------
    // API Orchestration & Data Loading
    // -------------------------------------------------------------

    async function fetchSummaryKPIs() {
        try {
            const res = await fetch(`/api/summary?${buildQueryString()}`);
            const json = await res.json();
            if (!json.success) throw new Error(json.error);
            const data = json.data;

            if (data.is_empty) {
                elements.emptyFilterState.style.display = "block";
                elements.filterRecordCount.textContent = "Analyzing 0 / 303 Records";
            } else {
                elements.emptyFilterState.style.display = "none";
                elements.filterRecordCount.textContent = `Analyzing ${data.total_patients} / 303 Records`;
            }

            elements.kpiTotalPatients.textContent = data.total_patients;
            elements.kpiDiseaseCases.textContent = data.disease_cases;
            elements.kpiDiseasePrevalence.textContent = data.disease_prevalence_display;
            elements.kpiAverageAge.textContent = data.average_age_display;
            elements.kpiAvgChol.textContent = data.average_cholesterol_display;
            elements.kpiAvgMaxHr.textContent = data.average_max_hr_display;
            elements.kpiAvgBp.textContent = data.average_resting_bp_display;
        } catch (err) {
            console.error("fetchSummaryKPIs error:", err);
            elements.kpiTotalPatients.textContent = "Err";
        }
    }

    async function fetchDiseaseDistribution() {
        try {
            const res = await fetch(`/api/distribution?${buildQueryString()}`);
            const json = await res.json();
            if (!json.success) throw new Error(json.error);
            const data = json.data;

            const ctx = document.getElementById("chartDiseaseDist");
            if (!ctx) return;

            if (state.charts.diseaseDist) {
                state.charts.diseaseDist.destroy();
            }

            state.charts.diseaseDist = new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.counts,
                        backgroundColor: [PALETTE.noDisease, PALETTE.disease],
                        hoverOffset: 6,
                        borderWidth: 2,
                        borderColor: "#ffffff"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: "bottom",
                            labels: {
                                boxWidth: 14,
                                font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
                                generateLabels: (chart) => {
                                    const orig = Chart.defaults.plugins.legend.labels.generateLabels(chart);
                                    orig.forEach((item, idx) => {
                                        item.text = `${data.labels[idx]} (${data.counts[idx]} - ${data.percentages[idx]}%)`;
                                    });
                                    return orig;
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    const idx = context.dataIndex;
                                    return ` ${data.labels[idx]}: ${data.counts[idx]} cases (${data.percentages[idx]}%)`;
                                }
                            }
                        }
                    },
                    cutout: "62%"
                }
            });

            if (elements.noteDiseaseDist) {
                elements.noteDiseaseDist.textContent = 
                    `Cohort: ${data.counts[1]} disease cases (${data.percentages[1]}%) vs ${data.counts[0]} without disease (${data.percentages[0]}%).`;
            }
        } catch (err) {
            console.error("fetchDiseaseDistribution error:", err);
        }
    }

    async function fetchAgeAnalysis() {
        try {
            const res = await fetch(`/api/age-analysis?${buildQueryString()}`);
            const json = await res.json();
            if (!json.success) throw new Error(json.error);
            const data = json.data;

            const ctx = document.getElementById("chartAgeDist");
            if (!ctx) return;

            if (state.charts.ageDist) {
                state.charts.ageDist.destroy();
            }

            state.charts.ageDist = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: data.categories,
                    datasets: [
                        {
                            label: "No Disease",
                            data: data.no_disease_counts,
                            backgroundColor: PALETTE.noDiseaseBg,
                            borderColor: PALETTE.noDisease,
                            borderWidth: 1,
                            borderRadius: 4
                        },
                        {
                            label: "Disease",
                            data: data.disease_counts,
                            backgroundColor: PALETTE.diseaseBg,
                            borderColor: PALETTE.disease,
                            borderWidth: 1,
                            borderRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { grid: { display: false } },
                        y: {
                            beginAtZero: true,
                            ticks: { precision: 0 },
                            grid: { color: "#f1f5f9" }
                        }
                    },
                    plugins: {
                        legend: { position: "top", labels: { boxWidth: 12 } },
                        tooltip: {
                            callbacks: {
                                afterBody: (ctxs) => {
                                    const idx = ctxs[0].dataIndex;
                                    return `Total: ${data.totals[idx]} | Disease Rate: ${data.disease_rates[idx]}%`;
                                }
                            }
                        }
                    }
                }
            });
        } catch (err) {
            console.error("fetchAgeAnalysis error:", err);
        }
    }

    async function fetchGenderAnalysis() {
        try {
            const res = await fetch(`/api/gender-analysis?${buildQueryString()}`);
            const json = await res.json();
            if (!json.success) throw new Error(json.error);
            const data = json.data;

            const ctx = document.getElementById("chartGenderDist");
            if (!ctx) return;

            if (state.charts.genderDist) {
                state.charts.genderDist.destroy();
            }

            state.charts.genderDist = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: data.categories,
                    datasets: [
                        {
                            label: "No Disease",
                            data: data.no_disease_counts,
                            backgroundColor: PALETTE.noDiseaseBg,
                            borderColor: PALETTE.noDisease,
                            borderWidth: 1,
                            borderRadius: 4
                        },
                        {
                            label: "Disease",
                            data: data.disease_counts,
                            backgroundColor: PALETTE.diseaseBg,
                            borderColor: PALETTE.disease,
                            borderWidth: 1,
                            borderRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { grid: { display: false } },
                        y: {
                            beginAtZero: true,
                            ticks: { precision: 0 },
                            grid: { color: "#f1f5f9" }
                        }
                    },
                    plugins: {
                        legend: { position: "top", labels: { boxWidth: 12 } },
                        tooltip: {
                            callbacks: {
                                afterBody: (ctxs) => {
                                    const idx = ctxs[0].dataIndex;
                                    return `Disease Prevalence: ${data.disease_rates[idx]}% (${data.disease_counts[idx]}/${data.totals[idx]})`;
                                }
                            }
                        }
                    }
                }
            });

            if (elements.noteGenderDist && data.categories.length >= 2) {
                elements.noteGenderDist.textContent = 
                    `Prevalence: Male ${data.disease_rates[0]}% vs Female ${data.disease_rates[1]}% in this sample.`;
            }
        } catch (err) {
            console.error("fetchGenderAnalysis error:", err);
        }
    }

    async function fetchChestPainAnalysis() {
        try {
            const res = await fetch(`/api/chest-pain-analysis?${buildQueryString()}`);
            const json = await res.json();
            if (!json.success) throw new Error(json.error);
            const data = json.data;

            const ctx = document.getElementById("chartChestPainDist");
            if (!ctx) return;

            if (state.charts.chestPainDist) {
                state.charts.chestPainDist.destroy();
            }

            state.charts.chestPainDist = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: data.categories,
                    datasets: [
                        {
                            label: "No Disease",
                            data: data.no_disease_counts,
                            backgroundColor: PALETTE.noDiseaseBg,
                            borderColor: PALETTE.noDisease,
                            borderWidth: 1,
                            borderRadius: 4
                        },
                        {
                            label: "Disease",
                            data: data.disease_counts,
                            backgroundColor: PALETTE.diseaseBg,
                            borderColor: PALETTE.disease,
                            borderWidth: 1,
                            borderRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { grid: { display: false } },
                        y: {
                            beginAtZero: true,
                            ticks: { precision: 0 },
                            grid: { color: "#f1f5f9" }
                        }
                    },
                    plugins: {
                        legend: { position: "top", labels: { boxWidth: 12 } },
                        tooltip: {
                            callbacks: {
                                afterBody: (ctxs) => {
                                    const idx = ctxs[0].dataIndex;
                                    return `Disease Rate: ${data.disease_rates[idx]}% (Total: ${data.totals[idx]})`;
                                }
                            }
                        }
                    }
                }
            });
        } catch (err) {
            console.error("fetchChestPainAnalysis error:", err);
        }
    }

    async function fetchClinicalAnalysis() {
        try {
            const res = await fetch(`/api/clinical-analysis?${buildQueryString()}`);
            const json = await res.json();
            if (!json.success) throw new Error(json.error);
            state.clinicalDataCache = json.data;
            renderClinicalTab(state.activeClinicalVar);
        } catch (err) {
            console.error("fetchClinicalAnalysis error:", err);
        }
    }

    function renderClinicalTab(varKey) {
        if (!state.clinicalDataCache || !state.clinicalDataCache[varKey]) return;
        const item = state.clinicalDataCache[varKey];

        elements.clinicalVarName.textContent = item.label;
        elements.clinicalVarUnit.textContent = `Unit: ${item.unit}`;

        elements.clinicalDisMean.textContent = item.disease.mean !== null ? `${item.disease.mean} ${item.unit}` : "N/A";
        elements.clinicalDisMedian.textContent = item.disease.median !== null ? `${item.disease.median} ${item.unit}` : "N/A";
        elements.clinicalDisIqr.textContent = item.disease.iqr !== null ? `${item.disease.iqr} ${item.unit}` : "N/A";
        elements.clinicalDisStd.textContent = item.disease.std !== null ? `${item.disease.std} ${item.unit}` : "N/A";

        elements.clinicalNoDisMean.textContent = item.no_disease.mean !== null ? `${item.no_disease.mean} ${item.unit}` : "N/A";
        elements.clinicalNoDisMedian.textContent = item.no_disease.median !== null ? `${item.no_disease.median} ${item.unit}` : "N/A";
        elements.clinicalNoDisIqr.textContent = item.no_disease.iqr !== null ? `${item.no_disease.iqr} ${item.unit}` : "N/A";
        elements.clinicalNoDisStd.textContent = item.no_disease.std !== null ? `${item.no_disease.std} ${item.unit}` : "N/A";

        elements.clinicalVarNote.textContent = item.note;

        // Render Histogram Comparison
        const ctx = document.getElementById("chartClinicalHistogram");
        if (!ctx) return;

        if (state.charts.clinicalHist) {
            state.charts.clinicalHist.destroy();
        }

        const hist = item.histogram;
        state.charts.clinicalHist = new Chart(ctx, {
            type: "bar",
            data: {
                labels: hist.bins,
                datasets: [
                    {
                        label: "No Disease",
                        data: hist.no_disease_counts,
                        backgroundColor: PALETTE.noDiseaseBg,
                        borderColor: PALETTE.noDisease,
                        borderWidth: 1,
                        borderRadius: 3
                    },
                    {
                        label: "Disease",
                        data: hist.disease_counts,
                        backgroundColor: PALETTE.diseaseBg,
                        borderColor: PALETTE.disease,
                        borderWidth: 1,
                        borderRadius: 3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: { display: true, text: `${item.label} (${item.unit})`, font: { size: 11 } },
                        grid: { display: false }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                        title: { display: true, text: "Number of Patients", font: { size: 11 } },
                        grid: { color: "#f1f5f9" }
                    }
                },
                plugins: {
                    legend: { position: "top", labels: { boxWidth: 12 } }
                }
            }
        });
    }

    async function fetchCorrelationMatrix() {
        try {
            const res = await fetch(`/api/correlation?${buildQueryString()}`);
            const json = await res.json();
            if (!json.success) throw new Error(json.error);
            renderHeatmap(json.data);
        } catch (err) {
            console.error("fetchCorrelationMatrix error:", err);
            elements.heatmapContainer.innerHTML = `<div class="p-4 text-center">Unable to load correlation matrix.</div>`;
        }
    }

    function renderHeatmap(data) {
        if (!data || !data.labels || data.labels.length === 0) {
            elements.heatmapContainer.innerHTML = `<div class="p-4 text-center">Insufficient data for correlation calculation.</div>`;
            return;
        }

        const labels = data.labels;
        const matrix = data.matrix;

        let tableHtml = `<table class="heatmap-table"><thead><tr><th></th>`;
        labels.forEach(l => {
            tableHtml += `<th>${l}</th>`;
        });
        tableHtml += `</tr></thead><tbody>`;

        for (let r = 0; r < matrix.length; r++) {
            tableHtml += `<tr><th>${labels[r]}</th>`;
            for (let c = 0; c < matrix[r].length; c++) {
                const val = matrix[r][c];
                const colorStyle = getHeatmapColorStyle(val);
                const tooltipText = `${labels[r]} ↔ ${labels[c]}: r = ${val > 0 ? "+" : ""}${val.toFixed(2)}`;
                tableHtml += `
                    <td style="${colorStyle}" title="${tooltipText}">
                        ${val.toFixed(2)}
                    </td>
                `;
            }
            tableHtml += `</tr>`;
        }
        tableHtml += `</tbody></table>`;
        elements.heatmapContainer.innerHTML = tableHtml;
    }

    function getHeatmapColorStyle(val) {
        // Diverging scale: -1 (Blue) -> 0 (Subtle Slate/White) -> +1 (Rose/Red)
        if (val === 1.0) {
            return "background-color: #fce7f3; color: #9d174d;";
        }
        if (val > 0) {
            const intensity = Math.min(1, val * 1.6);
            const r = 255;
            const g = Math.round(255 - intensity * 150);
            const b = Math.round(255 - intensity * 140);
            const textColor = intensity > 0.4 ? "#ffffff" : "#0f172a";
            return `background-color: rgb(${r}, ${g}, ${b}); color: ${textColor};`;
        } else {
            const intensity = Math.min(1, Math.abs(val) * 1.6);
            const r = Math.round(255 - intensity * 180);
            const g = Math.round(255 - intensity * 90);
            const b = 255;
            const textColor = intensity > 0.4 ? "#ffffff" : "#0f172a";
            return `background-color: rgb(${r}, ${g}, ${b}); color: ${textColor};`;
        }
    }

    async function fetchHypothesisTests() {
        try {
            const res = await fetch(`/api/statistics?${buildQueryString()}`);
            const json = await res.json();
            if (!json.success) throw new Error(json.error);
            const tests = json.data.tests;

            if (!tests || tests.length === 0) {
                elements.hypothesisTestBody.innerHTML = `<tr><td colspan="7" class="text-center py-4">No statistical tests could be run on this cohort subset.</td></tr>`;
                return;
            }

            let html = "";
            tests.forEach(t => {
                const sigBadge = t.is_significant
                    ? `<span class="badge-status badge-success">p &lt; 0.05</span>`
                    : `<span class="badge-status badge-neutral">p ≥ 0.05</span>`;

                html += `
                    <tr>
                        <td><strong>${t.variable}</strong></td>
                        <td><span class="chart-badge">${t.variable_type}</span></td>
                        <td>${t.test}</td>
                        <td><code>${t.statistic}</code></td>
                        <td><strong>${t.p_value_display}</strong></td>
                        <td>${sigBadge}</td>
                        <td><small>${t.interpretation}</small></td>
                    </tr>
                `;
            });
            elements.hypothesisTestBody.innerHTML = html;
        } catch (err) {
            console.error("fetchHypothesisTests error:", err);
            elements.hypothesisTestBody.innerHTML = `<tr><td colspan="7" class="text-center py-4">Error loading hypothesis testing data.</td></tr>`;
        }
    }

    async function fetchDynamicInsights() {
        try {
            const res = await fetch(`/api/insights?${buildQueryString()}`);
            const json = await res.json();
            if (!json.success) throw new Error(json.error);
            const insights = json.data;

            let html = "";
            insights.forEach(item => {
                html += `
                    <div class="insight-card">
                        <div class="insight-card-top">
                            <span class="insight-category-tag">${item.category}</span>
                            <span class="insight-badge">${item.badge}</span>
                        </div>
                        <h4 class="insight-title">${item.title}</h4>
                        <p class="insight-body">${item.finding}</p>
                    </div>
                `;
            });
            elements.insightsGrid.innerHTML = html;
        } catch (err) {
            console.error("fetchDynamicInsights error:", err);
            elements.insightsGrid.innerHTML = `<div class="insight-card"><p>Unable to load analytical findings.</p></div>`;
        }
    }

    // -------------------------------------------------------------
    // Patient Data Explorer (Search, Sort, Pagination)
    // -------------------------------------------------------------

    async function fetchPatients() {
        try {
            const params = {
                page: state.patients.page,
                per_page: state.patients.per_page,
                search: state.patients.search,
                sort: state.patients.sort,
                order: state.patients.order
            };

            const res = await fetch(`/api/patients?${buildQueryString(params)}`);
            const json = await res.json();
            if (!json.success) throw new Error(json.error);

            state.patients.total = json.total;
            state.patients.pages = json.pages;
            state.patients.page = json.page;

            renderPatientsTable(json.data);
            updatePaginationUI();
        } catch (err) {
            console.error("fetchPatients error:", err);
            elements.patientsTableBody.innerHTML = `<tr><td colspan="9" class="text-center py-4">Error loading patient table data.</td></tr>`;
        }
    }

    function renderPatientsTable(records) {
        if (!records || records.length === 0) {
            elements.patientsTableBody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center py-4">
                        No patient records found matching the criteria.
                    </td>
                </tr>
            `;
            return;
        }

        let html = "";
        records.forEach(p => {
            const outcomeBadge = p.target_binary === 1
                ? `<span class="badge-status badge-danger">Disease</span>`
                : `<span class="badge-status badge-success">No Disease</span>`;

            html += `
                <tr>
                    <td>#${p.patient_id}</td>
                    <td><strong>${p.age}</strong></td>
                    <td>${p.sex}</td>
                    <td>${p.chest_pain}</td>
                    <td>${p.resting_bp} mm Hg</td>
                    <td>${p.cholesterol} mg/dl</td>
                    <td>${p.max_hr} bpm</td>
                    <td>${p.oldpeak} mm</td>
                    <td>${outcomeBadge}</td>
                </tr>
            `;
        });
        elements.patientsTableBody.innerHTML = html;
    }

    function updatePaginationUI() {
        elements.pageInfoText.textContent = `Showing page ${state.patients.page} of ${state.patients.pages} (${state.patients.total} total matching records)`;
        elements.pageCurrentPill.textContent = state.patients.page;
        elements.prevPageBtn.disabled = state.patients.page <= 1;
        elements.nextPageBtn.disabled = state.patients.page >= state.patients.pages;
    }

    // -------------------------------------------------------------
    // Global Event Handlers
    // -------------------------------------------------------------

    function refreshAllAnalytics() {
        fetchSummaryKPIs();
        fetchDiseaseDistribution();
        fetchAgeAnalysis();
        fetchGenderAnalysis();
        fetchChestPainAnalysis();
        fetchClinicalAnalysis();
        fetchCorrelationMatrix();
        fetchHypothesisTests();
        fetchDynamicInsights();
        state.patients.page = 1; // Reset to page 1 on filter change
        fetchPatients();
    }

    // Filter Change Listeners
    [elements.filterGender, elements.filterAgeGroup, elements.filterOutcome, elements.filterChestPain].forEach(el => {
        if (el) {
            el.addEventListener("change", () => {
                state.filters.gender = elements.filterGender.value;
                state.filters.age_group = elements.filterAgeGroup.value;
                state.filters.outcome = elements.filterOutcome.value;
                state.filters.cp = elements.filterChestPain.value;
                refreshAllAnalytics();
            });
        }
    });

    // Reset Filters Listener
    function resetFilters() {
        state.filters = { gender: "all", age_group: "all", outcome: "all", cp: "all" };
        elements.filterGender.value = "all";
        elements.filterAgeGroup.value = "all";
        elements.filterOutcome.value = "all";
        elements.filterChestPain.value = "all";
        refreshAllAnalytics();
    }

    if (elements.resetFiltersBtn) {
        elements.resetFiltersBtn.addEventListener("click", resetFilters);
    }
    if (elements.emptyStateResetBtn) {
        elements.emptyStateResetBtn.addEventListener("click", resetFilters);
    }

    // Clinical Tabs Switcher
    if (elements.clinicalTabsNav) {
        elements.clinicalTabsNav.addEventListener("click", (e) => {
            const btn = e.target.closest(".tab-btn");
            if (!btn) return;
            const varKey = btn.getAttribute("data-var");
            if (!varKey) return;

            elements.clinicalTabsNav.querySelectorAll(".tab-btn").forEach(b => {
                b.classList.remove("active");
                b.setAttribute("aria-selected", "false");
            });

            btn.classList.add("active");
            btn.setAttribute("aria-selected", "true");
            state.activeClinicalVar = varKey;
            renderClinicalTab(varKey);
        });
    }

    // Patient Explorer: Debounced Search
    let searchDebounceTimeout = null;
    if (elements.patientSearchInput) {
        elements.patientSearchInput.addEventListener("input", (e) => {
            clearTimeout(searchDebounceTimeout);
            searchDebounceTimeout = setTimeout(() => {
                state.patients.search = e.target.value.trim();
                state.patients.page = 1;
                fetchPatients();
            }, 300);
        });
    }

    // Patient Explorer: Per Page Selector
    if (elements.perPageSelect) {
        elements.perPageSelect.addEventListener("change", (e) => {
            state.patients.per_page = parseInt(e.target.value, 10);
            state.patients.page = 1;
            fetchPatients();
        });
    }

    // Patient Explorer: Pagination Buttons
    if (elements.prevPageBtn) {
        elements.prevPageBtn.addEventListener("click", () => {
            if (state.patients.page > 1) {
                state.patients.page--;
                fetchPatients();
            }
        });
    }
    if (elements.nextPageBtn) {
        elements.nextPageBtn.addEventListener("click", () => {
            if (state.patients.page < state.patients.pages) {
                state.patients.page++;
                fetchPatients();
            }
        });
    }

    // Patient Explorer: Sortable Column Headers
    if (elements.sortableHeaders) {
        elements.sortableHeaders.forEach(th => {
            th.addEventListener("click", () => {
                const col = th.getAttribute("data-col");
                if (state.patients.sort === col) {
                    state.patients.order = state.patients.order === "asc" ? "desc" : "asc";
                } else {
                    state.patients.sort = col;
                    state.patients.order = "asc";
                }

                // Update sort indicators
                elements.sortableHeaders.forEach(h => {
                    const icon = h.querySelector(".sort-icon");
                    if (h === th) {
                        icon.textContent = state.patients.order === "asc" ? "▲" : "▼";
                        icon.style.opacity = "1";
                    } else {
                        icon.textContent = "↕";
                        icon.style.opacity = "0.5";
                    }
                });

                fetchPatients();
            });
        });
    }

    // Setup ScrollSpy & Initial Load
    setupScrollSpy();
    refreshAllAnalytics();
});
