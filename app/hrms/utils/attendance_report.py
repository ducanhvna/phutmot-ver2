from datetime import timedelta, datetime


class AttendanceAttemptInOut:
    def __init__(self, attempt):
        self.attempt = attempt
        self.inout = None


class InoutMode:
    In = "In"
    Out = "Out"
    NoneMode = "None"


def mergedTimeToScheduling(schedulings, shifts):
    merged_shift = {shift.name.replace('/', '_'): shift for shift in shifts}

    for scheduling in schedulings:
        if scheduling['shift_name'].replace('/', '_') in merged_shift:
            shift = merged_shift[scheduling['shift_name'].replace('/', '_')]
            date = datetime.strptime(scheduling['date'], "%Y-%m-%d")
            scheduling['shiftStartDateTime'] = date.replace(
                hour=shift.start_work_time.hour, minute=shift.start_work_time.minute)
            scheduling['shiftEndDateTime'] = date.replace(
                hour=shift.end_work_time.hour, minute=shift.end_work_time.minute)


def add_attempt_more_than_limit(listAttendanceTrans, scheduling_record, diffHoursWithNext, diffHoursWithPrev):
    attemptWithInoutArray = []
    attendanceAttemptArray = []
    if scheduling_record["shiftStartDateTime"] is not None and scheduling_record["shiftEndDateTime"] is not None:
        additionTrans = []
        shift_start = scheduling_record["shiftStartDateTime"]
        shift_end = scheduling_record["shiftEndDateTime"]
        # Chuyển đổi tất cả thời gian sang định dạng datetime một lần
        for e in listAttendanceTrans:
            e['time_dt'] = datetime.strptime(e['time'], "%Y-%m-%d %H:%M:%S")
        listitemTrans = [
            e for e in listAttendanceTrans
            if shift_start - timedelta(hours=diffHoursWithPrev) < e['time_dt'] < shift_end + timedelta(hours=diffHoursWithNext)
        ]
        listitemTrans.sort(key=lambda e: e['time_dt'])

        if listitemTrans:
            if not listitemTrans[0]['in_out']:
                listitemTrans[0]['in_out'] = 'I'
            if not listitemTrans[-1]['in_out']:
                listitemTrans[-1]['in_out'] = 'O'

        for tran in listitemTrans:
            additem = AttendanceAttemptInOut(attempt=tran['time_dt'])
            additem.inout = InoutMode.In if tran['in_out'] in ['I', 'i'] else InoutMode.Out if tran['in_out'] in ['O', 'o'] else InoutMode.NoneMode
            additionTrans.append(additem)

        attemptWithInoutArray = list(set(additionTrans + attemptWithInoutArray))

        attendanceAttemptArray = list(set(
            [e['time_dt'] for e in listitemTrans if e['time_dt'] not in attendanceAttemptArray and e['time_dt'].replace(second=0) not in attendanceAttemptArray] + attendanceAttemptArray
        ))
        attemptWithInoutArray.sort(key=lambda a: a.attempt)
    scheduling_record['attemptWithInoutArray'] = attemptWithInoutArray
    scheduling_record['attendanceAttemptArray'] = attendanceAttemptArray
    return scheduling_record
