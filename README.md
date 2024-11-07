This project scrapes recent clinical trials from https://clinicaltrials.gov/ and https://www.clinicaltrialsregister.eu/ctr-search/search?query=&dateFrom=2022-01-01&dateTo=2024-11-05. The results are updated every 12 hours and displayed in a table.
<img width="1313" alt="Screenshot 2024-11-06 at 5 02 39 PM" src="https://github.com/user-attachments/assets/6a320610-b186-4adf-b833-be99b28571f2">


Insights from the table are generated in another tab.
<img width="1217" alt="Screenshot 2024-11-06 at 5 03 14 PM" src="https://github.com/user-attachments/assets/3822fa01-9b77-4b19-ba56-926420c4452d">

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).
<img width="1255" alt="Screenshot 2024-11-06 at 5 03 24 PM" src="https://github.com/user-attachments/assets/530c20f3-6a56-4397-aa7b-8ae2cd7c2ab1">

## Getting Started

After cloning the repo, the following code will install all necessary requirements (as well as installing npm and Node.js):
```pip install -r requirements.txt```

You will additionall need a .env file with the NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY, and you will need to update the connection variables in lambda_function.py to run this code. 



