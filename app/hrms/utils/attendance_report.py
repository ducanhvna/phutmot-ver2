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
        listitemTrans = [
            e for e in listAttendanceTrans
            if datetime.strptime(e['time'], "%Y-%m-%d %H:%M:%S") < scheduling_record["shiftEndDateTime"] + timedelta(hours=diffHoursWithNext)
            if datetime.strptime(e['time'], "%Y-%m-%d %H:%M:%S") > scheduling_record["shiftStartDateTime"] - timedelta(hours=diffHoursWithPrev)
        ]
        listitemTrans.sort(key=lambda e: datetime.strptime(e['time'], "%Y-%m-%d %H:%M:%S"))

        if listitemTrans:
            if listitemTrans[0].in_out == '' or listitemTrans[0].in_out is None:
                listitemTrans[0].in_out = 'I'
            if listitemTrans[-1].in_out == '' or listitemTrans[-1].in_out is None:
                listitemTrans[-1].in_out = 'O'

        for tran in listitemTrans:
            additem = AttendanceAttemptInOut(attempt=datetime.strptime(tran['time'], "%Y-%m-%d %H:%M:%S"))
            additem.inout = InoutMode.In if tran.in_out in ['I', 'i'] else InoutMode.Out if tran.in_out in ['O', 'o'] else InoutMode.NoneMode
            additionTrans.append(additem)

        attemptWithInoutArray = list(set(additionTrans + attemptWithInoutArray))

        attendanceAttemptArray = list(set(
            [datetime.strptime(e['time'], "%Y-%m-%d %H:%M:%S") for e in listitemTrans
             if datetime.strptime(e['time'], "%Y-%m-%d %H:%M:%S") and datetime.strptime(e['time'], "%Y-%m-%d %H:%M:%S") not in attendanceAttemptArray and datetime.strptime(e['time'], "%Y-%m-%d %H:%M:%S").replace(second=0) not in attendanceAttemptArray] + attendanceAttemptArray
        ))
        attemptWithInoutArray.sort(key=lambda a: a.attempt)
    scheduling_record['attemptWithInoutArray'] = attemptWithInoutArray
    scheduling_record['attendanceAttemptArray'] = attendanceAttemptArray
    return scheduling_record
