import pandas as pd
import jobs as jobs_data
df=pd.DataFrame(jobs_data.jobs)
print(df)
name=input("Enter your name: ")
skills=input("Enter your skills : ").split()
joberole=input("Enter your desired job role: ")