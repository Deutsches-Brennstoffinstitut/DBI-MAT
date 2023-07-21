import time
from dbimat.source.helper.initialize_logger import LoggingLevels

import Test_01_Basic_Production_H2
import Test_02a_Basic_Consumption_Electric
import Test_02b_Basic_Consumption_Electric
import Test_03a_Basic_Consumption_H2
import Test_03b_Basic_Consumption_H2_Modularisation
import Test_04_Basic_Repowering
import Test_05a_Mischner_Pipeline
import Test_05b_Nimtz_Pipeline
import Test_07_Cost_Calculation_VDI

logging_level = LoggingLevels.CRITICAL

all_tests = [Test_01_Basic_Production_H2,
             Test_02a_Basic_Consumption_Electric,
             Test_02b_Basic_Consumption_Electric,
             Test_03a_Basic_Consumption_H2,
             Test_03b_Basic_Consumption_H2_Modularisation,
             Test_04_Basic_Repowering,
             Test_05a_Mischner_Pipeline,
             Test_05b_Nimtz_Pipeline,
             Test_07_Cost_Calculation_VDI]
failed_tests = []
for test in all_tests:
    try:
        print(f'Running Test:"{test.__name__}" ...')
        test.run_local(logging_level)
        print(f'Test "{test.__name__}" successful locally!\n')
    except:
        print(f'Test:"{test.__name__}" failed locally!\n')
        failed_tests.append(test.__name__)

print(f'\n\nResult: {len(all_tests) - len(failed_tests)} of {len(all_tests)} Tests are successful.')
time.sleep(2)
if len(failed_tests) > 0:
    print('Failed Tests are:\n')
    for test in failed_tests:
        print(test)
