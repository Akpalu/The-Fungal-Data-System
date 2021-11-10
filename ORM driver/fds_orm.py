from backend_utilities import execute_sql
from general_utilities import cFail
from datetime import date
from inspect import signature


"""**************************************
*****************
Main Driver
**************"""

def ORM_driver(orm_function_name, param_dict, test_flag=False):
    ORM_success_flag = cFail
    try:
        hot_function = globals()[orm_function_name] 
    except KeyError:
        Err_msg = """Error: SQL-writing function 
        \n --- """ + orm_function_name + """ ---
        \nnot found!"""
        return (Err_msg, ORM_success_flag)
    else:   
        sig = signature(hot_function)
        if param_dict.keys() != sig.parameters.keys():        
            Err_msg = "Error: parameter mismatch! "
            missing_params = [param_name for param_name in sig.parameters if param_name not in param_dict]
            extra_params = [param_name for param_name in param_dict if param_name not in sig.parameters]
            if missing_params:
                Err_msg = Err_msg + '''
                Missing parameters: ''' + ', '.join(missing_params)
            if extra_params:
                Err_msg = Err_msg + '''
                Extra parameters: ''' + ', '.join(extra_params)
            return (Err_msg, ORM_success_flag)
        hot_sql, sql_table, sql_action = hot_function(**param_dict)
        sql_execution_msg, ORM_success_flag = execute_sql(hot_sql)
        log_sql = make_log_sql((sql_execution_msg + " " + hot_sql), sql_table, sql_action)
        execute_sql(log_sql)
        success_sugar = "" if ORM_success_flag else "not "
        verb_ending = "d" if sql_action.endswith('e') else "ed"
        return_message = (sql_execution_msg + ": " + sql_table 
            + " entry " + success_sugar + sql_action + verb_ending)
        return (return_message, ORM_success_flag)


"""**************************************
*****************
SQL-generating routines
**************"""

def make_log_sql(sqlstatement, sql_table, sql_action):
    """Creates the SQL to add the current SQL action and a time stamp to the sqllog table."""
    safe_sql = escape_single_quotes(sqlstatement)
    currentdate = date.today()
    hotdate = (str(currentdate.year) + '-' + str(currentdate.month)
     + '-' + str(currentdate.day))
    SQLString = "INSERT INTO sqllog (sqlstatement, reftable, action, logdate) VALUES ('%s', '%s', '%s', '%s')" \
        %(safe_sql, sql_table, sql_action, hotdate)
    return SQLString


""" *********  Separators ********* """
def new_separator_sql(new_separator, language):
    """Returns the SQL string for adding a new separator character to the reference 
    tables."""
    SQLString = "INSERT INTO separators VALUES ('%s', '%s')" % (new_separator, language)
    return SQLString, 'separators', 'add'

def change_separator_language_sql(separator, new_language):
    """Return the SQL for changing the FDSValue associated with an npword.
    I guess it can also be used to change the word's category because it 
    sets that too.
    """
    SQLString = ("UPDATE separators SET (separatorlanguage) = " 
    "('%s') WHERE separator = '%s'" %(new_language, separator))
    return SQLString, 'separators', 'update'

def delete_separator(badseparator):
    """Delete an separator from the reference tables."""
    SQLString = "DELETE FROM separators WHERE separator = '%s'" %(badseparator)
    return SQLString, 'separators', 'delete'

def bad_separator_sql(new_separator, language, extra_param):
    """Returns a mismatched SQL string (for testing purposes)
    for adding a new separator character to the reference tables. 
    
    The SQL string generated here has an extra field, so it can be used to test
    if the execute_sql function is returning its error messages properly."""
    SQLString = "INSERT INTO separators VALUES ('%s', '%s', '%s')" % (new_separator, language, extra_param)
    return SQLString, 'separators', 'badd'


'''  ******** Utility functions *********** '''

def escape_single_quotes(hotstring):
    '''Escapes the single quotes in a string parameter for
    inclusion (as a field value) in a PGS SQL statement.
    '''
    returnstring = ''
    for char in hotstring:
        if char == "'":
            returnstring = returnstring + "''"
        else:
            returnstring = returnstring + char
    return returnstring
