# Instructor Assistant App

A tool to help PADI Scuba Diving Instructors complete the 'Record and Referral' form.

<div align="center">
<img src="Record_and_Referral_Form-1.png" height="300">
</div>
  

# Overview

"PADI® (Professional Association of Diving Instructors®) is the world’s largest ocean exploration and diver organization, operating in 186 countries and territories, with a global network of more than 6,600 dive centers and resorts and over 128,000 professional members worldwide. Issuing more than 1 million certifications each year, and with over 29 million certifications to date". https://www.padi.com/about/who-we-are

PADI Scuba Diving Instructors are required to complete the 'Record_and_Referral_Form' for every student after the PADI Open Water Course. The Instructor Assistant App aims to make that process fast and easy. By hand, completing one form takes approximately 8 - 10mins per student and 1 hour for a class of 6 students. With this tool Instructors will be able to complete paperwork for a full class in less then 5 minutes. 


# Description

### Save Instructor Details 

Add, delete and save your instructor details for future use.  After your password verification the Instructor Assistant App will automatically complete the required fields.  Keep in mind you will still need to physically sign the Instructor signature fields afterwords.   

<div align="center">
<img src="screengif.gif">

</div>

### Use Dive Templates

Customize and store templates to complete faster.  Each Instructor has a unique way of conducting the PADI Open Water Course and often repeats a similar course schedule.  For example, for the Confined Water One dive an Instructor may also complete Knowledge Review Section One, 200m swim and the 10min float on the same day.  Templates allow you to save these matching date pairs so you'll only need to complete the Confined Water One field date.  After pressing the "Set Template" button the subsequent date pairs will be updated.

### Import Student Information
The option to import bulk student information is available.  Currently the Instructor Assistant App supports imports from an excel file with the following column headings.

```
'first_name' 
'last_name'
'date_of_birth' 
'sex'
'phone' 
'email'
'street_address'
'city'
'province'
'postal'
'country'
```

For the 'date_of_birth' column data can be in a `datetime` or `string` format.  Use the 'dd/mm/yyyy' format when using strings.  

<div align="center">
<img src="student_import_example.png">

</div>

special thanks to @ryannayang 




  
