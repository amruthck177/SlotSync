// Data Manager for VTU Departments, Subjects, Teachers, Rooms, Sections & Settings

function extractSemesterFromCode(code) {
    if (!code) return null;
    const clean = code.trim().toUpperCase();
    // VTU scheme: e.g. 21CS51 -> 5, 21CSL55 -> 5, 21MAT11 -> 1, 21EC61 -> 6
    const vtuMatch = clean.match(/^\d{2}[A-Z]+(\d)/);
    if (vtuMatch) {
        const sem = parseInt(vtuMatch[1]);
        if (sem >= 1 && sem <= 8) return sem;
    }
    // Short prefix scheme: CS301 -> 3, IS401 -> 4, ME5A -> 5
    const prefixMatch = clean.match(/^[A-Z]+(\d)/);
    if (prefixMatch) {
        const sem = parseInt(prefixMatch[1]);
        if (sem >= 1 && sem <= 8) return sem;
    }
    return null;
}

window.DataManager = {
    activeTimeSlots: [],
    subjFilters: {
        search: "",
        branch: "",
        semester: "",
        type: ""
    },

    init() {
        this.bindAddButtons();
        this.bindFormSubmissions();
        this.bindSettingsForm();
        this.bindSubjectFilters();
        this.bindAutoSemesterDetection();
        this.bindImportModal();
    },

    renderAllTables() {
        this.renderDepartmentsHub();
        this.renderTeachersTable();
        this.renderSubjectsTable();
        this.renderRoomsTable();
        this.renderSectionsTable();
    },

    // =========================================================================
    // 1. VTU DEPARTMENTS HUB & SEMESTER CURRICULUM EXPLORER
    // =========================================================================
    renderDepartmentsHub() {
        const grid = document.getElementById("dept-cards-grid");
        if (!grid) return;
        grid.innerHTML = "";

        const depts = AppState.departments || [];
        if (depts.length === 0) {
            grid.innerHTML = `<div class="empty-state" style="grid-column: 1/-1;"><p>No departments loaded.</p></div>`;
            return;
        }

        // Set default active department if not set
        if (!AppState.activeDepartment && depts.length > 0) {
            AppState.activeDepartment = depts[0].code;
        }

        depts.forEach(d => {
            const card = document.createElement("div");
            const isSelected = d.code === AppState.activeDepartment;
            card.className = `dept-card ${isSelected ? 'selected' : ''}`;
            card.setAttribute("data-code", d.code);

            // Compute actual current subject count in DB
            const actualCount = AppState.subjects.filter(s => s.branch === d.code).length;

            card.innerHTML = `
                <div class="dept-card-top">
                    <div class="dept-icon-box ${d.color || 'indigo'}">
                        <i class="fa-solid ${d.icon || 'fa-graduation-cap'}"></i>
                    </div>
                    <span class="badge-tag badge-${d.color || 'cyan'}">${d.code}</span>
                </div>
                <div class="dept-card-title">${d.name}</div>
                <div class="dept-card-meta">
                    <span><i class="fa-solid fa-book text-muted"></i> <strong>${actualCount}</strong> Courses</span>
                    <span><i class="fa-solid fa-layer-group text-muted"></i> Sem 1 - 8</span>
                </div>
            `;

            card.addEventListener("click", () => {
                AppState.activeDepartment = d.code;
                document.querySelectorAll(".dept-card").forEach(c => c.classList.remove("selected"));
                card.classList.add("selected");
                this.renderActiveDepartmentWorkstation();
            });

            grid.appendChild(card);
        });

        this.renderActiveDepartmentWorkstation();
    },

    renderActiveDepartmentWorkstation() {
        const activeCode = AppState.activeDepartment || "CSE";
        const dept = (AppState.departments || []).find(d => d.code === activeCode) || {
            code: activeCode,
            name: activeCode,
            icon: "fa-graduation-cap",
            color: "indigo",
            desc: "Engineering and academic department curriculum."
        };

        // 1. Update Header Banner
        const titleElem = document.getElementById("active-dept-title");
        const codeElem = document.getElementById("active-dept-code");
        const descElem = document.getElementById("active-dept-desc");
        const iconElem = document.getElementById("active-dept-icon");
        const labelQuickSec = document.getElementById("label-quick-create-sec");

        if (titleElem) titleElem.innerText = dept.name;
        if (codeElem) codeElem.innerText = dept.code;
        if (descElem) descElem.innerText = dept.desc || "Engineering curriculum & semester courses.";
        if (iconElem) iconElem.className = `fa-solid ${dept.icon || 'fa-graduation-cap'}`;
        if (labelQuickSec) labelQuickSec.innerText = `Quick Create Section (${dept.code}-${AppState.activeSemester}A)`;

        // 2. Populate Branch Select in Add Subject Form
        const branchSelect = document.getElementById("dept-input-branch");
        if (branchSelect) {
            branchSelect.innerHTML = (AppState.departments || []).map(d => `
                <option value="${d.code}" ${d.code === dept.code ? 'selected' : ''}>${d.code} — ${d.name}</option>
            `).join("");
        }

        // 3. Render Semester Tabs (Sem 1 to 8)
        const tabsBar = document.getElementById("dept-semester-tabs");
        if (tabsBar) {
            tabsBar.innerHTML = "";
            for (let sem = 1; sem <= 8; sem++) {
                const semCount = AppState.subjects.filter(s => s.branch === activeCode && parseInt(s.semester) === sem).length;
                const btn = document.createElement("button");
                btn.type = "button";
                btn.className = `sem-tab-btn ${sem === AppState.activeSemester ? 'active' : ''}`;
                btn.innerHTML = `
                    <span>Semester ${sem}</span>
                    <span class="sem-count">${semCount}</span>
                `;
                btn.addEventListener("click", () => {
                    AppState.activeSemester = sem;
                    this.renderActiveDepartmentWorkstation();
                });
                tabsBar.appendChild(btn);
            }
        }

        // 4. Update Form Target Semester Badge & Default Sem
        const badgeTargetSem = document.getElementById("badge-target-sem");
        if (badgeTargetSem) badgeTargetSem.innerText = `Semester ${AppState.activeSemester}`;
        const inputSem = document.getElementById("dept-input-sem");
        if (inputSem && !inputSem.value) {
            inputSem.placeholder = `Auto (${AppState.activeSemester})`;
        }

        // 5. Render Semester Subjects List
        const listTitle = document.getElementById("dept-subjects-list-title");
        const listSubtitle = document.getElementById("dept-subjects-list-subtitle");
        const semCountBadge = document.getElementById("dept-sem-count-badge");
        const container = document.getElementById("dept-sem-subjects-container");

        const semSubjects = AppState.subjects.filter(s => s.branch === activeCode && parseInt(s.semester) === AppState.activeSemester);

        if (listTitle) listTitle.innerHTML = `<i class="fa-solid fa-book-bookmark text-cyan"></i> ${dept.code} Semester ${AppState.activeSemester} Curriculum`;
        if (listSubtitle) listSubtitle.innerText = `${semSubjects.length} courses configured for Semester ${AppState.activeSemester}.`;
        if (semCountBadge) semCountBadge.innerText = `${semSubjects.length} Courses`;

        if (!container) return;
        container.innerHTML = "";

        if (semSubjects.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="padding:32px 16px;">
                    <i class="fa-solid fa-folder-open"></i>
                    <h4>No Subjects in Semester ${AppState.activeSemester}</h4>
                    <p>Use the form on the left to add a course or click "Sync VTU Catalog" above.</p>
                </div>
            `;
            return;
        }

        semSubjects.forEach(s => {
            const item = document.createElement("div");
            item.className = "dept-subject-item";

            const typeBadge = s.needs_lab 
                ? `<span class="badge-tag" style="background:rgba(6,182,212,0.2); color:var(--cyan);"><i class="fa-solid fa-flask"></i> Laboratory</span>`
                : `<span class="badge-tag">Theory Lecture</span>`;

            const blockInfo = s.consecutive_hours > 1 ? `<span class="badge-tag badge-purple">${s.consecutive_hours} hrs Block</span>` : "";

            item.innerHTML = `
                <div class="dept-subj-main">
                    <span class="dept-subj-code-badge">${s.id}</span>
                    <div class="dept-subj-info">
                        <h5>${s.name}</h5>
                        <div class="subj-meta">
                            <span><i class="fa-regular fa-clock"></i> ${s.weekly_hours} hrs/week</span>
                            ${typeBadge}
                            ${blockInfo}
                        </div>
                    </div>
                </div>
                <div class="dept-subj-actions table-actions-cell">
                    <button class="btn-edit-outline" data-action="edit-dept-subj" data-id="${s.id}" title="Edit course">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                    <button class="btn-danger-outline" data-action="del-dept-subj" data-id="${s.id}" title="Remove course">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            `;
            container.appendChild(item);
        });

        // Bind edit subject buttons inside department workstation
        container.querySelectorAll("[data-action='edit-dept-subj']").forEach(btn => {
            btn.addEventListener("click", () => {
                const id = btn.getAttribute("data-id");
                this.openEditSubjectModal(id);
            });
        });

        // Bind delete subject buttons inside department workstation
        container.querySelectorAll("[data-action='del-dept-subj']").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = btn.getAttribute("data-id");
                if (!confirm(`Delete subject ${id}?`)) return;
                await fetch(`/api/subjects/${id}`, { method: "DELETE" });
                showToast(`Subject ${id} removed.`, "info");
                await loadAppData();
            });
        });
    },

    // =========================================================================
    // 2. TEACHERS TABLE
    // =========================================================================
    renderTeachersTable() {
        const tbody = document.getElementById("teachers-table-body");
        if (!tbody) return;
        tbody.innerHTML = "";

        AppState.teachers.forEach(t => {
            const tr = document.createElement("tr");

            // Subjects tags
            const subjTags = t.subjects.map(s => `<span class="badge-tag">${s}</span>`).join(" ");
            const crossTags = t.cross_branch_subjects.map(cb => {
                const code = typeof cb === "object" ? `${cb.code} (${cb.branch})` : cb;
                return `<span class="badge-tag badge-cross"><i class="fa-solid fa-shuffle"></i> ${code}</span>`;
            }).join(" ");

            tr.innerHTML = `
                <td><strong>${t.id}</strong></td>
                <td>${t.name}</td>
                <td><span class="badge-tag badge-cyan">${t.branch}</span></td>
                <td>${subjTags || '<span class="text-muted">None</span>'}</td>
                <td>${crossTags || '<span class="text-muted">—</span>'}</td>
                <td>${t.max_hours_per_day} hrs/day</td>
                <td class="table-actions-cell">
                    <button class="btn-edit-outline" data-action="edit-teacher" data-id="${t.id}" title="Edit faculty member">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                    <button class="btn-danger-outline" data-action="del-teacher" data-id="${t.id}" title="Delete faculty member">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        tbody.querySelectorAll("[data-action='edit-teacher']").forEach(btn => {
            btn.addEventListener("click", () => {
                const id = btn.getAttribute("data-id");
                const t = AppState.teachers.find(item => item.id === id);
                if (!t) return;
                const form = document.getElementById("form-teacher");
                form.reset();
                document.getElementById("input-t-mode").value = "edit";
                const idInput = document.getElementById("input-t-id");
                idInput.value = t.id;
                idInput.readOnly = true;
                document.getElementById("input-t-name").value = t.name || "";
                document.getElementById("input-t-branch").value = t.branch || "";
                document.getElementById("input-t-max-hours").value = t.max_hours_per_day || 4;
                document.getElementById("input-t-subjects").value = (t.subjects || []).join(", ");
                document.getElementById("input-t-cross").value = (t.cross_branch_subjects || []).map(cb => typeof cb === "object" ? `${cb.code}:${cb.branch}` : cb).join(", ");
                document.getElementById("modal-teacher-title").innerHTML = `<i class="fa-solid fa-pen-to-square text-cyan"></i> Edit Faculty: <strong>${t.name}</strong> <span class="input-readonly-badge">${t.id}</span>`;
                openModal("modal-teacher");
            });
        });

        tbody.querySelectorAll("[data-action='del-teacher']").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = btn.getAttribute("data-id");
                if (!confirm(`Delete teacher ${id}?`)) return;
                await fetch(`/api/teachers/${id}`, { method: "DELETE" });
                showToast(`Teacher ${id} removed.`, "info");
                await loadAppData();
            });
        });
    },

    // =========================================================================
    // 3. SUBJECTS TABLE & FILTERING
    // =========================================================================
    bindSubjectFilters() {
        const searchInput = document.getElementById("filter-subj-search");
        const branchSelect = document.getElementById("filter-subj-branch");
        const semSelect = document.getElementById("filter-subj-sem");
        const typeSelect = document.getElementById("filter-subj-type");

        if (searchInput) {
            searchInput.addEventListener("input", (e) => {
                this.subjFilters.search = e.target.value.trim().toLowerCase();
                this.renderSubjectsTable();
            });
        }
        if (branchSelect) {
            branchSelect.addEventListener("change", (e) => {
                this.subjFilters.branch = e.target.value;
                this.renderSubjectsTable();
            });
        }
        if (semSelect) {
            semSelect.addEventListener("change", (e) => {
                this.subjFilters.semester = e.target.value;
                this.renderSubjectsTable();
            });
        }
        if (typeSelect) {
            typeSelect.addEventListener("change", (e) => {
                this.subjFilters.type = e.target.value;
                this.renderSubjectsTable();
            });
        }
    },

    renderSubjectsTable() {
        const tbody = document.getElementById("subjects-table-body");
        if (!tbody) return;
        tbody.innerHTML = "";

        // Populate department filter dropdown options if empty
        const deptSelect = document.getElementById("filter-subj-branch");
        if (deptSelect && deptSelect.options.length <= 1) {
            const currentVal = deptSelect.value;
            const uniqueBranches = Array.from(new Set(AppState.subjects.map(s => s.branch).concat((AppState.departments || []).map(d => d.code)))).filter(Boolean).sort();
            deptSelect.innerHTML = `<option value="">All Departments</option>` + uniqueBranches.map(b => `<option value="${b}">${b}</option>`).join("");
            deptSelect.value = currentVal;
        }

        // Apply filters
        let filtered = AppState.subjects || [];
        if (this.subjFilters.search) {
            filtered = filtered.filter(s => 
                s.id.toLowerCase().includes(this.subjFilters.search) || 
                s.name.toLowerCase().includes(this.subjFilters.search)
            );
        }
        if (this.subjFilters.branch) {
            filtered = filtered.filter(s => s.branch === this.subjFilters.branch);
        }
        if (this.subjFilters.semester) {
            filtered = filtered.filter(s => String(s.semester) === this.subjFilters.semester);
        }
        if (this.subjFilters.type === "lab") {
            filtered = filtered.filter(s => s.needs_lab);
        } else if (this.subjFilters.type === "theory") {
            filtered = filtered.filter(s => !s.needs_lab);
        }

        if (filtered.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted" style="padding:32px;">No subjects matched the active filters.</td></tr>`;
            return;
        }

        filtered.forEach(s => {
            const tr = document.createElement("tr");
            const typeBadge = s.needs_lab 
                ? `<span class="badge-tag" style="background:rgba(6,182,212,0.2); color:var(--cyan);"><i class="fa-solid fa-flask"></i> Laboratory</span>`
                : `<span class="badge-tag">Theory Lecture</span>`;

            tr.innerHTML = `
                <td><strong>${s.id}</strong></td>
                <td>${s.name}</td>
                <td><span class="badge-tag badge-cyan">${s.branch}</span></td>
                <td><span class="badge-pill">Sem ${s.semester || 5}</span></td>
                <td><strong>${s.weekly_hours}</strong> hrs/week</td>
                <td>${typeBadge}</td>
                <td>${s.consecutive_hours} ${s.consecutive_hours > 1 ? 'hrs Block' : 'hr'}</td>
                <td class="table-actions-cell">
                    <button class="btn-edit-outline" data-action="edit-subject" data-id="${s.id}" title="Edit course">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                    <button class="btn-danger-outline" data-action="del-subject" data-id="${s.id}" title="Delete course">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        tbody.querySelectorAll("[data-action='edit-subject']").forEach(btn => {
            btn.addEventListener("click", () => {
                const id = btn.getAttribute("data-id");
                this.openEditSubjectModal(id);
            });
        });

        tbody.querySelectorAll("[data-action='del-subject']").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = btn.getAttribute("data-id");
                if (!confirm(`Delete subject ${id}?`)) return;
                await fetch(`/api/subjects/${id}`, { method: "DELETE" });
                showToast(`Subject ${id} removed.`, "info");
                await loadAppData();
            });
        });
    },

    // =========================================================================
    // 4. ROOMS TABLE
    // =========================================================================
    renderRoomsTable() {
        const tbody = document.getElementById("rooms-table-body");
        if (!tbody) return;
        tbody.innerHTML = "";

        AppState.rooms.forEach(r => {
            const tr = document.createElement("tr");
            const typeBadge = r.is_lab
                ? `<span class="badge-tag" style="background:rgba(6,182,212,0.2); color:var(--cyan);"><i class="fa-solid fa-flask"></i> Computer / Lab</span>`
                : `<span class="badge-tag">Lecture Hall</span>`;

            tr.innerHTML = `
                <td><strong>${r.id}</strong></td>
                <td>${typeBadge}</td>
                <td>${r.capacity} seats</td>
                <td><span class="badge-tag">${r.branch}</span></td>
                <td class="table-actions-cell">
                    <button class="btn-edit-outline" data-action="edit-room" data-id="${r.id}" title="Edit room">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                    <button class="btn-danger-outline" data-action="del-room" data-id="${r.id}" title="Delete room">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        tbody.querySelectorAll("[data-action='edit-room']").forEach(btn => {
            btn.addEventListener("click", () => {
                const id = btn.getAttribute("data-id");
                const r = AppState.rooms.find(item => item.id === id);
                if (!r) return;
                const form = document.getElementById("form-room");
                form.reset();
                document.getElementById("input-r-mode").value = "edit";
                const idInput = document.getElementById("input-r-id");
                idInput.value = r.id;
                idInput.readOnly = true;
                document.getElementById("input-r-type").value = r.type || "regular";
                document.getElementById("input-r-capacity").value = r.capacity || 60;
                document.getElementById("input-r-branch").value = r.branch || "GENERAL";
                document.getElementById("modal-room-title").innerHTML = `<i class="fa-solid fa-pen-to-square text-cyan"></i> Edit Room: <strong>${r.id}</strong>`;
                openModal("modal-room");
            });
        });

        tbody.querySelectorAll("[data-action='del-room']").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = btn.getAttribute("data-id");
                if (!confirm(`Delete room ${id}?`)) return;
                await fetch(`/api/rooms/${id}`, { method: "DELETE" });
                showToast(`Room ${id} removed.`, "info");
                await loadAppData();
            });
        });
    },

    // =========================================================================
    // 5. SECTIONS TABLE
    // =========================================================================
    renderSectionsTable() {
        const tbody = document.getElementById("sections-table-body");
        if (!tbody) return;
        tbody.innerHTML = "";

        AppState.sections.forEach(sec => {
            const tr = document.createElement("tr");
            const subjTags = sec.subjects.map(s => `<span class="badge-tag">${s}</span>`).join(" ");
            
            const elecTags = sec.electives.map(eg => {
                const opts = eg.options.join(", ");
                return `<div style="margin:2px 0;"><span class="badge-pill"><i class="fa-solid fa-bolt"></i> ${eg.group}:</span> <small>${opts}</small></div>`;
            }).join("");

            tr.innerHTML = `
                <td><strong>${sec.id}</strong></td>
                <td><span class="badge-tag badge-cyan">${sec.branch}</span></td>
                <td>Semester ${sec.semester}</td>
                <td>${subjTags}</td>
                <td>${elecTags || '<span class="text-muted">—</span>'}</td>
                <td class="table-actions-cell">
                    <button class="btn-edit-outline" data-action="edit-section" data-id="${sec.id}" title="Edit section">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                    <button class="btn-danger-outline" data-action="del-section" data-id="${sec.id}" title="Delete section">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        tbody.querySelectorAll("[data-action='edit-section']").forEach(btn => {
            btn.addEventListener("click", () => {
                const id = btn.getAttribute("data-id");
                const sec = AppState.sections.find(item => item.id === id);
                if (!sec) return;
                const form = document.getElementById("form-section");
                form.reset();
                document.getElementById("input-sec-mode").value = "edit";
                const idInput = document.getElementById("input-sec-id");
                idInput.value = sec.id;
                idInput.readOnly = true;
                document.getElementById("input-sec-branch").value = sec.branch || "";
                document.getElementById("input-sec-semester").value = sec.semester || 5;
                document.getElementById("input-sec-subjects").value = (sec.subjects || []).join(", ");
                document.getElementById("input-sec-electives").value = JSON.stringify(sec.electives || [], null, 2);
                document.getElementById("modal-section-title").innerHTML = `<i class="fa-solid fa-pen-to-square text-cyan"></i> Edit Section: <strong>${sec.id}</strong>`;
                openModal("modal-section");
            });
        });

        tbody.querySelectorAll("[data-action='del-section']").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = btn.getAttribute("data-id");
                if (!confirm(`Delete section ${id}?`)) return;
                await fetch(`/api/sections/${id}`, { method: "DELETE" });
                showToast(`Section ${id} removed.`, "info");
                await loadAppData();
            });
        });
    },

    // =========================================================================
    // 6. AUTO SEMESTER DETECTION LISTENERS
    // =========================================================================
    bindAutoSemesterDetection() {
        // Department Hub Form
        const deptCodeInput = document.getElementById("dept-input-code");
        const deptSemIndicator = document.getElementById("dept-auto-sem-indicator");
        const deptSemText = document.getElementById("dept-detected-sem-text");
        const deptSemInput = document.getElementById("dept-input-sem");

        if (deptCodeInput && deptSemIndicator && deptSemText) {
            deptCodeInput.addEventListener("input", (e) => {
                const detected = extractSemesterFromCode(e.target.value);
                if (detected) {
                    deptSemText.innerText = `Semester ${detected}`;
                    deptSemIndicator.style.display = "inline-flex";
                    if (deptSemInput && !deptSemInput.value) {
                        deptSemInput.placeholder = `Auto (${detected})`;
                    }
                } else {
                    deptSemIndicator.style.display = "none";
                }
            });
        }

        // Modal Subject Form
        const modalCodeInput = document.getElementById("input-s-id");
        const modalSemIndicator = document.getElementById("modal-auto-sem-indicator");
        const modalSemText = document.getElementById("modal-detected-sem-text");
        const modalSemInput = document.getElementById("input-s-sem");

        if (modalCodeInput && modalSemIndicator && modalSemText) {
            modalCodeInput.addEventListener("input", (e) => {
                const detected = extractSemesterFromCode(e.target.value);
                if (detected) {
                    modalSemText.innerText = `Semester ${detected}`;
                    modalSemIndicator.style.display = "inline-flex";
                    if (modalSemInput && !modalSemInput.value) {
                        modalSemInput.placeholder = `Auto (${detected})`;
                    }
                } else {
                    modalSemIndicator.style.display = "none";
                }
            });
        }
    },

    // =========================================================================
    // 7. BIND ADD BUTTONS & VTU SYLLABUS SYNC
    // =========================================================================
    bindAddButtons() {
        document.getElementById("btn-add-teacher")?.addEventListener("click", () => {
            const form = document.getElementById("form-teacher");
            form.reset();
            document.getElementById("input-t-mode").value = "add";
            const idInput = document.getElementById("input-t-id");
            idInput.value = "";
            idInput.readOnly = false;
            document.getElementById("modal-teacher-title").innerText = "Add Faculty Member";
            openModal("modal-teacher");
        });

        document.getElementById("btn-add-subject")?.addEventListener("click", () => {
            const form = document.getElementById("form-subject");
            form.reset();
            document.getElementById("input-s-mode").value = "add";
            const idInput = document.getElementById("input-s-id");
            idInput.value = "";
            idInput.readOnly = false;
            document.getElementById("modal-auto-sem-indicator").style.display = "none";
            document.getElementById("modal-subject-title").innerText = "Add Course / Subject";
            openModal("modal-subject");
        });

        // VTU Import Buttons
        const handleVtuImport = async () => {
            if (!confirm("Sync and import the official VTU Syllabus across all engineering branches (CSE, ISE, AIML, ECE, EEE, ME, CV, Sciences)? Existing custom subjects will be preserved.")) return;
            try {
                const res = await fetch("/api/subjects/import-vtu", { method: "POST" });
                const json = await res.json();
                if (json.status === "success") {
                    showToast(json.message, "success");
                    await loadAppData();
                }
            } catch (err) {
                showToast("Failed to import VTU syllabus.", "error");
            }
        };

        document.getElementById("btn-import-vtu")?.addEventListener("click", handleVtuImport);
        document.getElementById("btn-sync-vtu-catalog")?.addEventListener("click", handleVtuImport);

        // Quick Create Section Button
        document.getElementById("btn-quick-create-section")?.addEventListener("click", async () => {
            const branch = AppState.activeDepartment || "CSE";
            const semester = AppState.activeSemester || 5;
            const sectionId = `${branch}-${semester}A`;

            if (!confirm(`Create Section ${sectionId} automatically with all core courses and electives for ${branch} Semester ${semester}?`)) return;

            try {
                const res = await fetch("/api/departments/quick-create-section", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ branch, semester, section_id: sectionId })
                });
                const json = await res.json();
                if (json.status === "success") {
                    showToast(json.message, "success");
                    await loadAppData();
                } else {
                    showToast(json.message || "Failed to create section.", "error");
                }
            } catch (err) {
                showToast("Error creating section from semester.", "error");
            }
        });

        document.getElementById("btn-add-room")?.addEventListener("click", () => {
            const form = document.getElementById("form-room");
            form.reset();
            document.getElementById("input-r-mode").value = "add";
            const idInput = document.getElementById("input-r-id");
            idInput.value = "";
            idInput.readOnly = false;
            document.getElementById("modal-room-title").innerText = "Add Room";
            openModal("modal-room");
        });

        document.getElementById("btn-add-section")?.addEventListener("click", () => {
            const form = document.getElementById("form-section");
            form.reset();
            document.getElementById("input-sec-mode").value = "add";
            const idInput = document.getElementById("input-sec-id");
            idInput.value = "";
            idInput.readOnly = false;
            document.getElementById("modal-section-title").innerText = "Add Section & Electives";
            openModal("modal-section");
        });
    },

    // =========================================================================
    // 8. FORM SUBMISSIONS
    // =========================================================================
    bindFormSubmissions() {
        // Department Hub Add Subject Form
        document.getElementById("form-dept-add-subject")?.addEventListener("submit", async (e) => {
            e.preventDefault();
            const id = document.getElementById("dept-input-code").value.trim().toUpperCase();
            const name = document.getElementById("dept-input-name").value.trim();
            const branch = document.getElementById("dept-input-branch").value.trim() || AppState.activeDepartment;
            
            let semester = parseInt(document.getElementById("dept-input-sem").value);
            if (!semester || isNaN(semester) || semester < 1 || semester > 8) {
                // Auto-detect from course code or default to active semester
                semester = extractSemesterFromCode(id) || AppState.activeSemester || 5;
            }

            const weekly_hours = parseInt(document.getElementById("dept-input-hours").value) || 4;
            const consecutive_hours = parseInt(document.getElementById("dept-input-consecutive").value) || 1;
            const needs_lab = document.getElementById("dept-input-lab").checked;

            const payload = { id, name, branch, semester, weekly_hours, needs_lab, consecutive_hours };

            try {
                const res = await fetch("/api/subjects", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const json = await res.json();
                if (json.status === "success") {
                    showToast(`Course ${id} added to ${branch} Semester ${semester}!`, "success");
                    document.getElementById("form-dept-add-subject").reset();
                    document.getElementById("dept-auto-sem-indicator").style.display = "none";
                    await loadAppData();
                } else {
                    showToast(json.message || "Failed to save subject.", "error");
                }
            } catch (err) {
                showToast("Network error saving subject.", "error");
            }
        });

        // Subject Modal Form
        document.getElementById("form-subject")?.addEventListener("submit", async (e) => {
            e.preventDefault();
            const id = document.getElementById("input-s-id").value.trim().toUpperCase();
            const name = document.getElementById("input-s-name").value.trim();
            const branch = document.getElementById("input-s-branch").value.trim().toUpperCase();
            
            let semester = parseInt(document.getElementById("input-s-sem").value);
            if (!semester || isNaN(semester) || semester < 1 || semester > 8) {
                semester = extractSemesterFromCode(id) || 5;
            }

            const weekly_hours = parseInt(document.getElementById("input-s-hours").value);
            const consecutive_hours = parseInt(document.getElementById("input-s-consecutive").value);
            const needs_lab = document.getElementById("input-s-lab").checked;

            const payload = { id, name, branch, semester, weekly_hours, needs_lab, consecutive_hours };

            const res = await fetch("/api/subjects", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (json.status === "success") {
                showToast(json.message, "success");
                closeModal("modal-subject");
                await loadAppData();
            } else {
                showToast(json.message || "Failed to save subject.", "error");
            }
        });

        // Teacher Form
        document.getElementById("form-teacher")?.addEventListener("submit", async (e) => {
            e.preventDefault();
            const id = document.getElementById("input-t-id").value.trim();
            const name = document.getElementById("input-t-name").value.trim();
            const branch = document.getElementById("input-t-branch").value.trim();
            const maxHours = parseInt(document.getElementById("input-t-max-hours").value);
            
            const rawSubjects = document.getElementById("input-t-subjects").value.split(",").map(s => s.trim()).filter(Boolean);
            const rawCross = document.getElementById("input-t-cross").value.split(",").map(s => s.trim()).filter(Boolean);
            
            const cross_branch_subjects = rawCross.map(item => {
                if (item.includes(":")) {
                    const [code, br] = item.split(":");
                    return { code: code.trim(), branch: br.trim() };
                }
                return { code: item, branch: "EXTERNAL" };
            });

            const payload = {
                id, name, branch,
                subjects: rawSubjects,
                cross_branch_subjects,
                max_hours_per_day: maxHours
            };

            const res = await fetch("/api/teachers", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (json.status === "success") {
                showToast(json.message, "success");
                closeModal("modal-teacher");
                await loadAppData();
            } else {
                showToast(json.message || "Failed to save teacher.", "error");
            }
        });

        // Room Form
        document.getElementById("form-room")?.addEventListener("submit", async (e) => {
            e.preventDefault();
            const id = document.getElementById("input-r-id").value.trim();
            const type = document.getElementById("input-r-type").value;
            const capacity = parseInt(document.getElementById("input-r-capacity").value);
            const branch = document.getElementById("input-r-branch").value.trim();

            const payload = { id, type, capacity, branch };

            const res = await fetch("/api/rooms", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (json.status === "success") {
                showToast(json.message, "success");
                closeModal("modal-room");
                await loadAppData();
            } else {
                showToast(json.message || "Failed to save room.", "error");
            }
        });

        // Section Form
        document.getElementById("form-section")?.addEventListener("submit", async (e) => {
            e.preventDefault();
            const id = document.getElementById("input-sec-id").value.trim();
            const branch = document.getElementById("input-sec-branch").value.trim();
            const semester = parseInt(document.getElementById("input-sec-semester").value);
            const rawSubjects = document.getElementById("input-sec-subjects").value.split(",").map(s => s.trim()).filter(Boolean);
            
            let electives = [];
            const electivesStr = document.getElementById("input-sec-electives").value.trim();
            if (electivesStr) {
                try {
                    electives = JSON.parse(electivesStr);
                } catch (err) {
                    showToast("Invalid JSON in Elective Groups.", "error");
                    return;
                }
            }

            const payload = { id, branch, semester, subjects: rawSubjects, electives };

            const res = await fetch("/api/sections", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (json.status === "success") {
                showToast(json.message, "success");
                closeModal("modal-section");
                await loadAppData();
            } else {
                showToast(json.message || "Failed to save section.", "error");
            }
        });
    },

    // =========================================================================
    // 9. SETTINGS FORM
    // =========================================================================
    populateSettingsForm() {
        const config = AppState.config || {};
        const days = config.days || ["Mon", "Tue", "Wed", "Thu", "Fri"];
        const checkboxes = document.querySelectorAll("#settings-days-checkboxes input");
        checkboxes.forEach(cb => {
            cb.checked = days.includes(cb.value);
        });

        const startTimeInput = document.getElementById("settings-start-time");
        const durationInput = document.getElementById("settings-period-duration");
        const periodsInput = document.getElementById("settings-periods-count");
        const shortBreakAfterInput = document.getElementById("settings-short-break-after");
        const shortBreakDurInput = document.getElementById("settings-short-break-duration");
        const lunchBreakAfterInput = document.getElementById("settings-lunch-break-after");
        const lunchBreakDurInput = document.getElementById("settings-lunch-break-duration");

        if (startTimeInput) startTimeInput.value = config.start_time || "09:00";
        if (durationInput) durationInput.value = config.period_duration || 55;
        if (periodsInput) periodsInput.value = config.periods_per_day || 7;
        if (shortBreakAfterInput) shortBreakAfterInput.value = config.short_break_after !== undefined ? config.short_break_after : 2;
        if (shortBreakDurInput) shortBreakDurInput.value = config.short_break_duration || 15;
        if (lunchBreakAfterInput) lunchBreakAfterInput.value = config.lunch_break_after !== undefined ? config.lunch_break_after : 4;
        if (lunchBreakDurInput) lunchBreakDurInput.value = config.lunch_break_duration || 50;

        this.renderTimeSlotsTable(config.time_slots || []);
    },

    renderTimeSlotsTable(slots) {
        const tbody = document.getElementById("time-slots-tbody");
        if (!tbody) return;
        tbody.innerHTML = "";

        slots.forEach((slot, idx) => {
            const tr = document.createElement("tr");
            const isBreak = slot.type === "break" || slot.type === "lunch";
            if (isBreak) tr.className = "break-row";

            let typeIcon = `<i class="fa-solid fa-graduation-cap text-indigo"></i>`;
            let typeLabel = "Teaching";
            if (slot.type === "lunch") {
                typeIcon = `<i class="fa-solid fa-utensils text-amber"></i>`;
                typeLabel = "Lunch Break";
            } else if (slot.type === "break") {
                typeIcon = `<i class="fa-solid fa-mug-hot text-amber"></i>`;
                typeLabel = "Short Break";
            }

            tr.innerHTML = `
                <td>${typeIcon} <strong>${typeLabel}</strong></td>
                <td><input type="text" class="time-slot-input" style="width:110px;" value="${slot.label || ''}" data-idx="${idx}" data-field="label"></td>
                <td><input type="time" class="time-slot-input" value="${slot.start_time || ''}" data-idx="${idx}" data-field="start_time"></td>
                <td><input type="time" class="time-slot-input" value="${slot.end_time || ''}" data-idx="${idx}" data-field="end_time"></td>
                <td><small class="text-muted">${slot.duration || ''} mins</small></td>
            `;
            tbody.appendChild(tr);
        });

        this.activeTimeSlots = JSON.parse(JSON.stringify(slots));

        tbody.querySelectorAll(".time-slot-input").forEach(input => {
            input.addEventListener("change", (e) => {
                const idx = parseInt(e.target.getAttribute("data-idx"));
                const field = e.target.getAttribute("data-field");
                if (this.activeTimeSlots && this.activeTimeSlots[idx]) {
                    this.activeTimeSlots[idx][field] = e.target.value;
                }
            });
        });
    },

    bindSettingsForm() {
        document.getElementById("btn-recalculate-slots")?.addEventListener("click", async () => {
            const startTime = document.getElementById("settings-start-time").value || "09:00";
            const duration = parseInt(document.getElementById("settings-period-duration").value) || 55;
            const periods = parseInt(document.getElementById("settings-periods-count").value) || 7;
            const shortAfter = parseInt(document.getElementById("settings-short-break-after").value) || 0;
            const shortDur = parseInt(document.getElementById("settings-short-break-duration").value) || 0;
            const lunchAfter = parseInt(document.getElementById("settings-lunch-break-after").value) || 0;
            const lunchDur = parseInt(document.getElementById("settings-lunch-break-duration").value) || 0;

            try {
                const res = await fetch("/api/config/preview-slots", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        start_time: startTime,
                        period_duration: duration,
                        periods_per_day: periods,
                        short_break_after: shortAfter,
                        short_break_duration: shortDur,
                        lunch_break_after: lunchAfter,
                        lunch_break_duration: lunchDur
                    })
                });
                const json = await res.json();
                if (json.status === "success") {
                    this.renderTimeSlotsTable(json.time_slots);
                    showToast("Period timings recalculated.", "info");
                }
            } catch (err) {
                showToast("Failed to recalculate timings.", "error");
            }
        });

        document.getElementById("btn-save-settings")?.addEventListener("click", async () => {
            const checkedDays = Array.from(
                document.querySelectorAll("#settings-days-checkboxes input:checked")
            ).map(cb => cb.value);

            if (checkedDays.length === 0) {
                showToast("Please select at least 1 working day.", "error");
                return;
            }

            const startTime = document.getElementById("settings-start-time").value || "09:00";
            const duration = parseInt(document.getElementById("settings-period-duration").value) || 55;
            const periods = parseInt(document.getElementById("settings-periods-count").value) || 7;
            const shortAfter = parseInt(document.getElementById("settings-short-break-after").value) || 0;
            const shortDur = parseInt(document.getElementById("settings-short-break-duration").value) || 0;
            const lunchAfter = parseInt(document.getElementById("settings-lunch-break-after").value) || 0;
            const lunchDur = parseInt(document.getElementById("settings-lunch-break-duration").value) || 0;

            const payload = {
                days: checkedDays,
                periods_per_day: periods,
                start_time: startTime,
                period_duration: duration,
                short_break_after: shortAfter,
                short_break_duration: shortDur,
                lunch_break_after: lunchAfter,
                lunch_break_duration: lunchDur,
                time_slots: this.activeTimeSlots
            };

            const res = await fetch("/api/config", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (json.status === "success") {
                showToast("Academic grid & period timings saved successfully!", "success");
                await loadAppData();
            } else {
                showToast(json.message || "Failed to save configuration.", "error");
            }
        });
    },

    openEditSubjectModal(id) {
        const s = AppState.subjects.find(item => item.id === id);
        if (!s) return;
        const form = document.getElementById("form-subject");
        form.reset();
        document.getElementById("input-s-mode").value = "edit";
        const idInput = document.getElementById("input-s-id");
        idInput.value = s.id;
        idInput.readOnly = true;
        document.getElementById("input-s-name").value = s.name || "";
        document.getElementById("input-s-branch").value = s.branch || "";
        document.getElementById("input-s-sem").value = s.semester || "";
        document.getElementById("input-s-hours").value = s.weekly_hours || 4;
        document.getElementById("input-s-consecutive").value = s.consecutive_hours || 1;
        document.getElementById("input-s-lab").checked = Boolean(s.needs_lab);
        document.getElementById("modal-auto-sem-indicator").style.display = "none";
        document.getElementById("modal-subject-title").innerHTML = `<i class="fa-solid fa-pen-to-square text-cyan"></i> Edit Course: <strong>${s.id}</strong>`;
        openModal("modal-subject");
    },

    bindImportModal() {
        let currentTargetEntity = "teachers";
        let selectedFile = null;

        const updateTemplateLinks = (entity) => {
            const btnCsv = document.getElementById("btn-download-template-csv");
            const btnExcel = document.getElementById("btn-download-template-excel");
            const desc = document.getElementById("import-template-desc");

            if (entity === "workbook") {
                if (btnCsv) btnCsv.style.display = "none";
                if (btnExcel) {
                    btnExcel.style.display = "inline-flex";
                    btnExcel.href = `/api/import/template/workbook?format=xlsx`;
                    btnExcel.innerHTML = `<i class="fa-solid fa-file-excel"></i> Download Multi-Sheet Workbook (.xlsx)`;
                }
                if (desc) desc.innerText = "Download complete template workbook with Teachers, Subjects, Rooms, and Sections sheets.";
            } else {
                if (btnCsv) {
                    btnCsv.style.display = "inline-flex";
                    btnCsv.href = `/api/import/template/${entity}?format=csv`;
                    btnCsv.innerHTML = `<i class="fa-solid fa-file-csv"></i> Download CSV Template`;
                }
                if (btnExcel) {
                    btnExcel.style.display = "inline-flex";
                    btnExcel.href = `/api/import/template/${entity}?format=excel`;
                    btnExcel.innerHTML = `<i class="fa-solid fa-file-excel"></i> Download Excel Template`;
                }
                if (desc) desc.innerText = `Download pre-formatted example file for ${entity} with sample rows and column definitions.`;
            }
        };

        const resetImportForm = () => {
            selectedFile = null;
            const fileInput = document.getElementById("import-file-input");
            if (fileInput) fileInput.value = "";
            const previewPill = document.getElementById("file-preview-pill");
            if (previewPill) previewPill.style.display = "none";
            const resultsCard = document.getElementById("import-results-card");
            if (resultsCard) resultsCard.style.display = "none";
            const submitBtn = document.getElementById("btn-submit-import");
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<i class="fa-solid fa-upload"></i> <span id="btn-import-text">Import Records</span>`;
            }
        };

        // Open modal from buttons
        document.querySelectorAll("[data-import-entity]").forEach(btn => {
            btn.addEventListener("click", () => {
                const entity = btn.getAttribute("data-import-entity") || "teachers";
                currentTargetEntity = entity;
                document.querySelectorAll(".entity-pill").forEach(p => {
                    p.classList.toggle("active", p.getAttribute("data-entity") === entity);
                });
                updateTemplateLinks(entity);
                resetImportForm();
                openModal("modal-import");
            });
        });

        document.getElementById("btn-top-import-data")?.addEventListener("click", () => {
            currentTargetEntity = "teachers";
            document.querySelectorAll(".entity-pill").forEach(p => {
                p.classList.toggle("active", p.getAttribute("data-entity") === "teachers");
            });
            updateTemplateLinks("teachers");
            resetImportForm();
            openModal("modal-import");
        });

        // Pill selector clicks
        document.querySelectorAll(".entity-pill").forEach(pill => {
            pill.addEventListener("click", () => {
                const entity = pill.getAttribute("data-entity");
                currentTargetEntity = entity;
                document.querySelectorAll(".entity-pill").forEach(p => p.classList.remove("active"));
                pill.classList.add("active");
                updateTemplateLinks(entity);
                resetImportForm();
            });
        });

        // File Selection & Drag-and-Drop
        const dropzone = document.getElementById("import-dropzone");
        const fileInput = document.getElementById("import-file-input");
        const browseBtn = document.getElementById("btn-browse-file");
        const previewPill = document.getElementById("file-preview-pill");
        const previewName = document.getElementById("file-preview-name");
        const previewSize = document.getElementById("file-preview-size");
        const removeFileBtn = document.getElementById("btn-remove-file");
        const submitBtn = document.getElementById("btn-submit-import");

        const setFile = (file) => {
            if (!file) return;
            selectedFile = file;
            if (previewName) previewName.innerText = file.name;
            if (previewSize) previewSize.innerText = (file.size / 1024).toFixed(1) + " KB";
            if (previewPill) previewPill.style.display = "inline-flex";
            if (submitBtn) submitBtn.disabled = false;
        };

        browseBtn?.addEventListener("click", (e) => {
            e.stopPropagation();
            fileInput?.click();
        });

        dropzone?.addEventListener("click", () => {
            fileInput?.click();
        });

        fileInput?.addEventListener("change", (e) => {
            if (e.target.files && e.target.files[0]) {
                setFile(e.target.files[0]);
            }
        });

        removeFileBtn?.addEventListener("click", (e) => {
            e.stopPropagation();
            resetImportForm();
        });

        ["dragenter", "dragover"].forEach(eventName => {
            dropzone?.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add("dropzone-active");
            });
        });

        ["dragleave", "drop"].forEach(eventName => {
            dropzone?.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove("dropzone-active");
            });
        });

        dropzone?.addEventListener("drop", (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove("dropzone-active");
            if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
                setFile(e.dataTransfer.files[0]);
            }
        });

        // Submit Import
        submitBtn?.addEventListener("click", async () => {
            if (!selectedFile) return;

            submitBtn.disabled = true;
            submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Processing...`;

            const formData = new FormData();
            formData.append("file", selectedFile);

            try {
                const res = await fetch(`/api/import/${currentTargetEntity}`, {
                    method: "POST",
                    body: formData
                });
                const json = await res.json();

                const resultsCard = document.getElementById("import-results-card");
                const resultsSummary = document.getElementById("import-results-summary");
                const errorsContainer = document.getElementById("import-errors-container");
                const errorsList = document.getElementById("import-errors-list");

                if (resultsCard) resultsCard.style.display = "block";

                if (json.status === "success") {
                    const added = json.added || 0;
                    const updated = json.updated || 0;
                    const total = json.total || (added + updated);
                    const errors = json.errors || [];

                    if (resultsSummary) {
                        resultsSummary.innerHTML = `
                            <span class="import-stat-chip chip-success"><i class="fa-solid fa-check"></i> <strong>${added}</strong> Added</span>
                            <span class="import-stat-chip chip-info"><i class="fa-solid fa-rotate"></i> <strong>${updated}</strong> Updated</span>
                            <span class="import-stat-chip"><i class="fa-solid fa-table-list"></i> <strong>${total}</strong> Processed</span>
                        `;
                    }

                    if (errors.length > 0) {
                        if (errorsContainer) errorsContainer.style.display = "block";
                        if (errorsList) errorsList.innerHTML = errors.map(e => `<li>${e}</li>`).join("");
                    } else {
                        if (errorsContainer) errorsContainer.style.display = "none";
                    }

                    showToast(`Successfully imported ${added + updated} records!`, "success");
                    await loadAppData();
                } else {
                    if (resultsSummary) {
                        resultsSummary.innerHTML = `<span class="import-stat-chip chip-warn"><i class="fa-solid fa-xmark"></i> ${json.message || "Import encountered an error."}</span>`;
                    }
                    if (errorsContainer) errorsContainer.style.display = "none";
                    showToast(json.message || "Import failed.", "error");
                }
            } catch (err) {
                console.error("Import error:", err);
                showToast("Network error uploading file.", "error");
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = `<i class="fa-solid fa-upload"></i> <span id="btn-import-text">Import Records</span>`;
            }
        });
    }
};

document.addEventListener("DOMContentLoaded", () => {
    window.DataManager.init();
});
