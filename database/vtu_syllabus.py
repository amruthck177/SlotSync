"""
VTU (Visvesvaraya Technological University) Syllabus Subjects Database.
Covers major engineering branches across semesters (1st Year Common, CSE, ISE, AIML, ECE, EEE, ME, CV).
Deduplicated by subject code.
"""

from typing import List, Dict, Any

VTU_SYLLABUS_SUBJECTS: List[Dict[str, Any]] = [
    # ==========================================
    # 1. COMMON / FIRST YEAR (Physics & Chemistry Cycles)
    # ==========================================
    {"id": "21MAT11", "name": "Calculus and Linear Algebra", "branch": "MATHEMATICS", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21MAT21", "name": "Advanced Calculus and Numerical Methods", "branch": "MATHEMATICS", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21PHY12", "name": "Applied Physics for Engineers", "branch": "PHYSICS", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21PHYL16", "name": "Engineering Physics Laboratory", "branch": "PHYSICS", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21CHE12", "name": "Applied Chemistry for Engineers", "branch": "CHEMISTRY", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CHEL16", "name": "Engineering Chemistry Laboratory", "branch": "CHEMISTRY", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21PSP13", "name": "Problem Solving through Programming (C)", "branch": "CSE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CPL17", "name": "C Programming Laboratory", "branch": "CSE", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21ELE14", "name": "Basic Electrical Engineering", "branch": "EEE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ELN14", "name": "Basic Electronics & Communication", "branch": "ECE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EME15", "name": "Elements of Mechanical Engineering", "branch": "ME", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CIV14", "name": "Elements of Civil Engineering & Mechanics", "branch": "CV", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EGH18", "name": "Professional Writing Skills in English", "branch": "HUMANITIES", "weekly_hours": 2, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21IDT19", "name": "Innovation and Design Thinking", "branch": "GENERAL", "weekly_hours": 2, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CIP29", "name": "Constitution of India & Professional Ethics", "branch": "HUMANITIES", "weekly_hours": 2, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EVS39", "name": "Environmental Studies", "branch": "GENERAL", "weekly_hours": 2, "needs_lab": False, "consecutive_hours": 1},

    # ==========================================
    # 2. COMPUTER SCIENCE & ENGINEERING (CSE)
    # ==========================================
    {"id": "21MAT31", "name": "Transform Calculus, Fourier Series & Numerical Tech", "branch": "MATHEMATICS", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CS32", "name": "Data Structures and Applications", "branch": "CSE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CS33", "name": "Analog and Digital Electronics", "branch": "CSE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CS34", "name": "Computer Organization and Architecture", "branch": "CSE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CSL35", "name": "Data Structures Laboratory", "branch": "CSE", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21CS42", "name": "Design and Analysis of Algorithms", "branch": "CSE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CS43", "name": "Microcontrollers and Embedded Systems", "branch": "CSE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CS44", "name": "Operating Systems", "branch": "CSE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CSL46", "name": "Algorithms Laboratory", "branch": "CSE", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21CS51", "name": "Automata Theory and Computability", "branch": "CSE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CS52", "name": "Computer Networks", "branch": "CSE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CS53", "name": "Database Management Systems", "branch": "CSE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CS54", "name": "Artificial Intelligence & Machine Learning", "branch": "CSE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CSL55", "name": "DBMS and Networks Laboratory", "branch": "CSE", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21CSE561", "name": "Cloud Computing (Elective)", "branch": "CSE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CSE562", "name": "Cyber Security and Cyber Laws (Elective)", "branch": "CSE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CSE563", "name": "Software Architecture and Design Patterns (Elective)", "branch": "CSE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CS61", "name": "Software Engineering & Project Management", "branch": "CSE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CS62", "name": "Full Stack Web Development", "branch": "CSE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CSL66", "name": "Full Stack Development Laboratory", "branch": "CSE", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21CS71", "name": "Cryptography & Network Security", "branch": "CSE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CS72", "name": "Big Data Analytics", "branch": "CSE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CSL76", "name": "Big Data & Security Laboratory", "branch": "CSE", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},

    # ==========================================
    # 3. INFORMATION SCIENCE & ENGINEERING (ISE)
    # ==========================================
    {"id": "21IS51", "name": "File Structures and Storage Systems", "branch": "ISE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21IS52", "name": "Software Engineering Methodologies", "branch": "ISE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21IS53", "name": "Web Technology and Applications", "branch": "ISE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ISL55", "name": "Web Technologies & File Structures Lab", "branch": "ISE", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21ISE561", "name": "DevOps & Cloud Infrastructure (Elective)", "branch": "ISE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ISE562", "name": "Data Mining & Warehousing (Elective)", "branch": "ISE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21IS61", "name": "Advanced Data Structures & Algorithms", "branch": "ISE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21IS62", "name": "Mobile Application Development", "branch": "ISE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ISL66", "name": "Mobile Application Development Lab", "branch": "ISE", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},

    # ==========================================
    # 4. ARTIFICIAL INTELLIGENCE & MACHINE LEARNING (AIML)
    # ==========================================
    {"id": "21AI51", "name": "Deep Learning Techniques", "branch": "AIML", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21AI52", "name": "Natural Language Processing", "branch": "AIML", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21AI53", "name": "Knowledge Representation and Reasoning", "branch": "AIML", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21AIL54", "name": "Deep Learning & AI Laboratory", "branch": "AIML", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21AIE551", "name": "Computer Vision & Image Processing (Elective)", "branch": "AIML", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21AIE552", "name": "Reinforcement Learning (Elective)", "branch": "AIML", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21AI61", "name": "Generative AI and LLMs", "branch": "AIML", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21AI62", "name": "Robotics and Intelligent Systems", "branch": "AIML", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21AIL66", "name": "Generative AI & Robotics Lab", "branch": "AIML", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},

    # ==========================================
    # 5. ELECTRONICS & COMMUNICATION ENGINEERING (ECE)
    # ==========================================
    {"id": "21EC32", "name": "Digital System Design using Verilog", "branch": "ECE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EC33", "name": "Electronic Principles and Circuits", "branch": "ECE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EC34", "name": "Network Analysis and Synthesis", "branch": "ECE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ECL35", "name": "Analog & Digital Electronics Lab", "branch": "ECE", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21EC42", "name": "Signals and Systems", "branch": "ECE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EC43", "name": "Communication Theory", "branch": "ECE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EC44", "name": "Linear Integrated Circuits and Applications", "branch": "ECE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ECL46", "name": "LIC & Communication Theory Lab", "branch": "ECE", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21EC51", "name": "Digital Signal Processing", "branch": "ECE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EC52", "name": "Principles of Communication Systems", "branch": "ECE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EC53", "name": "Control Systems Engineering", "branch": "ECE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EC54", "name": "Digital Communication", "branch": "ECE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ECL55", "name": "DSP and Digital Communication Lab", "branch": "ECE", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21ECE561", "name": "VLSI Design & Technology (Elective)", "branch": "ECE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ECE562", "name": "Micro Electro Mechanical Systems (Elective)", "branch": "ECE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ECE563", "name": "Biomedical Signal Processing (Elective)", "branch": "ECE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EC61", "name": "Embedded System Design & IoT", "branch": "ECE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EC62", "name": "Microwave and Antenna Theory", "branch": "ECE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ECL66", "name": "Embedded Systems & IoT Lab", "branch": "ECE", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},

    # ==========================================
    # 6. ELECTRICAL & ELECTRONICS ENGINEERING (EEE)
    # ==========================================
    {"id": "21EE32", "name": "Electric Circuit Analysis", "branch": "EEE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EE33", "name": "Transformers and Generators", "branch": "EEE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EE34", "name": "Analog Electronic Circuits", "branch": "EEE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EEL35", "name": "Electrical Machines Laboratory - I", "branch": "EEE", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21EE42", "name": "Transmission and Distribution", "branch": "EEE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EE43", "name": "Electric Motors and Drives", "branch": "EEE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EE44", "name": "Electromagnetic Field Theory", "branch": "EEE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EE51", "name": "Power System Analysis", "branch": "EEE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EE52", "name": "Power Electronics & Applications", "branch": "EEE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EE53", "name": "Electrical Machines - II", "branch": "EEE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EEL55", "name": "Power Electronics & Simulation Lab", "branch": "EEE", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21EEE561", "name": "Renewable Energy Sources (Elective)", "branch": "EEE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EEE562", "name": "Smart Grid Technologies (Elective)", "branch": "EEE", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EE61", "name": "Power System Protection & Switchgear", "branch": "EEE", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21EEL66", "name": "Relay & High Voltage Lab", "branch": "EEE", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},

    # ==========================================
    # 7. MECHANICAL ENGINEERING (ME)
    # ==========================================
    {"id": "21ME32", "name": "Material Science and Metallurgy", "branch": "ME", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ME33", "name": "Thermodynamics", "branch": "ME", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ME34", "name": "Mechanics of Materials", "branch": "ME", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21MEL35", "name": "Computer Aided Machine Drawing (CAMD)", "branch": "ME", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21ME42", "name": "Kinematics of Machines", "branch": "ME", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ME43", "name": "Applied Thermodynamics", "branch": "ME", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ME44", "name": "Manufacturing Technology", "branch": "ME", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21MEL46", "name": "Mechanical Testing & Metallography Lab", "branch": "ME", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21ME51", "name": "Design of Machine Elements - I", "branch": "ME", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ME52", "name": "Fluid Mechanics and Machinery", "branch": "ME", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ME53", "name": "Dynamics of Machines", "branch": "ME", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ME54", "name": "Metrology and Quality Control", "branch": "ME", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21MEL55", "name": "Fluid Mechanics & Machinery Lab", "branch": "ME", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21MEE561", "name": "Finite Element Analysis (Elective)", "branch": "ME", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21MEE562", "name": "Automotive Engineering (Elective)", "branch": "ME", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21MEE563", "name": "Non-Conventional Energy Resources (Elective)", "branch": "ME", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ME61", "name": "Heat Transfer and Applications", "branch": "ME", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21ME62", "name": "Computer Integrated Manufacturing (CIM)", "branch": "ME", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21MEL66", "name": "Heat Transfer & CIM Laboratory", "branch": "ME", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},

    # ==========================================
    # 8. CIVIL ENGINEERING (CV)
    # ==========================================
    {"id": "21CV32", "name": "Strength of Materials", "branch": "CV", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CV33", "name": "Fluid Mechanics & Hydraulics", "branch": "CV", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CV34", "name": "Basic Surveying Techniques", "branch": "CV", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CVL35", "name": "Surveying Practice Laboratory", "branch": "CV", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21CV42", "name": "Analysis of Determinate Structures", "branch": "CV", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CV43", "name": "Building Materials and Construction", "branch": "CV", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CV44", "name": "Hydrology and Irrigation Engineering", "branch": "CV", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CVL46", "name": "Building Materials Testing Lab", "branch": "CV", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21CV51", "name": "Analysis of Indeterminate Structures", "branch": "CV", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CV52", "name": "Design of RC Structural Elements", "branch": "CV", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CV53", "name": "Geotechnical Engineering", "branch": "CV", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CV54", "name": "Water Supply & Treatment Engineering", "branch": "CV", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CVL55", "name": "Geotechnical Engineering Lab", "branch": "CV", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2},
    {"id": "21CVE561", "name": "Highway Engineering (Elective)", "branch": "CV", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CVE562", "name": "Air Pollution and Control (Elective)", "branch": "CV", "weekly_hours": 3, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CV61", "name": "Design of Steel Structural Elements", "branch": "CV", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CV62", "name": "Wastewater & Municipal Engineering", "branch": "CV", "weekly_hours": 4, "needs_lab": False, "consecutive_hours": 1},
    {"id": "21CVL66", "name": "Environmental Engineering Lab", "branch": "CV", "weekly_hours": 2, "needs_lab": True, "consecutive_hours": 2}
]

VTU_DEPARTMENTS = [
    {
        "code": "CSE",
        "name": "Computer Science & Engineering",
        "icon": "fa-laptop-code",
        "color": "indigo",
        "desc": "Data structures, algorithms, AI, cloud computing, and full-stack software development.",
        "semesters": [1, 2, 3, 4, 5, 6, 7, 8]
    },
    {
        "code": "ISE",
        "name": "Information Science & Engineering",
        "icon": "fa-server",
        "color": "cyan",
        "desc": "Information systems, DevOps, mobile apps, database systems, and data analytics.",
        "semesters": [1, 2, 3, 4, 5, 6, 7, 8]
    },
    {
        "code": "AIML",
        "name": "Artificial Intelligence & Machine Learning",
        "icon": "fa-brain",
        "color": "purple",
        "desc": "Deep learning, NLP, computer vision, robotics, reinforcement learning, and generative AI.",
        "semesters": [1, 2, 3, 4, 5, 6, 7, 8]
    },
    {
        "code": "ECE",
        "name": "Electronics & Communication Engineering",
        "icon": "fa-microchip",
        "color": "emerald",
        "desc": "Digital signal processing, VLSI design, communication systems, IoT, and embedded electronics.",
        "semesters": [1, 2, 3, 4, 5, 6, 7, 8]
    },
    {
        "code": "EEE",
        "name": "Electrical & Electronics Engineering",
        "icon": "fa-bolt-lightning",
        "color": "amber",
        "desc": "Power systems, renewable energy, electrical machines, high voltage, and smart grids.",
        "semesters": [1, 2, 3, 4, 5, 6, 7, 8]
    },
    {
        "code": "ME",
        "name": "Mechanical Engineering",
        "icon": "fa-gear",
        "color": "rose",
        "desc": "Thermodynamics, machine design, CAD/CAM, fluid machinery, metrology, and automotive systems.",
        "semesters": [1, 2, 3, 4, 5, 6, 7, 8]
    },
    {
        "code": "CV",
        "name": "Civil Engineering",
        "icon": "fa-building-columns",
        "color": "blue",
        "desc": "Structural analysis, geotechnical engineering, surveying, hydraulics, and environmental engineering.",
        "semesters": [1, 2, 3, 4, 5, 6, 7, 8]
    },
    {
        "code": "MATHEMATICS",
        "name": "Engineering Mathematics & Sciences",
        "icon": "fa-square-root-variable",
        "color": "teal",
        "desc": "Calculus, linear algebra, Fourier series, numerical methods, and transform calculus.",
        "semesters": [1, 2, 3, 4]
    },
    {
        "code": "PHYSICS",
        "name": "Engineering Physics",
        "icon": "fa-atom",
        "color": "blue",
        "desc": "Applied physics, semiconductor devices, optics, laser technology, and physics labs.",
        "semesters": [1, 2]
    },
    {
        "code": "CHEMISTRY",
        "name": "Engineering Chemistry",
        "icon": "fa-flask-vial",
        "color": "emerald",
        "desc": "Applied chemistry, battery technology, corrosion science, polymers, and chemistry labs.",
        "semesters": [1, 2]
    },
    {
        "code": "HUMANITIES",
        "name": "Humanities & Social Sciences",
        "icon": "fa-scale-balanced",
        "color": "amber",
        "desc": "Professional English, Constitution of India, professional ethics, and universal human values.",
        "semesters": [1, 2, 3]
    }
]

def import_vtu_syllabus():
    """
    Imports or syncs all VTU syllabus subjects into SQLite database without duplicates.
    """
    from database.db import get_all_subjects, save_subject
    from models.subject import extract_semester_from_code
    
    existing = get_all_subjects()
    existing_ids = {s["id"] for s in existing}
    
    added_count = 0
    updated_count = 0
    
    for subj in VTU_SYLLABUS_SUBJECTS:
        if "semester" not in subj or not subj["semester"]:
            subj["semester"] = extract_semester_from_code(subj["id"])
            
        save_subject(subj)
        if subj["id"] not in existing_ids:
            existing_ids.add(subj["id"])
            added_count += 1
        else:
            updated_count += 1
        
    return {
        "status": "success",
        "added": added_count,
        "updated": updated_count,
        "total_subjects": len(existing_ids)
    }

if __name__ == "__main__":
    res = import_vtu_syllabus()
    print(f"VTU Syllabus Import Result: Added {res['added']}, Updated {res['updated']}, Total: {res['total_subjects']}")
