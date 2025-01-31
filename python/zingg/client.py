"""
zingg.client
------------------------
This module is the main entry point of the Zingg Python API
"""

import logging
import argparse
import pandas as pd
from pyspark.sql import DataFrame

from pyspark import SparkConf, SparkContext, SQLContext
from pyspark.sql.session import SparkSession
from py4j.java_collections import SetConverter, MapConverter, ListConverter

LOG = logging.getLogger("zingg")

sc = SparkContext.getOrCreate()
sqlContext = SQLContext(sc)
#spark = SparkSession(sc)
spark = SparkSession.builder.getOrCreate()
#sc = SparkContext.getOrCreate()
jvm = sc._jvm
gateway = sc._gateway

ColName = jvm.zingg.common.client.util.ColName
MatchType = jvm.zingg.common.client.MatchType

def getDfFromDs(data):
    """ Method to convert spark dataset to dataframe

    :param data: provide spark dataset
    :type data: DataSet
    :return: converted spark dataframe
    :rtype: DataFrame 
    """
    return DataFrame(data.df(), sqlContext)

def getPandasDfFromDs(data):
    """ Method to convert spark dataset to pandas dataframe

    :param data: provide spark dataset
    :type data: DataSet
    :return: converted pandas dataframe
    :rtype: DataFrame 
    """
    df = getDfFromDs(data)
    return pd.DataFrame(df.collect(), columns=df.columns)


class Zingg:
    """ This class is the main point of interface with the Zingg matching product. Construct a client to Zingg using provided arguments and spark master. If running locally, set the master to local.

    :param args: arguments for training and matching
    :type args: Arguments
    :param options: client option for this class object
    :type options: ClientOptions

    """

    def __init__(self, args, options):
        self.client = jvm.zingg.spark.client.SparkClient(args.getArgs(), options.getClientOptions())

       
    def init(self):
        """ Method to initialize zingg client by reading internal configurations and functions """
        self.client.init()

    def execute(self):
        """ Method to execute this class object """
        self.client.execute()
        
    def initAndExecute(self):
        """ Method to run both init and execute methods consecutively """
        self.client.init()
        self.client.execute()

    def getMarkedRecords(self):
        """ Method to get marked record dataset from the inputpipe

        :return: spark dataset containing marked records
        :rtype: Dataset<Row> 
        """
        return self.client.getMarkedRecords()

    def getUnmarkedRecords(self):
        """ Method to get unmarked record dataset from the inputpipe

        :return: spark dataset containing unmarked records
        :rtype: Dataset<Row> 
        """
        return self.client.getUnmarkedRecords()

    def setArguments(self, args):
        """ Method to set Arguments

        :param args: provide arguments for this class object
        :type args: Arguments
        """
        self.client.setArguments()

    def getArguments(self):
        """ Method to get atguments of this class object

        :return: The pointer containing address of the Arguments object of this class object
        :rtype: pointer(Arguments)
        """
        return self.client.getArguments()

    def getOptions(self):
        """ Method to get client options of this class object

        :return: The pointer containing the address of the ClientOptions object of this class object
        :rtype: pointer(ClientOptions)
        """
        return self.client.getOptions()

    def setOptions(self, options):
        """ Method to set atguments of this class object

        :param options: provide client options for this class object
        :type options: ClientOptions
        :return: The pointer containing address of the ClientOptions object of this class object
        :rtype: pointer(ClientOptions) 
        """
        return self.client.setOptions(options)

    def getMarkedRecordsStat(self, markedRecords, value):
        """ Method to get No. of records that is marked

        :param markedRecords: spark dataset containing marked records
        :type markedRecords: Dataset<Row>
        :param value: flag value to check if markedRecord is initially matched or not
        :type value: long
        :return: The no. of marked records
        :rtype: int 
        """
        return self.client.getMarkedRecordsStat(markedRecords, value)

    def getMatchedMarkedRecordsStat(self):
        """ Method to get No. of records that are marked and matched

        :return: The bo. of matched marked records
        :rtype: int 
        """
        return self.client.getMatchedMarkedRecordsStat(self.getMarkedRecords())

    def getUnmatchedMarkedRecordsStat(self):
        """ Method to get No. of records that are marked and unmatched

        :return: The no. of unmatched marked records
        :rtype: int 
        """
        return self.client.getUnmatchedMarkedRecordsStat(self.getMarkedRecords())

    def getUnsureMarkedRecordsStat(self):
        """ Method to get No. of records that are marked and Not Sure if its matched or not

        :return: The no. of Not Sure marked records
        :rtype: int 
        """
        return self.client.getUnsureMarkedRecordsStat(self.getMarkedRecords())

    

class ZinggWithSpark(Zingg):

    """ This class is the main point of interface with the Zingg matching product. Construct a client to Zingg using provided arguments and spark master. If running locally, set the master to local.

    :param args: arguments for training and matching
    :type args: Arguments
    :param options: client option for this class object
    :type options: ClientOptions

    """

    def __init__(self, args, options):
        self.client = jvm.zingg.spark.client.SparkClient(args.getArgs(), options.getClientOptions(), spark._jsparkSession)


class Arguments:
    """ This class helps supply match arguments to Zingg. There are 3 basic steps in any match process.

    :Defining: specifying information about data location, fields, and our notion of similarity.
    :training: making Zingg learn the matching rules
    :Matching: Running the models on the entire dataset
    """

    def __init__(self):
        self.args = jvm.zingg.common.client.Arguments()

    def setFieldDefinition(self, fieldDef):
        """ Method convert python objects to java FieldDefinition objects and set the field definitions associated with this client

        :param fieldDef: python FieldDefinition object list
        :type fieldDef: List(FieldDefinition)
        """
        javaFieldDef = []
        for f in fieldDef:
            javaFieldDef.append(f.getFieldDefinition())
        self.args.setFieldDefinition(javaFieldDef)

    def getArgs(self):
        """ Method to get pointer address of this class

        :return: The pointer containing the address of this class object
        :rtype: pointer(Arguments)
        
        """
        return self.args

    def setArgs(self, argumentsObj):
        """ Method to set this class object

        :param argumentsObj: Argument object to set this object
        :type argumentsObj: pointer(Arguments)
        """
        self.args = argumentsObj

    def setData(self, *pipes):
        """ Method to set the file path of the file to be matched.

        :param pipes: input data pipes separated by comma e.g. (pipe1,pipe2,..)
        :type pipes: Pipe[]
        """
        dataPipe = gateway.new_array(jvm.zingg.common.client.pipe.Pipe, len(pipes))
        for idx, pipe in enumerate(pipes):
            dataPipe[idx] = pipe.getPipe()
        self.args.setData(dataPipe)

    def setOutput(self, *pipes):
        """ Method to set the output directory where the match result will be saved

        :param pipes: output data pipes separated by comma e.g. (pipe1,pipe2,..)
        :type pipes: Pipe[]
        """
        outputPipe = gateway.new_array(jvm.zingg.common.client.pipe.Pipe, len(pipes))
        for idx, pipe in enumerate(pipes):
            outputPipe[idx] = pipe.getPipe()
        self.args.setOutput(outputPipe)
    
    def getZinggBaseModelDir(self):
        return self.args.getZinggBaseModelDir()

    def getZinggModelDir(self):
        return self.args.getZinggModelDir()
    
    def getZinggBaseTrainingDataDir(self):
        """ Method to get the location of the folder where Zingg 
        saves the training data found by findTrainingData  
        """
        return self.args.getZinggBaseTrainingDataDir()

    def getZinggTrainingDataUnmarkedDir(self):
        """ Method to get the location of the folder where Zingg 
        saves the training data found by findTrainingData  
        """
        return self.args.getZinggTrainingDataUnmarkedDir()
    
    def getZinggTrainingDataMarkedDir(self):
        """ Method to get the location of the folder where Zingg 
        saves the marked training data labeled by the user  
        """
        return self.args.getZinggTrainingDataMarkedDir()
    
    def setTrainingSamples(self, *pipes):
        """ Method to set existing training samples to be matched.

        :param pipes: input training data pipes separated by comma e.g. (pipe1,pipe2,..)
        :type pipes: Pipe[]
        """
        dataPipe = gateway.new_array(jvm.zingg.common.client.pipe.Pipe, len(pipes))
        for idx, pipe in enumerate(pipes):
            dataPipe[idx] = pipe.getPipe()
        self.args.setTrainingSamples(dataPipe)

    def setModelId(self, id):
        """ Method to set the output directory where the match output will be saved

        :param id: model id value 
        :type id: String
        """
        self.args.setModelId(id)
    
    def getModelId(self):
        return self.args.getModelId()

    def setZinggDir(self, f):
        """ Method to set the location for Zingg to save its internal computations and models. Please set it to a place where the program has to write access.

        :param f: Zingg directory name of the models
        :type f: String
        """
        self.args.setZinggDir(f)

    def setNumPartitions(self, numPartitions):
        """ Method to set NumPartitions parameter value
        Sample size to use for seeding labeled data We don't want to run over all the data, as we want a quick way to seed some labeled data that we can manually edit

        :param numPartitions: number of partitions for given data pipes
        :type numPartitions: int
        """
        self.args.setNumPartitions(numPartitions)

    def setLabelDataSampleSize(self, labelDataSampleSize):
        """ Method to set labelDataSampleSize parameter value
        Set the fraction of data to be used from the complete data set to be used for seeding the labeled data Labelling is costly and we want a fast approximate way of looking at a small sample of the records and identifying expected matches and nonmatches

        :param labelDataSampleSize: value between 0.0 and 1.0 denoting portion of dataset to use in generating seed samples
        :type labelDataSampleSize: float
        """
        self.args.setLabelDataSampleSize(labelDataSampleSize)

    def writeArgumentsToJSON(self, fileName):
        """ Method to write JSON file from the object of this class 

        :param fileName: The CONF parameter value of ClientOption object or file address of json file
        :type fileName: String
        """
        jvm.zingg.common.client.Arguments.writeArgumentsToJSON(fileName, self.args)

    def setStopWordsCutoff(self, stopWordsCutoff):
        """ Method to set stopWordsCutoff parameter value
        By default, Zingg extracts 10% of the high frequency unique words from a dataset. If user wants different selection, they should set up StopWordsCutoff property

        :param stopWordsCutoff: The stop words cutoff parameter value of ClientOption object or file address of json file
        :type stopWordsCutoff: float
        """
        self.args.setStopWordsCutoff(stopWordsCutoff)

    @staticmethod
    def createArgumentsFromJSON(fileName, phase):
        """ Method to create an object of this class from the JSON file and phase parameter value.
        
        :param fileName: The CONF parameter value of ClientOption object
        :type fileName: String
        :param phase: The PHASE parameter value of ClientOption object
        :type phase: String
        :return: The pointer containing address of the this class object
        :rtype: pointer(Arguments)
        """
        obj = Arguments()
        obj.args = jvm.zingg.common.client.Arguments.createArgumentsFromJSON(fileName, phase)
        return obj
    
    
    def writeArgumentsToJSONString(self):
        """ Method to create an object of this class from the JSON file and phase parameter value.
        
        :param fileName: The CONF parameter value of ClientOption object
        :type fileName: String
        :param phase: The PHASE parameter value of ClientOption object
        :type phase: String
        :return: The pointer containing address of the this class object
        :rtype: pointer(Arguments)
        """
        return jvm.zingg.common.client.Arguments.writeArgumentstoJSONString(self.args)
    
    @staticmethod
    def createArgumentsFromJSONString(jsonArgs, phase):
        obj = Arguments()
        obj.args = jvm.zingg.common.client.Arguments.createArgumentsFromJSONString(jsonArgs, phase)
        return obj
    
    
    def copyArgs(self, phase):
        argsString = self.writeArgumentsToJSONString()
        return self.createArgumentsFromJSONString(argsString, phase)

   
    


class ClientOptions:
    """ Class that contains Client options for Zingg object
    :param phase: trainMatch, train, match, link, findAndLabel, findTrainingData etc
    :type phase: String
    :param args: Parse a list of Zingg command line options parameter values e.g. "--location" etc. optional argument for initializing this class.
    :type args: List(String) or None
    """
    PHASE = jvm.zingg.common.client.ClientOptions.PHASE 
    """:PHASE: phase parameter for this class"""
    CONF = jvm.zingg.common.client.ClientOptions.CONF
    """:CONF: conf parameter for this class"""
    LICENSE = jvm.zingg.common.client.ClientOptions.LICENSE
    """:LICENSE: license parameter for this class"""
    EMAIL = jvm.zingg.common.client.ClientOptions.EMAIL
    """:EMAIL: e-mail parameter for this class"""
    LOCATION = jvm.zingg.common.client.ClientOptions.LOCATION
    """:LOCATION: location parameter for this class"""
    REMOTE = jvm.zingg.common.client.ClientOptions.REMOTE
    """:REMOTE: remote option used internally for running on Databricks"""
    ZINGG_DIR = jvm.zingg.common.client.ClientOptions.ZINGG_DIR
    """:ZINGG_DIR: location where Zingg saves the model, training data etc"""
    MODEL_ID = jvm.zingg.common.client.ClientOptions.MODEL_ID
    """:MODEL_ID: ZINGG_DIR/MODEL_ID is used to save the model"""

    def __init__(self, argsSent=None):
        print(argsSent)
        if(argsSent == None):
            args = []
        else:
            args = argsSent.copy()
        if (not (self.PHASE in args)):
            args.append(self.PHASE)
            args.append("peekModel")
        if (not (self.LICENSE in args)):
            args.append(self.LICENSE)
            args.append("zinggLic.txt")
        if (not (self.EMAIL in args)):
            args.append(self.EMAIL)
            args.append("zingg@zingg.ai")
        if (not (self.CONF in args)):
            args.append(self.CONF)
            args.append("dummyConf.json")
        print("arguments for client options are ", args) 
        self.co = jvm.zingg.common.client.ClientOptions(args)
    
    
    def getClientOptions(self):
        """ Method to get pointer address of this class

        :return: The pointer containing address of the this class object
        :rtype: pointer(ClientOptions)
        """
        return self.co

    def getOptionValue(self, option):
        """ Method to get value for the key option

        :param option: key to geting the value
        :type option: String
        :return: The value which is mapped for given key 
        :rtype: String 
        """
        return self.co.getOptionValue(option)

    def setOptionValue(self, option, value):
        """ Method to map option key to the given value

        :param option: key that is mapped with value
        :type option: String
        :param value: value to be set for given key
        :type value: String
        """
        self.co.get(option).setValue(value)

    def getPhase(self):
        """ Method to get PHASE value

        :return: The PHASE parameter value
        :rtype: String 
        """
        return self.co.get(ClientOptions.PHASE).getValue()

    def setPhase(self, newValue):
        """ Method to set PHASE value

        :param newValue: name of the phase
        :type newValue: String
        :return: The pointer containing address of the this class object after seting phase
        :rtype: pointer(ClientOptions) 
        """
        self.co.get(ClientOptions.PHASE).setValue(newValue)

    def getConf(self):
        """ Method to get CONF value

        :return: The CONF parameter value
        :rtype: String 
        """
        return self.co.get(ClientOptions.CONF).getValue()

    def hasLocation(self):
        """ Method to check if this class has LOCATION parameter set as None or not

        :return: The boolean value if LOCATION parameter is present or not
        :rtype: Bool 
        """
        if(self.co.get(ClientOptions.LOCATION)==None):
            return False
        else:
            return True

    def getLocation(self):
        """ Method to get LOCATION value

        :return: The LOCATION parameter value
        :rtype: String 
        """
        return self.co.get(ClientOptions.LOCATION).getValue()


class FieldDefinition:
    """ This class defines each field that we use in matching We can use this to configure the properties of each field we use for matching in Zingg.

    :param name: name of the field
    :type name: String
    :param dataType: type of the data e.g. string, float, etc.
    :type dataType: String
    :param matchType: match type of this field e.g. FUSSY, EXACT, etc.
    :type matchType: MatchType
    """

    def __init__(self, name, dataType, *matchType):
        self.fd = jvm.zingg.common.client.FieldDefinition()
        self.fd.setFieldName(name)
        self.fd.setDataType(self.stringify(dataType))
        self.fd.setMatchType(matchType)
        self.fd.setFields(name)
    
    def setStopWords(self, stopWords):
        """ Method to add stopwords to this class object

        :param stopWords: The stop Words containing csv file's location
        :type stopWords: String
        """
        self.fd.setStopWords(stopWords)

    def getFieldDefinition(self):
        """ Method to get  pointer address of this class

        :return: The pointer containing the address of this class object
        :rtype: pointer(FieldDefinition)
        """
        return self.fd

    #  should be stringify'ed before it is set in fd object
    def stringify(self, str):
        """ Method to stringify'ed the dataType before it is set in FieldDefinition object
        
        :param str: dataType of the FieldDefinition
        :type str: String
        :return: The stringify'ed value of the dataType
        :rtype: String
        """
        return '"' + str + '"'
        

def parseArguments(argv):
    """ This method is used for checking mandatory arguments and creating an arguments list from Command line arguments

    :param argv: Values that are passed during the calling of the program along with the calling statement.
    :type argv: List
    :return: a list containing necessary arguments to run any phase
    :rtype: List
    """
    parser = argparse.ArgumentParser(description='Zingg\'s python APIs')
    mandatoryOptions = parser.add_argument_group('mandatory arguments')
    mandatoryOptions.add_argument('--phase', required=True,
                        help='python phase e.g. assessModel')
    mandatoryOptions.add_argument('--conf', required=True,
                        help='JSON configuration with data input output locations and field definitions')

    args, remaining_args = parser.parse_known_args()
    LOG.debug("args: ", args)
    return args
