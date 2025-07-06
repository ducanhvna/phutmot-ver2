const ROLE_RESOURCE_ACCESS: Record<string, string[]> = {
  admin: [
    "goals-setup",
    "daily-progress",
    "tests-review",
    "learning-overview",
    "grading",
    "analysis-dashboard",
    "learning-data-entry",
  ],
  teacher: [
    "top-teacher",
    "goals-setup",
    "daily-progress-teacher",
    "tests-review",
    "learning-overview",
    "grading",
    "analysis-dashboard",
    "learning-data-entry",
  ],
  student: [
    "top-student",
    "goals-setup",
    "daily-progress-student",
    "tests-review",
    "learning-overview",
  ],
};

export default ROLE_RESOURCE_ACCESS;
