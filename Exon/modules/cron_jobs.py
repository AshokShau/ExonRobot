"""
MIT License

Copyright (c) 2022 ABISHNOI69

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# ""DEAR PRO PEOPLE,  DON'T REMOVE & CHANGE THIS LINE
# TG :- @Abishnoi1m
#     UPDATE   :- Abishnoi_bots
#     GITHUB :- ABISHNOI69 ""


import datetime
import os
import shutil
import subprocess
from time import sleep

from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.filters import Filters
from telegram.update import Update

from Exon import BACKUP_PASS, DB_URL, DEV_USERS, LOGGER, OWNER_ID, dispatcher
from Exon.modules.helper_funcs.decorators import Exoncmd


@Exoncmd(command="backupdb", filters=Filters.user(DEV_USERS) | Filters.user(OWNER_ID))
def backup_now(_: Update, ctx: CallbackContext):
    cronjob.run(dispatcher=dispatcher)


@Exoncmd(command="stopjobs", filters=Filters.user(DEV_USERS) | Filters.user(OWNER_ID))
def stop_jobs(update: Update, _: CallbackContext):
    print(j.stop())
    update.effective_message.reply_text("Scheduler has been shut down")


@Exoncmd(command="startjobs", filters=Filters.user(DEV_USERS) | Filters.user(OWNER_ID))
def start_jobs(update: Update, _: CallbackContext):
    print(j.start())
    update.effective_message.reply_text("Scheduler started")


zip_pass = BACKUP_PASS


def backup_db(_: CallbackContext):
    bot = dispatcher.bot
    tmpmsg = "Performing backup, Please wait..."
    tmp = bot.send_message(OWNER_ID, tmpmsg)
    datenow = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dbbkpname = f"db_{bot.username}_{datenow}.tar"
    bkplocation = f"backups/{datenow}"
    bkpcmd = f"pg_dump {DB_URL} --format=tar > {bkplocation}/{dbbkpname}"

    if not os.path.exists(bkplocation):
        os.makedirs(bkplocation)
    LOGGER.info("Performing db backup")
    loginfo = "db backup"
    term(bkpcmd, loginfo)
    if not os.path.exists(f"{bkplocation}/{dbbkpname}"):
        bot.send_message(OWNER_ID, "An error occurred during the db backup")
        tmp.edit_text("Backup Failed!")
        sleep(8)
        tmp.delete()
        return
    else:
        LOGGER.info("Copying config, and logs to backup location")
        if os.path.exists("logs.txt"):
            print("Logs copied")
            shutil.copyfile("logs.txt", f"{bkplocation}/logs.txt")
        if os.path.exists("config.ini"):
            print("Config copied")
            shutil.copyfile("config.ini", f"{bkplocation}/config.ini")
        LOGGER.info("Zipping the backup")
        zipcmd = f"zip --password '{zip_pass}' {bkplocation} {bkplocation}/*"
        zipinfo = "zipping db backup"
        LOGGER.info("Zip initiated")
        term(zipcmd, zipinfo)
        LOGGER.info("Zip done")
        sleep(1)
        with open(f"backups/{datenow}.zip", "rb") as bkp:
            nm = f"{bot.username} backup \n{datenow}"
            bot.send_document(OWNER_ID, document=bkp, caption=nm, timeout=20)
        LOGGER.info("Removing zipped files")
        shutil.rmtree(f"backups/{datenow}")
        LOGGER.info("Backup done")
        tmp.edit_text("Backup complete!")
        sleep(5)
        tmp.delete()


@Exoncmd(
    command="purgebackups", filters=Filters.user(DEV_USERS) | Filters.user(OWNER_ID)
)
def del_bkp_fldr(update: Update, _: CallbackContext):
    shutil.rmtree("backups")
    update.effective_message.reply_text("'Backups' directory has been purged!")


def term(cmd, info):
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    stdout, stderr = process.communicate()
    stderr = stderr.decode()
    if stdout := stdout.decode():
        LOGGER.info(f"{info} successful!")
        LOGGER.info(f"{stdout}")
    if stderr:
        LOGGER.error(f"error while running {info}")
        LOGGER.info(f"{stderr}")


from Exon import updater as u

# run the backup daily at 1:00
twhen = datetime.datetime.strptime("01:00", "%H:%M").time()
j = u.job_queue
cronjob = j.run_daily(callback=backup_db, name="database backups", time=twhen)
