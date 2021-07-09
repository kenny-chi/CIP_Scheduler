import pandas as pd
import random
import os

MAX_SIZE = 15
MAX_WAITLIST_SIZE = 5
SESSION_NUM = 6
sign_ups = 'data/Summer Session 1 MS Sign-Ups (Responses) - Form Responses 1.csv'
choices = ['First Choice Class ', 'Second Choice Class ', 'Third Choice Class ', 'Fourth Choice Class ', 'Fifth Choice Class ']
likely = 'For the student: How likely are you to attend all your scheduled classes?'
desired_amount = 'How many classes would you like to enroll in? (Whether or not you will be placed in multiple classes will depend on how many students enroll in Connect-In-Place, as well as the popularity of the classes you are interested in.)'
student_email = "Student Email (where we'll send the Zoom link to)"
cancellations = ['Video Game Plot Analysis: Storytelling Through the Controller - Joey, Tu/Th 10-11am PT', 'Learning History Through Latin - Albertine, M/W 4-5pm PT', 'The Intersection of Psychology and Economics - Hazel, W 6-7pm PT']
print_cols = ['Parent Name', 'Parent Email', 'Student Full Name', student_email, 'Student Grade in the Fall', likely, 'Student Phone Number', 'Parent Phone Number']
roster_cols = ['Student Full Name', student_email, 'Parent Email', 'Student Grade in the Fall', 'Student Phone Number', 'class1', 'status1', 'class2', 'status2', 'class3', 'status3', 'class4', 'status4', 'class5', 'status5']
small_class = ['Angels and Demons: An Introduction to Spiritual Beings - Joseph, M/W 9-10am PT', 'The Capital Sins: How to be a Bad Person - Joseph, T/Th 9-10am PT', 'Art for Everyone: The Joy of Crafting - Eliza, Monday 1-2:30 pm PT', 'Get it on the Page: Making Writing Easy - Eliza, Thursday 2-3:30pm PT', 'Creative Writing: Beginning Your Bestseller - Selena, Tu/Th 2-3:30pm PT', 'Set Theory and Probability - Ratul, M/W 1-2pm PT']
big_class = []
max_big_class_waitlist = 25
whatever = 'Are you willing to take any class?'
dataframes = []

data = pd.read_csv(sign_ups).to_dict('records')
student_emails = set()
deduped = []
curr_dict = {'class name': "removed_duplicates"}


#eliminating duplicate entries
for row in data:
    if row['Student Full Name'] + row[student_email] in student_emails:
        for col in row:
            if col not in curr_dict:
                curr_dict[col] = []
            curr_dict[col].append(str(row[col]))
        continue
    student_emails.add(row['Student Full Name'] + row[student_email])
    row[likely] = int(row[likely][:row[likely].find('%')])
    row['classes_desired'] = row[desired_amount]
    row['schedule'] = []
    row['waitlist'] = []
    row['happiness'] = []
    row['suggestion'] = []
    deduped.append(row)
dataframes.append(curr_dict)

data = deduped

assignments = {}
waitlists = {}
ongoing = True
current_round = 0


#class matching
while ongoing:
    current_round += 1
    happiness = [0 for i in range(len(choices))]
    ongoing = False
    print(f'Round {current_round}')

    random.shuffle(data)
    if current_round > 1:
        data.sort(key=lambda row: -row[desired_amount])
    data.sort(key=lambda row: -row[likely])

    for row in data:
        if row['classes_desired'] == 0:
            continue

        #goes through one choice for each entry until enrolled or waitlisted
        for choice_idx, choice in enumerate(choices):
            classname = row[choice]
            if pd.isna(classname) or classname in cancellations: #checks if classname is null
                continue

            if classname not in assignments:
                assignments[classname] = []
                waitlists[classname] = []

            # if len(assignments[classname]) == MAX_SIZE:
            #     classes[classname]['full'] = True

            if ((classname not in small_class and len(assignments[classname]) < MAX_SIZE) or (classname in small_class and len(assignments[classname]) < MAX_SIZE / 2)) and classname not in row['schedule']:
                row['schedule'].append(classname)
                row['happiness'].append(choice_idx+1)
                row['classes_desired'] -= 1
                assignments[classname].append(row)
                happiness[choice_idx] += 1
                ongoing = True
                # classes[classname]['size'] += 1
                break
            elif classname not in row['waitlist'] and classname not in row['schedule'] and (len(waitlists[classname]) < MAX_WAITLIST_SIZE or (classname in big_class and len(waitlists[classname]) < max_big_class_waitlist)):
                row['waitlist'].append(classname)
                waitlists[classname].append(row)
                ongoing = True
            # elif len(row['waitlist']) + len(row['schedule']) < row[desired_amount] and classes[classname]['category'] not in row['suggestion']:
            #     row['suggestion'].append(classes[classname]['category'])

    #outputs how many matches sorted into choice number
    for choice_idx, choice in enumerate(choices):
        print(happiness[choice_idx], choice)

# classes['name'] = 'enrollment'
# dataframes.append(classes)


#output class rosters
for classname, roster in assignments.items():
    bad_chars = ['/', ':', ',', '<', '>', '(', ')', '?', ' ']
    classname_short = classname
    for i in bad_chars:
        classname_short = classname_short.replace(i, '')
    curr_dict = {col: [] for col in print_cols}
    curr_dict['class name'] = classname_short
    curr_dict['status'] = []
    for student in roster:
        for col in student:
            if col in print_cols:
                curr_dict[col].append(str(student[col]))
        curr_dict['status'].append('enrolled')
    for student in waitlists[classname]:
        for col in student:
            if col in print_cols:
                curr_dict[col].append(str(student[col]))
        curr_dict['status'].append('waitlist')
    dataframes.append(curr_dict)

#output individual student schedules
curr_dict = {col: [] for col in roster_cols}
curr_dict['classes_desired'] = []
curr_dict['class name'] = 'full_enrollment'
dropped = 0
for student in data:
    for key in curr_dict.keys():
        if key in student:
            curr_dict[key].append(student[key])
    for class_num in range(1, 6):
        if(class_num == 1 and len(student['schedule']) == 0):
            dropped += 1
            print(student['Student Full Name'] + student[whatever])
        if len(student['schedule']) > 0:
            curr_dict['class' + str(class_num)].append(student['schedule'].pop(0))
            curr_dict['status' + str(class_num)].append('E')
        elif len(student['waitlist']) > 0:
            curr_dict['class' + str(class_num)].append(student['waitlist'].pop(0))
            curr_dict['status' + str(class_num)].append('W')
        elif len(student['suggestion']) > 0:
            curr_dict['class' + str(class_num)].append(student['suggestion'].pop(0))
            curr_dict['status' + str(class_num)].append('S')
        else:
            curr_dict['class' + str(class_num)].append('')
            curr_dict['status' + str(class_num)].append('')
dataframes.append(curr_dict)
print("Dropped: ", dropped)



#TESTING: output full class list
# classes = {'full_name': [], 'class_name': [], 'teacher': [], 'class_time': []}
# for row in data:
#     for choice_idx, choice in enumerate(choices):
#         classname = row[choice]
#         if not pd.isna(classname):
#             try:
#                 if classname not in classes['full_name']:
#                     time = classname[classname.rindex(',') + 1:].strip()
#                     time_stripped = classname[:classname.rindex(',')]
#                     teacher = time_stripped[time_stripped.rindex('-') + 1:].strip()
#                     name = time_stripped[:time_stripped.rindex('-')].strip()
#                     classes['full_name'].append(classname)
#                     classes['class_time'].append(time)
#                     classes['teacher'].append(teacher)
#                     classes['class_name'].append(name)
#             except:
#                 print(classname)
# dataframes.append(classes)

#export to separate excel files
output_dir = 'output/s' + str(SESSION_NUM)
if not os.path.isdir(output_dir):
    print('Please make an output directory for your session as ' + output_dir)
directory = 'output/s{}/MS_SIZE{}_WAITLIST{}/'.format(SESSION_NUM, MAX_SIZE, MAX_WAITLIST_SIZE)
try:
    os.mkdir(directory)
except:
    print('overwrote existing directory ' + output_dir)
for data in dataframes:
    path = 'output/s{}/MS_SIZE{}_WAITLIST{}/{}.xlsx'.format(SESSION_NUM, MAX_SIZE, MAX_WAITLIST_SIZE, data['class name'])
    with pd.ExcelWriter(path) as writer:
        df = pd.DataFrame(data=data)
        df.to_excel(writer)
