Create a Django application for Residency and Fellowship programs under Graduate Medical Education (GME) at King Hussein Cancer Center (KHCC). The application will manage users, program applications, and roles for both KHCC staff and non-KHCC applicants.
Make sure to implement the backend and frontend for the application, and make sure the UI and UX are professional, clean and modern.

---

## Pages:

### **Welcome Page:**
- Two windows displaying information for:
  - Residency Programs
  - Fellowship Programs
- Two buttons for Login and Registration

---

## **User Types:**

1. **KHCC Staff Users**:
   - **GME Staff (System Admin)**  
   - **Program Director**  
   - **Interviewer**

2. **Non-KHCC Staff (Applicant)**

---

### **User Registration and Approval:**

- **KHCC Staff**:  
   - When registering, accounts must be approved by GME Staff.  
   - Email addresses must follow the format `@khcc.jo`.

   - The "Interviewer" and "Program Director" roles must select the program they are interviewing for
  
- **Non-KHCC Staff (Applicants)**:  
   - No approval required to register.

---

### **Login and Registration Pages**:  
- Standard login and registration functionality.

---

## **Dashboard**:

- Only **GME Staff** can access the dashboard.
- **GME Staff** can:
   - Filter and view applications for Residency and Fellowship programs.
   - Set eligibility and approval status for each application.
   - Bulk select applications and send emails to applicants (with customizable subject and body).

---

## **GME Staff Capabilities**:

- **Account Management**:
   - Approve or reject KHCC Staff accounts.
   
- **Program Management**:
   - Create and manage Residency or Fellowship programs with fields like:
     - Program Name
     - Program Type (Residency/Fellowship)
     - Start Date
     - End Date
     - Status (active/inactive)
   
- **Application Management**:
   - Review documents and eligibility for applications.
   - Approve or reject applications.

---

## **Applicant Capabilities**:

- Applicants can apply for **only one program at a time**.
- They can view their application status and program details.

---

## **Program Form**:

- Program fields to be filled by GME Staff when creating a program:
   - **Name**
   - **Program Type** (Residency/Fellowship)
   - **Start Date**
   - **End Date**
   - **Status** (Active/Inactive)

---

## **Application Form**:

1. **Program Selection**:
   - **Program Type** (Residency/Fellowship)
   - **Select Program**

2. **Education Information**:
   - University Name
   - GPA (Satisfactory, Good, Very Good, Excellent)

3. **Required Documents**:
   - National ID/Identification Card
   - Curriculum Vitae (CV)
   - Payment Receipt
   - University Certificate

4. **Personal Information**:
   - Name in English and Arabic (First, Second, Third, Last Name in both languages)

5. **Contact Information**:
   - Phone Number
   - National ID

---

## **Application Status**:

- The application can have one of the following statuses:
   - Submitted
   - Eligible
   - Not Eligible
   - Approved
   - Rejected


the ability for the applicant to draft their application and submit it later.

the ability for bulk choosing in the dashboard.

more filtering options (scores, gpa, program, status)

add the following status:
   - Invited for interview

the gme can upload a csv/excel file of the applicants national ID with their scores, and they will be autmomatically matched to the applicants profiles.

the gme can edit the applicants status in bulk.

after the scoring, the gme role can filter the scores and bulk select the ones to invite interview.

the interviewer dashboard only shows the "Invited for Interview" applicants for their registered program. 

for Interviewers:
- the interviewer dashboard only shows the "Invited for Interview" applicantions for their registered program. 
- the interviewer scores the applicants according to the intervieweing form below.


Residency Program Scoring Form (for interviewers):
```
Interview Area	Score
Professional Appearance:
Dress, attitude, avoid cross-legging, less stress, no stuttering …est	/ 5
Interest:
Why you choose this specialty? (should give details)
Why our institution? (should be aware of the surgical and medical practices of the center)	/ 5
Behavior:
“Tell me about one experience with patient you had trouble with”
“Tell me about one experience you made a mistake and had to tell a colleague about it”
“How would you deal with a resident who did not do his share of work”	/ 5
Future Plans:
“Where do you see yourself in 5 years”
“How would this training develop your career” 	/ 5
Personality:
“Tell me about your strengths and weaknesses”
“Tell me about one case you learned from”
“What do you do in your free time?”	/ 5
Handling emergencies and work load
Ask candidate about clinical scenarios (candidate should show his/her fast step in emergency cases to insure patient safety)	/ 5
Professional Attitude:
“Tell me about a time your work was criticized/ how did you react?”
“Tell me about a stressful situation you have been through and how you solved it”	/ 5
Knowledge:
“Ask about one clinical scenario related to specialty applied for and ask the applicant for differential diagnosis and next step management”	/ 5
Research:
One or more published papers = 5 marks
Ongoing project (IRB approved) = 2 mark	/5

Evaluation Area	Score
Test score	/ 75
Interview score	/ 15
Medical School Score:
Excellent        = 10 marks
Very Good     = 8 marks
Good              = 6 marks
Satisfactory = 4 marks	/10
Total Score	/ 100

```

Fellowship Program Scoring Form (for interviewers):
```
Interview Area	Score
Professional Appearance:
Dress, attitude, avoid cross-legging, less stress, no stuttering …etc.	/ 5
Interest:
Why you choose this specialty? (should give details)
Why our institution? (should be aware of the surgical and medical practices of the center)	/ 5
Behavior:
“Tell me about one experience with patient you had trouble with”
“Tell me about one experience you made a mistake and had to tell a colleague about it”
“How would you deal with a resident who did not do his share of work”	/ 5
Future Plans:
“Where do you see yourself in 5 years”
“How would this training develop your career” 	/ 5
Personality:
“Tell me about your strengths and weaknesses”
“Tell me about one case you learned from”
“What do you do in your free time?”	/ 5
Handling emergencies and work load
Ask candidate about clinical scenarios (candidate should show his/her fast step in emergency cases to insure patient safety)	/ 5
Professional Attitude:
“Tell me about a time your work was criticized/ how did you react?”
“Tell me about a stressful situation you have been through and how you solved it”	/ 5
Knowledge:
“Ask about one clinical scenario related to specialty applied for and ask the applicant for differential diagnosis and next step management”	/ 5
Research:
One or more published papers = 5 marks
Ongoing project (IRB approved) = 2 mark	/10
Tentative Available Date:	
Final Total l	/ 50

Evaluation Area	Score
Interview score	/ 50
Test score (written/Oral)	/ 40
Medical School Score:
Excellent        = 10 marks
Very Good     = 8 marks
Good              = 6 marks
Satisfactory = 4 marks	/10
Total Score	/ 100
```