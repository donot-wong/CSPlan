def delayMinTimeCalc():
    '''
    计算时间盲注时间判断基准
    '''
    # cnt = 0
    TIME_STDEV_COEFF = 7
    respTimeList = [0.063792, 0.064751, 0.06436, 0.067787, 0.069291, 0.058786, 0.061958, 0.066446, 0.071091, 0.069328, 0.063578, 0.064541, 0.059677]
    # print(respTimeList)
    min_resp_time = min(respTimeList)
    average_resp_time = sum(respTimeList) / len(respTimeList)
    print('average_resp_time: %s' % average_resp_time)
    _ = 0
    for i in respTimeList:
        _ += (i - average_resp_time)**2
    deviation = (_ / (len(respTimeList) - 1)) ** 0.5
    print('方差: %s' % deviation)
    delayTimeJudgeStandard = average_resp_time + TIME_STDEV_COEFF * deviation
    print('时间延时基准计算完成: %s' % delayTimeJudgeStandard)
    return True

if __name__ == '__main__':
    delayMinTimeCalc()