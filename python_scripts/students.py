# REQUIREMENTS ------------
# pip install requests
# -------------------------

# TODO:
# No validation done by assume everything is ok,
# But better to write validation logic too

import requests
import json
import os
import shutil

# Where the API is available
apiIndex = 'https://api.ce.pdn.ac.lk/people/v1/'

# Where the data is available
apiSource = 'https://people.ce.pdn.ac.lk/api/students/'

# Validate and format the registration number


def validateRegNumber(regNumber):
    if len(regNumber) == 2:
        regNumber = '0' + regNumber
    elif len(regNumber) == 1:
        regNumber = '00' + regNumber

    return regNumber

# Split the email address into 2 fields


def emailFilter(email):
    words = email.split('@')
    # There could be something else than a email in that field
    if len(words) == 2:
        return {'name': words[0], 'domain': words[1]}
    elif len(words) > 0:
        # if its something else. just send it as the name
        return {'name': email, 'domain': ""}
    else:
        return {'name': "", 'domain': ""}

# Delete the existing files first
def del_old_files():
    dir_path = "../people/v1/students/"
    try:
        shutil.rmtree(dir_path)
    except error as e:
        print("Error!")

# Write the /students/index.json


def write_index(batch_groups):
    dict = {}
    for batch in batch_groups:
        url = apiIndex + 'students/' + batch + '/'
        count = len(batch_groups[batch].keys())
        dict[batch] = {'batch': batch, 'url': url, 'count': count}

    filename = "../people/v1/students/index.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(json.dumps(dict, indent=4))

# Write the /students/{batch}/index.json files


def write_batches(batch_groups):
    for batch in batch_groups:
        filename = "../people/v1/students/" + batch.upper() + "/index.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        data = {}

        for student in batch_groups[batch]:
            regNumber = validateRegNumber(batch_groups[batch][student]['eNumber'].split('/')[2])
            url = apiIndex + 'students/' + batch.upper() + '/' + regNumber + '/'
            data[student] = {'url': url}

        with open(filename, "w") as f:
            f.write(json.dumps(data, indent=4))

# Write the /students/{batch}/{regNumber}/index.json files


def write_students(batch, batch_group):
    for student in batch_group:
        eNumber = batch_group[student]['eNumber'].upper()
        regNumber = validateRegNumber(eNumber.split('/')[2])

        filename = "../people/v1/students/" + batch.upper() + "/" + regNumber + "/index.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # print(json.dumps(batch_group[student], indent = 4))
        with open(filename, "w") as f:
            f.write(json.dumps(batch_group[student], indent=4))


def write_all(batch_groups):
    data_all = {}

    for batch in batch_groups:
        for student in batch_groups[batch]:
            eNumber = batch_groups[batch][student]['eNumber'].upper()
            data_all[eNumber] = batch_groups[batch][student]

    filename = "../people/v1/students/all/index.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # print(json.dumps(batch_groups[batch], indent = 4))

    with open(filename, "w") as f:
        f.write(json.dumps(data_all, indent=4))


# ------------------------------------------------------------------------------

# Delete the existing files first
del_old_files()

r = requests.get(apiSource)
batch_groups = {}

# Fetch data from the people.ce.pdn.ac.lk
if r.status_code == 200:
    data = json.loads(r.text)
    # print(data)

    for eNumber in data:
        # print(data[eNumber])

        # Split the email address to avoid spaming
        data[eNumber]['emails']['personal'] = emailFilter(data[eNumber]['emails']['personal'])
        data[eNumber]['emails']['faculty'] = emailFilter(data[eNumber]['emails']['faculty'])

        batch = data[eNumber]['batch']
        if batch not in batch_groups:
            batch_groups[batch] = {}
        batch_groups[batch][eNumber] = data[eNumber]


# Write the index file for the students
write_index(batch_groups)

# Create files for each batch
write_batches(batch_groups)

# Write individual student files
for batch in batch_groups:
    write_students(batch, batch_groups[batch])

write_all(batch_groups)
