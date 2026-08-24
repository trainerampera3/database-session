import pandas as pd

df = pd.read_csv('./data/Enhanced_Gym_Dataset_10000.csv')
branches = df['Branch'].unique()
trainers = df['TrainerAssigned'].unique()
diet_plan = df['DietPlan'].unique()
fitness = df['FitnessGoal'].unique()
plan = df['PlanType'].unique()

goal_ids = {
    "Athlete Training": "GO26AT",
    "Weight Loss": "GO26WL",
    "Fitness": "GO26FT",
    "Muscle Gain": "GO26MG"
}

trainer_ids = {
    "Trainer A": "TRA26A",
    "Trainer B": "TRA26B",
    "Trainer C": "TRA26C",
    "Trainer D": "TRA26D",
    "Trainer E": "TRA26E"
}

diet_ids = {
    "Standard": "DP26ST",
    "Keto": "DP26KT",
    "High Protein": "DP26HP",
    "Muscle Gain": "DP26MG",
    "Weight Loss": "DP26WL"
}

branch_ids = {
    "North": "BR26NO",
    "South": "BR26SU",
    "East": "BR26ES",
    "West": "BR26WE",
    "Downtown": "BR26DT"
}

plan_ids = {
    "Half-Yearly": "PLAHY",
    "Monthly": "PLAMN",
    "Annual": "PLAAN",
    "Quarterly": "PLAQU"
}

def insert(conn):
    
    with conn.cursor() as cur:

#       for i in plan:
#         
#         cur.execute("insert into plans(plan_id, plan_type) values(%s, %s)", [plan_ids.get(i), i])

        for i in diet_plan:
            cur.execute("insert into dietplan(diet_id, diet_name) values(%s, %s)", [diet_ids.get(i), i])

        for i in trainers:

            cur.execute("insert into trainers(trainer_id, trainer_name) values(%s, %s)", [trainer_ids.get(i), i])

        for i in branches:

            cur.execute('insert into branch(branch_id, branch_name) values(%s, %s)',[branch_ids.get(i), i])

        for i in fitness:

            cur.execute('insert into goals(goal_id, goal_name) values(%s, %s)',[goal_ids.get(i), i])


        for row in df.itertuples(index=False):
            cur.execute('insert into customer(cust_id, fullname, age, gender, joindate, expirydate, renewal_status, trainer_id, branch_id, goal_id, plan_id, diet_id ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[ row.MembershipNumber, row.FullName,row.Age, row.Gender,row.JoinDate, row.ExpiryDate, row.RenewalStatus, trainer_ids.get(row.TrainerAssigned), branch_ids.get(row.Branch), goal_ids.get(row.FitnessGoal), plan_ids.get(row.PlanType), diet_ids.get(row.DietPlan)] )

        conn.commit()

        print('Values inserted Successfullly')


