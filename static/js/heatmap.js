// Teacher Workload Heatmap Manager
window.WorkloadHeatmap = {
    searchQuery: "",
    branchFilter: "",

    init() {
        const btnList = document.getElementById("btn-view-teachers-list");
        const btnHeatmap = document.getElementById("btn-view-teachers-heatmap");
        const listView = document.getElementById("teachers-list-container");
        const heatmapView = document.getElementById("teachers-heatmap-container");

        if (btnList && btnHeatmap && listView && heatmapView) {
            btnList.addEventListener("click", () => {
                btnList.classList.add("active");
                btnHeatmap.classList.remove("active");
                listView.style.display = "block";
                heatmapView.style.display = "none";
            });

            btnHeatmap.addEventListener("click", () => {
                btnHeatmap.classList.add("active");
                btnList.classList.remove("active");
                listView.style.display = "none";
                heatmapView.style.display = "block";
                this.render();
            });
        }

        // Heatmap search and filter listeners
        const searchInput = document.getElementById("filter-heat-search");
        if (searchInput) {
            searchInput.addEventListener("input", (e) => {
                this.searchQuery = e.target.value.toLowerCase().trim();
                this.renderGrid();
            });
        }

        const branchSelect = document.getElementById("filter-heat-branch");
        if (branchSelect) {
            branchSelect.addEventListener("change", (e) => {
                this.branchFilter = e.target.value;
                this.renderGrid();
            });
        }
    },

    render() {
        this.populateBranchFilter();
        this.renderStats();
        this.renderGrid();
    },

    populateBranchFilter() {
        const select = document.getElementById("filter-heat-branch");
        if (!select) return;

        const currentVal = select.value;
        select.innerHTML = `<option value="">All Departments</option>`;
        
        const depts = AppState.departments && AppState.departments.length > 0
            ? AppState.departments.map(d => d.code)
            : Array.from(new Set(AppState.teachers.map(t => t.branch))).filter(Boolean);

        depts.forEach(d => {
            const opt = document.createElement("option");
            opt.value = d;
            opt.textContent = d;
            select.appendChild(opt);
        });

        if (currentVal) select.value = currentVal;
    },

    computeTeacherLoad(teacherId) {
        const days = (AppState.config && AppState.config.days) || ["Mon", "Tue", "Wed", "Thu", "Fri"];
        const dayLoads = {};
        days.forEach(d => { dayLoads[d] = []; });

        let totalHours = 0;

        if (AppState.timetable && AppState.timetable.length > 0) {
            AppState.timetable.forEach(entry => {
                if (entry.teacher_id === teacherId && dayLoads[entry.day] !== undefined) {
                    dayLoads[entry.day].push(entry);
                    totalHours++;
                }
            });
        }

        return { dayLoads, totalHours };
    },

    renderStats() {
        const teachers = AppState.teachers || [];
        if (teachers.length === 0) return;

        let totalAssigned = 0;
        let overloadedCount = 0;
        let optimalCount = 0;
        let underCount = 0;

        teachers.forEach(t => {
            const { totalHours } = this.computeTeacherLoad(t.id);
            totalAssigned += totalHours;
            const maxCap = (t.max_hours_per_day || 4) * 5;

            if (totalHours > maxCap) {
                overloadedCount++;
            } else if (totalHours >= 12) {
                optimalCount++;
            } else {
                underCount++;
            }
        });

        const avgLoad = (totalAssigned / teachers.length).toFixed(1);

        const avgElem = document.getElementById("heat-stat-avg");
        const optElem = document.getElementById("heat-stat-optimal");
        const overElem = document.getElementById("heat-stat-overloaded");
        const facultyElem = document.getElementById("heat-stat-faculty");

        if (avgElem) avgElem.textContent = `${avgLoad} hrs/wk`;
        if (optElem) optElem.textContent = optimalCount;
        if (overElem) overElem.textContent = overloadedCount;
        if (facultyElem) facultyElem.textContent = teachers.length;
    },

    renderGrid() {
        const container = document.getElementById("heatmap-table-container");
        if (!container) return;

        const teachers = AppState.teachers || [];
        const days = (AppState.config && AppState.config.days) || ["Mon", "Tue", "Wed", "Thu", "Fri"];

        const filtered = teachers.filter(t => {
            const matchSearch = !this.searchQuery || 
                t.name.toLowerCase().includes(this.searchQuery) || 
                t.id.toLowerCase().includes(this.searchQuery);
            const matchBranch = !this.branchFilter || t.branch === this.branchFilter;
            return matchSearch && matchBranch;
        });

        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-user-xmark"></i>
                    <h4>No Faculty Found</h4>
                    <p>No faculty members match the current search filters.</p>
                </div>
            `;
            return;
        }

        let html = `
            <div class="table-responsive">
                <table class="heatmap-table">
                    <thead>
                        <tr>
                            <th class="th-faculty">Faculty Member</th>
                            <th class="th-branch">Dept</th>
                            <th class="th-progress">Weekly Workload</th>
        `;

        days.forEach(d => {
            html += `<th class="th-day">${d}</th>`;
        });

        html += `
                            <th class="th-action">Action</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        filtered.forEach(t => {
            const { dayLoads, totalHours } = this.computeTeacherLoad(t.id);
            const maxAllowed = (t.max_hours_per_day || 4) * 5;
            const pct = Math.min(100, Math.round((totalHours / maxAllowed) * 100));

            let statusColor = "var(--emerald)";
            let badgeClass = "badge-heat-optimal";
            let statusText = "Optimal";

            if (totalHours > maxAllowed) {
                statusColor = "var(--rose)";
                badgeClass = "badge-heat-overload";
                statusText = "Overloaded";
            } else if (totalHours < 10) {
                statusColor = "var(--cyan)";
                badgeClass = "badge-heat-light";
                statusText = "Light";
            }

            const initials = t.name.split(" ").map(n => n[0]).slice(0, 2).join("").toUpperCase();

            html += `
                <tr class="heatmap-row" data-teacher-id="${t.id}">
                    <td class="td-faculty">
                        <div class="faculty-avatar-group">
                            <div class="faculty-avatar">${initials}</div>
                            <div>
                                <div class="faculty-name">${t.name}</div>
                                <div class="faculty-id">${t.id}</div>
                            </div>
                        </div>
                    </td>
                    <td class="td-branch">
                        <span class="badge-dept">${t.branch || 'GEN'}</span>
                    </td>
                    <td class="td-progress">
                        <div class="load-bar-wrapper">
                            <div class="load-bar-header">
                                <span class="load-numbers"><strong>${totalHours}</strong> / ${maxAllowed} hrs</span>
                                <span class="badge-load-status ${badgeClass}">${statusText}</span>
                            </div>
                            <div class="load-bar-track">
                                <div class="load-bar-fill" style="width: ${pct}%; background: ${statusColor};"></div>
                            </div>
                        </div>
                    </td>
            `;

            days.forEach(d => {
                const entries = dayLoads[d] || [];
                const hours = entries.length;
                let heatClass = "heat-0";
                if (hours === 1 || hours === 2) heatClass = "heat-1";
                else if (hours === 3 || hours === 4) heatClass = "heat-2";
                else if (hours === 5) heatClass = "heat-3";
                else if (hours >= 6) heatClass = "heat-4";

                // Tooltip content
                let tooltip = `No classes on ${d}`;
                if (hours > 0) {
                    const items = entries.map(e => `• P${e.period}: ${e.subject_id} (${e.section_id} in ${e.room_id})`).join("\n");
                    tooltip = `${t.name} on ${d} (${hours} hrs):\n${items}`;
                }

                html += `
                    <td class="td-heat-cell" title="${tooltip}" data-teacher="${t.id}" data-day="${d}">
                        <div class="heat-chip ${heatClass}">
                            <span class="heat-val">${hours > 0 ? `${hours}h` : '—'}</span>
                        </div>
                    </td>
                `;
            });

            html += `
                    <td class="td-action">
                        <button class="btn-inspect-teacher" data-teacher-id="${t.id}" title="View timetable in Grid">
                            <i class="fa-solid fa-table-cells"></i> View Grid
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = html;

        // Attach click actions to jump to timetable view
        container.querySelectorAll(".btn-inspect-teacher").forEach(btn => {
            btn.addEventListener("click", () => {
                const tId = btn.dataset.teacherId;
                this.jumpToTeacherGrid(tId);
            });
        });

        container.querySelectorAll(".td-heat-cell").forEach(cell => {
            cell.addEventListener("click", () => {
                const tId = cell.dataset.teacher;
                const day = cell.dataset.day;
                this.jumpToTeacherGrid(tId, day);
            });
        });
    },

    jumpToTeacherGrid(teacherId, day = null) {
        // Switch to Timetable tab
        const tabBtn = document.querySelector('[data-tab="tab-timetable"]');
        if (tabBtn) tabBtn.click();

        AppState.currentViewType = "teacher";
        const viewTypeSelect = document.getElementById("filter-view-type");
        if (viewTypeSelect) viewTypeSelect.value = "teacher";

        if (window.TimetableRenderer) {
            window.TimetableRenderer.updateFilterOptions();
        }

        AppState.currentTargetId = teacherId;
        const targetSelect = document.getElementById("filter-target-id");
        if (targetSelect) targetSelect.value = teacherId;

        if (window.TimetableRenderer) {
            window.TimetableRenderer.render();
        }

        if (day) {
            setTimeout(() => {
                const rows = document.querySelectorAll(".timetable-grid tbody tr");
                rows.forEach(row => {
                    const header = row.querySelector("th.day-header");
                    if (header && header.textContent.trim() === day) {
                        row.classList.add("slot-highlight-pulse");
                        row.scrollIntoView({ behavior: "smooth", block: "center" });
                        setTimeout(() => row.classList.remove("slot-highlight-pulse"), 3000);
                    }
                });
            }, 300);
        }

        if (window.showToast) {
            showToast(`Switched to Teacher Schedule: ${teacherId}${day ? ` (${day})` : ''}`, "info");
        }
    }
};
