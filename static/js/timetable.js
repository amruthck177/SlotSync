// Timetable Grid Renderer
window.TimetableRenderer = {
    init() {
        const viewTypeSelect = document.getElementById("filter-view-type");
        const targetSelect = document.getElementById("filter-target-id");

        if (viewTypeSelect) {
            viewTypeSelect.addEventListener("change", (e) => {
                AppState.currentViewType = e.target.value;
                this.updateFilterOptions();
                this.render();
            });
        }

        if (targetSelect) {
            targetSelect.addEventListener("change", (e) => {
                AppState.currentTargetId = e.target.value;
                this.render();
            });
        }
    },

    updateFilterOptions() {
        const targetContainer = document.getElementById("container-filter-target");
        const targetLabel = document.getElementById("label-filter-target");
        const targetSelect = document.getElementById("filter-target-id");
        if (!targetSelect) return;

        targetSelect.innerHTML = "";

        if (AppState.currentViewType === "master") {
            targetContainer.style.display = "none";
            return;
        }

        targetContainer.style.display = "flex";

        if (AppState.currentViewType === "section") {
            targetLabel.innerHTML = `<i class="fa-solid fa-users"></i> Select Section`;
            AppState.sections.forEach(s => {
                const opt = document.createElement("option");
                opt.value = s.id;
                opt.textContent = `${s.id} (${s.branch} - Sem ${s.semester})`;
                targetSelect.appendChild(opt);
            });
        } else if (AppState.currentViewType === "teacher") {
            targetLabel.innerHTML = `<i class="fa-solid fa-user-tie"></i> Select Teacher`;
            AppState.teachers.forEach(t => {
                const opt = document.createElement("option");
                opt.value = t.id;
                opt.textContent = `${t.id} - ${t.name} (${t.branch})`;
                targetSelect.appendChild(opt);
            });
        } else if (AppState.currentViewType === "room") {
            targetLabel.innerHTML = `<i class="fa-solid fa-door-open"></i> Select Room`;
            AppState.rooms.forEach(r => {
                const opt = document.createElement("option");
                opt.value = r.id;
                opt.textContent = `${r.id} (${r.type} - Cap ${r.capacity})`;
                targetSelect.appendChild(opt);
            });
        }

        // Restore or set default
        if (targetSelect.options.length > 0) {
            if (!AppState.currentTargetId || !Array.from(targetSelect.options).some(o => o.value === AppState.currentTargetId)) {
                AppState.currentTargetId = targetSelect.options[0].value;
            }
            targetSelect.value = AppState.currentTargetId;
        }
    },

    render() {
        const renderArea = document.getElementById("timetable-render-area");
        if (!renderArea) return;

        if (!AppState.timetable || AppState.timetable.length === 0) {
            renderArea.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-calendar-xmark"></i>
                    <h4>No Timetable Generated Yet</h4>
                    <p>Click "Generate Timetable" in the top bar to run the OR-Tools AI Solver.</p>
                </div>
            `;
            return;
        }

        if (AppState.currentViewType === "master") {
            this.renderMasterView(renderArea);
        } else {
            this.renderSingleGrid(renderArea);
        }
    },

    renderSingleGrid(container) {
        const config = AppState.config || {};
        const days = config.days || ["Mon", "Tue", "Wed", "Thu", "Fri"];
        const timeSlots = config.time_slots && config.time_slots.length > 0 
            ? config.time_slots 
            : Array.from({ length: config.periods_per_day || 7 }, (_, i) => ({
                period: i + 1,
                type: "teaching",
                label: `Period ${i + 1}`,
                start_time: "",
                end_time: ""
            }));

        const subjectsMap = Object.fromEntries(AppState.subjects.map(s => [s.id, s]));
        const teachersMap = Object.fromEntries(AppState.teachers.map(t => [t.id, t]));

        let html = `
            <table class="timetable-grid">
                <thead>
                    <tr>
                        <th class="day-header">Day / Time</th>
        `;

        timeSlots.forEach(slot => {
            const isBreak = slot.type === "break" || slot.type === "lunch";
            const timeSub = slot.start_time && slot.end_time ? `<span class="grid-time-sub">${slot.start_time} - ${slot.end_time}</span>` : '';
            
            if (isBreak) {
                const icon = slot.type === "lunch" ? "fa-utensils" : "fa-mug-hot";
                html += `<th style="background:rgba(245,158,11,0.15); color:var(--amber); min-width:85px;"><i class="fa-solid ${icon}"></i> ${slot.label}${timeSub}</th>`;
            } else {
                html += `<th>${slot.label}${timeSub}</th>`;
            }
        });

        html += `
                    </tr>
                </thead>
                <tbody>
        `;

        days.forEach(day => {
            html += `
                <tr>
                    <th class="day-header">${day}</th>
            `;

            timeSlots.forEach(slot => {
                if (slot.type === "break" || slot.type === "lunch") {
                    const icon = slot.type === "lunch" ? "fa-utensils" : "fa-mug-hot";
                    html += `
                        <td>
                            <div class="slot-cell grid-break-cell">
                                <i class="fa-solid ${icon}"></i>
                                <span>${slot.label}</span>
                            </div>
                        </td>
                    `;
                    return;
                }

                const p = slot.period;
                // Filter entries based on active view
                let entries = [];
                if (AppState.currentViewType === "section") {
                    entries = AppState.timetable.filter(
                        e => e.section_id === AppState.currentTargetId && e.day === day && e.period === p
                    );
                } else if (AppState.currentViewType === "teacher") {
                    entries = AppState.timetable.filter(
                        e => e.teacher_id === AppState.currentTargetId && e.day === day && e.period === p
                    );
                } else if (AppState.currentViewType === "room") {
                    entries = AppState.timetable.filter(
                        e => e.room_id === AppState.currentTargetId && e.day === day && e.period === p
                    );
                }

                html += `<td>${this.renderCellContent(entries, subjectsMap, teachersMap, day, p)}</td>`;
            });

            html += `</tr>`;
        });

        html += `
                </tbody>
            </table>
        `;

        container.innerHTML = html;
        this.attachCellEventListeners(container);
    },

    renderMasterView(container) {
        const config = AppState.config || {};
        const days = config.days || ["Mon", "Tue", "Wed", "Thu", "Fri"];
        const timeSlots = config.time_slots && config.time_slots.length > 0 
            ? config.time_slots 
            : Array.from({ length: config.periods_per_day || 7 }, (_, i) => ({
                period: i + 1,
                type: "teaching",
                label: `P${i + 1}`,
                start_time: "",
                end_time: ""
            }));

        const subjectsMap = Object.fromEntries(AppState.subjects.map(s => [s.id, s]));
        const teachersMap = Object.fromEntries(AppState.teachers.map(t => [t.id, t]));

        let html = `<div style="display:flex; flex-direction:column; gap:28px;">`;

        AppState.sections.forEach(sec => {
            html += `
                <div style="border-bottom: 1px solid var(--border-color); padding-bottom: 20px;">
                    <h3 style="font-family:var(--font-heading); font-size:16px; margin-bottom:12px; display:flex; align-items:center; gap:8px;">
                        <i class="fa-solid fa-users text-indigo"></i> Section: ${sec.id} <span style="font-size:12px; color:var(--text-muted); font-weight:normal;">(${sec.branch} - Sem ${sec.semester})</span>
                    </h3>
                    <table class="timetable-grid">
                        <thead>
                            <tr>
                                <th class="day-header">Day</th>
                                ${timeSlots.map(s => {
                                    const timeSub = s.start_time ? `<br><small style="font-size:9px; font-weight:normal; color:#94a3b8;">${s.start_time}</small>` : '';
                                    return `<th>${s.label}${timeSub}</th>`;
                                }).join('')}
                            </tr>
                        </thead>
                        <tbody>
            `;

            days.forEach(day => {
                html += `<tr><th class="day-header">${day}</th>`;
                timeSlots.forEach(slot => {
                    if (slot.type === "break" || slot.type === "lunch") {
                        html += `<td><div class="slot-cell grid-break-cell" style="font-size:9px;">${slot.label}</div></td>`;
                        return;
                    }
                    const p = slot.period;
                    const entries = AppState.timetable.filter(
                        e => e.section_id === sec.id && e.day === day && e.period === p
                    );
                    html += `<td>${this.renderCellContent(entries, subjectsMap, teachersMap, day, p)}</td>`;
                });
                html += `</tr>`;
            });

            html += `
                        </tbody>
                    </table>
                </div>
            `;
        });

        html += `</div>`;
        container.innerHTML = html;
        this.attachCellEventListeners(container);
    },

    renderCellContent(entries, subjectsMap, teachersMap, day, period) {
        if (!entries || entries.length === 0) {
            return `
                <div class="slot-cell">
                    <div class="slot-empty">—</div>
                </div>
            `;
        }

        if (entries.length === 1) {
            const e = entries[0];
            const subj = subjectsMap[e.subject_id] || { name: e.subject_id, needs_lab: false };
            const teacher = teachersMap[e.teacher_id] || { name: e.teacher_id };
            const isLab = subj.needs_lab;
            const isLocked = e.is_locked;

            let cardClass = "slot-cell has-content";
            if (isLocked) cardClass += " slot-locked";
            else if (isLab) cardClass += " slot-lab";

            return `
                <div class="${cardClass}" data-day="${day}" data-period="${period}" data-section="${e.section_id}" data-subject="${e.subject_id}" data-locked="${isLocked ? 'true' : 'false'}">
                    <div class="slot-header">
                        <span class="slot-code">${isLab ? '<i class="fa-solid fa-flask text-cyan"></i> ' : ''}${e.subject_id}</span>
                        <div class="slot-actions">
                            <button class="btn-pin-slot ${isLocked ? 'locked' : ''}" title="${isLocked ? 'Click to Unlock' : 'Click to Pin / Lock this slot'}" data-action="toggle-pin">
                                <i class="fa-solid ${isLocked ? 'fa-lock' : 'fa-lock-open'}"></i>
                            </button>
                        </div>
                    </div>
                    <div class="slot-title" title="${subj.name}">${subj.name}</div>
                    <div class="slot-footer">
                        <span class="slot-teacher" title="${teacher.name}">${e.teacher_id} (${teacher.name ? teacher.name.split(' ')[0] : ''})</span>
                        <span class="slot-room"><i class="fa-solid fa-location-dot"></i> ${e.room_id}</span>
                    </div>
                </div>
            `;
        } else {
            // Parallel Electives
            const grp = entries[0].elective_group || "Elective";
            return `
                <div class="slot-cell has-content slot-elective">
                    <div class="slot-header" style="margin-bottom:4px;">
                        <span class="badge-pill" style="font-size:9px; margin-left:0;"><i class="fa-solid fa-bolt"></i> ${grp} (${entries.length})</span>
                    </div>
                    <div class="slot-elective-group">
                        ${entries.map(e => `
                            <div class="elective-sub-slot">
                                <strong>${e.subject_id}</strong>
                                <span>${e.teacher_id} / ${e.room_id}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
    },

    attachCellEventListeners(container) {
        container.querySelectorAll("[data-action='toggle-pin']").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                e.stopPropagation();
                const cell = btn.closest(".slot-cell");
                if (!cell) return;

                const day = cell.getAttribute("data-day");
                const period = parseInt(cell.getAttribute("data-period"));
                const section_id = cell.getAttribute("data-section");
                const subject_id = cell.getAttribute("data-subject");
                const currentLocked = cell.getAttribute("data-locked") === "true";
                const newLocked = !currentLocked;

                try {
                    const res = await fetch("/api/timetable/lock", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            day,
                            period,
                            section_id,
                            subject_id,
                            is_locked: newLocked
                        })
                    });
                    const json = await res.json();
                    if (json.status === "success") {
                        showToast(`Slot ${day} P${period} ${newLocked ? 'pinned 🔒' : 'unpinned 🔓'}.`, "info");
                        // Update local state
                        const targetEntry = AppState.timetable.find(
                            item => item.day === day && item.period === period && item.section_id === section_id && item.subject_id === subject_id
                        );
                        if (targetEntry) {
                            targetEntry.is_locked = newLocked;
                        }
                        this.render();
                    }
                } catch (err) {
                    showToast("Failed to update slot lock status.", "error");
                }
            });
        });
    }
};

document.addEventListener("DOMContentLoaded", () => {
    window.TimetableRenderer.init();
});
