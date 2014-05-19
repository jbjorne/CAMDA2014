import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.example import exampleOptions
import time
from connection.UnixConnection import UnixConnection
from connection.SLURMConnection import SLURMConnection

CLASSIFIER_ARGS = {
    #'ensemble.RandomForest':{'n_estimators':[10,100],'max_features':['auto',None]},
    'ensemble.ExtraTreesClassifier':"n_estimators=[250]",
    'svm.LinearSVC':"C=logrange(-10, 10)"}

ANALYZE = ['ensemble.ExtraTreesClassifier']
ALL_CAMDA_PROJECTS = ["KIRC-US", "LUAD-US", "HNSC-US"]
ALL_PROJECTS = ["BLCA-US","BOCA-UK","BRCA-UK","BRCA-US","CESC-US","CLLE-ES",
                "CMDI-UK","COAD-US","EOPC-DE","ESAD-UK","GBM-US","HNSC-US",
                "KIRC-US","KIRP-US","LAML-US","LGG-US","LICA-FR","LIHC-US",
                "LINC-JP","LIRI-JP","LUAD-US","LUSC-US","MALY-DE","NBL-US",
                "ORCA-IN","OV-AU","OV-US","PAAD-US","PACA-AU","PACA-CA",
                "PAEN-AU","PBCA-DE","PRAD-CA","PRAD-US","READ-US","RECA-CN",
                "RECA-EU","SKCM-US","STAD-US","THCA-SA","THCA-US","UCEC-US"]


def getJobs(resultPath, experiments=None, projects=None, classifiers=None):
    global ALL_CAMDA_PROJECTS, ALL_PROJECTS
    if experiments == None:
        experiments = "ALL"
    if isinstance(experiments, basestring):
        experiments = experiments.replace("ALL", "CANCER_OR_CONTROL,REMISSION")
        experiments = experiments.split(",")
    if projects == None:
        projects = "ALL_CAMDA"
    if isinstance(projects, basestring):
        projects = projects.replace("ALL_CAMDA", ",".join(ALL_CAMDA_PROJECTS))
        projects = projects.replace("ALL", ",".join(ALL_PROJECTS))
        projects = projects.split(",")
    if classifiers == None:
        classifiers = 'ensemble.ExtraTreesClassifier'
    if isinstance(classifiers, basestring):
        classifiers = classifiers.split(",")
    
    jobs = []
    for experiment in experiments:
        for project in projects:
            for classifier in classifiers:
                resultFileName = experiment + "-" + project + "-" + classifier + ".json"
                job = {"result":os.path.join(resultPath, resultFileName),
                       "experiment":experiment,
                       "project":project,
                       "classifier":classifier
                       }
                jobs.append(job)
    return jobs

def waitForJobs(maxJobs, submitCount, connection, sleepTime=15):
    currentJobs = connection.getNumJobs()
    print >> sys.stderr, "Current jobs", str(currentJobs) + ", max jobs", str(maxJobs) + ", submitted jobs", submitCount
    if maxJobs != None:
        while(currentJobs >= maxJobs):
            time.sleep(sleepTime)
            currentJobs = connection.getNumJobs()
            print >> sys.stderr, "Current jobs", str(currentJobs) + ", max jobs", str(maxJobs) + ", submitted jobs", submitCount

def submitJob(command, connection, jobDir, jobName, dummy=False, rerun=None, hideFinished=False):
    print >> sys.stderr, "Processing job", jobName, "for input", input
    jobStatus = connection.getJobStatusByName(jobDir, jobName)
    if jobStatus != None:
        if rerun != None and jobStatus in rerun:
            print >> sys.stderr, "Rerunning job", jobName, "with status", jobStatus
        else:
            if jobStatus == "RUNNING":
                print >> sys.stderr, "Skipping currently running job"
            elif not hideFinished:
                print >> sys.stderr, "Skipping already processed job with status", jobStatus
            return False
    
    if not dummy:
        connection.submit(command, jobDir, jobName, 
                          os.path.join(jobDir, jobName + ".stdout"),
                          os.path.join(jobDir, jobName + ".stderr"))
    else:
        print >> sys.stderr, "Dummy mode"
        if connection.debug:
            print >> sys.stderr, "------- Job command -------"
            print >> sys.stderr, connection.makeJobScript(command, jobDir, jobName)
            print >> sys.stderr, "--------------------------"
    return True
    
def batch(runDir, jobDir, resultPath, experiments, projects, classifiers, 
          limit=1, sleepTime=15, dummy=False, rerun=None, hideFinished=False, 
          clearCache=False):
    global ANALYZE, CLASSIFIER_ARGS
    if sleepTime == None:
        sleepTime = 15
    submitCount = 0
    jobs = getJobs(resultPath, experiments, projects, classifiers)
    for index, job in enumerate(jobs):
        waitForJobs(limit, submitCount, connection, sleepTime)
        print "Processing job", str(index+1) + "/" + str(len(jobs)), job
        script = ""
        if runDir != None:
            script = "cd " + runDir + "\n"
        script += "python learn.py"
        script += " -e " + job["experiment"] + " -o \"project=" + job["project"] + ",include=both\""
        script += " -c " + job["classifier"] + " -a \"" + CLASSIFIER_ARGS[job["classifier"]] + "\""
        script += " -r " + job["result"]
        if job["classifier"] in ANALYZE:
            script += " --analyze"
        if clearCache:
            script += " --clearCache"
        jobName = os.path.basename(job["result"])
        if submitJob(script, connection, jobDir, jobName, dummy, rerun, hideFinished):
            submitCount += 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-e','--experiments', help='', default=None)
    parser.add_argument('-p','--projects', help='', default=None)
    parser.add_argument('-c','--classifiers', help='', default=None)
    parser.add_argument('-r','--results', help='Output directory', default=None)
    parser.add_argument('--slurm', help='', default=False, action="store_true")
    #parser.add_argument('--cacheDir', help='Cache directory (optional)', default=os.path.join(tempfile.gettempdir(), "CAMDA2014"))
    parser.add_argument("--debug", default=False, action="store_true", dest="debug", help="Print jobs on screen")
    parser.add_argument("--dummy", default=False, action="store_true", dest="dummy", help="Don't submit jobs")
    parser.add_argument("--rerun", default=None, dest="rerun", help="Rerun jobs which have one of these states (comma-separated list)")
    parser.add_argument("-l", "--limit", default=None, type=int, dest="limit", help="Maximum number of jobs in queue/running")
    parser.add_argument("--hideFinished", default=False, action="store_true", dest="hideFinished", help="")
    parser.add_argument("--runDir", default=None, dest="runDir", help="")
    parser.add_argument("--jobDir", default="/tmp/jobs", dest="jobDir", help="")
    parser.add_argument('--clearCache', default=False, action="store_true")
    options = parser.parse_args()
    
    if options.slurm:
        connection = SLURMConnection()
    else:
        connection = UnixConnection()
    if not os.path.exists(options.jobDir):
        os.makedirs(options.jobDir)
    connection.debug = options.debug
    batch(runDir=options.runDir, jobDir=options.jobDir, resultPath=options.results, 
          experiments=options.experiments, projects=options.projects, 
          classifiers=options.classifiers, limit=options.limit, sleepTime=15, rerun=options.rerun,
          hideFinished=options.hideFinished, dummy=options.dummy, clearCache=options.clearCache)