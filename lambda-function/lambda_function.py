import logging
import pyodbc
import boto3

log = logging.getLogger()
log.setLevel(logging.INFO)

sm = boto3.client("secretsmanager")

SQLCREDSSECRET = os.environ["SQLCREDSSECRET"]

def lambda_handler(event, context):
    connection_creds = GetSecret(SQLCREDSSECRET)

    connection = ConnectToSql(
            server=connection_creds["server"],
            port=connection_creds["port"],
            database=connection_creds["database"],
            user=connection_creds["user"],
            password=connection_creds["password"],
        )

    query = "SELECT TOP 100 * FROM Users"

    query_results = QuerySql(connection, query)

    print(f'RESULTS: {query_results}')



def GetSecret(secretName):
    try:
        get_secret_value_response = sm.get_secret_value(SecretId=secretName)
    except Exception as error:
        log.error(f"Unable to retrieve secret values for {secretName}")
        raise error
    else:
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
        else:
            secret = base64.b64decode(get_secret_value_response["SecretBinary"])
    result = json.loads(secret)
    return result

def ConnectToSql(server, port, database, user, password):
    log.info(f"Connecting to database")
    try:
        conn_str = (
            'DRIVER=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.7.so.2.1;'
            f'SERVER={server},{port};'
            f'DATABASE={database};'
            f'UID={user};'
            f'PWD={password};'
        )
        connection = pyodbc.connect(conn_str)
    except Exception as error:
        log.error("Failed to connect to the database")
        raise error
    return connection

def QuerySql(connection, query):
    try:
        cursor = connection.cursor()
        results = cursor.execute(query).fetchall
    except Exception as error:
        log.error("Failed to run query")
        raise error
    return results