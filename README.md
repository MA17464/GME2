# KHCC Medical Programs Application System

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
   - **Bulk choose applications** for further processing.
   - Access **advanced filtering options** (scores, GPA, program, status).
   - **Upload CSV/Excel files** containing applicant National IDs with scores for automatic matching.
   - **Edit applicant status in bulk**.
   - **Filter scores and bulk select applicants** to invite for interviews.

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
   - **Invite applicants for interviews**.

---

## **Applicant Capabilities**:

- Applicants can apply for **only one program at a time**.
- They can view their application status and program details.
- They can **save applications as drafts** and submit them later.

---

## **Interviewer Capabilities**:

- Access a dashboard showing **only "Invited for Interview" applicants** for their registered program.
- Score applicants according to the appropriate interview scoring form (Residency or Fellowship).

---

## **Program Director Capabilities**:

- Access a dashboard showing **"Invited for Interview" applicants** for their program.
- View interview results and scores submitted by interviewers.
- See the average interview score for each applicant displayed in the dashboard.
- Conduct final review and submit the applicant's final score after all interviews are completed.

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
   - Payment Receipt (Required for Residency, Not Required for Fellowship)
   - University Certificate (Required for Residency, Not Required for Fellowship)
   - Board Certification (Optional, Fellowship Only)

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
   - **Invited for Interview**

---

## **Interview Scoring Forms**:

### **Residency Program Scoring Form**:

| Interview Area | Score |
|----------------|-------|
| **Professional Appearance**: <br>Dress, attitude, avoid cross-legging, less stress, no stuttering, etc. | / 5 |
| **Interest**: <br>Why you choose this specialty? (should give details)<br>Why our institution? (should be aware of the surgical and medical practices of the center) | / 5 |
| **Behavior**: <br>"Tell me about one experience with patient you had trouble with"<br>"Tell me about one experience you made a mistake and had to tell a colleague about it"<br>"How would you deal with a resident who did not do his share of work" | / 5 |
| **Future Plans**: <br>"Where do you see yourself in 5 years"<br>"How would this training develop your career" | / 5 |
| **Personality**: <br>"Tell me about your strengths and weaknesses"<br>"Tell me about one case you learned from"<br>"What do you do in your free time?" | / 5 |
| **Handling emergencies and work load**: <br>Ask candidate about clinical scenarios (candidate should show his/her fast step in emergency cases to ensure patient safety) | / 5 |
| **Professional Attitude**: <br>"Tell me about a time your work was criticized/ how did you react?"<br>"Tell me about a stressful situation you have been through and how you solved it" | / 5 |
| **Knowledge**: <br>"Ask about one clinical scenario related to specialty applied for and ask the applicant for differential diagnosis and next step management" | / 5 |
| **Research**: <br>One or more published papers = 5 marks<br>Ongoing project (IRB approved) = 2 marks | / 5 |

| Evaluation Area | Score |
|-----------------|-------|
| Test score | / 75 |
| Interview score | / 15 (45 divided by 3)|
| **Medical School Score**: <br>Excellent = 10 marks<br>Very Good = 8 marks<br>Good = 6 marks<br>Satisfactory = 4 marks | / 10 |
| **Total Score** | / 100 |

### **Fellowship Program Scoring Form**:

| Interview Area | Score |
|----------------|-------|
| **1. Professionalism**: <br>Appearance and attitude (Dress, avoid cross-legging, less stress, no stuttering, friendly, collegial) | / 5 |
| **2. Time management and managing work load**: <br>• How do you plan your work when you have multiple conflicting tasks?<br>• Tell me about a project where the deadline was approaching and you still needed more time. How did you approach that with your senior and colleagues? | / 5 |
| **3. Flexibility and Team Work**: <br>• Give one example of when your priorities changed quickly – how did you deal with it?<br>• Give me an example of a team member that was acting in a way that you perceived as negative to patient care or project outcomes. | / 5 |
| **4. Takes feedback appropriately**: <br>• Tell me about a time when you disagreed with the evaluation you received from your mentor and how you handled it? | / 5 |
| **5. Stress Coping**: <br>• Give me an example of situation that upset you and how did you react to the situation.<br>• Tell me about a time when you had to adopt to handle a stressful situation? | / 5 |
| **6. Problem Solving**: <br>• Give me a specific example of when you solved a tough problem?<br>• Give me an example of when you were able to see and implement a new way of doing things in your position/company/department how you accomplish this and what was the outcome? | / 5 |
| **7. Leadership**: <br>• Give me an example of strategy you have used to motivate others.<br>• Tell me about a time when your team had to work on a tight deadline. How did you ensure everyone complete their work on time? | / 5 |
| **8. Interest and Future plans**: <br>• Why you choose this specialty? (should give details)<br>• Why our institution? (should be aware of the practices of KHCC)<br>• What is your 5-year or 10-year plan? How does our program fit into that? | / 5 |
| **Tentative Available Date**: | |

**Scoring scale for each category:**<br>
Poor (-1) | Average (1-2) | Good (3-4) | Excellent (5) | Not sure (0)

| Evaluation Area | Score |
|-----------------|-------|
| Test score | / 60 |
| Interview score | / 40 |
| **Total Score** | / 100 |

**- The Interview Score is the sum of all the scores in the interview form (maximum 40 points).**
**- Test Score is automatically taken from the score that was uploaded by the GME Staff in the upload scores page.**
**- The Total Score is calculated as the sum of Interview Score and Test Score (maximum 100 points).**

---
