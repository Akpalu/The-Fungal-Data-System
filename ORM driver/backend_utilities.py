import pg8000
from general_utilities import (cPG_Commit_Error_Msg,
    cPG_Commit_Success_Msg, cSuccess, cFail)

PGconn = pg8000.connect(user="username", password="Y00urPassword", database="your_database")
PGcursor = PGconn.cursor()

def execute_sql(input_sql: str) -> tuple:
    '''
    This routine executes the SQL routines that change reftable contents,
    as opposed to the two above that retrieve recordsets.
    
    Returns a success or error message with identifying information.
    Uses arbitrary_sql_is_okay for vetting the SQL input.
    '''
    success_flag = cFail
    if not arbitrary_sql_is_okay(input_sql):
        identifying_message = (' Operation failed: '
        + ' SQL statement "' + input_sql + '" failed vetting process.')
        return_message = cPG_Commit_Error_Msg + identifying_message
        return return_message, success_flag
    try:
        PGcursor.execute(input_sql)
        PGconn.commit()
        success_flag = cSuccess
        return_message = cPG_Commit_Success_Msg
    except Exception as ex1:
        PGconn.rollback()
        error_type = type(ex1).__name__
        if error_type in ("ProgrammingError", "DatabaseError", "IntegrityError"):
            template = """: A PostGres {0} occurred when attempting to execute the SQL statement.
            \n --- """ + input_sql + """ ---
            \nProblems: {1!r} """
            err_param_dictionary = ex1.args[0]
            relevent_error_arg = err_param_dictionary["M"] 
            if "D" in err_param_dictionary:
                relevent_error_arg = relevent_error_arg + " " + err_param_dictionary["D"]
        else:
            template = """: An unanticipated exception of type {0} occurred. 
            \nProblems: {1!r} """
            relevent_error_arg = str(ex1.args)
        internalmessage = template.format(error_type, relevent_error_arg)
        return_message = cPG_Commit_Error_Msg + internalmessage
    return return_message, success_flag


def arbitrary_sql_is_okay(hot_sql: str) -> bool:
    '''
    Vet arbitrary SQL for
    a) being a DROP TABLE command
    b) DELETE statement without a WHERE clause
    c) Containing an internal semi-colon
    '''
    hot_sql = hot_sql.upper()
    if hot_sql.find('DROP') > -1:
        return False
    if hot_sql.find('DELETE') > -1 and hot_sql.find('WHERE') < 0:
        return False
    semicolon_pos = hot_sql.find(';')
    if (semicolon_pos > -1) and (semicolon_pos < len(hot_sql) -1):
        return False
    return True