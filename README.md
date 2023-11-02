# Wave Software Development Challenge

Applicants for the Full-stack Developer role at Wave must
complete the following challenge, and submit a solution prior to the onsite
interview.

The purpose of this exercise is to create something that we can work on
together during the onsite. We do this so that you get a chance to collaborate
with Wavers during the interview in a situation where you know something better
than us (it's your code, after all!)

There isn't a hard deadline for this exercise; take as long as you need to
complete it. However, in terms of total time spent actively working on the
challenge, we ask that you not spend more than a few hours, as we value your
time and are happy to leave things open to discussion in the on-site interview.

Please use whatever programming language and framework you feel the most
comfortable with.

Feel free to email [dev.careers@waveapps.com](dev.careers@waveapps.com) if you
have any questions.

## Project Description

Imagine that this is the early days of Wave's history, and that we are prototyping a new payroll system API. A front end (that hasn't been developed yet, but will likely be a single page application) is going to use our API to achieve two goals:

1. Upload a CSV file containing data on the number of hours worked per day per employee
1. Retrieve a report detailing how much each employee should be paid in each _pay period_

All employees are paid by the hour (there are no salaried employees.) Employees belong to one of two _job groups_ which determine their wages; job group A is paid $20/hr, and job group B is paid $30/hr. Each employee is identified by a string called an "employee id" that is globally unique in our system.

Hours are tracked per employee, per day in comma-separated value files (CSV).
Each individual CSV file is known as a "time report", and will contain:

1. A header, denoting the columns in the sheet (`date`, `hours worked`,
   `employee id`, `job group`)
1. 0 or more data rows

In addition, the file name should be of the format `time-report-x.csv`,
where `x` is the ID of the time report represented as an integer. For example, `time-report-42.csv` would represent a report with an ID of `42`.

You can assume that:

1. Columns will always be in that order.
1. There will always be data in each column and the number of hours worked will always be greater than 0.
1. There will always be a well-formed header line.
1. There will always be a well-formed file name.

A sample input file named `time-report-42.csv` is included in this repo.

### What your API must do:

We've agreed to build an API with the following endpoints to serve HTTP requests:

1. An endpoint for uploading a file.

   - This file will conform to the CSV specifications outlined in the previous section.
   - Upon upload, the timekeeping information within the file must be stored to a database for archival purposes.
   - If an attempt is made to upload a file with the same report ID as a previously uploaded file, this upload should fail with an error message indicating that this is not allowed.

2. An endpoint for retrieving a payroll report structured in the following way:

   _NOTE:_ It is not the responsibility of the API to return HTML, as we will delegate the visual layout and redering to the front end. The expectation is that this API will only return JSON data.

   - Return a JSON object `payrollReport`.
   - `payrollReport` will have a single field, `employeeReports`, containing a list of objects with fields `employeeId`, `payPeriod`, and `amountPaid`.
   - The `payPeriod` field is an object containing a date interval that is roughly biweekly. Each month has two pay periods; the _first half_ is from the 1st to the 15th inclusive, and the _second half_ is from the 16th to the end of the month, inclusive. `payPeriod` will have two fields to represent this interval: `startDate` and `endDate`.
   - Each employee should have a single object in `employeeReports` for each pay period that they have recorded hours worked. The `amountPaid` field should contain the sum of the hours worked in that pay period multiplied by the hourly rate for their job group.
   - If an employee was not paid in a specific pay period, there should not be an object in `employeeReports` for that employee + pay period combination.
   - The report should be sorted in some sensical order (e.g. sorted by employee id and then pay period start.)
   - The report should be based on all _of the data_ across _all of the uploaded time reports_, for all time.

As an example, given the upload of a sample file with the following data:

   | date       | hours worked | employee id | job group |
   | ---------- | ------------ | ----------- | --------- |
   | 4/1/2023   | 10           | 1           | A         |
   | 14/1/2023  | 5            | 1           | A         |
   | 20/1/2023  | 3            | 2           | B         |
   | 20/1/2023  | 4            | 1           | A         |

A request to the report endpoint should return the following JSON response:

   ```json
   {
     "payrollReport": {
       "employeeReports": [
         {
           "employeeId": "1",
           "payPeriod": {
             "startDate": "2023-01-01",
             "endDate": "2023-01-15"
           },
           "amountPaid": "$300.00"
         },
         {
           "employeeId": "1",
           "payPeriod": {
             "startDate": "2023-01-16",
             "endDate": "2023-01-31"
           },
           "amountPaid": "$80.00"
         },
         {
           "employeeId": "2",
           "payPeriod": {
             "startDate": "2023-01-16",
             "endDate": "2023-01-31"
           },
           "amountPaid": "$90.00"
         }
       ]
     }
   }
   ```

We consider ourselves to be language agnostic here at Wave, so feel free to use any combination of technologies you see fit to both meet the requirements and showcase your skills. We only ask that your submission:

- Is easy to set up
- Can run on either a Linux or Mac OS X developer machine
- Does not require any non open-source software
- Includes all the source code you write for the submission, including any models used for setting up your database

### Documentation:

Please commit the following to this `README.md`:

1. Instructions on how to build/run your application
1. Answers to the following questions:
   - How did you test that your implementation was correct?
   - If this application was destined for a production environment, what would you add or change?
   - What compromises did you have to make as a result of the time constraints of this challenge?

## Instructions

I used a virtual environment to run the project but have included a `requirements.txt` file instead for testing without it.

### Virtual Environment setup

1.  If you don't have `pipenv` installed, you can install it using pip:

   ```bash
   pip install pipenv
   ```

2. Install the project's dependencies:

   ```bash
   pipenv install
   ```

   - This will create a virtual environment and install the required packages specified in the `Pipfile.lock`.

3. Exit the environment at any time with `exit` and re-activate it with:

   ```
   pipenv shell
   ```

### requirements.txt

- Install dependencies with:

  ```
  pip install -r requirements.txt
  ```

### Build/Run

1. In the root folder create and make database migrations:

   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

   - A db.sqlite3 database file should be created.

2. Run the project:

   ```
   python manage.py runserver
   ```

   - The app should be available on `localhost:8000`.

3. Send curl requests to test the endpoints. On Windows:

   ```bash
   curl -X POST -F "csv_file=@time-report-42.csv" http://127.0.0.1:8000/upload-csv/
   curl -X GET http://127.0.0.1:8000/payroll-reports/
   ```

## Answers

1. Tests were implemented for core functionality. They are located within `test.py`. These can be run with:

   ```bash
   python manage.py test payroll
   ```

   - These test could be extended as noted in some comments.

2. Some comments already hint at this but having more error handling like CSV content checking or data validation throughout is the obvious answer.

   - Additionally duplication issues are to be considered. A report with identical data could be entered with a different id.
   - Some standard API documentation of the endpoints could be added.
   - Depending on the scale of the expected database, queries could become inefficient and optimization might be needed. A production ready database like Postgres could be used instead, indexing could be added, saved queries into it's own database.
   - If extensibility of this feature was in mind I might design the implementation slightly differently.
     - I would have an Employee table that is saved to when reports are uploaded that has all these calculated and transformed values already. 
     - Then report generation doesn't need to recalculate anything and can only consist of filters and queries based on employees, time spans, job types, paid amounts, etc. Custom queries would likely be an obvious extension.
   - There are plenty of other production considerations that could be relevant like authentication may be required, or adding to automated testing pipelines, or load/performance/concurrency tests.
   - Oh, and of course the DEBUG flag should be set to False :)

3. I did what I thought was feature complete for the scope but as noted above, extra care should be taken in validation and duplicates.

   - Further "separation of concerns" can be done by moving logic out where needed.
     - A validation function instead of it being all under the post function.
     - Like specified earlier the get request doesn't have to calculate all the json values if they're already saved in a database and optimization is needed.

## Submission Instructions

1. Clone the repository.
1. Complete your project as described above within your local repository.
1. Ensure everything you want to commit is committed.
1. Create a git bundle: `git bundle create your_name.bundle --all`
1. Email the bundle file to [dev.careers@waveapps.com](dev.careers@waveapps.com) and CC the recruiter you have been in contact with.

## Evaluation

Evaluation of your submission will be based on the following criteria.

1. Did you follow the instructions for submission?
1. Did you complete the steps outlined in the _Documentation_ section?
1. Were models/entities and other components easily identifiable to the
   reviewer?
1. What design decisions did you make when designing your models/entities? Are
   they explained?
1. Did you separate any concerns in your application? Why or why not?
1. Does your solution use appropriate data types for the problem as described?
