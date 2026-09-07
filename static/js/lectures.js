// Lectures Manager — Teaching Assignments (Subject + Teacher + Section)
window.LecturesManager = {
    filters: {
        search: "",
        branch: "",
        semester: ""
    },

    init() {
        this.bindForm();
        this.bindFilters();
        this.bindDropdownCascade();
    },

    // =========================================================================
    // POPULATE DROPDOWNS
    // =========================================================================
    populateDropdowns() {
        // Sections dropdown
        const secSelect = document.getElementById("lec-section-select");
        if (secSelect) {
            const currentVal = secSelect.value;
            secSelect.innerHTML = `<option value="">-- Select Section --</option>`;
            AppState.sections.forEach(sec => {
                secSelect.innerHTML += `<option value="${sec.id}">${sec.id} (${sec.branch} Sem ${sec.semester})</option>`;
            });
            if (currentVal) secSelect.value = currentVal;
        }

        // Subjects dropdown (all subjects initially)
        this.refreshSubjectsDropdown();

        // Teachers dropdown (all teachers initially)
        this.refreshTeachersDropdown();

        // Filter dropdowns — department
        const filterBranch = document.getElementById("filter-lec-branch");
        if (filterBranch) {
            const curVal = filterBranch.value;
            filterBranch.innerHTML = `<option value="">All Departments</option>`;
            const branches = [...new Set(AppState.subjects.map(s => s.branch))].sort();
            branches.forEach(b => {
                filterBranch.innerHTML += `<option value="${b}">${b}</option>`;
            });
            if (curVal) filterBranch.value = curVal;
        }
    },

    refreshSubjectsDropdown(branchFilter) {
        const subjSelect = document.getElementById("lec-subject-select");
        if (!subjSelect) return;
        subjSelect.innerHTML = `<option value="">-- Select Subject --</option>`;

        let subjects = AppState.subjects;
        if (branchFilter) {
            subjects = subjects.filter(s => s.branch === branchFilter);
        }
        subjects.forEach(s => {
            const labTag = s.needs_lab ? " 🧪 Lab" : "";
            subjSelect.innerHTML += `<option value="${s.id}">${s.id} — ${s.name}${labTag} (${s.weekly_hours}hrs)</option>`;
        });
    },

    refreshTeachersDropdown(subjectId) {
        const teacherSelect = document.getElementById("lec-teacher-select");
        const hint = document.getElementById("lec-teacher-hint");
        if (!teacherSelect) return;

        teacherSelect.innerHTML = `<option value="">-- Select Teacher --</option>`;

        let teachers = AppState.teachers;
        if (subjectId) {
            // Filter to teachers who can teach this subject
            teachers = teachers.filter(t => {
                const ownSubjects = t.subjects || [];
                const crossSubjects = (t.cross_branch_subjects || []).map(cb =>
                    typeof cb === "string" ? cb : (cb.code || "")
                );
                return ownSubjects.includes(subjectId) || crossSubjects.includes(subjectId);
            });

            if (hint) {
                if (teachers.length > 0) {
                    hint.innerText = `${teachers.length} teacher(s) qualified for ${subjectId}.`;
                    hint.style.color = "var(--accent-emerald)";
                } else {
                    hint.innerText = `No teachers found for ${subjectId}. Showing all teachers.`;
                    hint.style.color = "var(--accent-rose)";
                    teachers = AppState.teachers; // Fallback to all
                }
            }
        } else {
            if (hint) {
                hint.innerText = "Showing teachers qualified for selected subject.";
                hint.style.color = "";
            }
        }

        teachers.forEach(t => {
            teacherSelect.innerHTML += `<option value="${t.id}">${t.id} — ${t.name} (${t.branch})</option>`;
        });
    },

    // =========================================================================
    // CASCADING DROPDOWNS
    // =========================================================================
    bindDropdownCascade() {
        // When section changes, filter subjects to that branch
        document.getElementById("lec-section-select")?.addEventListener("change", (e) => {
            const sectionId = e.target.value;
            const section = AppState.sections.find(s => s.id === sectionId);
            if (section) {
                this.refreshSubjectsDropdown(section.branch);
                // Auto-set preferred room type
            } else {
                this.refreshSubjectsDropdown(); // Show all
            }
            // Reset teacher dropdown
            this.refreshTeachersDropdown();
        });

        // When subject changes, filter teachers who can teach it
        document.getElementById("lec-subject-select")?.addEventListener("change", (e) => {
            const subjectId = e.target.value;
            this.refreshTeachersDropdown(subjectId);

            // Auto-set preferred room type based on subject
            if (subjectId) {
                const subj = AppState.subjects.find(s => s.id === subjectId);
                if (subj) {
                    const roomTypeSelect = document.getElementById("lec-room-type");
                    if (roomTypeSelect) {
                        roomTypeSelect.value = subj.needs_lab ? "lab" : "regular";
                    }
                    const creditsInput = document.getElementById("lec-credits");
                    if (creditsInput) {
                        creditsInput.value = subj.weekly_hours || 4;
                    }
                }
            }
        });
    },

    // =========================================================================
    // RENDER LECTURE CARDS
    // =========================================================================
    renderLectures() {
        const container = document.getElementById("lectures-cards-container");
        const badge = document.getElementById("lectures-total-badge");
        if (!container) return;

        let lectures = AppState.lectures || [];

        // Apply filters
        if (this.filters.search) {
            const q = this.filters.search.toLowerCase();
            lectures = lectures.filter(l =>
                l.subject_id.toLowerCase().includes(q) ||
                l.subject_name.toLowerCase().includes(q) ||
                l.teacher_id.toLowerCase().includes(q) ||
                l.teacher_name.toLowerCase().includes(q) ||
                l.section_id.toLowerCase().includes(q) ||
                l.description.toLowerCase().includes(q)
            );
        }
        if (this.filters.branch) {
            lectures = lectures.filter(l => l.subject_branch === this.filters.branch || l.section_branch === this.filters.branch);
        }
        if (this.filters.semester) {
            const sem = parseInt(this.filters.semester);
            lectures = lectures.filter(l => l.semester === sem || l.section_semester === sem);
        }

        if (badge) badge.innerText = `${lectures.length} Lecture${lectures.length !== 1 ? "s" : ""}`;

        if (lectures.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-chalkboard"></i>
                    <h4>No Lecture Assignments Found</h4>
                    <p>${this.filters.search || this.filters.branch || this.filters.semester
                        ? "Try adjusting the filters above."
                        : "Use the form on the left to assign teachers to subjects for specific sections."
                    }</p>
                </div>
            `;
            return;
        }

        container.innerHTML = "";
        lectures.forEach(lec => {
            const card = document.createElement("div");
            card.className = `lecture-card ${lec.needs_lab ? "lecture-card-lab" : ""} ${lec.is_tutorial ? "lecture-card-tutorial" : ""}`;

            const roomIcon = lec.preferred_room_type === "lab"
                ? '<i class="fa-solid fa-flask text-cyan"></i> Lab'
                : '<i class="fa-solid fa-chalkboard text-indigo"></i> Lecture Hall';

            const tutorialBadge = lec.is_tutorial
                ? '<span class="badge-tag badge-amber"><i class="fa-solid fa-pen-ruler"></i> Tutorial</span>'
                : "";

            const labBadge = lec.needs_lab
                ? '<span class="badge-tag badge-cyan"><i class="fa-solid fa-flask"></i> Lab</span>'
                : "";

            card.innerHTML = `
                <div class="lecture-card-top">
                    <div class="lecture-card-subject">
                        <span class="lecture-code">${lec.subject_id}</span>
                        <span class="lecture-name">${lec.subject_name}</span>
                    </div>
                    <button class="btn-danger-outline btn-sm" data-action="del-lecture" data-id="${lec.id}" title="Remove lecture assignment">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
                <div class="lecture-card-body">
                    <div class="lecture-detail-row">
                        <i class="fa-solid fa-user-tie text-indigo"></i>
                        <span><strong>${lec.teacher_name}</strong> <small class="text-muted">(${lec.teacher_id})</small></span>
                    </div>
                    <div class="lecture-detail-row">
                        <i class="fa-solid fa-users-rectangle text-purple"></i>
                        <span>Section <strong>${lec.section_id}</strong></span>
                    </div>
                    <div class="lecture-detail-row">
                        <i class="fa-solid fa-clock text-amber"></i>
                        <span>${lec.weekly_hours} hrs/week &bull; ${lec.credits} credits</span>
                    </div>
                    <div class="lecture-detail-row">
                        ${roomIcon}
                    </div>
                    ${lec.description ? `<div class="lecture-description">${lec.description}</div>` : ""}
                </div>
                <div class="lecture-card-footer">
                    <span class="badge-tag badge-${getBranchColor(lec.subject_branch)}">${lec.subject_branch}</span>
                    <span class="badge-tag">Sem ${lec.semester}</span>
                    ${labBadge}
                    ${tutorialBadge}
                </div>
            `;

            container.appendChild(card);
        });

        // Bind delete
        container.querySelectorAll("[data-action='del-lecture']").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = btn.getAttribute("data-id");
                if (!confirm("Remove this lecture assignment?")) return;
                try {
                    const res = await fetch(`/api/lectures/${id}`, { method: "DELETE" });
                    const json = await res.json();
                    if (json.status === "success") {
                        showToast(json.message, "info");
                        await loadAppData();
                    }
                } catch (err) {
                    showToast("Error removing lecture.", "error");
                }
            });
        });
    },

    // =========================================================================
    // FORM SUBMISSION
    // =========================================================================
    bindForm() {
        document.getElementById("form-lecture")?.addEventListener("submit", async (e) => {
            e.preventDefault();

            const sectionId = document.getElementById("lec-section-select").value;
            const subjectId = document.getElementById("lec-subject-select").value;
            const teacherId = document.getElementById("lec-teacher-select").value;
            const description = document.getElementById("lec-description").value.trim();
            const credits = parseInt(document.getElementById("lec-credits").value) || 4;
            const preferredRoomType = document.getElementById("lec-room-type").value;
            const isTutorial = document.getElementById("lec-is-tutorial").checked;

            if (!sectionId || !subjectId || !teacherId) {
                showToast("Please select Section, Subject, and Teacher.", "error");
                return;
            }

            // Check for duplicate
            const existing = (AppState.lectures || []).find(l =>
                l.section_id === sectionId && l.subject_id === subjectId && l.teacher_id === teacherId
            );
            if (existing) {
                showToast("This lecture assignment already exists.", "error");
                return;
            }

            try {
                const res = await fetch("/api/lectures", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        subject_id: subjectId,
                        teacher_id: teacherId,
                        section_id: sectionId,
                        description,
                        credits,
                        preferred_room_type: preferredRoomType,
                        is_tutorial: isTutorial
                    })
                });
                const json = await res.json();
                if (json.status === "success") {
                    showToast(json.message, "success");
                    document.getElementById("form-lecture").reset();
                    await loadAppData();
                } else {
                    showToast(json.message || "Failed to save lecture.", "error");
                }
            } catch (err) {
                showToast("Network error saving lecture.", "error");
            }
        });
    },

    // =========================================================================
    // FILTERS
    // =========================================================================
    bindFilters() {
        document.getElementById("filter-lec-search")?.addEventListener("input", (e) => {
            this.filters.search = e.target.value;
            this.renderLectures();
        });
        document.getElementById("filter-lec-branch")?.addEventListener("change", (e) => {
            this.filters.branch = e.target.value;
            this.renderLectures();
        });
        document.getElementById("filter-lec-sem")?.addEventListener("change", (e) => {
            this.filters.semester = e.target.value;
            this.renderLectures();
        });
    }
};

// Helper for branch color mapping
function getBranchColor(branch) {
    const map = {
        "CSE": "indigo",
        "ISE": "cyan",
        "AIML": "purple",
        "ECE": "emerald",
        "EEE": "amber",
        "ME": "rose",
        "CV": "orange"
    };
    return map[branch] || "cyan";
}
