import os
import shlex
from subprocess import Popen,PIPE
from datetime import datetime,timedelta

from .extensions import db,jobmanager
from .models import Jobs


reschedule = lambda time : time + timedelta(minutes=3)

def runjob(job,attemp=1):
    print('Job {} - {} starting.'.format(job.name,job.id))

    command = shlex.split(job.task)
     
    PROC = Popen(command, stdout=PIPE, stderr=PIPE,close_fds=True)
    exitcode = PROC.wait()

    if exitcode:
        logger(job.id,job.name,PROC.stderr)

        if attemp > 2:
            print('Error on job {} - {}. Attemp {}, abandoning task.'.format(job.name,job.id,attemp))
            return update_status(job.id,'Error')

        print('Error on job {} - {}. Attemp {}, retrying.'.format(job.name,job.id,attemp))

        finish_time = datetime.now().replace(second=0, microsecond=0)
        newjob = update_status(job.id,'Retrying',reschedule(finish_time))

        return jobmanager.add_job(
            str(job.id),
            func=runjob,
            trigger='date',
            run_date=reschedule(finish_time),
            args=[newjob,attemp+1]
        )

    update_status(job.id,'Success')
    print('Job {} - {} successfully finished.'.format(job.name,job.id))


def update_status(jobid,status,time=False):
    with jobmanager.app.app_context(): # Had to call app_context this way to work
        temp = Jobs.query.get(jobid)
        temp.status = status

        if time:
            temp.start = time
        
        db.session.commit()
    
        return Jobs.query.get(jobid)

def logger(id,name,pipe):
    with open('app/logs/logs.txt','a+') as logger:
        logger.write('\n')

        for line in iter(pipe.readline, b''):
            # print('{} - {}: {}'.format(id,name,str(line)))
            logger.write('{} - {}: {}\n'.format(id,name,line))
        
        