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
    scheduling_record["attendanceAttempt1"] = attendanceAttemptArray[0] if len(attendanceAttemptArray) > 0 else None
    return scheduling_record


def process_missing_attendance(hrLeaves, scheduling_record):
    attemptWithInoutArray = scheduling_record['attemptWithInoutArray']
    attendanceAttemptArray = scheduling_record['attendanceAttemptArray']
    list_addItem_out = []
    for e in listAttendanceTrans:
        e['holidayStatusName'] = e['holiday_status_id'] if e['holiday_status_id'][1] else ''
    listMissingLeaves = [element for element in hrLeaves if 'thiếu chấm công' in f"{element['holidayStatusName']}".lower()]
    shiftStartDateTime = scheduling_record["shiftStartDateTime"]
    shiftEndDateTime = scheduling_record["shiftEndDateTime"]
    if shiftStartDateTime is not None:
        additionTrans = []

        for leaveItem in listMissingLeaves:
            scheduling_record["missing_checkin_break"] = False

            if 'chấm công ra' in f"{leaveItem['holidayStatusName']}".lower() and leaveItem.get('attendance_missing_to') and (leaveItem['attendance_missing_to'].day == shiftStartDateTime.day or leaveItem['attendance_missing_to'].day == shiftEndDateTime.day):
                attendance_missing_to = leaveItem['attendance_missing_to']
                if attendance_missing_to < shiftStartDateTime:
                    attendance_missing_to += timedelta(days=1)

                if attendance_missing_to not in attendanceAttemptArray:
                    attendanceAttemptArray.append(attendance_missing_to)

                additem = AttendanceAttemptInOut(attempt=attendance_missing_to)
                additem.inout = InoutMode.Out

                for in_out_addItem_before in [item for item in list_addItem_out if item.attempt <= additem.attempt]:
                    in_out_addItem_before.inout = InoutMode.NoneMode

                additionTrans.append(additem)

            elif 'chấm công vào' in f"{leaveItem['holidayStatusName'].lower()}" and leaveItem.get('attendance_missing_from') and (leaveItem['attendance_missing_from'].day == shiftStartDateTime.day or leaveItem['attendance_missing_from'].day == shiftEndDateTime.day):
                attendanceMissingFrom = leaveItem['attendance_missing_from']
                if not attendanceMissingFrom < (shiftStartDateTime - timedelta(hours=3)):
                    attendanceMissingFrom += timedelta(days=1)

                if attendanceMissingFrom not in attendanceAttemptArray:
                    attendanceAttemptArray.append(attendanceMissingFrom)

                additem = AttendanceAttemptInOut(attempt=attendanceMissingFrom)
                additem.inout = InoutMode.In
                additionTrans.append(additem)

            elif leaveItem.get('attendance_missing_to') and leaveItem.get('attendance_missing_from') and (leaveItem['attendance_missing_from'].day == shiftStartDateTime.day or leaveItem['attendance_missing_from'].day == shiftEndDateTime.day or leaveItem['attendance_missing_to'].day == shiftStartDateTime.day or leaveItem['attendance_missing_to'].day == shiftEndDateTime.day):
                attendanceMissingTo = leaveItem['attendance_missing_to']
                if attendanceMissingTo < (shiftStartDateTime - timedelta(hours=3)):
                    attendanceMissingTo += timedelta(days=1)

                if attendanceMissingTo not in attendanceAttemptArray:
                    attendanceAttemptArray.append(attendanceMissingTo)

                additem = AttendanceAttemptInOut(attempt=attendanceMissingTo)
                additem.inout = InoutMode.Out

                for in_out_addItem_before in [item for item in list_addItem_out if item.attempt <= additem.attempt]:
                    in_out_addItem_before.inout = InoutMode.NoneMode

                additionTrans.append(additem)

                attendanceMissingFrom = leaveItem['attendance_missing_from']
                if attendanceMissingFrom < shiftStartDateTime:
                    attendanceMissingFrom += timedelta(days=1)

                if attendanceMissingFrom not in attendanceAttemptArray:
                    attendanceAttemptArray.append(attendanceMissingFrom)

                additem = AttendanceAttemptInOut(attempt=attendanceMissingFrom)
                additem.inout = InoutMode.In
                additionTrans.append(additem)

        attemptWithInoutArray = list(set(additionTrans + attemptWithInoutArray))
        attemptWithInoutArray.sort(key=lambda a: a.attempt)

    attendanceAttemptArray.sort()
    return attemptWithInoutArray, attendanceAttemptArray
