// Conflict Diagnostics Panel Manager
window.DiagnosticsManager = {
    diagnosticsData: null,
    activeFilter: "all",

    init() {
        const btnOpen = document.getElementById("btn-open-diagnostics");
        const modal = document.getElementById("modal-diagnostics");
        const closeBtn = document.querySelector('[data-close="modal-diagnostics"]');

        if (btnOpen && modal) {
            btnOpen.addEventListener("click", () => {
                modal.classList.add("active");
                this.loadDiagnostics();
            });
        }

        if (closeBtn && modal) {
            closeBtn.addEventListener("click", () => {
                modal.classList.remove("active");
            });
        }

        // Close on backdrop click
        if (modal) {
            modal.addEventListener("click", (e) => {
                if (e.target === modal) modal.classList.remove("active");
            });
        }

        // Filter tabs in modal
        const filterBtns = document.querySelectorAll(".diag-filter-btn");
        filterBtns.forEach(btn => {
            btn.addEventListener("click", (e) => {
                filterBtns.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                this.activeFilter = btn.dataset.filter || "all";
                this.renderIssuesList();
            });
        });
    },

    async loadDiagnostics() {
        const listContainer = document.getElementById("diagnostics-issues-list");
        if (listContainer) {
            listContainer.innerHTML = `
                <div class="diag-loading">
                    <i class="fa-solid fa-circle-notch fa-spin"></i>
                    <span>Running comprehensive clash analysis & constraint checks...</span>
                </div>
            `;
        }

        try {
            const res = await fetch("/api/diagnostics");
            const data = await res.json();
            if (data.status === "success") {
                this.diagnosticsData = data;
                this.updateBadge(data.summary);
                this.renderSummary(data.summary);
                this.renderIssuesList();
            }
        } catch (err) {
            console.error("Failed to load diagnostics:", err);
            if (listContainer) {
                listContainer.innerHTML = `
                    <div class="empty-state">
                        <i class="fa-solid fa-triangle-exclamation text-rose"></i>
                        <h4>Diagnostics Check Failed</h4>
                        <p>${err.message}</p>
                    </div>
                `;
            }
        }
    },

    updateBadge(summary) {
        const badge = document.getElementById("badge-conflict-count");
        if (!badge) return;

        const count = summary ? summary.total_issues : 0;
        const criticalCount = summary ? summary.critical_count : 0;
        badge.textContent = count;

        if (criticalCount > 0) {
            badge.className = "count-badge badge-conflict-critical";
        } else if (count > 0) {
            badge.className = "count-badge badge-conflict-warning";
        } else {
            badge.className = "count-badge badge-conflict-ok";
        }
    },

    renderSummary(summary) {
        const scoreElem = document.getElementById("diag-health-score");
        const statusText = document.getElementById("diag-health-status");
        const criticalBadge = document.getElementById("diag-count-critical");
        const warningBadge = document.getElementById("diag-count-warning");
        const infoBadge = document.getElementById("diag-count-info");

        if (scoreElem) {
            scoreElem.textContent = `${summary.health_score}%`;
            if (summary.health_score >= 95) scoreElem.style.color = "var(--emerald)";
            else if (summary.health_score >= 75) scoreElem.style.color = "var(--amber)";
            else scoreElem.style.color = "var(--rose)";
        }

        if (statusText) {
            if (summary.critical_count === 0 && summary.warning_count === 0) {
                statusText.textContent = "Optimal Schedule — Zero Clashes";
                statusText.style.color = "var(--emerald)";
            } else if (summary.critical_count > 0) {
                statusText.textContent = `${summary.critical_count} Critical Double-Booking(s) Detected`;
                statusText.style.color = "var(--rose)";
            } else {
                statusText.textContent = "Clash-Free with Soft Optimization Warnings";
                statusText.style.color = "var(--amber)";
            }
        }

        if (criticalBadge) criticalBadge.textContent = summary.critical_count;
        if (warningBadge) warningBadge.textContent = summary.warning_count;
        if (infoBadge) infoBadge.textContent = summary.info_count;
    },

    renderIssuesList() {
        const container = document.getElementById("diagnostics-issues-list");
        if (!container || !this.diagnosticsData) return;

        const issues = this.diagnosticsData.issues || [];
        const filtered = issues.filter(issue => {
            if (this.activeFilter === "all") return true;
            return issue.severity === this.activeFilter;
        });

        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="diag-empty-state">
                    <i class="fa-solid fa-circle-check text-emerald"></i>
                    <h4>No Issues Found in this Category</h4>
                    <p>All constraints, teacher allocations, and room capacities are fully satisfied.</p>
                </div>
            `;
            return;
        }

        let html = "";
        filtered.forEach(issue => {
            let icon = "fa-triangle-exclamation";
            let severityClass = "diag-severity-warning";
            let severityLabel = "Warning";

            if (issue.severity === "critical") {
                icon = "fa-circle-xmark";
                severityClass = "diag-severity-critical";
                severityLabel = "Critical Clash";
            } else if (issue.severity === "info") {
                icon = "fa-circle-info";
                severityClass = "diag-severity-info";
                severityLabel = "Notice";
            }

            const canJump = issue.target_type && issue.target_id;

            html += `
                <div class="diag-issue-card ${severityClass}">
                    <div class="diag-card-icon">
                        <i class="fa-solid ${icon}"></i>
                    </div>
                    <div class="diag-card-body">
                        <div class="diag-card-header">
                            <span class="diag-badge ${severityClass}">${severityLabel}</span>
                            <span class="diag-time-tag">${issue.day || ''} ${issue.period ? `• Period ${issue.period}` : ''}</span>
                        </div>
                        <h4 class="diag-card-title">${issue.title}</h4>
                        <p class="diag-card-desc">${issue.message}</p>
                    </div>
                    ${canJump ? `
                        <div class="diag-card-action">
                            <button class="btn-jump-slot" data-type="${issue.target_type}" data-id="${issue.target_id}" data-day="${issue.day || ''}" data-period="${issue.period || ''}" title="Navigate to grid slot">
                                <i class="fa-solid fa-arrow-up-right-from-square"></i>
                                <span>Inspect</span>
                            </button>
                        </div>
                    ` : ''}
                </div>
            `;
        });

        container.innerHTML = html;

        // Bind jump buttons
        container.querySelectorAll(".btn-jump-slot").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const targetType = btn.dataset.type;
                const targetId = btn.dataset.id;
                const day = btn.dataset.day;
                const period = btn.dataset.period;
                this.jumpToGrid(targetType, targetId, day, period);
            });
        });
    },

    jumpToGrid(targetType, targetId, day, period) {
        const modal = document.getElementById("modal-diagnostics");
        if (modal) modal.classList.remove("active");

        // Switch to Timetable tab
        const tabBtn = document.querySelector('[data-tab="tab-timetable"]');
        if (tabBtn) tabBtn.click();

        // Switch view type & target
        if (targetType) {
            AppState.currentViewType = targetType;
            const viewTypeSelect = document.getElementById("filter-view-type");
            if (viewTypeSelect) viewTypeSelect.value = targetType;

            if (window.TimetableRenderer) {
                window.TimetableRenderer.updateFilterOptions();
            }

            if (targetId) {
                AppState.currentTargetId = targetId;
                const targetSelect = document.getElementById("filter-target-id");
                if (targetSelect) targetSelect.value = targetId;
            }

            if (window.TimetableRenderer) {
                window.TimetableRenderer.render();
            }
        }

        // Highlight slot if day and period are provided
        if (day && period) {
            setTimeout(() => {
                const cells = document.querySelectorAll(`[data-day="${day}"][data-period="${period}"]`);
                cells.forEach(cell => {
                    cell.classList.add("slot-highlight-pulse");
                    cell.scrollIntoView({ behavior: "smooth", block: "center" });
                    setTimeout(() => cell.classList.remove("slot-highlight-pulse"), 3500);
                });
            }, 300);
        }

        if (window.showToast) {
            showToast(`Inspecting: ${targetType.toUpperCase()} ${targetId || ''} (${day} P${period || ''})`, "info");
        }
    }
};
