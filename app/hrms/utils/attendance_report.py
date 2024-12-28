from datetime import timedelta, datetime


class AttendanceAttemptInOut:
    def __init__(self, attempt):
        self.attempt = attempt
        self.inout = None


class InoutMode:
    In = "In"
    Out = "Out"
    NoneMode = "None"


def calculate_worktime_without_inout(realTimein, realTimeout, scheduling_record):
    result = 0
    totalWorkTime = ['totalWorkTime']
    restStartDateTime = scheduling_record['restStartDateTime']
    restEndDateTime = scheduling_record['restEndDateTime']
    shiftStartDateTime = scheduling_record['shiftStartDateTime']
    shiftEndDateTime = scheduling_record['shiftEndDateTime']
    realTimein = realTimein.replace(second=0)
    realTimeout = realTimeout.replace(second=0)

    # if shift is not None:
    currentProgram = (realTimeout if realTimeout < restStartDateTime else restStartDateTime) - (realTimein if realTimein > shiftStartDateTime else shiftStartDateTime)
    stageFist = max(0, currentProgram.total_seconds() // 60)

    currentProgram = (realTimeout if realTimeout < shiftEndDateTime else shiftEndDateTime) - (realTimein if realTimein > restEndDateTime else restEndDateTime)
    stageSecond = max(0, currentProgram.total_seconds() // 60)

    result = stageFist + stageSecond

    return int(result)


def calculate_Holiday_worktime_without_inout(realTimein, realTimeout, scheduling_record):
    holidayStartDatetime = scheduling_record['holidayStartDatetime']
    isHoliday = scheduling_record['isHoliday']
    shiftName = scheduling_record['shiftName']
    holidayEndDatetime = scheduling_record['holidayEndDatetime']
    restStartDateTime = scheduling_record['restStartDateTime']
    restEndDateTime = scheduling_record['restEndDateTime']
    shiftStartDateTime = scheduling_record['shiftStartDateTime']
    shiftEndDateTime = scheduling_record['shiftEndDateTime']

    result = 0
    if (shift is not None and isHoliday and 
        (calculate_worktime_without_inout(holidayStartDatetime, holidayEndDatetime) > 0 or 'PH' in shiftName)):

        stageStart = restStartDateTime if restStartDateTime < holidayEndDatetime else holidayEndDatetime
        current_program = (realTimeout.replace(second=0) if realTimeout < stageStart else stageStart) - (realTimein.replace(second=0) if realTimein > holidayStartDatetime else holidayStartDatetime)
        stage_fist = max(0, int(current_program.total_seconds() // 60))

        stageEnd = restEndDateTime if restEndDateTime > holidayStartDatetime else holidayStartDatetime
        current_program = (realTimeout if realTimeout < holidayEndDatetime else holidayEndDatetime) - (realTimein.replace(second=0) if realTimein > stageEnd else stageEnd)
        stage_second = max(0, int(current_program.total_seconds() // 60))

        result = stage_fist + stage_second
    return result

def calculate_Night_Holiday_without_inout(realTimein, realTimeout):
    holidayNightStageFistStartDatetime = scheduling_record['holidayNightStageFistStartDatetime']
    holidayNightStageFistEndDatetime = scheduling_record['holidayNightStageFistEndDatetime']
    holidayNightStageLastStartDatetime = scheduling_record['holidayNightStageLastStartDatetime']
    holidayNightStageLastEndDatetime = scheduling_record['holidayNightStageLastEndDatetime']
    restStartDateTime = scheduling_record['restStartDateTime']
    restEndDateTime = scheduling_record['restEndDateTime']
    result = 0
    if shift is not None:
        stageFistWorktime = 0
        stageLastWorktime = 0

        if shift is not None and holidayNightStageFistEndDatetime is not None:
            stageStart = restStartDateTime if restStartDateTime < holidayNightStageFistEndDatetime else holidayNightStageFistEndDatetime
            currentProgram = (realTimeout.replace(second=0) if realTimeout < stageStart else stageStart) - (realTimein.replace(second=0) if realTimein > holidayNightStageFistStartDatetime else holidayNightStageFistStartDatetime)
            stageFist = max(0, int(currentProgram.total_seconds() // 60))

            stageEnd = restEndDateTime if restEndDateTime > holidayNightStageFistStartDatetime else holidayNightStageFistStartDatetime
            currentProgram = (realTimeout.replace(second=0) if realTimeout < holidayNightStageFistEndDatetime else holidayNightStageFistEndDatetime) - (realTimein.replace(second=0) if realTimein > stageEnd else stageEnd)
            stageSecond = max(0, int(currentProgram.total_seconds() // 60))

            stageFistWorktime = stageFist + stageSecond
        else:
            stageFistWorktime = 0

        if shift is not None and holidayNightStageLastEndDatetime is not None:
            stageStart = restStartDateTime if restStartDateTime < holidayNightStageLastEndDatetime else holidayNightStageLastEndDatetime
            currentProgram = (realTimeout.replace(second=0) if realTimeout < stageStart else stageStart) - (realTimein.replace(second=0) if realTimein > holidayNightStageLastStartDatetime else holidayNightStageLastStartDatetime)
            stageFist = max(0, int(currentProgram.total_seconds() // 60))

            stageEnd = restEndDateTime if restEndDateTime > holidayNightStageLastStartDatetime else holidayNightStageLastStartDatetime
            currentProgram = (realTimeout.replace(second=0) if realTimeout < holidayNightStageLastEndDatetime else holidayNightStageLastEndDatetime) - (realTimein.replace(second=0) if realTimein > stageEnd else stageEnd)
            stageSecond = max(0, int(currentProgram.total_seconds() // 60))

            stageLastWorktime = stageFist + stageSecond
        else:
            stageLastWorktime = 0

        result = stageFistWorktime + stageLastWorktime

    return result


def check_last_in_out(scheduling_record):
    attemptWithInoutArray = scheduling_record['attemptWithInoutArray']
    list_addItem_out = scheduling_record['list_addItem_out']
    attemptWithInoutArray.sort(key=lambda x: x.attempt)

    if attemptWithInoutArray:
        if attemptWithInoutArray[-1].inout != InoutMode.Out:
            addItem = AttendanceAttemptInOut(attempt=attemptWithInoutArray[-1].attempt)
            addItem.inout = InoutMode.Out

            for in_out_addItem_before in [item for item in list_addItem_out if item.attempt <= attemptWithInoutArray[-1].attempt]:
                in_out_addItem_before.inout = InoutMode.NoneMode

            list_addItem_out.append(addItem)
            attemptWithInoutArray.append(addItem)

            add_in_item = AttendanceAttemptInOut(attempt=attemptWithInoutArray[-1].attempt + timedelta(milliseconds=10))
            add_in_item.inout = InoutMode.In
            attemptWithInoutArray.append(add_in_item)


def calculate_night_worktime_custom(realTimein, realTimeout, nightStageStart, nightStageEnd, scheduling_record):
    restStartDateTime = scheduling_record['restStartDateTime']
    restEndDateTime = scheduling_record['restEndDateTime']
    # Đặt giây của thời gian bằng 0
    nightStageStart = nightStageStart.replace(second=0)
    nightStageEnd = nightStageEnd.replace(second=0)

    stageFistWorktime = 0
    # if shift is not None:
    # Tính toán thời gian bắt đầu giai đoạn
    stageStart = restStartDateTime if restStartDateTime < nightStageEnd else nightStageEnd
    currentProgram = (realTimeout.replace(second=0) if realTimeout < stageStart else stageStart) - (realTimein.replace(second=0) if realTimein > nightStageStart else nightStageStart)
    stageFist = max(0, currentProgram.total_seconds() // 60)

    # Tính toán thời gian kết thúc giai đoạn
    stageEnd = restEndDateTime if restEndDateTime > nightStageStart else nightStageStart
    currentProgram = (realTimeout.replace(second=0) if realTimeout < nightStageEnd else nightStageEnd) - (realTimein.replace(second=0) if realTimein > stageEnd else stageEnd)
    stageSecond = max(0, currentProgram.total_seconds() // 60)

    stageFistWorktime = stageFist + stageSecond

    return int(stageFistWorktime)


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
            scheduling['restStartDateTime'] = date.replace(
                hour=shift.start_work_time.hour, minute=shift.start_rest_time.minute)
            scheduling['restEndDateTime'] = date.replace(
                hour=shift.end_work_time.hour, minute=shift.end_rest_time.minute)


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

    # Chuẩn hóa tên trạng thái ngày nghỉ
    for e in hrLeaves:
        e['holidayStatusName'] = e['holiday_status_id'][0] if e['holiday_status_id'][1] else ''

    # Lọc các phần tử có trạng thái thiếu chấm công
    listMissingLeaves = [
        element for element in hrLeaves
        if 'thiếu chấm công' in f"{element['holidayStatusName']}".lower()
    ]

    shiftStartDateTime = scheduling_record["shiftStartDateTime"]
    shiftEndDateTime = scheduling_record["shiftEndDateTime"]

    if shiftStartDateTime is not None:
        additionTrans = []

        for leaveItem in listMissingLeaves:
            scheduling_record["missing_checkin_break"] = False

            def add_to_attempt_array(attendance_time, mode):
                if attendance_time not in attendanceAttemptArray:
                    attendanceAttemptArray.append(attendance_time)

                additem = AttendanceAttemptInOut(attempt=attendance_time)
                additem.inout = mode

                for in_out_addItem_before in [
                    item for item in list_addItem_out
                    if item.attempt <= additem.attempt
                ]:
                    in_out_addItem_before.inout = InoutMode.NoneMode

                additionTrans.append(additem)

            if 'chấm công ra' in f"{leaveItem['holidayStatusName']}".lower() and leaveItem.get('attendance_missing_to'):
                attendance_missing_to = leaveItem['attendance_missing_to']
                if attendance_missing_to.day in {shiftStartDateTime.day, shiftEndDateTime.day}:
                    if attendance_missing_to < shiftStartDateTime:
                        attendance_missing_to += timedelta(days=1)
                    add_to_attempt_array(attendance_missing_to, InoutMode.Out)

            if 'chấm công vào' in f"{leaveItem['holidayStatusName']}".lower() and leaveItem.get('attendance_missing_from'):
                attendanceMissingFrom = leaveItem['attendance_missing_from']
                if attendanceMissingFrom.day in {shiftStartDateTime.day, shiftEndDateTime.day}:
                    if attendanceMissingFrom < (shiftStartDateTime - timedelta(hours=3)):
                        attendanceMissingFrom += timedelta(days=1)
                    add_to_attempt_array(attendanceMissingFrom, InoutMode.In)

            if leaveItem.get('attendance_missing_to') and leaveItem.get('attendance_missing_from'):
                if {leaveItem['attendance_missing_from'].day, leaveItem['attendance_missing_to'].day} & {shiftStartDateTime.day, shiftEndDateTime.day}:
                    attendanceMissingTo = leaveItem['attendance_missing_to']
                    if attendanceMissingTo < (shiftStartDateTime - timedelta(hours=3)):
                        attendanceMissingTo += timedelta(days=1)
                    add_to_attempt_array(attendanceMissingTo, InoutMode.Out)

                    attendanceMissingFrom = leaveItem['attendance_missing_from']
                    if attendanceMissingFrom < shiftStartDateTime:
                        attendanceMissingFrom += timedelta(days=1)
                    add_to_attempt_array(attendanceMissingFrom, InoutMode.In)

        attemptWithInoutArray = list(set(additionTrans + attemptWithInoutArray))
        attemptWithInoutArray.sort(key=lambda a: a.attempt)
    scheduling_record['list_addItem_out'] = list_addItem_out
    attendanceAttemptArray.sort()
    return attemptWithInoutArray, attendanceAttemptArray


def find_attendance_hue4_time_mode(scheduling_record):
    attendanceAttemptArray = scheduling_record['attendanceAttemptArray']
    restStartDateTime = scheduling_record['restStartDateTime']
    restEndDateTime = scheduling_record['restEndDateTime']
    shiftStartDateTime = scheduling_record['shiftStartDateTime']
    shiftEndDateTime = scheduling_record['shiftEndDateTime']
    attendanceAttemptArray.sort()

    beforeRestEndStartIndex = -1
    beforeRestEndEndIndex = -1
    afterRestStartStartIndex = -1
    afterRestStartEndIndex = -1
    HueStage1Start = None
    HueStage1End = None
    HueStage2Start = None
    HueStage2End = None
    stage1WorktimeTemp = None
    stage2WorktimeTemp = None

    if restStartDateTime is not None and restEndDateTime is not None:
        for index in range(len(attendanceAttemptArray)):
            if attendanceAttemptArray[index] <= restEndDateTime:
                if beforeRestEndStartIndex == -1:
                    beforeRestEndStartIndex = index
                if beforeRestEndEndIndex == -1 or (attendanceAttemptArray[index] - attendanceAttemptArray[beforeRestEndEndIndex]).total_seconds() > 1:
                    beforeRestEndEndIndex = index

            if attendanceAttemptArray[index] >= restStartDateTime:
                if afterRestStartStartIndex == -1:
                    afterRestStartStartIndex = index
                if afterRestStartEndIndex == -1 or (attendanceAttemptArray[index] - attendanceAttemptArray[afterRestStartEndIndex]).total_seconds() > 1:
                    afterRestStartEndIndex = index

        HueStage1Start = attendanceAttemptArray[beforeRestEndStartIndex] if beforeRestEndStartIndex > -1 else None
        HueStage2End = attendanceAttemptArray[afterRestStartEndIndex] if afterRestStartEndIndex > -1 else None

        if beforeRestEndEndIndex > afterRestStartStartIndex and afterRestStartStartIndex >= 0:
            HueStage1End = attendanceAttemptArray[afterRestStartStartIndex] if afterRestStartStartIndex > -1 else None
            HueStage2Start = attendanceAttemptArray[beforeRestEndEndIndex]
        elif beforeRestEndEndIndex < afterRestStartStartIndex and beforeRestEndEndIndex >= 0:
            HueStage1End = attendanceAttemptArray[beforeRestEndEndIndex] if beforeRestEndEndIndex > -1 else None
            HueStage2Start = attendanceAttemptArray[afterRestStartStartIndex]
        else:
            if beforeRestEndEndIndex >= 0 and HueStage1Start is not None and HueStage2End is not None:
                tempStart1End = next((e for e in reversed(attendanceAttemptArray) if e > HueStage1Start and e < attendanceAttemptArray[beforeRestEndEndIndex]), None)
                tempStart2Start = next((e for e in attendanceAttemptArray if e < HueStage2End and e > attendanceAttemptArray[beforeRestEndEndIndex]), None)

                stage1WorktimeTemp = calculate_night_worktime_custom(HueStage1Start, attendanceAttemptArray[beforeRestEndEndIndex], shiftStartDateTime, restStartDateTime) + (calculate_night_worktime_custom(tempStart2Start, HueStage2End, restEndDateTime, shiftEndDateTime) if tempStart2Start else 0)
                stage2WorktimeTemp = (calculate_night_worktime_custom(HueStage1Start, tempStart1End, restEndDateTime, shiftEndDateTime) if tempStart1End else 0) + calculate_night_worktime_custom(attendanceAttemptArray[beforeRestEndEndIndex], HueStage2End, restEndDateTime, shiftEndDateTime)

                if stage1WorktimeTemp > stage2WorktimeTemp:
                    HueStage1End = attendanceAttemptArray[beforeRestEndEndIndex]
                    HueStage2Start = tempStart2Start
                else:
                    HueStage1End = tempStart1End
                    HueStage2Start = attendanceAttemptArray[beforeRestEndEndIndex]

    if HueStage1End is not None and HueStage1Start is not None:
        if not HueStage1End > HueStage1Start:
            HueStage1End = None
    if HueStage2End is not None and HueStage2Start is not None:
        if not HueStage2End > HueStage2Start:
            HueStage2Start = None
    if HueStage1Start is not None and HueStage1End is not None and shiftStartDateTime is not None and restStartDateTime is not None:
        stage1WorktimeTemp = calculate_night_worktime_custom(HueStage1Start, HueStage1End, shiftStartDateTime, restStartDateTime)
    else:
        stage1WorktimeTemp = 0
    if HueStage2Start is not None and HueStage2End is not None and shiftEndDateTime is not None and restEndDateTime is not None:
        stage2WorktimeTemp = calculate_night_worktime_custom(HueStage2Start, HueStage2End, restEndDateTime, shiftEndDateTime)
    else:
        stage2WorktimeTemp = 0
    check_last_in_out(scheduling_record=scheduling_record)

    scheduling_record["HueStage1Start"] = HueStage1Start,
    scheduling_record["HueStage1End"] = HueStage1End,
    scheduling_record["HueStage2Start"] = HueStage2Start,
    scheduling_record["HueStage2End"] = HueStage2End,
    scheduling_record["stage1WorktimeTemp"] = stage1WorktimeTemp,
    scheduling_record["stage2WorktimeTemp"] = stage2WorktimeTemp
