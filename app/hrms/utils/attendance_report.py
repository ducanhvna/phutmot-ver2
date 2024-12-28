from datetime import timedelta


class AttendanceAttemptInOut:
    def __init__(self, attempt):
        self.attempt = attempt
        self.inout = None


class InoutMode:
    In = "In"
    Out = "Out"
    NoneMode = "None"


def add_attempt_more_than_limit(listAttendanceTrans, scheduling_record, diffHoursWithNext, diffHoursWithPrev):
    attemptWithInoutArray = []
    attendanceAttemptArray = []
    if scheduling_record["shiftStartDateTime"] is not None and scheduling_record["shiftEndDateTime"] is not None:
        additionTrans = []
        listitemTrans = [
            e for e in listAttendanceTrans
            if e.name is not None
            if e.time is not None
            if e.time < scheduling_record["shiftEndDateTime"] + timedelta(hours=diffHoursWithNext)
            if e.time > scheduling_record["shiftStartDateTime"] - timedelta(hours=diffHoursWithPrev)
        ]
        listitemTrans.sort(key=lambda e: e.time)

        if listitemTrans:
            if listitemTrans[0].in_out == '' or listitemTrans[0].in_out is None:
                listitemTrans[0].in_out = 'I'
            if listitemTrans[-1].in_out == '' or listitemTrans[-1].in_out is None:
                listitemTrans[-1].in_out = 'O'

        for tran in listitemTrans:
            additem = AttendanceAttemptInOut(attempt=tran.time)
            additem.inout = InoutMode.In if tran.in_out in ['I', 'i'] else InoutMode.Out if tran.in_out in ['O', 'o'] else InoutMode.NoneMode
            additionTrans.append(additem)

        attemptWithInoutArray = list(set(additionTrans + attemptWithInoutArray))

        attendanceAttemptArray = list(set(
            [e.time for e in listitemTrans
             if e.time and e.time not in attendanceAttemptArray
             and e.time.replace(second=0) not in attendanceAttemptArray] + attendanceAttemptArray
        ))
        attemptWithInoutArray.sort(key=lambda a: a.attempt)
    scheduling_record['attemptWithInoutArray'] = attemptWithInoutArray
    scheduling_record['attendanceAttemptArray'] = attendanceAttemptArray
    return scheduling_record
