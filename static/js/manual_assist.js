// Manual Assist (Permutation & Combination Patch Mode)
window.ManualAssist = {
    init() {
        const teacherSelect = document.getElementById("manual-teacher-select");
        const sectionSelect = document.getElementById("manual-section-select");
        const calcBtn = document.getElementById("btn-calc-permutations");

        teacherSelect?.addEventListener("change", () => this.updateSubjectDropdown());
        sectionSelect?.addEventListener("change", () => this.updateSubjectDropdown());

        calcBtn?.addEventListener("click", () => this.calculateCandidates());
    },

    populateDropdowns() {
        const teacherSelect = document.getElementById("manual-teacher-select");
        const sectionSelect = document.getElementById("manual-section-select");
        if (!teacherSelect || !sectionSelect) return;

        // Populate Teachers
        const currentTeacherVal = teacherSelect.value;
        teacherSelect.innerHTML = `<option value="">-- Choose Teacher --</option>`;
        AppState.teachers.forEach(t => {
            const opt = document.createElement("option");
            opt.value = t.id;
            opt.textContent = `${t.id} - ${t.name} (${t.branch})`;
            teacherSelect.appendChild(opt);
        });
        if (currentTeacherVal) teacherSelect.value = currentTeacherVal;

        // Populate Sections
        const currentSectionVal = sectionSelect.value;
        sectionSelect.innerHTML = `<option value="">-- Choose Section --</option>`;
        AppState.sections.forEach(s => {
            const opt = document.createElement("option");
            opt.value = s.id;
            opt.textContent = `${s.id} (${s.branch})`;
            sectionSelect.appendChild(opt);
        });
        if (currentSectionVal) sectionSelect.value = currentSectionVal;

        this.updateSubjectDropdown();
    },

    updateSubjectDropdown() {
        const teacherSelect = document.getElementById("manual-teacher-select");
        const sectionSelect = document.getElementById("manual-section-select");
        const subjectSelect = document.getElementById("manual-subject-select");
        if (!subjectSelect) return;

        const teacherId = teacherSelect?.value;
        const sectionId = sectionSelect?.value;

        subjectSelect.innerHTML = `<option value="">-- Choose Subject --</option>`;
        if (!teacherId || !sectionId) return;

        const teacher = AppState.teachers.find(t => t.id === teacherId);
        const section = AppState.sections.find(s => s.id === sectionId);

        if (!teacher || !section) return;

        // Find intersection of teacher's qualified subjects and section's required subjects (including electives)
        const secSubjList = [...section.subjects];
        section.electives.forEach(eg => secSubjList.push(...eg.options));

        const qualifiedTeacherCodes = [
            ...teacher.subjects,
            ...teacher.cross_branch_subjects.map(cb => typeof cb === "object" ? cb.code : cb)
        ];

        const matchCodes = secSubjList.filter(code => qualifiedTeacherCodes.includes(code));

        matchCodes.forEach(code => {
            const subj = AppState.subjects.find(s => s.id === code);
            const opt = document.createElement("option");
            opt.value = code;
            opt.textContent = subj ? `${subj.id} - ${subj.name} (${subj.weekly_hours} hrs)` : code;
            subjectSelect.appendChild(opt);
        });
    },

    async calculateCandidates() {
        const teacherId = document.getElementById("manual-teacher-select")?.value;
        const sectionId = document.getElementById("manual-section-select")?.value;
        const subjectId = document.getElementById("manual-subject-select")?.value;
        const container = document.getElementById("candidates-container");
        const countBadge = document.getElementById("candidate-count-badge");
        const calcBtn = document.getElementById("btn-calc-permutations");

        if (!teacherId || !sectionId || !subjectId) {
            showToast("Please select Teacher, Section, and Subject.", "error");
            return;
        }

        calcBtn.disabled = true;
        calcBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Calculating...`;
        container.innerHTML = `<div class="empty-state"><i class="fa-solid fa-gear fa-spin"></i><h4>Evaluating Permutations...</h4></div>`;

        try {
            const res = await fetch("/api/manual-assist/candidates", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    teacher_id: teacherId,
                    section_id: sectionId,
                    subject_id: subjectId
                })
            });
            const json = await res.json();

            if (json.status === "success" && json.options && json.options.length > 0) {
                countBadge.innerText = `${json.options.length} Options`;
                this.renderCandidatesList(json.options, container);
            } else {
                countBadge.innerText = "0 Found";
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fa-solid fa-triangle-exclamation text-amber"></i>
                        <h4>No Clash-Free Permutations Found</h4>
                        <p>No clash-free slot combination exists for this combination under current locked constraints.</p>
                    </div>
                `;
            }
        } catch (err) {
            console.error("Candidates error:", err);
            showToast("Failed to calculate permutations.", "error");
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-circle-exclamation text-rose"></i>
                    <h4>Calculation Error</h4>
                    <p>Could not connect to permutation engine.</p>
                </div>
            `;
        } finally {
            calcBtn.disabled = false;
            calcBtn.innerHTML = `<i class="fa-solid fa-calculator"></i> Calculate Valid Combinations`;
        }
    },

    renderCandidatesList(options, container) {
        container.innerHTML = "";

        options.forEach((opt, idx) => {
            const card = document.createElement("div");
            card.className = "candidate-card";

            const slotPills = opt.slots.map(s => `
                <span class="slot-pill"><i class="fa-regular fa-clock"></i> ${s.day} Period ${s.period} &bull; ${s.room_id}</span>
            `).join("");

            card.innerHTML = `
                <div class="candidate-info">
                    <h4>Option #${idx + 1} <span style="font-size:12px; color:var(--emerald); font-weight:500;">(Score: ${opt.score})</span></h4>
                    <p style="font-size:12px; color:var(--text-muted);">${opt.description}</p>
                    <div class="candidate-slots-pills">${slotPills}</div>
                </div>
                <button class="btn-apply-candidate" data-index="${idx}">
                    <i class="fa-solid fa-thumbtack"></i> Pin & Re-Solve
                </button>
            `;

            card.querySelector(".btn-apply-candidate").addEventListener("click", () => {
                this.applyCandidateOption(opt);
            });

            container.appendChild(card);
        });
    },

    async applyCandidateOption(option) {
        if (!confirm("Pin this slot arrangement and re-solve the remaining timetable around it?")) return;

        showToast("Applying arrangement & re-solving remaining slots...", "info");

        try {
            const res = await fetch("/api/manual-assist/apply", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    slots: option.slots,
                    resolve_remainder: true
                })
            });
            const json = await res.json();

            if (json.status === "success") {
                showToast(json.message, "success");
                await loadAppData();

                // Switch to Timetable tab
                document.getElementById("nav-timetable")?.click();
            } else {
                showToast(json.message || "Failed to re-solve timetable.", "error");
            }
        } catch (err) {
            console.error("Apply candidate error:", err);
            showToast("Network error applying candidate.", "error");
        }
    }
};

document.addEventListener("DOMContentLoaded", () => {
    window.ManualAssist.init();
});
