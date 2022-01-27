# REQUIREMENTS ------------
# pip install requests
# -------------------------

# TODO:
# No validation done by assume everything is ok,
# But better to write validation logic too

import requests
import json
import os

# Where the API is available
apiBase = "https://api.ce.pdn.ac.lk"
apiIndex = apiBase + "/projects/"

studentSource = apiBase + "/people/v1/students/all/"
projectSource = apiBase + "/projects/v1/all/"

student_dict = {}

# Gather Student API data
req_students = requests.get(studentSource)
if req_students.status_code==200:
    students = json.loads(req_students.text)

# Gather Project API data
req_projects = requests.get(projectSource)
if req_projects.status_code==200:
    projects = json.loads(req_projects.text)


for p_cat in projects:
    proj_cat = projects[p_cat]
    print(p_cat)

    for batch in proj_cat['batches']:
        batch_projects = proj_cat['batches'][batch]
        print('-' + batch)

        for proj in batch_projects['projects']:
            p = batch_projects['projects'][proj]
            print('--' + p['title'])

            # Each project

            # read the project information from the file
            filename = p['api_url'].replace('http://api.ce.pdn.ac.lk', '..') + "index.json"
            # print('\t' + filename)

            proj_data = json.load(open(filename, "r"))
            cat_code = proj_data['category']['code']
            # print(json.dumps(proj_data, indent = 4))

            proj_tag = {
                'title': proj_data['title'],
                'category': {
                    'code': cat_code,
                    'api_url': apiBase + '/projects/v1/' + cat_code + '/'
                },
                # 'project_url': proj_data['project_url'],
                # 'repo_url': proj_data['repo_url'],
                # 'page_url': proj_data['page_url'],
                'api_url': p['api_url']
            }

            if 'team' in proj_data:
                for student in proj_data['team']:
                    # print(student)
                    if student!="" and student!="E/YY/XXX":
                        if student not in student_dict: student_dict[student] = []
                        student_dict[student].append(proj_tag)
            # break
        # break
    # break


# print(json.dumps(student_dict, indent = 4))

# Sort the dictionary with ENumber
student_dict_sorted = {}
for key in sorted(student_dict):
    student_dict_sorted[key] = student_dict[key]

studentFilter_filename = "../projects/v1/filter/students/index.json"
os.makedirs(os.path.dirname(studentFilter_filename), exist_ok=True)

with open(studentFilter_filename, "w") as f:
    f.write(json.dumps(student_dict_sorted, indent = 4))
