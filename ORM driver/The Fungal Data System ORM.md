## The FDS ORM
The FDS ORM handles edits to the FDS reference tables. These PostGreSQL tables contain reference data that the program uses to parse text mushroom descriptions into JSON. When a text contains terms that aren’t already in the reftables, the system must add them and the user must properly categorize them, otherwise the FDS can’t parse the text. The front end is responsible for providing the user with appropriate operations to choose from, and requiring the user to select or input any ancillary information that’s necessary. The front end then passes the name of the appropriate SQL-writing function to the ORM driver, along with a dictionary of the parameters that the function requires:  
  
`def ORM_driver(orm_function_name, param_dict):`  
  
The ORM driver then attempts to look up the SQL-writing function in the globals() dictionary, and assign that function to a variable:  
  
`try:
. . .  hot_function = globals()[orm_function_name]`  
     
If the SQL-writing function isn’t found in the globals() dictionary, the ORM driver returns an error message. If the function is found, the ORM driver proceeds by checking the parameters it requires against the ones that were supplied. If there’s a mismatch it again returns an error message:  
  
`sig = signature(hot_function)  
if param_dict.keys() != sig.parameters.keys():    
. . . Err_msg = "Error: parameter mismatch!"`  
  
If everything checks out so far, the ORM driver retrieves a tuple from the SQL-writing function. The tuple contains the SQL to be run, the table affected by the SQL, and the type of operation on that table. The table and action are logged later on.   
  
`hot_sql, sql_table, sql_action = hot_function(**param_dict)`  
  
Then tries to run the SQL. The routine running the SQL returns a success (or diagnostic) message to show the user, and a flag indicating whether the operation went through or ran into problems and had to be rolled back.     
   
`sql_execution_msg, ORM_success_flag = execute_sql(hot_sql)`  
     
Lastly, the ORM driver makes a time-stamped log entry documenting the whole operation (whether it succeeded or failed).  
  
`log_sql = make_log_sql((sql_execution_msg + " " + hot_sql), sql_table, sql_action)  
execute_sql(log_sql)`  

## The bad old days
My first attempt at implementing this functionality was very bad. My idea was that the front end would simply send back the name of the table to be edited, the action to be performed, and the new term (and perhaps ancillary data, like tokenization for the term). The ORM in this case was basically a huge switch statement that matched the intended task with the proper SQL-writing function and then checked to make sure the correct parameters for that function had been passed, and so on. So in a sense the architecture was the same.  
  
There were a couple of problems with this. First of all, it’s maintenance-intensive. The central ORM has to maintain some sort of record of what all the available SQL-writing functions there are, and what parameters they take. If I change the arity of a SQL-writing function (or add a new one), I have to update (or add) its corresponding record in the ORM. Ain’t nobody got time for that, especially when Python maintains a perfectly fine table of all that information for you.  
  
Another aspect to the maintenance issue is that I want the front end to be calling each SQL-writing function by name. That way if there’s any problem, I will know the target SQL-writing function immediately and I can look up whether it exists, what parameters the front end must supply, and so on, rather than having to trace the operation that it’s requesting through the ORM and out the other side. So there’s an explicit versus implicit issue.  
  
There’s also just the complexity issue. The ORM doesn't just add and delete records; it can perform complex operations involving tokenizing and other issues. Building the “intelligence” into the ORM to direct all these sorts of requests to the proper SQL-writing function is not a trivial task. Besides the challenge of building it in the first place, it’s easy to drop the ball as the program evolves.   
  
One last word on the logging: in this Bad Old Implementation, the name of the affected table and the operation to perform on it weren’t just passed from the front end; they were passed all the way through the ORM to the logging function. So that again has points where breakage can occur. I still wanted to log the table and operation under the new implementation, so I had each SQL-writing function return those along with its actual SQL. That way each SQL-writing function is responsible for its own characterization in the log, so this is another thing I don’t have to keep in sync between different parts of the program.  