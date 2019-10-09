import pandas as pd 
import itertools, time

dataset_walmart = pd.read_csv('Datasets/Walmart.csv')
dataset_7_11 = pd.read_csv('Datasets/7-11.csv')
dataset_esty = pd.read_csv('Datasets/Esty.csv')
dataset_k_mart = pd.read_csv('Datasets/K-mart.csv')

datasets = [dataset_walmart, dataset_7_11, dataset_esty, dataset_k_mart]

'''Custom Exceptions Definition'''
#custom numeric exception for range value issues. 
class customNumericException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

'''Take inputs for Support and Confidence. Also handle numeric exceptions. '''
support = confidence = 40
#Flag to trigger support or confidence input sequence/event
action = 1 
#an infite loop for input sequence
while True: 
    try: 
        if(action): 
            support = int(input("Enter Support Value(0-100):"))
            #check if the support value is in the range, otherwise trigger the custom exception with message.
            if support<0 or support>100: 
                raise customNumericException({"support"})
            else:
                #if support is in the range, then check the flag value and skip the loop execution for the later part.
                action = 0
                continue

        else:
            confidence = int(input("Enter Confidence Value(0-100):"))
            #check if the support value is in the range, otherwise trigger the custom exception with message.
            if confidence<0 or confidence>100: 
                raise customNumericException({"confidence"})
            # No need to change the flag value as the confidence value can only be taken after the support has been given.
        
        #break the loop when both values have been recived in the range correctly.
        break

    #in-bulit exception for numeric value error
    except ValueError:
        print("Only Numeric Values are allowed. ")

    #custom exception to handle range issues. 
    except customNumericException as e:
        #e.message has our message argument given from the raise statement. 
        message = e.message.pop()
        print("Wrong range for " + message + " Values. Range is 0-100") 
        #change the action flag bit according to the message value
        action = 1 if message == "support" else 0 

#Print support and confidence values.
print("Support and confidence values have been taken:" , support, confidence)

'''
Function Definitions
'''
#get association sets of number r using itertools combinations
def getAssociationSet(arr, r):
    return list(itertools.combinations(arr, r))

#indices to delete from the list with respect to the support value selected. 
def delete_indices(i, support):
    del_indices = []

    #loop for adding the indices to the del_indices
    j = 0
    for x in L[i][1]:
        if x < support:
            del_indices.append(j)   
        j +=1

    return del_indices 


#The List C has the association names
C = []

#The List L has the association names and support values
#L[][0] = Association Values, L[][1] = Support values
L = []

#First association set 
product_list = list(dataset_walmart.columns.values)
C.append(product_list)
L.append([product_list,list(dataset_walmart.sum(axis=0, skipna=True)/0.2)])


#call the functions to figure out the indices to delete from L where support value is low
del_indices = delete_indices(0, support)
#check the defintion of L to understand what is being enumerated. Basically we are removing the indices which has lesser
#support values for the association set.
C[0] = L[0][0] = [x for  i, x  in enumerate(L[0][0]) if i not in del_indices]
L[0][1] = [x for  i, x  in enumerate(L[0][1]) if i not in del_indices]

i = 0 
while True:
    
    #add combination values to a variable called temp_c; because we are going to manipulate the values, so a temporary value.
    temp_c = getAssociationSet(list(C[0]), i+2)
    #Now, add those association values to a list named C
    C.append(list(temp_c))

    #create a temporary list called temp_l
    temp_l = []

    #loop through all the possible association values from temp_c
    for s in temp_c:
        #dataset_walmart[list(s)] =  Association Combination
        # .eq(1, axis ='index') = check on indexes for value 1 
        # .all(1) = for all columns [This is a condition which gives answer only and only if the output is common for all columns.]
        obj = dataset_walmart[list(s)].eq(1, axis='index').all(1)
        #count the numbers of all the indexes where output is True, also change the range
        temp_l.append(len(obj[obj == True].index)/0.2)
        # print(list(s),"  ",len(obj[obj == True].index))
    
    #now append those values to L.
    L.append([C[i+1], temp_l])
    # print(L)
    #We have to remove those association where the support value is lesser than the given amount
    del_indices = delete_indices(i+1, support)
    #check the defintion of L to understand what is being enumerated. Basically we are removing the indices which has lesser
    #support values for the association set.
    L[i+1][0] = [x for  j, x  in enumerate(L[i+1][0]) if j not in del_indices]
    L[i+1][1] = [x for  j, x  in enumerate(L[i+1][1]) if j not in del_indices]
    
    #Break out of the loop if the list has no assocation sets.
    if L[i+1] == [[], []]: 
        L = L[:-1]
        break 

    i+=1

#blocks for traversing association values and support values
association_values_ = []
support_values_ = []

#Loop through the list to get the association and support values
for i in range(len(L)):
    association_values_= association_values_ + L[i][0]
    support_values_ = support_values_ + L[i][1]

#Rule Mining 

#association rules = [antecedent, consequent, confidence]
association_rules_ = []
#loop through the association values and make rules of the assocations with the rest of the values in the list
for x in association_values_:
    for y in association_values_:

        association_rule_confidence = 0.0
        z_support = 0.0
        x_support = support_values_[association_values_.index(x)]
        #if the value of y is not same as x assocation proceed further
        if y != x:
            #check if the the type of x is tuple or not - we have different logics 
            #for tuples and strings because if x is tuple then it may or may not be part of y.
            if type(x) is tuple:
                #1st condition when x and y are both tuple. Tuples can't be compared easily, so 
                #converted them into sets. 2nd condition for when y is not tuple and can be a part of x. 
                if set(x) not in set(y) and y not in x:
                    #when y is not tupple, then convert it into a tuple for concatenation
                    if type(y) is not tuple:
                        y = (y,)
                    # concate x and y to make z for confidence count
                    z = (x + y)
                    # print(z)
                   
            else:
                if x not in y:
                    #when x=str. y=str then just make a tuple out of them.
                    if type(y) is not tuple:
                        z = (x, y) 
                    #when x=str, but y=tuple then make x a tuple and oncatenate them.
                    else:
                        z = ((x,) + y)
                    # print(z)
                    
            
            #get the support value for z to count confidence        
            if z in association_values_:
                z_support =  support_values_[association_values_.index(z)]
            else:
            #check support logic for explanation
                obj = dataset_walmart[list(z)].eq(1, axis='index').all(1)
                z_support =  len(obj[obj == True].index)/0.2

            #confidenc is support(x,y)/support(x)
            association_rule_confidence = float(z_support/ x_support) 
                                    
            #check if the confidence is greater than or equals user_input, then add it to the association rules list
            if(association_rule_confidence*100 >= confidence):
                association_rules_.append([[x], [y], association_rule_confidence])
            

print(L)
print(association_rules_)