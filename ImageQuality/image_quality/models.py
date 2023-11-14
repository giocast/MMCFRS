from tokenize import Name
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.enums import ChoicesMeta
from django.db.models.fields import AutoField, CharField, DateTimeField
from django.db.models.fields.related import ForeignKey
from .choices import *
from django.core.validators import MaxValueValidator, MinValueValidator
from django_countries.fields import CountryField
from multiselectfield import MultiSelectField

# Create your models here.


class Personal_info(models.Model):
    
    id = models.AutoField(primary_key=True)
    title = models.CharField(
        max_length=50,
        editable=False,
        default='Personal_info')

    created = models.DateTimeField(auto_now_add=True)

    age = models.CharField(max_length=120,
                           choices=Age_choices,
                           verbose_name='age',
                           default=None,
                           blank=False
                           )

    country = CountryField(blank_label='')

    education = models.CharField(max_length=120,
                                 choices=EducationLevel,
                                 verbose_name='education',
                                 default=None,
                                 blank=False

                                 )


    gender = models.CharField(max_length=300,
                              choices=Gender_choices,
                              verbose_name='gender',
                              default=None,
                              blank=False
                              )
    # FK_9 =  models.CharField(max_length = 300,
    #                          choices = FK__choices,
    #                          verbose_name = 'FK_9',
    #                          default=None,
    #                          blank = False)
    # FK_10 =  models.CharField(max_length = 300,
    #                          choices = FK__choices,
    #                          verbose_name = 'FK_10',
    #                          default=None,
    #                          blank = False)
    # FK_11 =  models.CharField(max_length = 300,
    #                          choices = FK__choices,
    #                          verbose_name = 'FK_11',
    #                          default=None,
    #                          blank = False)
    # FK_12 = models.CharField(max_length = 300,
 	# 		    choices = FK__choices,
	# 		  verbose_name = 'FK_12',
	# 		default = None,
	# 		blank = False)
    # # FK_13 = models.CharField(max_length = 300,
 	# 		    choices = FK__choices,
	# 		  verbose_name = 'FK_13',
	# 		default = None,
	# 		blank = False)
    # FK_14 = models.CharField(max_length = 300,
 	# 		    choices = FK__choices,
	# 		  verbose_name = 'FK_14',
	# 		default = None,
	# 		blank = False)
    # FK_15 = models.CharField(max_length = 300,
 	# 		    choices = FK__choices,
	# 		  verbose_name = 'FK_15',
	# 		default = None,
	# 		blank = False)
      




    # other_diet = models.CharField(("other_diet"), max_length=50, default='0')
    session_id = models.CharField(max_length=100, blank=False, default=None)
    class Meta:
        verbose_name = 'personal_info'
        ordering = ['id']
        db_table = 'personal_info'

    def __str__(self):
        return "{}".format(self.id)

class Ghs_fk(models.Model):
    id = models.AutoField(primary_key = True)
    title = models.CharField(max_length=50,
		editable=False,
                default='Cooking_knowledge')


    person = models.ForeignKey(
        Personal_info,
        on_delete = models.CASCADE
    )

    FK_9 = models.CharField(max_length = 300,
                            choices = FK__choices,
                            verbose_name = 'FK_1',
                            default = None,
                            blank = False)
    FK_10 = models.CharField(max_length = 300,
                            choices = FK__choices,
                            verbose_name = 'FK_2',
                            default = None,
                            blank = False)
    FK_11 = models.CharField(max_length = 300,
                            choices = FK__choices,
                            verbose_name = 'FK_3',
                            default = None,
                            blank =False)
    FK_12 =  models.CharField(max_length = 300,
                            choices = FK__choices,
                            verbose_name = 'FK_4',
                            default=None,
                            blank = False)
    
    CS_9 =  models.CharField(max_length = 300,
                             choices = FK__choices,
                             verbose_name = 'CS_9',
                             default=None,
                             blank = False)
    CS_10 =  models.CharField(max_length = 300,
                             choices = FK__choices,
                             verbose_name = 'CS_10',
                             default=None,
                             blank = False)
    CS_11 =  models.CharField(max_length = 300,
                             choices = FK__choices,
                             verbose_name = 'CS_11',
                             default=None,
                             blank = False)
    CS_12 = models.CharField(max_length = 300,
 			    choices = FK__choices,
			  verbose_name = 'CS_12',
			default = None,
			blank = False)
    CS_13 = models.CharField(max_length = 300,
 			    choices = FK__choices,
			  verbose_name = 'CS_13',
			default = None,
			blank = False)
    CS_14 = models.CharField(max_length = 300,
 			    choices = FK__choices,
			  verbose_name = 'CS_14',
			default = None,
			blank = False)

    class Meta:
        verbose_name = 'Ghs_fk'
        ordering = ['id']
        db_table = 'ghs_fk'
    
    def __str__(self):
    	return "{}".format(self.id)
    
    
 

  

class recipes(models.Model):
    id = models.IntegerField(primary_key=True)
    Name = models.CharField( max_length=1000)
    image_link = models.CharField( max_length=1000)
    attractiveness = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    
    
    class Meta:
        verbose_name = "recipes"
        ordering  = ['id']
        db_table = 'recipes'
    def __str__(self):
        return self.Name
        
class  recipesRating(models.Model):
    
    id = models.AutoField(primary_key=True)
    rating = models.CharField( max_length=500,
                              choices = ratings,
                              verbose_name = 'rating',
                              default=None,
                              blank = False
                              
                              )
    person = models.ForeignKey(
        Personal_info,
        on_delete=models.CASCADE
    )
    recipes = models.ForeignKey(
        recipes,
        on_delete=models.CASCADE
    )
    judging = models.CharField(
        max_length=500,
        verbose_name='judging',
        default=None,
        blank=False
    )
    seen = models.CharField(max_length=30, blank=True)
    created = models.DateTimeField(auto_now_add=True)	
    # seen = models.AutoField(
    #     primary_key=False
        
    # )
    class Meta:
        verbose_name = "Ratings"
        ordering  = ['id']
        db_table = 'recipesRatings'
        unique_together = (("person","recipes"))
    # def __str__(self):
    #     return self.recipes.Name


class Profile(models.Model):
    
    id = models.AutoField(primary_key=True)
    person = models.ForeignKey(
        Personal_info,
        on_delete=models.CASCADE
    )
    title = models.CharField(
        max_length=50,
        editable=False,
        default='Profile')
    
    Height = models.IntegerField()
    
    Weight = models.IntegerField()
    
    RecipeWebUsage =  models.CharField(max_length = 300,
 			choices = DayFrequency,
			verbose_name = 'RecipeWebUsage',
			default = None,
			blank = False)
    
    HomeCook = models.CharField(max_length = 300,
                                choices = DayFrequency,
                                verbose_name = 'HomeCook',
                                default = None,
                                blank = False
                                )
    CookingExp = models.CharField(max_length = 300,
                                choices = LowHighChoices,
                                verbose_name = 'CookingExp',
                                default = None,
                                blank = False
                                )
    EatingGoals = models.CharField(max_length = 300,
                                choices = EatingGoalsChoiecs,
                                verbose_name = 'HomeCook',
                                default = None,
                                blank = False
                                )
    Depression = models.CharField(max_length = 300,
                                choices = mood,
                                verbose_name = 'mood',
                                default = None,
                                blank = False
                                )
    PhysicalActivity = models.CharField(max_length = 300,
                                choices = PhyActi,
                                verbose_name = 'PhysicalActivity',
                                default = None,
                                blank = False
                                )
    SleepHours = models.CharField(max_length = 300,
                                choices = sleephours,
                                verbose_name = 'sleephours',
                                default = None,
                                blank = False
                                )
    CookingTime =  models.CharField(max_length = 300,
                                choices = CookingTime,
                                verbose_name = 'CookingTime',
                                default = None,
                                blank = False
                                )    


    class Meta:
        verbose_name = 'Profile'
        ordering = ['id']
        db_table = 'Profile'

    def __str__(self):
        return "{}".format(self.id)
    
    


class EvaluateChoices(models.Model):
    id = models.AutoField(primary_key=True)


    person = models.ForeignKey(
        Personal_info,
        on_delete=models.CASCADE
    )

    appearance = models.CharField(max_length=100,
        choices=FK__choices,
        verbose_name='appearance',
        default=None,
        blank=False
    )
    taste = models.CharField(max_length=100,
        choices=FK__choices,
        verbose_name='taste',
        default=None,
        blank=False
    )
    healthiness = models.CharField(max_length=100,
        choices=FK__choices,
        verbose_name='healthiness',
        default=None,
        blank=False
    )
    familiarity = models.CharField(max_length=100,
        choices=FK__choices,
        verbose_name='familiarity',
        default=None,
        blank=False
    )



    created = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=False, default=None)
    class Meta:
        verbose_name = 'EvaluateChoices'
        ordering = ['id']
        db_table = 'EvaluateChoices'

    def __str__(self):
        return "{}".format(self.id)
