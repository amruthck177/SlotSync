// Global SlotSync Application State
const AppState = {
    teachers: [],
    subjects: [],
    rooms: [],
    sections: [],
    departments: [],
    lectures: [],
    activeDepartment: "CSE",
    activeSemester: 5,
    config: {
        days: ["Mon", "Tue", "Wed", "Thu", "Fri"],
        periods_per_day: 7,
        lunch_break_period: 4
    },
    timetable: [],
    stats: {},
    currentViewType: "section",
    currentTargetId: null,
    isGenerating: false
};

// Toast Notifications
function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let icon = "fa-circle-info text-indigo";
    if (type === "success") icon = "fa-circle-check text-emerald";
    if (type === "error") icon = "fa-circle-exclamation text-rose";
    
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(30px)";
        toast.style.transition = "all 0.3s ease";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Fetch all initial data
async function loadAppData() {
    try {
        const res = await fetch("/api/data");
        const json = await res.json();
        if (json.status === "success") {
            AppState.teachers = json.teachers;
            AppState.subjects = json.subjects;
            AppState.rooms = json.rooms;
            AppState.sections = json.sections;
            AppState.departments = json.departments || [];
            AppState.config = json.config;
            AppState.timetable = json.timetable;
            AppState.lectures = json.lectures || [];
            AppState.stats = json.stats;

            updateBadgeCounts();
            
            // Set default view target if null
            if (!AppState.currentTargetId && AppState.sections.length > 0) {
                AppState.currentTargetId = AppState.sections[0].id;
            }

            // Trigger components render
            if (window.TimetableRenderer) {
                window.TimetableRenderer.updateFilterOptions();
                window.TimetableRenderer.render();
            }
            if (window.DataManager) {
                window.DataManager.renderDepartmentsHub();
                window.DataManager.renderAllTables();
                window.DataManager.populateSettingsForm();
            }
            if (window.ManualAssist) {
                window.ManualAssist.populateDropdowns();
            }
            if (window.LecturesManager) {
                window.LecturesManager.populateDropdowns();
                window.LecturesManager.renderLectures();
            }
            if (window.DiagnosticsManager) {
                window.DiagnosticsManager.loadDiagnostics();
            }
            if (window.WorkloadHeatmap) {
                window.WorkloadHeatmap.render();
            }
        }
    } catch (err) {
        console.error("Error loading app data:", err);
        showToast("Failed to connect to backend server.", "error");
    }
}

function updateBadgeCounts() {
    const deptBadge = document.getElementById("badge-departments-count");
    if (deptBadge) deptBadge.innerText = AppState.departments.length;
    document.getElementById("badge-teachers-count").innerText = AppState.teachers.length;
    document.getElementById("badge-subjects-count").innerText = AppState.subjects.length;
    document.getElementById("badge-rooms-count").innerText = AppState.rooms.length;
    document.getElementById("badge-sections-count").innerText = AppState.sections.length;
    const lecBadge = document.getElementById("badge-lectures-count");
    if (lecBadge) lecBadge.innerText = AppState.lectures.length;

    const statusDesc = document.getElementById("status-engine-desc");
    if (AppState.timetable.length > 0) {
        statusDesc.innerText = `${AppState.timetable.length} Slots Clash-Free`;
    } else {
        statusDesc.innerText = "Ready to Generate";
    }
}

// Tab Switching
function initTabs() {
    const navItems = document.querySelectorAll(".nav-item");
    const panels = document.querySelectorAll(".tab-panel");
    const pageTitle = document.getElementById("page-title");
    const pageSubtitle = document.getElementById("page-subtitle");

    const titles = {
        "tab-timetable": {
            title: "Timetable Grid Explorer",
            subtitle: "Interactive clash-free schedule view with filter by Section, Teacher, or Room."
        },
        "tab-manual": {
            title: "Manual Assist (Permutation Mode)",
            subtitle: "Explore clash-free candidate slot layouts for individual teachers or sections."
        },
        "tab-departments": {
            title: "VTU Academic Departments & Curriculum Hub",
            subtitle: "Browse syllabus by department (CSE, ISE, AIML, ECE, EEE, ME, CV), explore semester-wise subjects, and manage curriculum."
        },
        "tab-teachers": {
            title: "Faculty & Teaching Assignments",
            subtitle: "Manage faculty members, departments, core subjects, and cross-branch qualifications."
        },
        "tab-subjects": {
            title: "Courses & VTU Curriculum",
            subtitle: "Define subjects, weekly credit hours, semester mappings, and laboratory room requirements."
        },
        "tab-lectures": {
            title: "Lecture Assignments",
            subtitle: "Manage teaching assignments — link teachers to subjects for specific sections with lecture details."
        },
        "tab-rooms": {
            title: "Classrooms & Laboratories",
            subtitle: "Manage available lecture halls, computer labs, and engineering workshops."
        },
        "tab-sections": {
            title: "Sections & Elective Groups",
            subtitle: "Configure student cohorts and synchronize parallel elective group offerings."
        },
        "tab-settings": {
            title: "Grid & Academic Settings",
            subtitle: "Configure weekly working days, periods per day, and lunch break periods."
        }
    };

    navItems.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");
            if (!targetTab) return;

            navItems.forEach(b => b.classList.remove("active"));
            panels.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            const panel = document.getElementById(targetTab);
            if (panel) panel.classList.add("active");

            if (titles[targetTab]) {
                pageTitle.innerText = titles[targetTab].title;
                pageSubtitle.innerText = titles[targetTab].subtitle;
            }
        });
    });
}

// Generate Timetable Handler
function initGenerateButton() {
    const btn = document.getElementById("btn-generate-timetable");
    const indicator = document.querySelector(".status-indicator");
    const statusDesc = document.getElementById("status-engine-desc");

    btn.addEventListener("click", async () => {
        if (AppState.isGenerating) return;
        AppState.isGenerating = true;

        btn.disabled = true;
        btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Solving (OR-Tools)...</span>`;
        indicator.className = "status-indicator busy";
        statusDesc.innerText = "OR-Tools CP-SAT Running...";

        try {
            const res = await fetch("/api/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ preserve_locked: true })
            });
            const json = await res.json();

            if (json.status === "success") {
                AppState.timetable = json.timetable;
                showToast(`Generated clash-free timetable in ${json.stats.time_taken_seconds}s!`, "success");
                indicator.className = "status-indicator ready";
                statusDesc.innerText = `${json.stats.num_entries} Slots Assigned`;
                if (window.TimetableRenderer) {
                    window.TimetableRenderer.render();
                }
                if (window.DiagnosticsManager) {
                    window.DiagnosticsManager.loadDiagnostics();
                }
                if (window.WorkloadHeatmap) {
                    window.WorkloadHeatmap.render();
                }
            } else {
                showToast(json.message || "Solver failed to find a valid schedule.", "error");
                indicator.className = "status-indicator error";
                statusDesc.innerText = "Solving Error";
            }
        } catch (err) {
            console.error("Generate error:", err);
            showToast("Network error while generating timetable.", "error");
            indicator.className = "status-indicator error";
        } finally {
            AppState.isGenerating = false;
            btn.disabled = false;
            btn.innerHTML = `<i class="fa-solid fa-microchip"></i> <span>Generate Timetable</span>`;
        }
    });
}

// Seed Demo Data
function initSeedButton() {
    const btn = document.getElementById("btn-seed-data");
    btn.addEventListener("click", async () => {
        if (!confirm("Reset database with the demo engineering college dataset (CSE, ISE, ECE)?")) return;
        try {
            const res = await fetch("/api/seed", { method: "POST" });
            const json = await res.json();
            if (json.status === "success") {
                showToast(json.message, "success");
                await loadAppData();
            }
        } catch (err) {
            showToast("Failed to reset demo data.", "error");
        }
    });
}

// Unlock All
function initUnlockButton() {
    const btn = document.getElementById("btn-unlock-all");
    btn.addEventListener("click", async () => {
        try {
            const res = await fetch("/api/timetable/unlock-all", { method: "POST" });
            const json = await res.json();
            if (json.status === "success") {
                showToast("All slots unpinned.", "info");
                await loadAppData();
            }
        } catch (err) {
            showToast("Error unpinning slots.", "error");
        }
    });
}

// Export Dropdown & Print
function initExportMenu() {
    const btn = document.getElementById("btn-export-menu");
    const dropdown = document.querySelector(".dropdown-export");
    const printBtn = document.getElementById("export-print-btn");

    btn.addEventListener("click", (e) => {
        e.stopPropagation();
        dropdown.classList.toggle("open");
    });

    document.addEventListener("click", () => {
        dropdown.classList.remove("open");
    });

    if (printBtn) {
        printBtn.addEventListener("click", () => {
            window.print();
        });
    }
}

// Modals Helper
function initModals() {
    document.querySelectorAll("[data-close]").forEach(btn => {
        btn.addEventListener("click", () => {
            const modalId = btn.getAttribute("data-close");
            const modal = document.getElementById(modalId);
            if (modal) modal.classList.remove("open");
        });
    });

    document.querySelectorAll(".modal-overlay").forEach(overlay => {
        overlay.addEventListener("click", (e) => {
            if (e.target === overlay) overlay.classList.remove("open");
        });
    });
}

function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.add("open");
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove("open");
}

// Theme Manager (Dark / Light Mode)
const ThemeManager = {
    theme: "dark",

    init() {
        const saved = localStorage.getItem("slotsync-theme");
        if (saved) {
            this.theme = saved;
        } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) {
            this.theme = "light";
        }
        this.applyTheme(this.theme);

        const toggleBtn = document.getElementById("btn-theme-toggle");
        if (toggleBtn) {
            toggleBtn.addEventListener("click", () => {
                this.toggleTheme();
            });
        }
    },

    toggleTheme() {
        this.theme = this.theme === "dark" ? "light" : "dark";
        localStorage.setItem("slotsync-theme", this.theme);
        this.applyTheme(this.theme);
        showToast(`Switched to ${this.theme === "light" ? "Light" : "Dark"} Mode`, "info");
    },

    applyTheme(theme) {
        const body = document.body;
        const label = document.getElementById("theme-label-text");
        const icon = document.getElementById("theme-toggle-icon");

        if (theme === "light") {
            body.classList.remove("dark-mode");
            body.classList.add("light-mode");
            if (label) label.textContent = "Dark Mode";
            if (icon) icon.className = "fa-solid fa-moon";
        } else {
            body.classList.remove("light-mode");
            body.classList.add("dark-mode");
            if (label) label.textContent = "Light Mode";
            if (icon) icon.className = "fa-solid fa-sun";
        }
    }
};

// Boot
document.addEventListener("DOMContentLoaded", () => {
    ThemeManager.init();
    initTabs();
    initGenerateButton();
    initSeedButton();
    initUnlockButton();
    initExportMenu();
    initModals();
    if (window.LecturesManager) {
        window.LecturesManager.init();
    }
    if (window.DiagnosticsManager) {
        window.DiagnosticsManager.init();
    }
    if (window.WorkloadHeatmap) {
        window.WorkloadHeatmap.init();
    }
    loadAppData();
});

