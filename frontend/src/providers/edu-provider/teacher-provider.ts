import axios from 'axios';

export interface TeacherDailyLeaningLogCreate {
    name: string;
    status: string;
    period_from?: string;
    period_to?: string;
    subject?: string;
    subject_id?: number;
    school_year?: number;
    grade?: number;
    group?: string;
    template?: string;
    creator?: string;
    answer_request?: string;
    answer_content?: string;
}

export async function createTeacherDailyLeaningLog(
    data: TeacherDailyLeaningLogCreate,
    token?: string
) {
    const res = await axios.post(
        '/api/education/teacher/daily-leaning-log/',
        data,
        token
            ? { headers: { Authorization: `Bearer ${token}` } }
            : undefined
    );
    return res.data;
}
