import uuid
import subprocess
import re
import os
import time
regex = r"sendKeys: \[.*\]\{(.*)\}"

def format_number(a):
    if "}" in a:
        a=a.replace('}','')
    return hex(int(a)).replace('0x','').upper().zfill(2)

# Create folder
jobID = uuid.uuid4().hex

os.mkdir(jobID)

with open(os.path.join(jobID,'row_log.log'),'w') as fp:
    fp.close()

with open(os.path.join(jobID,'output.log'),'w') as fp:
    fp.close()

with open(os.path.join(jobID,'finder_key.log'),'w') as fp:
    fp.close()


row_log = ""

output_log = ""

finder_key_log = ""

start_parse_string = False
tempdata = [] # for save temp data during logcat 
logcat = subprocess.Popen(["adb", "logcat"], stdout=subprocess.PIPE)
while not logcat.poll():
    line = logcat.stdout.readline().decode()
    row_log += (line + "\n")
    if line :
        if "startPoweredOffMode" in line:
            start_parse_string = False
            print("!!!! Stop Recording Data")
            break
        if start_parse_string:
            print(line)
            try:
                temp = re.search(regex, line).group(0)
                ar = temp.split(',')[6:]
                tempdata += ar
                finder_key_log += (line + "\n")
            except:
                pass
        if "enterPoweredOffMode" in line:
            start_parse_string = True
            print("!!!! Start Recording Data")
    else:
        break

logcat.kill()
data_count = 1
output_array = []
temp_arr= [] # for save 
print("\n")
if len(tempdata) == 0:
    print("Fail to get log, please check row ")
    with open(os.path.join(jobID,'row_log.log'),'w', encoding='UTF-8') as fp:
        fp.write(row_log)
        fp.close()

    with open(os.path.join(jobID,'output.log'),'w+', encoding='UTF-8') as fp:
        fp.write(output_log)
        fp.close()

    with open(os.path.join(jobID,'finder_key.log'),'w+', encoding='UTF-8') as fp:
        fp.write(finder_key_log)
        fp.close()

else:
    for i in tempdata:
        temp_arr.append(format_number(i))
        if data_count == 20:
            data_count = 0
            output_array.append(temp_arr.copy())
            temp_arr.clear()
        data_count += 1

    for index,data in enumerate(output_array):
        output_log +=  (str(index+1) +'. ' + ' '.join(data)+ "\n")




    with open(os.path.join(jobID,'row_log.log'),'w', encoding='UTF-8') as fp:
        fp.write(row_log)
        fp.close()

    with open(os.path.join(jobID,'output.log'),'w+', encoding='UTF-8') as fp:
        fp.write(output_log)
        fp.close()

    with open(os.path.join(jobID,'finder_key.log'),'w+', encoding='UTF-8') as fp:
        fp.write(finder_key_log)
        fp.close()



    print("\n\n================== output ===================")
    for index,data in enumerate(output_array):
        print( (str(index+1) +' ' + ' '.join(data)+ "\n"))

    print("\n\n================== end ===================")
    print("please check folder : "+jobID)