import yadisk
import os
import datetime as dt

def upload(app):
    app.change_synch_label("Uploading...")
    y = False
    with open("ya_id.txt", "r") as f:
        tok = f.read()
    y = yadisk.YaDisk(token=tok)
    app.write_to_log(y.check_token()) # Проверим токен
    y.upload(app.Data_base_file, "/TSH/techsupport_base", overwrite=True)
    app.change_synch_label("Up to date")


def download():
    global app
    try:
        with open("ya_id.txt", "r") as f:
            tok = f.read()
        y = yadisk.YaDisk(token=tok)
        # Download "/some-file-to-download.txt" to "downloaded.txt"
        y.download("/TSH/techsupport_base", "techsupport_base")
        return True
    except yadisk.exceptions.PathNotFoundError:
        return False
    except ConnectionError:
        app.write_to_log("connection error")
        return False
    

def is_cloud_more_fresh(app):
    try:
        with open("ya_id.txt", "r") as f:
            tok = f.read()
        y = yadisk.YaDisk(token=tok)

        resobj = y.get_meta("/TSH/techsupport_base")
        file_mode_time_epoch = os.path.getmtime(app.Data_base_file)
        file_mode_time = dt.datetime.utcfromtimestamp(file_mode_time_epoch)

        print(f"{file_mode_time=}")
        print(f"{resobj['modified'].replace(tzinfo=None)=}")
        time_delta = resobj["modified"].replace(tzinfo=None) - file_mode_time

        if time_delta >= dt.timedelta(seconds=100):

            app.write_to_log("CLoud is more fresh")
            return "Cloud"
        else:
            app.write_to_log("Disk is more fresh")
            return "Disk"
    except yadisk.exceptions.PathNotFoundError:
        app.write_to_log("PathNotFoundError")
        return "Empty cloud"
    except FileNotFoundError:
        app.write_to_log("Filenotfound")
        return "Empty disk"
    except Exception as e:
        app.write_to_log(f"{e=}")
        app.change_sync_mode("event", False)
        return "Error"

# if __name__ == "__main__":
#     file_mode_time_epoch = os.path.getmtime("techsupport_base")
#     file_mode_time = dt.datetime.utcfromtimestamp(file_mode_time_epoch)
#     with open("ya_id.txt", "r") as f:
#         tok = f.read()
#     y = yadisk.YaDisk(token=tok)
#     try:
#         resobj = y.get_meta("/TSH/techsupport_base")
#         print(resobj["modified"].replace(tzinfo=None), "resobj")
#         print(file_mode_time, "file_mode_time")
#         print(dt.timedelta(seconds=5), "dt.timedelta(seconds=5)")
#         print(resobj["modified"].replace(tzinfo=None) - file_mode_time, 'resobj["modified"].replace(tzinfo=None) - file_mode_time')
#         print(file_mode_time-resobj["modified"].replace(tzinfo=None), 'file_mode_time-resobj["modified"].replace(tzinfo=None)')
#         if resobj["modified"].replace(tzinfo=None) - file_mode_time < dt.timedelta(seconds=5):
#             print ("True")
#         else:
#             print ("False")
#     except yadisk.exceptions.PathNotFoundError:
#         print ("exception")
