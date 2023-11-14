#  (to_be stored, human readable)
 
 
 # ________________gender__________________


Age_choices = [
    (None,''),
        ('under_18','Under 18'),
        ('b18_24','18-24'),
        ('b25_35','25-35'),
        ('b35_45','35-45'),
        ('b45_55','45-55'),
        ('bover_55','Over 55')
    ]
DietRestrictions = [
    ('No_dietary_restrictions','No Dietary Restrictions'),
    ('Diabetes','Diabetes'),
    ('Gluten_free','Gluten-free'),
    ('Halal','Halal'),
    ('Kosher','Kosher'),
    ('Lactose_intolerance','Lactose intolerance'),
    ('Pescatarian','Pescatarian'),
    ('Vegetarian','Vegetarian'),
    ('Other','Other'),
    

]

DietGoal = [
    ('No_goals','No goals'),
    ('Eat_less_salt', 'Eat less salt'),
    ('Eat_less_sugar','Eat less sugar'),
    ('Eat_more_fruit', 'Eat more fruit'),
    ('Eat_more_protein', 'Eat more protein'),
    ('Eat_more_vegetables','Eat more vegetables'),
    ('Gain_weight','Gain weight'),
    ('Lose_weight','Lose weight'),
]

CookingExprience = [
    ('Very_Low','Very Low'),
    ('Low','Low'),
    ('Medium','Medium'),
    ('High','High'),
    ('Very High','Very high'),
    ]


EducationLevel=[
    (None,''),
    ('Less_high_school','Less than high school'),
    ('High_school','High school or equivalent'),
    ('BA','Bachelor degree (e.g. BA, BSc)'),
    ('MSc','Master degree (e.g. MA, MSc)'),
    ('Doctorate','Doctorate (e.g. PhD)'),
    ('Not','Prefer not to say'),
]


foodCategories =[
    (None, ''),
    # ('Salad','Salad'),
    ('Fruits and Vegetables','Fruits and Vegetables'),
    #('Seafood','Seafood'),
    ('Meat and Poultry','Meat and Poultry'),
    #('Pasta and Noodles','Pasta and Noodles'),
    # ('Soups and Chili','Soups and Chili'),
    ('Barbecue','Barbecue'),
    ('Seafood Pasta and Noodles','Seafood Pasta and Noodles')
]

(Str_D,Str_N)= ('Strongly_Disagree','Strongly Disagree')
(Dis_D,Dis_N)= ('Disagree','Disagree')
(Nt_D,Nt_N)= ('Neutral','Neutral')
(Ag_D,Ag_N)= ('Agree','Agree')
(StrAG_D,StrAG_N)= ('Strongly_Agree','Strongly Agree')






FK__choices = [ 
         (None, '')   ,   
        (Str_D,Str_N),
        (Dis_D,Dis_N),
        (Nt_D,Nt_N),
        (Ag_D,Ag_N),
        (StrAG_D,StrAG_N)
]


ratings = [
    (None, ''),
    ('1','1 Very Unattractive'),
    ('2','2'),
    ('3','3'),
    ('4','4'),
    ('5','5'),
    ('6','6'),
    ('7','7 Very Attractive')
]


#  (to_be stored, human readable)
 
 
 # ________________gender__________________
Gender_choices = [
        ('Male','Male'),
        ('Female','Female'),
        ('refuse_to_disc','Other / Prefer not to say')
    ]







EatingHabit = [
    ('Very_unhealthy','Very Unhealthy'),
    ('Unhealthy','Unhealthy'),
    ('Neither_healthy_no_unhealthy','Neither healthy, nor unhealthy'),
    ('Healthy','Healthy'),
    ('Very_Healthy','Very Healthy'),
]



DayFrequency = [
    (None, ''),
    ('Daily','Daily'),
    ('Weekly','Weekly'),
    ('Monthly','Monthly'),
]










FK__choices = [ 
        (None,''),
        (Str_D,Str_N),
        (Dis_D,Dis_N),
        (Nt_D,Nt_N),
        (Ag_D,Ag_N),
        (StrAG_D,StrAG_N)
]


LowHighChoices = [
    (None, ''),
    ('Very_Low', 'Very Low'),
    ('Low','Low'),
    ('Medium','Medium'),
    ('High','High'),
    ('Very_High', 'Very High')
]


EatingGoalsChoiecs = [
    (None, ''),
    ('Lose Weight','Lose Weight'),
    ('Gain Weight','Gain Weigh'),
    ('No Goal','No Goal'),
    
]
mood = [
    (None, ''),
    ('Not at all','Not at all'),
    ('Somewhat', 'Somewhat'),
    ('Quite a lot','Quite a lot'),
    # Not at all, somewhat, quite a lot
    
]
PhyActi = [
    (None, ''),
    ('A lot (>9h)','A lot >9h'),
    ('Average (=6h)', 'Average (=6h)'),
    ('Not enough (<3h)','Not enough (<3h)'),
]
sleephours = [
     (None, ''),
    ('≤7h', '≤7h'),
    ('7-9h', '7-9h'),
    ('≥9h', '≥9h'),
]
yesno=  [

    ('Yes', 'Yes'),
    ('No', 'No'),
]
CookingTime = [
    (None, ''),
    ('≤30min', '≤30min'),
    ('30-60min', '30-60min'),
    ('≥60min', '≥60min'),

]