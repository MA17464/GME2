I want to create a django application for Residency and Fellowship programs "Graduate Medical Education" (gme) for the King Hussein Cancer Center


## Welcome Page:
* Two windows for Residency and Fellowship programs info
* Two buttons for Login and Register

## Users:
There're two main user types:
-> KHCC Staff
    -> GME Staff (System Admin)
    -> Program Director
    -> Interviewer
-> Non-KHCC Staff (Applicant)


* The KHCC Staff users when signed up, the GME Staff should approve their account to continue. and their email should be "@khcc.jo"
* The Non-KHCC staff can register without approval.

For Interviewer and Program Director roles they have to choose the department they are in:
- Internal Medicine Department
- Pediatrics Department 
- General Surgery Department
- Radiation Oncology Department
- Pathology and Laboratory Medicine Department
- Nuclear Medicine Department
- Diagnostic Radiology Department
- Anesthesia Department

* Make a login and registration page.

## Dashboard:
* Only GME Staff can see and filter the applications for the programs and set eligibility and approval status.
* the GME staff can select in bulk and filter the applications for the programs to send emails to the applicants (add a button to send emails and the ability to add a subject and body to the email).

## GME Staff:
* GME Staff can approve or reject the KHCC Staff accounts.
* GME Staff can create the Residency or Fellowship programs (name, type, capacity, start date, end date, status, etc...).
* GME Staff checks the documents and eligibility of the applications for the programs and approve or reject them.

## Applicant:
* Applicant can apply only for one program at a time.
* Applicant can view the application status and info.

## Program Form:
- Name (department name)
- Program Type (Residency, Fellowship)
- Start Date
- End Date
- Status (active, inactive)
- Capacity

## Application Form:
Program Selection
- Program Type
- Select Program

Education Information
- University Name
- GPA (either in percentage or scale of 4)

Required Documents (handle the naming of the documents)
- National ID/Identification Card
- Curriculum Vitae (CV)
- Payment Receipt
- University Certificate

Personal Information
- Name in English
- First Name (English)
- Second Name (English)
- Third Name (English)
- Last Name (English)
- Name in Arabic
- Last Name (Arabic)
- Third Name (Arabic)
- Second Name (Arabic)
- First Name (Arabic)

Contact Information
- Phone Number
- National ID


## Application Status:
* Application Status
- Submitted
- Eligible
- Not Eligible
- Approved
- Rejected